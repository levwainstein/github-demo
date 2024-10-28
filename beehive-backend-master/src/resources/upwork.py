import io
import json
from datetime import timedelta
import time
import csv

from flask import current_app, request, Response, stream_with_context
from flask.views import MethodView
from sqlalchemy.sql import and_

from ..models.user import User
from ..models.upwork import UpworkAuthToken, UpworkDiary
from ..models.diary_log import DiaryLog

from ..utils.db import db
from ..utils.auth import inner_auth, admin_jwt_required
from ..utils.upwork import UpworkClient, save_upwork_diaries, update_work_records_net_duration
from ..utils.marshmallow import parser
from ..utils.errors import abort

from ..schemas.upwork import UpworkWorkdiaryRequestSchema, UpworkDiaryResponseSchema, UpworkCallbackRequestSchema, UpworkCallbackResponseSchema, UpworkCostReportRequestSchema

class UpworkWorkDiary(MethodView):
    @inner_auth
    @parser.use_args(UpworkWorkdiaryRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, start_date, end_date):
        """
        Utility endpoint for querying upwork diaries and calculating corresponding work recods net duration
        used for past data to seed the db
        """
        # fetch diary for specific date from upwork api
        delta = timedelta(days=1)
        all_upwork_diaries = []
        while start_date <= end_date:
            upwork_diaries = save_upwork_diaries(start_date)
            if upwork_diaries:
                update_work_records_net_duration(upwork_diaries)
                # to update session with related objects
                for d in upwork_diaries:
                    db.session.refresh(d)
                
                all_upwork_diaries.extend(upwork_diaries)

            start_date += delta
            time.sleep(5)               ## without this delay we get a 'token expired' error fromupwork client

            db.session.expunge_all()    # otherwise tests raise sqlalchemy.orm.exc.DetachedInstanceError
        
        if not all_upwork_diaries:
            current_app.logger.error('fetching upwork diaries failed for all given dates')
            abort(500)

        return UpworkDiaryResponseSchema(many=True).jsonify(all_upwork_diaries)


class UpworkCallback(MethodView):
    @parser.use_args(UpworkCallbackRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, code=None, state=None):
        # support for implicit grant
        if not code:
            msg = f'code parameter is not found in callback url query string: {request.url}, copy #access_token fragment in url if using implicit grant'
            current_app.logger.error(msg)
            return abort(400, description=msg)

        request_url = f'{current_app.config["UPWORK_CALLBACK_URL"]}?code={code}'
        if state:
            request_url += f'&state={state}'


        ## for local testing we need to change the url schema otherwise upwork raise an error
        if 'UPWORK_LOCAL_MODE' in current_app.config and current_app.config['UPWORK_LOCAL_MODE'] is True:
            import os, urllib
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            parsed_url = urllib.parse.urlparse(request.url)
            production_callback_url = urllib.parse.urlparse(current_app.config['UPWORK_CALLBACK_URL'])
            request_url = parsed_url._replace(
                scheme=production_callback_url.scheme,
                netloc=production_callback_url.netloc,
                path=production_callback_url.path
            ).geturl()
        

        # authorization code grant
        client = UpworkClient(
            current_app.config['UPWORK_CONSUMER_KEY'],
            current_app.config['UPWORK_CONSUMER_SECRET'],
            current_app.config['UPWORK_CALLBACK_URL']
        )

        token = client.get_access_token(request_url)
        UpworkAuthToken.insert_or_update(
            token['access_token'],
            token['refresh_token'],
            token['token_type'],
            token['expires_in'],
            token['expires_at']
        )
        db.session.commit()
        return UpworkCallbackResponseSchema().jsonify(token)

class UpworkCostReport(MethodView):
    @admin_jwt_required
    @parser.use_args(UpworkCostReportRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, start_date, end_date):
        """
        endpoint for creating a CSV that generates the cost per work record for a given date range 
        (with work ID, name, contributor ID & name, project name, skills, and time). 
        """

        def generate_cost_report(start_date, end_date):

            current_app.logger.info(f'getting upwork report for dates {start_date.strftime("%Y%m%d")}-{end_date.strftime("%Y%m%d")}')

            header = [
                'ID',
                'Upwork user id',
                'Upwork user name',
                'Upwork interval',
                'Upwork duration',
                'Upwork cost',
                'Net duration',
                'Work Record id', 
                'Work id', 
                'Task id', 
                'Task name', 
                'User id', 
                'User name', 
                'Project', 
                'Skills',
                'Work Record interval',
                'Work Record duration',
            ]
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_ALL)
            writer.writerow(header)

            # main query for all upwork diaries in date range
            upwork_diary_items = UpworkDiary.query \
                .filter(
                    and_(
                        db.func.date(UpworkDiary.rounded_utc_start_time) <= end_date,
                        db.func.date(UpworkDiary.rounded_utc_end_time) >= start_date
                    ) \
                ) \
                .group_by(UpworkDiary.id) \
                .order_by(UpworkDiary.id.asc()) \
                .all()

            for upwork_diary in upwork_diary_items:
            
                upwork_diary_id = upwork_diary.id
                upwork_user_id = upwork_diary.upwork_user_id
                upwork_user_name = upwork_diary.upwork_user_name
                upwork_interval = upwork_diary.duration_string
                upwork_diary_duration = str(timedelta(minutes=upwork_diary.duration_min))

                upwork_diary_work_records = [wrud.work_record for wrud in upwork_diary.work_record_upwork_diaries]
                if not upwork_diary_work_records:
                    # try the user details if we recognize it
                    try:
                        user = User.query.filter(User.upwork_user == upwork_user_id).first()
                        user_id = user.id if user else None
                        user_name = user.name if user else None
                    except:
                        user_id = None
                        user_name = None

                    row = [
                        upwork_diary_id,
                        upwork_user_id,
                        upwork_user_name,
                        upwork_interval,
                        upwork_diary_duration,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        user_id,
                        user_name,
                        None,
                        None,
                        None,
                        None
                    ]
                    writer.writerow(row)
                    continue

                for work_record in upwork_diary_work_records:
                    work_record_id = work_record.id
                    work_id = work_record.work_id
                    task_id = work_record.work.task_id
                    task_name = work_record.work.task.name

                    user_id = work_record.user_id
                    user_name = work_record.user.name
                    
                    project = ';'.join([t.name for t in work_record.work.tags])
                    skills = ';'.join([s.name for s in work_record.work.skills])

                    work_record_interval = f'{work_record.utc_start_time.strftime("%Y/%m/%d %H:%M")} - {work_record.utc_end_time.strftime("%Y/%m/%d %H:%M")}'
                    work_record_duration = str(timedelta(seconds=work_record.duration_seconds))
                    
                    upwork_cost = str([wrud.upwork_cost for wrud in upwork_diary.work_record_upwork_diaries if wrud.work_record_id == work_record_id][0])
                    net_duration = [str(timedelta(seconds=wrud.upwork_duration_seconds)) for wrud in upwork_diary.work_record_upwork_diaries if wrud.work_record_id == work_record_id][0]

                    row = [
                        upwork_diary_id,
                        upwork_user_id,
                        upwork_user_name,
                        upwork_interval,
                        upwork_diary_duration,
                        upwork_cost,
                        net_duration,
                        work_record_id,
                        work_id,
                        task_id,
                        task_name,
                        user_id,
                        user_name,
                        project,
                        skills,
                        work_record_interval,
                        work_record_duration
                    ]
                    writer.writerow(row)
            
            # extra query for all external manual diary logs that originate elsewhere than upwork
            manual_diary_items = DiaryLog.query \
                .filter(
                    and_(
                        db.func.date(DiaryLog.date) <= end_date,
                        db.func.date(DiaryLog.date) >= start_date
                    ) \
                ) \
                .order_by(DiaryLog.id.asc()) \
                .all()

            for manual_diary in manual_diary_items:
                row = [
                    manual_diary.id,
                    None,
                    None,
                    None,
                    manual_diary.date,
                    manual_diary.cost,
                    str(timedelta(minutes=int(manual_diary.duration_hours*60))),
                    None,
                    None,
                    None,
                    manual_diary.text,
                    manual_diary.user_role.email,
                    None,
                    manual_diary.project,
                    None,
                    None,
                    None
                ]
                writer.writerow(row)

            return output.getvalue()

        return Response(
            stream_with_context(generate_cost_report(start_date, end_date)),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=cost_{start_date.strftime("%Y%m%d")}-{end_date.strftime("%Y%m%d")}.csv'}
        )

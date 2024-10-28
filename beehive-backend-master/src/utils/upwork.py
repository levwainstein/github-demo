from datetime import datetime, timedelta
import requests
from sqlalchemy import and_

from flask import current_app

from upwork import Config, Client
from upwork.routers import graphql
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

from ..utils.db import db
from ..utils.email import send_admin_unrecognized_users_email

from ..schemas.upwork import UpworkDiarySchema

from ..models.upwork import UpworkAuthToken, UpworkDiary, WorkRecordUpworkDiary
from ..models.user import User
from ..models.work_record import WorkRecord

UPWORK_MARKETPLACE_HOURLY_FEE = 0.05

class UpworkClient():

    config = None
    client = None
    organization_id = None

    UPWORK_ACCESS_TOKEN_REQUEST_URL = 'https://www.upwork.com/api/v3/oauth2/token'

    def __init__(self, consumer_key, consumer_secret, redirect_url, token=None):
        if token:
            self.config = Config({
                'client_id': consumer_key,
                'client_secret': consumer_secret,
                'token': token,
                'redirect_uri': redirect_url
        })
        else:
            self.config = Config({
                'client_id': consumer_key,
                'client_secret': consumer_secret,
                'redirect_uri': redirect_url
            })

        self.client = Client(self.config)
        self.config = self.client.get_actual_config() ## used to make sure token is refreshed
        if hasattr(self.config, 'token') and self.config.token:
            token = UpworkAuthToken.insert_or_update(
                self.config.token['access_token'],
                self.config.token['refresh_token'],
                self.config.token['token_type'],
                self.config.token['expires_in'],
                self.config.token['expires_at']
            )
            db.session.commit()
            self.config.token = self.refresh_token(token=self.config.token)

        # organization id is optional, flow should not break if this is unavailable
        try:
            self.organization_id = self.get_organization_id()
        except InvalidGrantError as e:
            current_app.logger.warn(f'Upwork invalid grant error while fetching organization id: {str(e)}')

    def refresh_token(self, token=None, code=None):
        """
        Refreshes token if expired and saves new token to database. 
        Does not use the python SDK but simple requests library because SDK does not correctly refresh the token.
        Args:
            token (dict or None): invalid token to refresh or None if this doesn't exist
            code (str or None): code for authorization or none
        Returns:
            token (dict or None): result of refresh token or None on error
        """
        if token and token.get('refresh_token', None):
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': token['refresh_token'],
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret
            }
        elif code:
            payload = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.config.redirect_uri,
                'client_id': self.config.client_id
            }
        else:
            current_app.logger.error('Cannot get acess token without refresh token or authorization code')
            return None

        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }

        res = requests.post(
            url=f'{self.UPWORK_ACCESS_TOKEN_REQUEST_URL}',
            data=payload,
            headers=headers
        )
        if res.status_code != 200:
            current_app.logger.error(f'Error in requesting access token from upwork: {res.text}')
            return False
        
        token_json = res.json()
        token = UpworkAuthToken.insert_or_update(
            token_json['access_token'],
            token_json['refresh_token'],
            token_json['token_type'],
            token_json['expires_in'],
            token_json.get('expires_at', datetime.utcnow().timestamp() + token_json['expires_in'])
        )
        db.session.commit()

        return token_json


    def get_access_token(self, redirect_url):
        """
        Gets upwork access token as part of upwork authorization process.
        Args:
            redirect_url (str): redirect url to upwork callback endpoint. 
                            Expected query string parameters are 'code' and 'state'.
        Returns:
            access_token (dict): token dictionary containing fields access_token (str), refresh_token (str), token_type (str), expires_in (int), expires_at (decimal).
        """
        current_app.logger.info(f"Retrieving upwork access and refresh tokens.... url {redirect_url}")
        return self.client.get_access_token(redirect_url)

    def get_organization_id(self):
        """
        Get upwork organization id via companySelector GraphQL schema.
        Returns:
            organization_id (str) | None: organization identifier or None if such was not found.
        """
        query = """
            query {
                companySelector {
                    items {
                        title
                        organizationId
                    }
                }
            }
        """
        json_data = self.execute_graphql_query(query)
        if not json_data:
            current_app.logger.error("Error querying upwork for organization id")
            return None
        companies_json = json_data.get('companySelector').get('items')
        for company in companies_json:
            if company.get('title') == 'Beehive Software Inc.':
                return company.get('organizationId')
        
        return None

    def execute_graphql_query(self, query, variables={}):
        """
        Execute graphQL query in upwork api. 
        If organization_id is present as class property it will update the X-Upwork-API-TenantId header.
        Args:
            query (str): string representing the query (see docs https://www.upwork.com/developer/documentation/graphql/api/docs/index.html). 
            variables (dict): optional dictionary of variables for the given query.
        Returns:
            data (dict) | None: dict of response or None if there was a client error.
        """
        if self.organization_id:
            self.client.set_org_uid_header(self.organization_id)
        res = graphql.Api(self.client).execute({'query': query, 'variables': variables})
        if not res.get('data', None):
            current_app.logger.error(f'Error querying graphql: {res}')
            return None
        return res.get('data', None)

    def get_work_diary(self, date=None, company_id=None):
        """
        Get upwork work diaries from upwork client for a specific date for given company. 
        If organization_id is present as class property it will update the X-Upwork-API-TenantId header.
        Args:
            date (str): string representing date in '%Y%m%d' format, if not present defaults to yesterday.
            company_id (str): string identifier of upwork company id, if not present will be taken from app configuration.
        Returns:
            data (UpworkDiarySchema) | None: parsed response of work diaries or None if there was a client error.
        """
        if not date:
            date = datetime.utcnow() - timedelta(1)
        date = date.strftime('%Y%m%d')

        company_id = company_id or current_app.config['UPWORK_BEEHIVE_COMPANY_ID']
        if not company_id:
            current_app.logger.error('missing upwork company id from configuration')
            return None

        current_app.logger.info(f'Getting work diaries for company {company_id} for date {date}')

        query = """
            query workDiaryCompany($workDiaryCompanyInput: WorkDiaryCompanyInput!) {
                workDiaryCompany(workDiaryCompanyInput: $workDiaryCompanyInput) {
                    total
                    snapshots {
                        contract {
                            id
                            contractTitle
                        }
                        user {
                            id
                            name
                        }
                        duration
                        durationInt
                        task {
                            id
                            code
                            description
                            memo
                        }
                        time {
                            trackedTime
                            manualTime
                            overtime
                            firstWorked
                            lastWorked
                            firstWorkedInt
                            lastWorkedInt
                            lastScreenshot
                        }
                        screenshots {
                            activity
                            screenshotUrl
                            screenshotImage
                            screenshotImageLarge
                            screenshotImageMedium
                            screenshotImageThumbnail
                            hasScreenshot
                            hasWebcam
                            webcamUrl
                            webcamImage
                            webcamImageThumbnail
                            flags {
                                hideScreenshot
                                downSampleScreenshots
                            }
                        }
                    }
                }
            }
        """

        variables = {
            "workDiaryCompanyInput": {
                "companyId": company_id,
                "date": date
            }
        }

        work_diary = self.execute_graphql_query(query, variables)
        if not work_diary or not work_diary.get('workDiaryCompany', None):
            current_app.logger.error(f'unrecognized work diary response: {work_diary}')
            return None


        return UpworkDiarySchema().load(work_diary.get('workDiaryCompany'))
        

def save_upwork_diaries(date):
    """
    Wrapper utility method that gets upwork diaries from upwork client and inserts/updates our database with the diaries. 
    This will also send an admin email about users that appear in the upwork response but are not registered in our system.
    Args:
        date (str): string representing date in '%Y%m%d' format.
    Returns:
        upwork_diaries (UpworkDiary[]) | None: array of upwork diaries data model or None if there was an error.
    """
    token = UpworkAuthToken.get_recent_token()
    client = UpworkClient(
        current_app.config['UPWORK_CONSUMER_KEY'],
        current_app.config['UPWORK_CONSUMER_SECRET'],
        current_app.config['UPWORK_CALLBACK_URL'],
        token
    )
    # fetch diary for specific date from upwork api
    work_diary = client.get_work_diary(date)
    if not work_diary:
        current_app.logger.error(f'error retrieveing work diary for {date}')
        return None
    
    upwork_diaries = []
    unrecognized_users = []
    for snapshot in work_diary.get('snapshots', []):
        upwork_user_id = snapshot.get('user').get('id') if snapshot.get('user', None) else None
        upwork_user_name = snapshot.get('user').get('name') if snapshot.get('user', None) else None
        start_time_epoch_ms = int(snapshot.get('time').get('first_worked_int')) * 1000
        end_time_epoch_ms = int(snapshot.get('time').get('last_worked_int')) * 1000
        duration_min = snapshot.get('duration_int', None)
        description = snapshot.get('task', None).get('memo', None) if snapshot.get('task', None) else None
        
        # match upwork user to beehive user, to find corresponding work record, otherwise append to unknowns list (for admin email)
        user_id = None
        if upwork_user_id:
            user = User.query.filter_by(upwork_user=upwork_user_id).first()
            if user:
                user_id = user.id
            
        if not user_id:
            unrecognized_users.append({
                'id': upwork_user_id,
                'name': upwork_user_name,
                'error': 'user not found'
            })

        # create diary record in db
        upwork_diary = UpworkDiary.insert_or_update(
            user_id,
            upwork_user_id,
            upwork_user_name,
            start_time_epoch_ms,
            end_time_epoch_ms,
            duration_min,
            description
        )
        upwork_diaries.append(upwork_diary)

    if unrecognized_users:
        send_admin_unrecognized_users_email(unrecognized_users)

    db.session.commit()
    return upwork_diaries

def update_work_records_net_duration(upwork_diaries):
    if not upwork_diaries:
        current_app.logger.info(f'No upwork diaries given to process for work records duration calculation')
        return
        
    for upwork_diary in upwork_diaries:
        user_id = upwork_diary.user_id
        if not user_id: 
            current_app.logger.info(f'Skipping upwork diary {upwork_diary.id} with no beehive user id')
            continue

        # match diary record to beehive work record
        matched_work_records = db.session.query(WorkRecord) \
            .filter(
                WorkRecord.user_id == user_id,
                and_(
                    WorkRecord.start_time_diff_sec(upwork_diary.utc_start_time) < 172800,
                    WorkRecord.end_time_diff_sec(upwork_diary.utc_end_time) < 172800
                )
            ) \
            .order_by(WorkRecord.start_time_diff_sec(upwork_diary.utc_start_time).asc()) \
            .all()

        for work_record in matched_work_records:
            # work records in progress do not have end time
            current_work_record_end_time_utc = work_record.utc_end_time
            if not current_work_record_end_time_utc:
                current_work_record_end_time_utc = datetime.utcnow()

            # calculate intersection between the upwork diary and work record time ranges
            work_record_net_duration_seconds = int((min(current_work_record_end_time_utc, upwork_diary.utc_end_time) - max(work_record.utc_start_time, upwork_diary.utc_start_time)).total_seconds())
            if work_record_net_duration_seconds > 0:
                current_app.logger.info(f'found corresponding work record ({work_record.id}) for diary record ({upwork_diary.id}). net seconds {work_record_net_duration_seconds}')
                                
                # calculate upwork time, as they calculate to the closest 10-minute segment
                work_record_upwork_duration_seconds = int((min(current_work_record_end_time_utc, upwork_diary.rounded_utc_end_time) - max(work_record.utc_start_time, upwork_diary.rounded_utc_start_time)).total_seconds())

                work_record_cost = None
                work_record_upwork_cost = None
                if upwork_diary.user.price_per_hour:
                    work_record_cost = float(upwork_diary.user.price_per_hour) * work_record_net_duration_seconds / 60 / 60
                    work_record_upwork_cost = float(upwork_diary.user.price_per_hour) * work_record_upwork_duration_seconds / 3600 * (1 + UPWORK_MARKETPLACE_HOURLY_FEE)
                
                WorkRecordUpworkDiary.insert_or_update(
                    work_record.id,
                    upwork_diary.id,
                    work_record_net_duration_seconds,
                    work_record_cost,
                    work_record_upwork_duration_seconds,
                    work_record_upwork_cost
                )

    db.session.commit()

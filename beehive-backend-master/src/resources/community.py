import decimal
from flask.views import MethodView
from ..models.upwork import WorkRecordUpworkDiary

from ..resources.shared_queries import get_contributor_stats


from ..models.skill import Skill, UserSkill
from ..models.task import Task, TaskStatus
from ..models.user import User
from ..models.work import Work, WorkStatus
from ..models.work_record import WorkOutcome, WorkRecord
from ..schemas.community import SkillBreakdownResponseSchema, CommunityContributorsResponseSchema
from ..utils.auth import admin_jwt_required
from ..utils.db import db
from sqlalchemy import and_, or_
from sqlalchemy.sql import label

class SkillsBreakdown(MethodView):
    # get all supported packages
    @admin_jwt_required
    def get(self):
        """
        Get skills breakdown
        """
        results = db.session.query(Skill.name, db.func.count()) \
            .outerjoin(UserSkill, UserSkill.skill_id == Skill.id) \
            .group_by(Skill.name) \
            .all()
        breakdown = [{'name': r[0], 'count': r[1]} for r in results]
        return SkillBreakdownResponseSchema().jsonify({
            'breakdown': breakdown
        })

class ContributorsBreakdown(MethodView):
    @admin_jwt_required
    def get(self):

        """
        Get community contributors breakdown
        """

        contributors = []
        users = db.session.query(User).all()
        for user in users:
            last_work_record = WorkRecord.query \
                .filter(WorkRecord.user_id == user.id) \
                .filter(or_(WorkRecord.outcome.notin_([WorkOutcome.SKIPPED]), WorkRecord.outcome.is_(None))) \
                .order_by(WorkRecord.id.desc()).first()
            
            first_work_record = WorkRecord.query \
                .filter(WorkRecord.user_id == user.id) \
                .order_by(WorkRecord.id.asc()).first()
            
            work_record_upwork_diary_stats = WorkRecordUpworkDiary.query \
                .join(WorkRecord, WorkRecordUpworkDiary.work_record_id == WorkRecord.id) \
                .filter(WorkRecord.user_id == user.id) \
                .filter(WorkRecordUpworkDiary.net_duration_seconds != None) \
                .add_columns(
                    label(
                        'work_records_net_duration_seconds',
                        db.func.sum(WorkRecordUpworkDiary.net_duration_seconds)
                    ),
                    label(
                        'work_records_cost',
                        db.func.sum(WorkRecordUpworkDiary.cost)
                    )
                ) \
                .group_by(WorkRecordUpworkDiary.id, WorkRecord.work_id).all()
            
            billable_hours_availabilty_ratio = 0
            if len(work_record_upwork_diary_stats) > 0 and first_work_record != None and last_work_record != None:
                weeks = ((last_work_record.utc_end_time or last_work_record.utc_start_time) - first_work_record.utc_start_time).days / 7 
                average_billable_per_week = sum(x.work_records_net_duration_seconds or 0 for x in work_record_upwork_diary_stats) / max(decimal.Decimal(weeks), 1)
                average_billable_per_week_hours = average_billable_per_week / 60 / 60
                if user.availability_weekly_hours:
                    billable_hours_availabilty_ratio = average_billable_per_week_hours / user.availability_weekly_hours * 100

            user_stats = get_contributor_stats(user)
            user_stats['weekly_availability'] = user.availability_weekly_hours
            user_stats['billable_hours_ratio'] = billable_hours_availabilty_ratio

            contributors.append(user_stats)

        return CommunityContributorsResponseSchema().jsonify({
            'breakdown': contributors
        })

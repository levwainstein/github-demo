from ..utils.marshmallow import ma

class SkillBreakdownSchema(ma.Schema):

    name = ma.String()
    count = ma.Integer()

class SkillBreakdownResponseSchema(ma.Schema):
    breakdown = ma.List(ma.Nested(SkillBreakdownSchema))

class CommunityContributorResponseSchema(ma.Schema):
    name = ma.String()
    country = ma.String()
    active = ma.Boolean(required=False)
    last_work = ma.String(data_key='lastWork')
    last_engagement = ma.String(data_key='lastEngagement')
    reserved_works = ma.Integer(data_key='reservedWorks')
    works_in_review = ma.Integer(data_key='worksInReview')
    billable_hours_ratio = ma.Integer(data_key='billableHoursRatio')
    weekly_availability = ma.Integer(data_key='weeklyAvailability')
    hourly_rate = ma.Decimal(data_key='hourlyRate', places=2, as_string=True)
    projects = ma.List(ma.String())
    skills = ma.List(ma.String())

class CommunityContributorsResponseSchema(ma.Schema):
    breakdown = ma.List(ma.Nested(CommunityContributorResponseSchema))
    

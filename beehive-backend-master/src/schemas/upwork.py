from marshmallow.validate import Length
from marshmallow.exceptions import ValidationError
from datetime import datetime

from ..utils.marshmallow import BeehiveSchemaMixin, ma

class UpworkCallbackRequestSchema(ma.Schema):
    code = ma.String(required=False, validate=Length(min=4))
    state = ma.String(required=False, data_key='state')

class UpworkAuthTokenSchema(ma.Schema):
    access_token = ma.String(data_key='access_token')
    refresh_token = ma.String(data_key='refresh_token')
    token_type = ma.String(data_key='token_type')
    expires_in = ma.Integer(data_key='expires_in')
    expires_at = ma.String(data_key='expires_at')

class UpworkCallbackResponseSchema(UpworkAuthTokenSchema, BeehiveSchemaMixin):
    pass

class UpworkWorkdiaryRequestSchema(ma.Schema):
    start_date = ma.Date(format='%Y%m%d', data_key='startDate')
    end_date = ma.Date(format='%Y%m%d', data_key='endDate')

class UpworkDiaryResponseSchema(ma.Schema, BeehiveSchemaMixin):
    id = ma.Integer(data_key='id')
    user_id = ma.String(data_key='userId')
    upwork_user_id = ma.String(data_key='upworkUserId')
    upwork_user_name = ma.String(data_key='upworkUserName')
    start_time_epoch_ms = ma.Integer(data_key='startTimeEpochMs')
    end_time_epoch_ms = ma.Integer(data_key='endTimeEpochMs')
    duration_min = ma.Integer(data_key='durationMin')
    description = ma.String(data_key='description')
    start_time = ma.Function(lambda obj: datetime.fromtimestamp(obj.start_time_epoch_ms / 1000).strftime('%Y-%m-%d %H:%M:%S'), data_key='startTime')
    end_time = ma.Function(lambda obj: datetime.fromtimestamp(obj.end_time_epoch_ms / 1000).strftime('%Y-%m-%d %H:%M:%S'), data_key='endTime')
    work_records = ma.Function(lambda obj: [udwr.work_record_id for udwr in obj.work_record_upwork_diaries], data_key='workRecords')


class DictOrListField(ma.Field):
    """
    Some upwork diary attributes (like users, contracts) might return as list or dict
    """
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, dict) or isinstance(value, list):
            return value
        else:
            raise ValidationError('Field should be dict or list')

class UpworkSnapshotContractSchema(ma.Schema):
    id = ma.String(data_key='id')
    user_id = ma.String(data_key='userId')
    contract_title = ma.String(data_key='contractTitle')

class UpworkSnapshotUserSchema(ma.Schema):
    name = ma.String(data_key='name')
    id = ma.String(data_key='id')
    portrait_url = ma.String(data_key='portraitUrl')

class UpworkSnapshotTaskSchema(ma.Schema):
    id = ma.String(data_key='id', allow_none=True, load_default=None)
    code = ma.String(data_key='code', allow_none=True, load_default=None)
    description = ma.String(data_key='description', allow_none=True, load_default=None)
    memo = ma.String(data_key='memo', allow_none=True, load_default=None)

class UpworkSnapshotTimeSchema(ma.Schema):
    tracked_time = ma.Integer(data_key='trackedTime')
    manual_time = ma.Integer(data_key='manualTime')
    overtime = ma.Integer(data_key='overtime')
    first_worked = ma.String(data_key='firstWorked')
    last_worked = ma.String(data_key='lastWorked')
    first_worked_int = ma.Integer(data_key='firstWorkedInt')
    last_worked_int = ma.Integer(data_key='lastWorkedInt')
    last_screenshot = ma.String(data_key='lastScreenshot')

class UpworkScreenshotFlagSchema(ma.Schema):
    hide_screenshot = ma.Boolean(data_key='hideScreenshot', falsy = {0, '', 'OFF', 'N', 'Off', 'f', 'no', 'False', 'n', 'NO', 'FALSE', 'off', 'false', 'No', '0', 'F'})
    down_sample_screenshots = ma.Boolean(data_key='downSampleScreenshots', falsy = {0, '', 'OFF', 'N', 'Off', 'f', 'no', 'False', 'n', 'NO', 'FALSE', 'off', 'false', 'No', '0', 'F'})

class UpworkScreenshotSchema(ma.Schema):
    activity = ma.Integer(data_key='activity')
    flags = DictOrListField(keys=ma.String, values=ma.Nested(UpworkScreenshotFlagSchema), data_key='flags', required=False, allow_none=True, allow_blank=True)
    has_screenshot = ma.Boolean(data_key='hasScreenshot', falsy = {0, '', 'OFF', 'N', 'Off', 'f', 'no', 'False', 'n', 'NO', 'FALSE', 'off', 'false', 'No', '0', 'F'})
    screenshot_url = ma.String(data_key='screenshotUrl', allow_none=True)
    screenshot_img = ma.String(data_key='screenshotImage', allow_none=True)
    screenshot_img_lrg = ma.String(data_key='screenshotImageLarge', allow_none=True)
    screenshot_img_med = ma.String(data_key='screenshotImageMedium', allow_none=True)
    screenshot_img_thmb = ma.String(data_key='screenshotImageThumbnail', allow_none=True)
    has_webcam = ma.Boolean(data_key='hasWebcam', falsy = {0, '', 'OFF', 'N', 'Off', 'f', 'no', 'False', 'n', 'NO', 'FALSE', 'off', 'false', 'No', '0', 'F'})
    webcam_url = ma.String(data_key='webcamUrl', allow_none=True)
    webcam_img = ma.String(data_key='webcamImage', allow_none=True)
    webcam_img_thmb = ma.String(data_key='webcamImageThumbnail', allow_none=True)

class UpworkSnapshotSchema(ma.Schema):
    contract = ma.Nested(UpworkSnapshotContractSchema, data_key='contract')
    user = ma.Nested(UpworkSnapshotUserSchema, data_key='user')
    duration = ma.String(data_key='duration', required=False)
    duration_int = ma.Integer(data_key='durationInt', required=False)
    task = ma.Nested(UpworkSnapshotTaskSchema, data_key='task', allow_none=True, load_default=None)
    time = ma.Nested(UpworkSnapshotTimeSchema, data_key='time')
    screenshots = ma.List(ma.Nested(UpworkScreenshotSchema), data_key='screenshots', allow_none=True)

class UpworkDiarySchema(ma.Schema):
    id = ma.Integer(data_key='id')
    total = ma.Integer(data_key='total', required=True)
    snapshots = ma.List(ma.Nested(UpworkSnapshotSchema), data_key='snapshots', required=True)

class UpworkCostReportRequestSchema(ma.Schema):
    start_date = ma.Date(format='%Y%m%d', data_key='startDate', required=True)
    end_date = ma.Date(format='%Y%m%d', data_key='endDate', required=True)
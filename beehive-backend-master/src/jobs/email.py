from boto3 import Session as boto_session
from flask import current_app

from ..models.user import User
from ..utils.metrics import user_send_email_exception, admin_send_email_exception
from ..utils.rq import rq


@rq.job('high', timeout=30, result_ttl=3600)
@user_send_email_exception.count_exceptions()
def user_send_email(user_id, email_type, subject, body):
    current_app.logger.info(f'sending user {user_id} email of type "{email_type}"')

    # find user
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise Exception('user not found')

    # send email
    try:
        session = boto_session(
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY'],
            region_name=current_app.config['AWS_REGION_NAME']
        )
        client = session.client('ses')

        res = client.send_email(
            Source=current_app.config['EMAIL_NOTIFICATION_SOURCE_ADDRESS'],
            Destination={
                'ToAddresses': [user.email]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Html': {
                        'Data': body
                    }
                }
            }
        )

        split_recipient = user.email.split('@', 1)
        redacted_recipient = '@'.join([split_recipient[0][:2] + '***', split_recipient[1]])
        current_app.logger.info(f'successfully sent email of type "{email_type}" to {redacted_recipient} with message id: "{res["MessageId"]}"')
    except Exception as ex:
        current_app.logger.error(f'failed to send "{email_type}" email with error: {str(ex)}')



@rq.job('high', timeout=30, result_ttl=3600)
@admin_send_email_exception.count_exceptions()
def admin_send_email(email_type, subject, body):
    email_address = current_app.config['EMAIL_NOTIFICATION_ADMIN_ADDRESS']
    current_app.logger.info(f'sending admin {email_address} email of type "{email_type}"')

    # send email
    try:
        session = boto_session(
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY'],
            region_name=current_app.config['AWS_REGION_NAME']
        )
        client = session.client('ses')

        res = client.send_email(
            Source=current_app.config['EMAIL_NOTIFICATION_SOURCE_ADDRESS'],
            Destination={
                'ToAddresses': [email_address]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Html': {
                        'Data': body
                    }
                }
            }
        )

        current_app.logger.info(f'successfully sent email of type "{email_type}" to {email_address} with message id: "{res["MessageId"]}"')
    except Exception as ex:
        current_app.logger.error(f'failed to send "{email_type}" email with error: {str(ex)}')

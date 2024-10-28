from flask import current_app

from ..utils.email import send_user_activation_email, send_user_reset_password_email


def activation_email(user_id: str, activation_token: str):
    # add base url from config
    activation_url = \
        f'{current_app.config["FRONTEND_BASE_URL"]}/register/activate?c={activation_token}'

    # send email
    send_user_activation_email(user_id, activation_url)


def reset_password_email(user_id: str, reset_token: str):
    # add base url from config
    reset_url = \
        f'{current_app.config["FRONTEND_BASE_URL"]}/reset/change?c={reset_token}'

    # send email
    send_user_reset_password_email(user_id, reset_url)

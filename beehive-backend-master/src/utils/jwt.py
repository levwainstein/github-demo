from flask_jwt_extended import JWTManager

from .db import db
from .errors import handle_unauthorized
from ..models.revoked_token import RevokedToken


jwt_manager = JWTManager()


@jwt_manager.token_verification_failed_loader
def claims_verification_failed_loader():
    # TODO: log?
    return handle_unauthorized()


@jwt_manager.expired_token_loader
def expired_token_loader(_expired_jwt_header: dict, _expired_jwt_data: dict):
    # TODO: log?
    return handle_unauthorized()


@jwt_manager.invalid_token_loader
def invalid_token_loader(cause):
    # TODO: log?
    return handle_unauthorized()


@jwt_manager.revoked_token_loader
def revoked_token_loader(_jwt_header: dict, _jwt_data: dict):
    # TODO: log?
    return handle_unauthorized()


@jwt_manager.unauthorized_loader
def unauthorized_loader(cause):
    # TODO: log?
    return handle_unauthorized()


# Check if the token jti is revoked
@jwt_manager.token_in_blocklist_loader
def is_token_revoked(_jwt_headers: dict, jwt_data: dict) -> bool:
    jti = jwt_data['jti']

    token = RevokedToken.query.filter_by(token_id=jti).first()
    return token is not None


# Mark a token as revoked (i.e. blacklisted)
def add_revoked_token(jti, user_id):
    token = RevokedToken(jti, user_id)
    db.session.add(token)
    db.session.commit()

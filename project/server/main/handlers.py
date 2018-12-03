from flask_api import status

from project.server.main.api import auth, api_blueprint
from project.server.main.utils import error_response


@api_blueprint.app_errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request_handler(resp):
    return resp.data, status.HTTP_400_BAD_REQUEST


@api_blueprint.app_errorhandler(status.HTTP_404_NOT_FOUND)
def not_found_handler(resp):
    return {'message': 'Not found'}, status.HTTP_404_NOT_FOUND


@auth.error_handler
def token_auth_error():
    """
    Replace 401 auth error with 403 to avoid browser auth popup window.
    :return:
    """
    return error_response(status.HTTP_403_FORBIDDEN)

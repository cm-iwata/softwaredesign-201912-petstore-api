from http import HTTPStatus

from utils.json_util import JsonUtil


def _create_response(status_code, body, headers):
    return {
        'statusCode': status_code,
        'body': body,
        'headers': headers
        }


class HttpResponseUtil:

    @staticmethod
    def bad_request(errors, headers={}):
        return _create_response(HTTPStatus.BAD_REQUEST,
                                JsonUtil.dumps({
                                    'message': errors
                                }),
                                headers)

    @staticmethod
    def conflict(message, headers={}):
        return _create_response(HTTPStatus.CONFLICT,
                                JsonUtil.dumps({
                                    'message': message
                                }),
                                headers)

    @staticmethod
    def created(data, headers={}):
        return _create_response(HTTPStatus.CREATED,
                                JsonUtil.dumps(data),
                                headers)

    @staticmethod
    def not_found(message, headers={}):
        return _create_response(HTTPStatus.NOT_FOUND,
                                JsonUtil.dumps({
                                    'message': message
                                }),
                                headers)

    @staticmethod
    def ok(data, headers={}):
        return _create_response(HTTPStatus.OK, JsonUtil.dumps(data), headers)

    @staticmethod
    def pet_not_found():
        return HttpResponseUtil.not_found('the specified pet was not found')

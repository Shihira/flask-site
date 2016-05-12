# We define exception classes here. When there is an error you want to handle,
# add an exception here without hesitation.

from werkzeug.exceptions import HTTPException

errors_dict = {}

def as_restful_error(except_type):
    errors_dict.update({
            except_type.__name__: { }
        })
    return except_type

class ApiError(HTTPException):
    status_code = 0
    message = ""
    code = 200
    response = None

    def __init__(self, message=""):
        self.message = message

    @property
    def data(self):
        return {
                'status_info': {
                    'code': self.status_code,
                    'message': self.message,
                }
            }

################################################################################
# Define Exceptions Here

@as_restful_error
class AtLeastOneOfArguments(ApiError):
    def __init__(self, args):
        self.status_code = 1
        self.message = 'At least one of {} should be provided'.format(
                ", ".join(args))

@as_restful_error
class CredentialNotFound(ApiError):
    def __init__(self, cred_type, cred_value):
        self.status_code = 2
        self.message = 'Credential ({}) {} is not valid'.format(
                cred_type, cred_value)

@as_restful_error
class PasswordIncorrect(ApiError):
    def __init__(self):
        self.status_code = 3
        self.message = "Password is incorrect"


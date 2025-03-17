class APIError(Exception):
    def __init__(self, status_code: int,code : int, message: str):
        self.code = code
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"APIError(status_code={self.status_code}, code={self.code}, message={self.message})"

def get_error(exc: Exception) -> APIError:
    if isinstance(exc, APIError):
        return exc
    return APIError(status_code=500, code=500, message=f"Unknown Error: {str(exc)}")

def new_error(status_code: int, code: int, message: str) -> APIError:
    return APIError(status_code=status_code, code=code, message=message)

Success = new_error(status_code=200, code=0, message="success")
Forbidden = new_error(status_code=403, code=403, message="Forbidden")
Unauthorized = new_error(status_code=401, code=401, message="Unauthorized")
NotFound = new_error(status_code=404, code=404, message="Not Found")
Conflict = new_error(status_code=409, code=409, message="Conflict")
BadRequest = new_error(status_code=400, code=400, message="Bad Request")
UnprocessableEntity = new_error(status_code=422, code=422, message="Unprocessable Entity")
TooManyRequests = new_error(status_code=429, code=429, message="Too Many Requests")
InternalServerError = new_error(status_code=500, code=500, message="Internal Server Error")
UnknownError = new_error(status_code=500, code=500, message="Unknown Error")



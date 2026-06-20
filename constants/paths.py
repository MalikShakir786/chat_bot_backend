
prefix = "/api/v1"

files_storage = "data/uploads"

class DocumentRoutes:
    UPLOAD = "/documents/upload"
    GET_ALL = "/documents/getall"
    DELETE = "/documents/delete"


class ChatRoutes:
    SEND_MESSAGE = "/chat/send"
    HISTORY = "/chat/history"


class AuthRoutes:
    LOGIN = "/auth/login"
    TOKEN = "/auth/token"
    SIGNUP = "/auth/signup"
    REFRESH = "/auth/refresh"
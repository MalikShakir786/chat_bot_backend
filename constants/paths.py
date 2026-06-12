
prefix = "/api/v1"
class DocumentRoutes:
    UPLOAD = "/documents/upload"
    GET_ALL = "/documents/getall"
    DELETE = "/documents/delete/{document_id}"


class ChatRoutes:
    SEND_MESSAGE = "/chat/send"
    HISTORY = "/chat/history"


class AuthRoutes:
    LOGIN = "/auth/login"
    SIGNUP = "/auth/signup"
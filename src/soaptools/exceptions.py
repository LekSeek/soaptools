class ApplicationException(Exception):
    def __init__(self, message="No message attached"):
        super(ApplicationException, self).__init__(message)
        self.message = message

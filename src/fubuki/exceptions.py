class AlreadyRegistedError(Exception):
    pass

class GearException(Exception):
    pass

class ConnectionClosed(Exception):
    pass

class TemplateError(Exception):
    pass

class TemplateWarning(Warning):
    pass
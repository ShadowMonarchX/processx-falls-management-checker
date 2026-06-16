class ProcessXError(Exception):
    pass


class ParseError(ProcessXError):
    pass


class ValidationError(ProcessXError):
    pass


class WorkbookError(ProcessXError):
    pass


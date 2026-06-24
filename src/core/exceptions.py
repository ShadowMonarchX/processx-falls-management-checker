class ProcessXError(Exception):
    # A shared root type makes it easier to distinguish expected application
    # failures from programming errors during orchestration and logging.
    pass


class ParseError(ProcessXError):
    # Parsing failures usually mean the source document shape changed or the
    # upstream extractor produced text that cannot be normalized safely.
    pass


class ValidationError(ProcessXError):
    # Validation errors are reserved for business-rule violations, not schema
    # issues from third-party SDKs, so callers can decide whether to retry.
    pass


class WorkbookError(ProcessXError):
    # Workbook errors indicate the output file could not be read or written in
    # the expected Excel format.
    pass

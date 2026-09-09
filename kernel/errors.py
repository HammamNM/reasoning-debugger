class ReasoningKernelError(Exception):
    """Base class for all Kernel errors."""
    pass

class InvalidTraceSchemaError(ReasoningKernelError):
    """Raised when trace input does not match the canonical contract."""
    pass

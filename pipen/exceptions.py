"""Provide exception classes"""

class PipenException(Exception):
    """Base exception class for pipen"""

class ProcInputTypeError(PipenException, TypeError):
    """When an unsupported input type is provided"""

class ProcScriptFileNotFound(PipenException, FileNotFoundError):
    """When script file specified as 'file://' cannot be found"""

class ProcOutputNameError(PipenException, NameError):
    """When no name or malformatted output is provided"""

class ProcOutputTypeError(PipenException, TypeError):
    """When an unsupported output type is provided"""

class ProcOutputValueError(PipenException, ValueError):
    """When a malformatted output value is provided"""

class ProcDependencyError(PipenException):
    """When there is something wrong the process dependencies"""

class NoSuchSchedulerError(PipenException):
    """When specified scheduler cannot be found"""

class WrongSchedulerTypeError(PipenException, TypeError):
    """When specified scheduler is not a subclass of Scheduler"""

class NoSuchTemplateEngineError(PipenException):
    """When specified template engine cannot be found"""

class WrongTemplateEnginTypeError(PipenException, TypeError):
    """When specified tempalte engine is not a subclass of Scheduler"""

class ConfigurationError(PipenException):
    """When something wrong set as configuration"""

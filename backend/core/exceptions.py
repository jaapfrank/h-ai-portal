"""
Custom exceptions for the Hoeflon ERP AI system
"""

class HoeflonAIException(Exception):
    """Base exception for Hoeflon AI system"""
    pass

class DatabaseConnectionError(HoeflonAIException):
    """Raised when database connection fails"""
    pass

class QueryExecutionError(HoeflonAIException):
    """Raised when SQL query execution fails"""
    pass

class QueryValidationError(HoeflonAIException):
    """Raised when SQL query validation fails"""
    pass

class RoutingError(HoeflonAIException):
    """Raised when query routing fails"""
    pass

class SessionError(HoeflonAIException):
    """Raised when session management fails"""
    pass

class CompanyDataError(HoeflonAIException):
    """Raised when company data lookup fails"""
    pass
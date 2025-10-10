"""
Excepciones personalizadas para el sistema de autenticación
"""


class AuthenticationError(Exception):
    """Excepción base para errores de autenticación"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Excepción para credenciales inválidas"""
    pass


class UserNotFoundError(AuthenticationError):
    """Excepción para usuario no encontrado"""
    pass


class UserAlreadyExistsError(AuthenticationError):
    """Excepción para usuario que ya existe"""
    pass


class ValidationError(Exception):
    """Excepción para errores de validación"""
    pass


class DatabaseError(Exception):
    """Excepción para errores de base de datos"""
    pass


class ServiceError(Exception):
    """Excepción base para errores de servicios"""
    pass


class BusinessLogicError(ServiceError):
    """Excepción para errores de lógica de negocio"""
    pass


class NotFoundError(ServiceError):
    """Excepción para recursos no encontrados"""
    pass


class FileProcessingError(ValidationError):
    """Excepción para errores de procesamiento de archivos"""
    pass
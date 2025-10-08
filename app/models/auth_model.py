"""
Modelo de Autenticación - Entidad para gestionar credenciales de login
"""
import re
from typing import Dict, Any
from .base_model import BaseModel


class AuthCredentials(BaseModel):
    """Modelo para credenciales de autenticación"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = kwargs.get('user', '')
        self.password = kwargs.get('password', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario (sin incluir password por seguridad)"""
        return {
            'user': self.user
        }
    
    def validate(self) -> None:
        """Valida las credenciales de autenticación"""
        errors = []
        
        # Validar campo user (obligatorio)
        if not self.user or not self.user.strip():
            errors.append("El campo 'user' es obligatorio")
        elif len(self.user.strip()) > 100:
            errors.append("El campo 'user' no puede exceder 100 caracteres")
        elif not self._is_valid_email(self.user.strip()):
            errors.append("El campo 'user' debe ser un email válido")
        
        # Validar campo password (obligatorio)
        if not self.password or not self.password.strip():
            errors.append("El campo 'password' es obligatorio")
        elif len(self.password.strip()) < 1:
            errors.append("El campo 'password' no puede estar vacío")
        
        if errors:
            raise ValueError("; ".join(errors))
    
    def _is_valid_email(self, email: str) -> bool:
        """Valida el formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def __repr__(self) -> str:
        return f"<AuthCredentials(user='{self.user}')>"


class AuthResponse(BaseModel):
    """Modelo para respuesta de autenticación exitosa"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.access_token = kwargs.get('access_token', '')
        self.expires_in = kwargs.get('expires_in', 0)
        self.refresh_expires_in = kwargs.get('refresh_expires_in', 0)
        self.refresh_token = kwargs.get('refresh_token', '')
        self.token_type = kwargs.get('token_type', '')
        self.not_before_policy = kwargs.get('not-before-policy', 0)
        self.session_state = kwargs.get('session_state', '')
        self.scope = kwargs.get('scope', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return {
            'access_token': self.access_token,
            'expires_in': self.expires_in,
            'refresh_expires_in': self.refresh_expires_in,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type,
            'not-before-policy': self.not_before_policy,
            'session_state': self.session_state,
            'scope': self.scope
        }
    
    def validate(self) -> None:
        """Valida la respuesta de autenticación"""
        errors = []
        
        # Validar campos obligatorios de la respuesta
        if not self.access_token or not self.access_token.strip():
            errors.append("El campo 'access_token' es obligatorio en la respuesta")
        
        if not self.token_type or not self.token_type.strip():
            errors.append("El campo 'token_type' es obligatorio en la respuesta")
        
        if self.expires_in <= 0:
            errors.append("El campo 'expires_in' debe ser mayor a 0")
        
        if errors:
            raise ValueError("; ".join(errors))
    
    def __repr__(self) -> str:
        return f"<AuthResponse(token_type='{self.token_type}', expires_in={self.expires_in})>"

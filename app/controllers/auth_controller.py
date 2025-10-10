"""
Controlador de Autenticación - Endpoints REST para login
"""
from flask import request
from flask_restful import Resource
from typing import Dict, Any, Tuple

from .base_controller import BaseController
from ..services.auth_service import AuthService
from ..exceptions.custom_exceptions import ValidationError, BusinessLogicError


class AuthController(BaseController):
    """Controlador para operaciones de autenticación"""
    
    def __init__(self, auth_service=None):
        self.auth_service = auth_service or AuthService()
    
    def post(self) -> Tuple[Dict[str, Any], int]:
        """POST /auth/token - Autenticar usuario"""
        try:
            # Obtener datos del request
            json_data = request.get_json()
            if not json_data:
                return self.error_response("El cuerpo de la petición JSON está vacío", 400)
            
            # Extraer datos del request
            user_email = json_data.get('user', '').strip()
            password = json_data.get('password', '').strip()
            
            # Autenticar usuario usando el servicio
            auth_result = self.auth_service.authenticate_user(user_email, password)
            
            # Retornar directamente la respuesta de Keycloak
            return auth_result, 200
            
        except ValidationError as e:
            return self.error_response(str(e), 400)
        except BusinessLogicError as e:
            # Si el error es un dict (respuesta de Keycloak), retornarlo directamente
            if isinstance(e.args[0], dict):
                return self.error_response(e.args[0], 401)
            return self.error_response(str(e), 401)
        except Exception as e:
            return self.handle_exception(e)


class LogoutController(BaseController):
    """Controlador para operaciones de logout"""
    
    def __init__(self, auth_service=None):
        self.auth_service = auth_service or AuthService()
    
    def post(self) -> Tuple[Dict[str, Any], int]:
        """POST /auth/logout - Cerrar sesión de usuario"""
        try:
            # Obtener datos del request
            json_data = request.get_json()
            if not json_data:
                return self.error_response("El cuerpo de la petición JSON está vacío", 400)
            
            # Extraer refresh_token del request
            refresh_token = json_data.get('refresh_token', '').strip()
            
            # Cerrar sesión usando el servicio
            logout_result = self.auth_service.logout_user(refresh_token)
            
            # Si la respuesta es exitosa (logout successful), retornar 204
            if isinstance(logout_result, dict) and logout_result.get('message') == 'Logout successful':
                return logout_result, 204
            
            # Si hay error en la respuesta de Keycloak, retornar el error
            return logout_result, 400
            
        except ValidationError as e:
            return self.error_response(str(e), 400)
        except BusinessLogicError as e:
            # Si el error es un dict (respuesta de Keycloak), retornarlo directamente
            if isinstance(e.args[0], dict):
                return self.error_response(e.args[0], 400)
            return self.error_response(str(e), 400)
        except Exception as e:
            return self.handle_exception(e)
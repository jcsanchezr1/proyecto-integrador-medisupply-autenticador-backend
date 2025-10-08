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
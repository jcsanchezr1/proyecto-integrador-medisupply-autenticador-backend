"""
Controlador de Usuario - Endpoints REST para gestión de usuarios
"""
from flask import request
from flask_restful import Resource
from typing import Dict, Any, Tuple

from .base_controller import BaseController
from ..services.user_service import UserService
from ..exceptions.custom_exceptions import ValidationError, BusinessLogicError, NotFoundError


class UserController(BaseController):
    """Controlador para operaciones REST de usuarios"""
    
    def __init__(self, user_service=None):
        self.user_service = user_service or UserService()
    
    def get(self, user_id: str = None) -> Tuple[Dict[str, Any], int]:
        """GET /auth/user o GET /auth/user/{id}"""
        try:
            if user_id:
                # Obtener un usuario específico
                user = self.user_service.get_by_id(user_id)
                if not user:
                    return self.error_response("Usuario no encontrado", 404)
                
                return self.success_response(
                    data=user.to_dict(),
                    message="Usuario obtenido exitosamente"
                )
            else:
                # Obtener lista de usuarios con paginación
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                
                # Validar parámetros de paginación
                if page < 1:
                    return self.error_response("El parámetro 'page' debe ser mayor a 0", 400)
                
                if per_page < 1 or per_page > 100:
                    return self.error_response("El parámetro 'per_page' debe estar entre 1 y 100", 400)
                
                offset = (page - 1) * per_page
                
                # Obtener usuarios y total
                users = self.user_service.get_users_summary(
                    limit=per_page,
                    offset=offset
                )
                total = self.user_service.get_users_count()
                
                # Calcular información de paginación
                total_pages = (total + per_page - 1) // per_page  # Ceiling division
                has_next = page < total_pages
                has_prev = page > 1
                
                return self.success_response(
                    data={
                        'users': users,
                        'pagination': {
                            'page': page,
                            'per_page': per_page,
                            'total': total,
                            'total_pages': total_pages,
                            'has_next': has_next,
                            'has_prev': has_prev,
                            'next_page': page + 1 if has_next else None,
                            'prev_page': page - 1 if has_prev else None
                        }
                    },
                    message="Lista de usuarios obtenida exitosamente"
                )
                
        except BusinessLogicError as e:
            return self.error_response(str(e), 500)
        except Exception as e:
            return self.handle_exception(e)
    
    def post(self) -> Tuple[Dict[str, Any], int]:
        """POST /auth/user - Crear nuevo usuario (solo JSON)"""
        try:
            # Procesar petición JSON
            user_data = self._process_json_request()
            
            # Crear usuario
            user = self.user_service.create_user_with_validation(**user_data)
            
            return self.success_response(
                data=user.to_dict(),
                message="Usuario registrado exitosamente",
                status_code=201
            )
            
        except ValidationError as e:
            return self.error_response(str(e), 400)
        except BusinessLogicError as e:
            return self.error_response(f"Error de negocio: {str(e)}", 500)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error en crear usuario: {error_trace}")  # Log para debugging
            return self.error_response(f"Error del sistema: {str(e)}", 500)
    
    def _process_json_request(self) -> Dict[str, Any]:
        """Procesa una petición JSON"""
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError("El cuerpo de la petición JSON está vacío")
            
            # Validar campos requeridos
            required_fields = ['institution_name', 'email', 'password', 'confirm_password']
            for field in required_fields:
                if field not in json_data or not json_data[field]:
                    raise ValidationError(f"El campo '{field}' es obligatorio")
            
            return {
                'institution_name': json_data['institution_name'].strip(),
                'tax_id': json_data.get('tax_id', '').strip(),
                'email': json_data['email'].strip(),
                'address': json_data.get('address', '').strip(),
                'phone': json_data.get('phone', '').strip(),
                'institution_type': json_data.get('institution_type', '').strip(),
                'logo_filename': json_data.get('logo_filename', '').strip(),
                'specialty': json_data.get('specialty', '').strip(),
                'applicant_name': json_data.get('applicant_name', '').strip(),
                'applicant_email': json_data.get('applicant_email', '').strip(),
                'password': json_data['password'].strip(),
                'confirm_password': json_data['confirm_password'].strip()
            }
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Error al procesar JSON: {str(e)}")
    


class UserHealthController(BaseController):
    """Controlador para health check de usuarios"""
    
    def get(self) -> Tuple[Dict[str, Any], int]:
        """GET /auth/user/ping - Health check"""
        try:
            return self.success_response(
                data={
                    'service': 'users',
                    'status': 'healthy',
                    'version': '1.0.0'
                },
                message="Servicio de usuarios funcionando correctamente"
            )
        except Exception as e:
            return self.handle_exception(e)


class UserDeleteAllController(BaseController):
    """Controlador para eliminar todos los usuarios"""
    
    def __init__(self, user_service=None):
        self.user_service = user_service or UserService()
    
    def delete(self) -> Tuple[Dict[str, Any], int]:
        """DELETE /auth/user/all - Eliminar todos los usuarios"""
        try:
            # Eliminar todos los usuarios
            deleted_count = self.user_service.delete_all()
            
            return self.success_response(
                data={
                    'deleted_count': deleted_count
                },
                message=f"Se eliminaron {deleted_count} usuarios exitosamente"
            )
            
        except BusinessLogicError as e:
            return self.error_response("Error temporal del sistema. Contacte soporte técnico si persiste", 500)
        except Exception as e:
            return self.error_response("Error temporal del sistema. Contacte soporte técnico si persiste", 500)
"""
Servicio de Usuario - Lógica de negocio para usuarios
"""
from typing import List, Optional

from .base_service import BaseService
from ..repositories.user_repository import UserRepository
from ..models.user_model import User
from ..exceptions.custom_exceptions import ValidationError, BusinessLogicError
from ..external.keycloak_client import KeycloakClient


class UserService(BaseService):
    """Servicio para operaciones de negocio de usuarios"""
    
    def __init__(self, user_repository=None, keycloak_client=None):
        self.user_repository = user_repository or UserRepository()
        self.keycloak_client = keycloak_client or KeycloakClient()
    
    def create(self, **kwargs) -> User:
        """Crea un nuevo usuario con validaciones de negocio"""
        try:
            # Validar reglas de negocio
            self.validate_business_rules(**kwargs)
            
            # Crear usuario
            user = self.user_repository.create(**kwargs)
            
            return user
            
        except ValueError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise BusinessLogicError(f"Error al crear usuario: {str(e)}")
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Obtiene un usuario por ID"""
        try:
            return self.user_repository.get_by_id(user_id)
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener usuario: {str(e)}")
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[User]:
        """Obtiene todos los usuarios con paginación"""
        try:
            return self.user_repository.get_all(limit=limit, offset=offset)
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener usuarios: {str(e)}")
    
    def update(self, user_id: str, **kwargs) -> Optional[User]:
        """Actualiza un usuario"""
        try:
            return self.user_repository.update(user_id, **kwargs)
        except Exception as e:
            raise BusinessLogicError(f"Error al actualizar usuario: {str(e)}")
    
    def delete(self, user_id: str) -> bool:
        """Elimina un usuario"""
        try:
            return self.user_repository.delete(user_id)
        except Exception as e:
            raise BusinessLogicError(f"Error al eliminar usuario: {str(e)}")
    
    def delete_all(self) -> int:
        """Elimina todos los usuarios de la base de datos"""
        try:
            return self.user_repository.delete_all()
        except Exception as e:
            raise BusinessLogicError(f"Error al eliminar todos los usuarios: {str(e)}")
    
    def validate_business_rules(self, **kwargs) -> None:
        """Valida las reglas de negocio específicas para usuarios"""
        errors = []
        
        # Validar campos obligatorios
        if 'institution_name' in kwargs:
            institution_name = kwargs['institution_name'].strip() if kwargs['institution_name'] else ''
            if not institution_name:
                errors.append("El campo 'Nombre de la institución' es obligatorio")
            elif len(institution_name) > 100:
                errors.append("El nombre de la institución no puede exceder 100 caracteres")
            elif len(institution_name) < 2:
                errors.append("El nombre de la institución debe tener al menos 2 caracteres")
        
        if 'email' in kwargs:
            email = kwargs['email'].strip() if kwargs['email'] else ''
            if not email:
                errors.append("El campo 'Correo electrónico' es obligatorio")
            elif len(email) > 100:
                errors.append("El correo electrónico no puede exceder 100 caracteres")
            elif '@' not in email or '.' not in email.split('@')[-1]:
                errors.append("El campo 'Correo electrónico' debe tener un formato válido")
        
        if 'password' in kwargs:
            password = kwargs['password'].strip() if kwargs['password'] else ''
            if not password:
                errors.append("El campo 'Contraseña' es obligatorio")
            elif len(password) < 8:
                errors.append("El campo 'Contraseña' debe tener al menos 8 caracteres")
        
        if 'confirm_password' in kwargs:
            confirm_password = kwargs['confirm_password'].strip() if kwargs['confirm_password'] else ''
            if not confirm_password:
                errors.append("El campo 'Confirmar contraseña' es obligatorio")
        
        # Validar que las contraseñas coincidan
        if 'password' in kwargs and 'confirm_password' in kwargs:
            if kwargs['password'] != kwargs['confirm_password']:
                errors.append("Los campos 'Contraseña' y 'Confirmar contraseña' deben ser iguales")
        
        # Validar campos opcionales con límites
        if 'tax_id' in kwargs and kwargs['tax_id'] and len(kwargs['tax_id'].strip()) > 50:
            errors.append("El número de identificación tributaria no puede exceder 50 caracteres")
        
        if 'address' in kwargs and kwargs['address'] and len(kwargs['address'].strip()) > 200:
            errors.append("La dirección no puede exceder 200 caracteres")
        
        if 'phone' in kwargs and kwargs['phone']:
            phone = kwargs['phone'].strip()
            if len(phone) > 20:
                errors.append("El teléfono no puede exceder 20 caracteres")
            elif len(phone) < 7:
                errors.append("El teléfono debe tener al menos 7 dígitos")
            elif not phone.isdigit():
                errors.append("El teléfono debe contener solo números")
        
        if 'institution_type' in kwargs and kwargs['institution_type']:
            if kwargs['institution_type'] not in ['Clínica', 'Hospital', 'Laboratorio']:
                errors.append("El tipo de institución debe ser: Clínica, Hospital o Laboratorio")
        
        if 'specialty' in kwargs and kwargs['specialty']:
            if kwargs['specialty'] not in ['Cadena de frío', 'Alto valor', 'Seguridad']:
                errors.append("La especialidad debe ser: Cadena de frío, Alto valor o Seguridad")
        
        if 'applicant_name' in kwargs and kwargs['applicant_name'] and len(kwargs['applicant_name'].strip()) > 80:
            errors.append("El nombre del solicitante no puede exceder 80 caracteres")
        
        if 'applicant_email' in kwargs and kwargs['applicant_email']:
            applicant_email = kwargs['applicant_email'].strip()
            if len(applicant_email) > 100:
                errors.append("El email del solicitante no puede exceder 100 caracteres")
            elif '@' not in applicant_email or '.' not in applicant_email.split('@')[-1]:
                errors.append("El email del solicitante debe tener un formato válido")
        
        # Validar rol
        if 'role' in kwargs:
            role = kwargs['role'].strip() if kwargs['role'] else ''
            valid_roles = ['Administrador', 'Compras', 'Ventas', 'Logistica', 'Cliente']
            if not role:
                errors.append("El campo 'Rol' es obligatorio")
            elif role not in valid_roles:
                errors.append(f"El campo 'Rol' debe ser uno de los siguientes: {', '.join(valid_roles)}")
        
        # Validar email único
        if 'email' in kwargs and kwargs['email']:
            existing_user = self.user_repository.get_by_email(kwargs['email'].strip())
            if existing_user:
                errors.append("Ya existe un usuario con este correo electrónico")
        
        if errors:
            raise ValueError("; ".join(errors))
    
    
    def get_users_summary(self, limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        """Obtiene un resumen de usuarios para listado"""
        try:
            users = self.get_all(limit=limit, offset=offset)
            
            return [
                {
                    'id': user.id,
                    'institution_name': user.institution_name,
                    'email': user.email,
                    'institution_type': user.institution_type,
                    'phone': user.phone
                }
                for user in users
            ]
            
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener resumen de usuarios: {str(e)}")
    
    def get_users_count(self) -> int:
        """Obtiene el total de usuarios"""
        try:
            return self.user_repository.count_all()
        except Exception as e:
            raise BusinessLogicError(f"Error al contar usuarios: {str(e)}")
    
    def create_user_with_validation(self, **kwargs) -> User:
        """Crea un usuario con validaciones completas y sincronización con Keycloak"""
        try:
            # Asignar rol Cliente por defecto
            kwargs['role'] = 'Cliente'
            # Establecer enabled=False por defecto
            kwargs['enabled'] = False
            
            # Crear modelo temporal para validar
            temp_user = User(**kwargs)
            temp_user.validate()
            
            # Validar rol específico para Keycloak
            valid_roles = self.keycloak_client.get_available_roles()
            if kwargs.get('role') not in valid_roles:
                raise ValidationError(f"Rol '{kwargs.get('role')}' no válido. Roles disponibles: {', '.join(valid_roles)}")
            
            # Crear usuario en la base de datos local
            user = self.create(**kwargs)
            
            try:
                # Crear usuario en Keycloak
                keycloak_user_id = self.keycloak_client.create_user(
                    email=kwargs['email'],
                    password=kwargs['password'],
                    institution_name=kwargs['institution_name']
                )
                
                # Asignar rol en Keycloak
                self.keycloak_client.assign_role_to_user(
                    user_id=keycloak_user_id,
                    role_name=kwargs['role']
                )
                
            except Exception as keycloak_error:
                # Si falla Keycloak, eliminar usuario de la base de datos local
                try:
                    self.user_repository.delete(user.id)
                except:
                    pass  # Si no se puede eliminar, al menos loguear el error
                
                raise BusinessLogicError(f"Error al crear usuario en Keycloak: {str(keycloak_error)}")
            
            return user
            
        except ValidationError as e:
            # Re-lanzar ValidationError para que se maneje correctamente en el controlador
            raise e
        except ValueError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise BusinessLogicError(f"Error al crear usuario: {str(e)}")
"""
Servicio de Usuario - Lógica de negocio para usuarios
"""
import logging
from typing import List, Optional, Dict, Any
from werkzeug.datastructures import FileStorage

from .base_service import BaseService
from .cloud_storage_service import CloudStorageService
from ..repositories.user_repository import UserRepository
from ..models.user_model import User, AdminUserCreate
from ..exceptions.custom_exceptions import ValidationError, BusinessLogicError
from ..external.keycloak_client import KeycloakClient
from ..config.settings import Config

logger = logging.getLogger(__name__)


class UserService(BaseService):
    """Servicio para operaciones de negocio de usuarios"""
    
    def __init__(self, user_repository=None, keycloak_client=None, cloud_storage_service=None, config=None):
        self.user_repository = user_repository or UserRepository()
        self.keycloak_client = keycloak_client or KeycloakClient()
        self.config = config or Config()
        self.cloud_storage_service = cloud_storage_service or CloudStorageService(self.config)
        
        logger.info("UserService inicializado con CloudStorageService")
    
    def create(self, **kwargs) -> User:
        """Crea un nuevo usuario con validaciones de negocio"""
        try:
            # Validar reglas de negocio
            self.validate_business_rules(**kwargs)
            
            # Procesar archivo de logo si se proporciona
            logo_file = kwargs.get('logo_file')
            logo_filename = None
            logo_url = None
            
            if logo_file is not None:
                logo_filename, logo_url = self._process_logo_file(logo_file)
                if logo_filename:
                    kwargs['logo_filename'] = logo_filename
                    kwargs['logo_url'] = logo_url
            
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
        if 'name' in kwargs:
            name = kwargs['name'].strip() if kwargs['name'] else ''
            if not name:
                errors.append("El campo 'Nombre' es obligatorio")
            elif len(name) > 100:
                errors.append("El nombre no puede exceder 100 caracteres")
            elif len(name) < 2:
                errors.append("El nombre debe tener al menos 2 caracteres")
        
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
                    'name': user.name,
                    'email': user.email,
                    'institution_type': user.institution_type,
                    'phone': user.phone,
                    'role': self.keycloak_client.get_user_role(user.email)
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
                    name=kwargs['name']
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
    
    def _process_logo_file(self, logo_file: Optional[FileStorage]) -> tuple[Optional[str], Optional[str]]:
        """
        Procesa el archivo de logo y lo sube a Google Cloud Storage
        
        Args:
            logo_file: Archivo de imagen del logo
            
        Returns:
            tuple[Optional[str], Optional[str]]: (filename, url_pública)
        """
        if not logo_file or not logo_file.filename:
            logger.info("No se proporcionó archivo de logo")
            return None, None
        
        try:
            logger.info(f"Procesando archivo de logo: {logo_file.filename}")
            
            # Generar nombre único para el archivo
            user_model = User()
            unique_filename = user_model.generate_logo_filename(logo_file.filename)
            logger.info(f"Nombre único generado: {unique_filename}")
            
            # Subir imagen a Google Cloud Storage
            success, message, public_url = self.cloud_storage_service.upload_image(
                logo_file, unique_filename
            )
            
            logger.info(f"Resultado de subida - Success: {success}, URL: {public_url}")
            
            if not success:
                raise ValidationError(f"Error al subir imagen: {message}")
            
            logger.info(f"Logo procesado exitosamente - Filename: {unique_filename}, URL: {public_url}")
            return unique_filename, public_url
            
        except Exception as e:
            logger.error(f"Error en _process_logo_file: {str(e)}")
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Error al procesar archivo de logo: {str(e)}")
    
    def create_admin_user(self, name: str, email: str, password: str, role: str) -> Dict[str, Any]:
        """
        Crea un usuario administrado por un administrador
        
        Args:
            name: Nombre del usuario
            email: Email del usuario
            password: Contraseña del usuario
            role: Rol del usuario en Keycloak
            
        Returns:
            Dict con la información del usuario creado
            
        Raises:
            ValidationError: Si los datos de entrada son inválidos
            BusinessLogicError: Si hay error en la lógica de negocio
        """
        # Crear modelo de datos y validar
        try:
            admin_user = AdminUserCreate(
                name=name,
                email=email,
                password=password,
                confirm_password=password,  # Para validación
                role=role
            )
            admin_user.validate()
        except ValueError as e:
            raise ValidationError(str(e))
        
        # Verificar que el usuario no existe
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise BusinessLogicError("Ya existe un usuario con este email")
        
        # Crear usuario en Keycloak
        try:
            keycloak_id = self.keycloak_client.create_user(email, password, name)
            
            # Asignar rol en Keycloak
            self.keycloak_client.assign_role_to_user(keycloak_id, role)
            
            # Crear usuario en base de datos local
            # Usar método específico para usuarios admin que no valida todos los campos
            created_user = self.user_repository.create_admin_user(
                name=name,
                email=email,
                keycloak_id=keycloak_id,
                enabled=True
            )
            
            return {
                'id': created_user.id,
                'name': created_user.name,
                'email': created_user.email,
                'role': role,
                'enabled': created_user.enabled,
                'created_at': created_user.created_at.isoformat() if created_user.created_at else None
            }
            
        except Exception as e:
            # Si hay error, intentar limpiar el usuario de Keycloak
            try:
                if 'keycloak_id' in locals():
                    self.keycloak_client.delete_user(keycloak_id)
            except:
                pass  # Ignorar errores de limpieza
            
            raise BusinessLogicError(f"Error al crear usuario: {str(e)}")
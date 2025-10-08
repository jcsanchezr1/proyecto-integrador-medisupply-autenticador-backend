"""
Modelo de Usuario - Entidad para gestionar usuarios de instituciones
"""
import re
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from .base_model import BaseModel


class User(BaseModel):
    """Modelo de Usuario con validaciones específicas"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.name = kwargs.get('name', '')
        self.tax_id = kwargs.get('tax_id', '')
        self.email = kwargs.get('email', '')
        self.address = kwargs.get('address', '')
        self.phone = kwargs.get('phone', '')
        self.institution_type = kwargs.get('institution_type', '')
        self.logo_filename = kwargs.get('logo_filename', '')
        self.logo_url = kwargs.get('logo_url', '')
        self.specialty = kwargs.get('specialty', '')
        self.applicant_name = kwargs.get('applicant_name', '')
        self.applicant_email = kwargs.get('applicant_email', '')
        self.password = kwargs.get('password', '')
        self.confirm_password = kwargs.get('confirm_password', '')
        self.role = kwargs.get('role', '')
        self.keycloak_id = kwargs.get('keycloak_id', '')
        self.enabled = kwargs.get('enabled', False)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'tax_id': self.tax_id,
            'email': self.email,
            'address': self.address,
            'phone': self.phone,
            'institution_type': self.institution_type,
            'logo_filename': self.logo_filename,
            'logo_url': self.logo_url,
            'specialty': self.specialty,
            'applicant_name': self.applicant_name,
            'applicant_email': self.applicant_email,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def validate(self) -> None:
        """Valida los datos del modelo según las reglas de negocio"""
        errors = []
        
        # Validar nombre (obligatorio, máximo 100 caracteres)
        if not self.name or not self.name.strip():
            errors.append("El campo 'Nombre' es obligatorio")
        elif len(self.name.strip()) > 100:
            errors.append("El campo 'Nombre' no puede exceder 100 caracteres")
        
        # Validar número de identificación tributaria (obligatorio, máximo 50 caracteres)
        if not self.tax_id or not self.tax_id.strip():
            errors.append("El campo 'Número de identificación tributaria' es obligatorio")
        elif len(self.tax_id.strip()) > 50:
            errors.append("El campo 'Número de identificación tributaria' no puede exceder 50 caracteres")
        
        # Validar correo electrónico (obligatorio, máximo 100 caracteres)
        if not self.email or not self.email.strip():
            errors.append("El campo 'Correo electrónico' es obligatorio")
        elif len(self.email.strip()) > 100:
            errors.append("El campo 'Correo electrónico' no puede exceder 100 caracteres")
        elif not self._is_valid_email(self.email.strip()):
            errors.append("El campo 'Correo electrónico' debe tener un formato válido")
        
        # Validar dirección (obligatorio, máximo 200 caracteres)
        if not self.address or not self.address.strip():
            errors.append("El campo 'Dirección' es obligatorio")
        elif len(self.address.strip()) > 200:
            errors.append("El campo 'Dirección' no puede exceder 200 caracteres")
        
        # Validar teléfono (obligatorio, máximo 20 caracteres)
        if not self.phone or not self.phone.strip():
            errors.append("El campo 'Teléfono de contacto' es obligatorio")
        elif len(self.phone.strip()) > 20:
            errors.append("El campo 'Teléfono de contacto' no puede exceder 20 caracteres")
        elif not re.match(r'^\d+$', self.phone.strip()):
            errors.append("El campo 'Teléfono de contacto' debe contener solo números")
        
        # Validar tipo de institución (obligatorio, valores específicos)
        if not self.institution_type or not self.institution_type.strip():
            errors.append("El campo 'Tipo de institución' es obligatorio")
        elif self.institution_type not in ['Clínica', 'Hospital', 'Laboratorio']:
            errors.append("El campo 'Tipo de institución' debe ser: Clínica, Hospital o Laboratorio")
        
        # Validar logo (opcional, string simple)
        if self.logo_filename and len(self.logo_filename.strip()) > 255:
            errors.append("El campo 'Logo' no puede exceder 255 caracteres")
        
        # Validar especialidad (obligatorio, valores específicos)
        if not self.specialty or not self.specialty.strip():
            errors.append("El campo 'Especialidad' es obligatorio")
        elif self.specialty not in ['Cadena de frío', 'Alto valor', 'Seguridad']:
            errors.append("El campo 'Especialidad' debe ser: Cadena de frío, Alto valor o Seguridad")
        
        # Validar nombre del solicitante (obligatorio, máximo 80 caracteres)
        if not self.applicant_name or not self.applicant_name.strip():
            errors.append("El campo 'Nombre del solicitante' es obligatorio")
        elif len(self.applicant_name.strip()) > 80:
            errors.append("El campo 'Nombre del solicitante' no puede exceder 80 caracteres")
        
        # Validar email del solicitante (obligatorio, máximo 100 caracteres)
        if not self.applicant_email or not self.applicant_email.strip():
            errors.append("El campo 'Email del solicitante' es obligatorio")
        elif len(self.applicant_email.strip()) > 100:
            errors.append("El campo 'Email del solicitante' no puede exceder 100 caracteres")
        elif not self._is_valid_email(self.applicant_email.strip()):
            errors.append("El campo 'Email del solicitante' debe tener un formato válido")
        
        # Validar contraseña (obligatorio)
        if not self.password or not self.password.strip():
            errors.append("El campo 'Contraseña' es obligatorio")
        elif len(self.password.strip()) < 8:
            errors.append("El campo 'Contraseña' debe tener al menos 8 caracteres")
        
        # Validar confirmar contraseña (obligatorio)
        if not self.confirm_password or not self.confirm_password.strip():
            errors.append("El campo 'Confirmar contraseña' es obligatorio")
        
        # Validar que las contraseñas coincidan
        if self.password and self.confirm_password and self.password != self.confirm_password:
            errors.append("Los campos 'Contraseña' y 'Confirmar contraseña' deben ser iguales")
        
        # Validar rol (obligatorio, valores específicos)
        valid_roles = ['Administrador', 'Compras', 'Ventas', 'Logistica', 'Cliente']
        if not self.role or not self.role.strip():
            errors.append("El campo 'Rol' es obligatorio")
        elif self.role.strip() not in valid_roles:
            errors.append(f"El campo 'Rol' debe ser uno de los siguientes: {', '.join(valid_roles)}")
        
        if errors:
            raise ValueError("; ".join(errors))
    
    def _is_valid_email(self, email: str) -> bool:
        """Valida el formato de email con dominio válido"""
        # Verificar que contenga @
        if '@' not in email:
            return False
        
        # Dividir en usuario y dominio
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        username, domain = parts
        
        # Verificar que el dominio tenga al menos un punto
        if '.' not in domain:
            return False
        
        # Verificar que el dominio tenga extensión válida
        domain_parts = domain.split('.')
        if len(domain_parts) < 2:
            return False
        
        # Verificar que la extensión tenga al menos 2 caracteres
        extension = domain_parts[-1]
        if len(extension) < 2:
            return False
        
        # Patrón más estricto para validar formato completo
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def generate_logo_filename(self, original_filename: str) -> str:
        """Genera un nombre único para el archivo de logo"""
        if not original_filename:
            return ''
        
        # Obtener extensión
        if '.' not in original_filename:
            return ''
        
        extension = original_filename.lower().split('.')[-1]
        
        # Generar nombre único con UUID
        unique_id = str(uuid.uuid4())
        return f"logo_{unique_id}.{extension}"
    
    def __repr__(self) -> str:
        return f"<User(id='{self.id}', name='{self.name}', email='{self.email}')>"


class AdminUserCreate(BaseModel):
    """Modelo para creación de usuario por administrador"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get('name', '')
        self.email = kwargs.get('email', '')
        self.password = kwargs.get('password', '')
        self.confirm_password = kwargs.get('confirm_password', '')
        self.role = kwargs.get('role', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario (sin incluir password por seguridad)"""
        return {
            'name': self.name,
            'email': self.email,
            'role': self.role
        }
    
    def validate(self) -> None:
        """Valida los datos del modelo según las reglas de negocio"""
        errors = []
        
        # Validar campo name (obligatorio, máximo 100 caracteres)
        if not self.name or not self.name.strip():
            errors.append("El campo 'name' es obligatorio")
        elif len(self.name.strip()) > 100:
            errors.append("El campo 'name' no puede exceder 100 caracteres")
        
        # Validar campo email (obligatorio, máximo 100 caracteres)
        if not self.email or not self.email.strip():
            errors.append("El campo 'email' es obligatorio")
        elif len(self.email.strip()) > 100:
            errors.append("El campo 'email' no puede exceder 100 caracteres")
        elif not self._is_valid_email(self.email.strip()):
            errors.append("El campo 'email' debe ser un email válido")
        
        # Validar campo password (obligatorio, mínimo 8 caracteres)
        if not self.password or not self.password.strip():
            errors.append("El campo 'password' es obligatorio")
        elif len(self.password.strip()) < 8:
            errors.append("El campo 'password' debe tener al menos 8 caracteres")
        
        # Validar campo confirm_password (obligatorio)
        if not self.confirm_password or not self.confirm_password.strip():
            errors.append("El campo 'confirm_password' es obligatorio")
        
        # Validar que las contraseñas coincidan
        if self.password and self.confirm_password and self.password != self.confirm_password:
            errors.append("Los campos 'password' y 'confirm_password' deben ser iguales")
        
        # Validar campo role (obligatorio, valores específicos)
        valid_roles = ['Administrador', 'Compras', 'Ventas', 'Logistica', 'Cliente']
        if not self.role or not self.role.strip():
            errors.append("El campo 'role' es obligatorio")
        elif self.role.strip() not in valid_roles:
            errors.append(f"El campo 'role' debe ser uno de los siguientes: {', '.join(valid_roles)}")
        
        if errors:
            raise ValueError("; ".join(errors))
    
    def _is_valid_email(self, email: str) -> bool:
        """Valida el formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def __repr__(self) -> str:
        return f"<AdminUserCreate(name='{self.name}', email='{self.email}', role='{self.role}')>"
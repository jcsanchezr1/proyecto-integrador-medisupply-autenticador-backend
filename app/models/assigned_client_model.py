"""
Modelo de Cliente Asignado - Entidad para gestionar asignaciones vendedor-cliente
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from .base_model import BaseModel


class AssignedClient(BaseModel):
    """Modelo de Cliente Asignado con validaciones específicas"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.seller_id = kwargs.get('seller_id', '')
        self.client_id = kwargs.get('client_id', '')
        self.created_at = kwargs.get('created_at', datetime.now(timezone.utc))
        self.updated_at = kwargs.get('updated_at', datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'client_id': self.client_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def validate(self) -> None:
        """Valida los datos del modelo según las reglas de negocio"""
        errors = []
        
        # Validar seller_id (obligatorio)
        if not self.seller_id or not self.seller_id.strip():
            errors.append("El campo 'seller_id' es obligatorio")
        
        # Validar client_id (obligatorio)
        if not self.client_id or not self.client_id.strip():
            errors.append("El campo 'client_id' es obligatorio")
        
        # Validar que seller_id y client_id sean diferentes
        if self.seller_id and self.client_id and self.seller_id == self.client_id:
            errors.append("El vendedor no puede ser asignado como su propio cliente")
        
        if errors:
            raise ValueError("; ".join(errors))
    
    def __repr__(self) -> str:
        return f"<AssignedClient(id='{self.id}', seller_id='{self.seller_id}', client_id='{self.client_id}')>"


"""
Servicio de Cliente Asignado - Lógica de negocio para clientes asignados
"""
import logging
from typing import List, Optional, Dict, Any

from .base_service import BaseService
from ..repositories.assigned_client_repository import AssignedClientRepository
from ..repositories.user_repository import UserRepository
from ..models.assigned_client_model import AssignedClient
from ..exceptions.custom_exceptions import ValidationError, BusinessLogicError, NotFoundError

logger = logging.getLogger(__name__)


class AssignedClientService(BaseService):
    """Servicio para operaciones de negocio de clientes asignados"""
    
    def __init__(self, assigned_client_repository=None, user_repository=None):
        self.assigned_client_repository = assigned_client_repository or AssignedClientRepository()
        self.user_repository = user_repository or UserRepository()
        logger.info("AssignedClientService inicializado")
    
    def create(self, **kwargs) -> AssignedClient:
        """Crea una nueva asignación cliente-vendedor con validaciones de negocio"""
        try:
            # Validar reglas de negocio
            self.validate_business_rules(**kwargs)
            
            # Crear asignación
            assigned_client = self.assigned_client_repository.create(**kwargs)
            
            # Actualizar el campo enabled del cliente a True
            client_id = kwargs.get('client_id')
            if client_id:
                self.user_repository.update(client_id, enabled=True)
            
            return assigned_client
            
        except ValueError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise BusinessLogicError(f"Error al crear asignación: {str(e)}")
    
    def get_by_id(self, assigned_client_id: str) -> Optional[AssignedClient]:
        """Obtiene una asignación por ID"""
        try:
            return self.assigned_client_repository.get_by_id(assigned_client_id)
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener asignación: {str(e)}")
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[AssignedClient]:
        """Obtiene todas las asignaciones con paginación"""
        try:
            return self.assigned_client_repository.get_all(limit=limit, offset=offset)
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener asignaciones: {str(e)}")
    
    def get_by_seller_id(self, seller_id: str) -> List[AssignedClient]:
        """Obtiene todas las asignaciones de un vendedor específico"""
        try:
            return self.assigned_client_repository.get_by_seller_id(seller_id)
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener clientes asignados: {str(e)}")
    
    def get_assigned_clients_with_details(self, seller_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene los clientes asignados a un vendedor con información completa del usuario
        
        Args:
            seller_id: ID del vendedor
            
        Returns:
            Lista de diccionarios con información de los clientes asignados
            
        Raises:
            NotFoundError: Si el vendedor no existe
            BusinessLogicError: Si hay error en la lógica de negocio
        """
        try:
            # Verificar que el vendedor existe
            seller = self.user_repository.get_by_id(seller_id)
            if not seller:
                raise NotFoundError(f"No se encontró el vendedor con ID: {seller_id}")
            
            # Obtener asignaciones del vendedor
            assignments = self.get_by_seller_id(seller_id)
            
            # Enriquecer con información de los clientes
            assigned_clients_details = []
            for assignment in assignments:
                # Obtener información del cliente
                client = self.user_repository.get_by_id(assignment.client_id)
                
                if client:
                    # Devolver todos los campos del cliente usando to_dict()
                    assigned_clients_details.append(client.to_dict())
                else:
                    # Si el cliente no existe, registrar el problema pero continuar
                    logger.warning(f"Cliente con ID {assignment.client_id} no encontrado en la base de datos")
            
            return assigned_clients_details
            
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener clientes asignados con detalles: {str(e)}")
    
    def update(self, assigned_client_id: str, **kwargs) -> Optional[AssignedClient]:
        """Actualiza una asignación"""
        try:
            return self.assigned_client_repository.update(assigned_client_id, **kwargs)
        except Exception as e:
            raise BusinessLogicError(f"Error al actualizar asignación: {str(e)}")
    
    def delete(self, assigned_client_id: str) -> bool:
        """Elimina una asignación"""
        try:
            return self.assigned_client_repository.delete(assigned_client_id)
        except Exception as e:
            raise BusinessLogicError(f"Error al eliminar asignación: {str(e)}")
    
    def validate_business_rules(self, **kwargs) -> None:
        """Valida las reglas de negocio específicas para asignaciones"""
        errors = []
        
        seller_id = kwargs.get('seller_id', '').strip() if kwargs.get('seller_id') else ''
        client_id = kwargs.get('client_id', '').strip() if kwargs.get('client_id') else ''
        
        # Validar seller_id (obligatorio)
        if not seller_id:
            errors.append("El campo 'seller_id' es obligatorio")
        
        # Validar client_id (obligatorio)
        if not client_id:
            errors.append("El campo 'client_id' es obligatorio")
        
        # Validar que seller_id y client_id sean diferentes
        if seller_id and client_id and seller_id == client_id:
            errors.append("El vendedor no puede ser asignado como su propio cliente")
        
        # Verificar que el vendedor existe
        if seller_id:
            seller = self.user_repository.get_by_id(seller_id)
            if not seller:
                errors.append(f"No existe un vendedor con ID: {seller_id}")
        
        # Verificar que el cliente existe
        if client_id:
            client = self.user_repository.get_by_id(client_id)
            if not client:
                errors.append(f"No existe un cliente con ID: {client_id}")
        
        # Verificar que la asignación no existe ya
        if seller_id and client_id:
            if self.assigned_client_repository.exists_assignment(seller_id, client_id):
                errors.append("Esta asignación vendedor-cliente ya existe")
        
        if errors:
            raise ValueError("; ".join(errors))


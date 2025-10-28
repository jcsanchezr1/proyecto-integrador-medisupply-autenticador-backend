"""
Controlador de Cliente Asignado - Endpoints REST para gestión de clientes asignados
"""
from flask import request
from flask_restful import Resource
from typing import Dict, Any, Tuple

from .base_controller import BaseController
from ..services.assigned_client_service import AssignedClientService
from ..exceptions.custom_exceptions import ValidationError, BusinessLogicError, NotFoundError


class AssignedClientController(BaseController):
    """Controlador para operaciones REST de clientes asignados"""
    
    def __init__(self, assigned_client_service=None):
        self.assigned_client_service = assigned_client_service or AssignedClientService()
    
    def get(self, user_id: str) -> Tuple[Dict[str, Any], int]:
        """GET /auth/assigned-clients/<user_id> - Obtiene los clientes asignados a un vendedor"""
        try:
            # Obtener clientes asignados con información completa
            assigned_clients = self.assigned_client_service.get_assigned_clients_with_details(user_id)
            
            return self.success_response(
                data={
                    'seller_id': user_id,
                    'assigned_clients': assigned_clients,
                    'total': len(assigned_clients)
                },
                message="Clientes asignados obtenidos exitosamente"
            )
            
        except NotFoundError as e:
            return self.error_response(str(e), 404)
        except BusinessLogicError as e:
            return self.error_response(str(e), 500)
        except Exception as e:
            return self.handle_exception(e)
    
    def post(self) -> Tuple[Dict[str, Any], int]:
        """POST /auth/assigned-clients - Crear nueva asignación cliente-vendedor"""
        try:
            # Obtener datos del request
            json_data = request.get_json()
            if not json_data:
                return self.error_response("El cuerpo de la petición JSON está vacío", 400)
            
            # Validar campos obligatorios
            seller_id = json_data.get('seller_id', '').strip() if json_data.get('seller_id') else ''
            client_id = json_data.get('client_id', '').strip() if json_data.get('client_id') else ''
            
            if not seller_id:
                return self.error_response("El campo 'seller_id' es obligatorio", 400)
            
            if not client_id:
                return self.error_response("El campo 'client_id' es obligatorio", 400)
            
            # Crear asignación
            assigned_client = self.assigned_client_service.create(
                seller_id=seller_id,
                client_id=client_id
            )
            
            return self.success_response(
                data=assigned_client.to_dict(),
                message="Asignación creada exitosamente",
                status_code=201
            )
            
        except ValidationError as e:
            return self.error_response(str(e), 400)
        except BusinessLogicError as e:
            return self.error_response(str(e), 500)
        except Exception as e:
            return self.handle_exception(e)


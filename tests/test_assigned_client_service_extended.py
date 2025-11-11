"""
Tests extendidos para el servicio AssignedClientService - Para incrementar cobertura
"""
import unittest
from unittest.mock import Mock, MagicMock
from app.services.assigned_client_service import AssignedClientService
from app.models.assigned_client_model import AssignedClient
from app.models.user_model import User
from app.exceptions.custom_exceptions import ValidationError, BusinessLogicError, NotFoundError


class TestAssignedClientServiceExtended(unittest.TestCase):
    """Tests extendidos para AssignedClientService"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_assigned_client_repo = Mock()
        self.mock_user_repo = Mock()
        self.service = AssignedClientService(
            assigned_client_repository=self.mock_assigned_client_repo,
            user_repository=self.mock_user_repo
        )
    
    def test_get_by_id(self):
        """Test: Obtener asignación por ID"""
        assignment_id = '123e4567-e89b-12d3-a456-426614174000'
        mock_assignment = Mock(spec=AssignedClient)
        mock_assignment.id = assignment_id
        
        self.mock_assigned_client_repo.get_by_id.return_value = mock_assignment
        
        result = self.service.get_by_id(assignment_id)
        
        self.assertEqual(result, mock_assignment)
        self.mock_assigned_client_repo.get_by_id.assert_called_once_with(assignment_id)
    
    def test_get_by_id_with_error(self):
        """Test: Error al obtener asignación por ID"""
        self.mock_assigned_client_repo.get_by_id.side_effect = Exception("Database error")
        
        with self.assertRaises(BusinessLogicError):
            self.service.get_by_id('some-id')
    
    def test_get_all(self):
        """Test: Obtener todas las asignaciones"""
        mock_assignments = [Mock(spec=AssignedClient) for _ in range(3)]
        self.mock_assigned_client_repo.get_all.return_value = mock_assignments
        
        result = self.service.get_all(limit=10, offset=0)
        
        self.assertEqual(len(result), 3)
        self.mock_assigned_client_repo.get_all.assert_called_once_with(limit=10, offset=0)
    
    def test_get_all_with_error(self):
        """Test: Error al obtener todas las asignaciones"""
        self.mock_assigned_client_repo.get_all.side_effect = Exception("Database error")
        
        with self.assertRaises(BusinessLogicError):
            self.service.get_all()
    
    def test_get_by_seller_id(self):
        """Test: Obtener asignaciones por seller_id"""
        seller_id = '123e4567-e89b-12d3-a456-426614174000'
        mock_assignments = [Mock(spec=AssignedClient) for _ in range(2)]
        
        self.mock_assigned_client_repo.get_by_seller_id.return_value = mock_assignments
        
        result = self.service.get_by_seller_id(seller_id)
        
        self.assertEqual(len(result), 2)
    
    def test_get_by_seller_id_with_error(self):
        """Test: Error al obtener asignaciones por seller_id"""
        self.mock_assigned_client_repo.get_by_seller_id.side_effect = Exception("Database error")
        
        with self.assertRaises(BusinessLogicError):
            self.service.get_by_seller_id('some-id')
    
    def test_get_assigned_clients_with_missing_client(self):
        """Test: Obtener clientes asignados cuando un cliente no existe"""
        seller_id = '123e4567-e89b-12d3-a456-426614174000'
        
        # Mock del vendedor
        mock_seller = Mock(spec=User)
        mock_seller.id = seller_id
        
        # Mock de asignación
        mock_assignment = Mock(spec=AssignedClient)
        mock_assignment.client_id = 'non-existent-client'
        
        self.mock_user_repo.get_by_id.side_effect = [mock_seller, None]  # Vendedor existe, cliente no
        self.mock_assigned_client_repo.get_by_seller_id.return_value = [mock_assignment]
        
        # Ejecutar
        result = self.service.get_assigned_clients_with_details(seller_id)
        
        # Verificar que retorna lista vacía (sin el cliente inexistente)
        self.assertEqual(len(result), 0)
    
    def test_update(self):
        """Test: Actualizar asignación"""
        assignment_id = '123e4567-e89b-12d3-a456-426614174000'
        mock_assignment = Mock(spec=AssignedClient)
        
        self.mock_assigned_client_repo.update.return_value = mock_assignment
        
        result = self.service.update(assignment_id, seller_id='new-seller')
        
        self.assertEqual(result, mock_assignment)
    
    def test_update_with_error(self):
        """Test: Error al actualizar asignación"""
        self.mock_assigned_client_repo.update.side_effect = Exception("Database error")
        
        with self.assertRaises(BusinessLogicError):
            self.service.update('some-id', seller_id='new-seller')
    
    def test_delete(self):
        """Test: Eliminar asignación"""
        self.mock_assigned_client_repo.delete.return_value = True
        
        result = self.service.delete('some-id')
        
        self.assertTrue(result)
    
    def test_delete_with_error(self):
        """Test: Error al eliminar asignación"""
        self.mock_assigned_client_repo.delete.side_effect = Exception("Database error")
        
        with self.assertRaises(BusinessLogicError):
            self.service.delete('some-id')
    
    def test_validate_business_rules_empty_client_id(self):
        """Test: Validar con client_id vacío"""
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(seller_id='seller', client_id='')
        
        self.assertIn("client_id", str(context.exception))
    
    def test_validate_business_rules_client_not_found(self):
        """Test: Validar cuando el cliente no existe"""
        seller_id = '123e4567-e89b-12d3-a456-426614174000'
        client_id = '456e7890-e89b-12d3-a456-426614174111'
        
        # Mock: vendedor existe, cliente no
        mock_seller = Mock(spec=User)
        self.mock_user_repo.get_by_id.side_effect = [mock_seller, None]
        
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(seller_id=seller_id, client_id=client_id)
        
        self.assertIn("No existe un cliente", str(context.exception))
    
    def test_create_updates_client_enabled(self):
        """Test: Crear asignación actualiza enabled y status del cliente"""
        seller_id = '123e4567-e89b-12d3-a456-426614174000'
        client_id = '456e7890-e89b-12d3-a456-426614174111'
        
        # Mock de validaciones
        mock_seller = Mock(spec=User)
        mock_client = Mock(spec=User)
        self.mock_user_repo.get_by_id.side_effect = [mock_seller, mock_client]
        self.mock_assigned_client_repo.exists_assignment.return_value = False
        
        # Mock de creación
        mock_assignment = Mock(spec=AssignedClient)
        self.mock_assigned_client_repo.create.return_value = mock_assignment
        
        # Ejecutar
        self.service.create(seller_id=seller_id, client_id=client_id)
        
        # Verificar que se actualizó el campo enabled y status
        self.mock_user_repo.update.assert_called_once_with(client_id, enabled=True, status='APROBADO')
    
    def test_get_assigned_clients_with_details_with_error(self):
        """Test: Error al obtener clientes con detalles"""
        # Mock: error en el repositorio
        self.mock_user_repo.get_by_id.side_effect = Exception("Database error")
        
        with self.assertRaises(BusinessLogicError):
            self.service.get_assigned_clients_with_details('some-id')


if __name__ == '__main__':
    unittest.main()


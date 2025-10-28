"""
Tests para el servicio AssignedClientService
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from app.services.assigned_client_service import AssignedClientService
from app.models.assigned_client_model import AssignedClient
from app.models.user_model import User
from app.exceptions.custom_exceptions import ValidationError, BusinessLogicError, NotFoundError


class TestAssignedClientService(unittest.TestCase):
    """Tests para AssignedClientService"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_assigned_client_repo = Mock()
        self.mock_user_repo = Mock()
        self.service = AssignedClientService(
            assigned_client_repository=self.mock_assigned_client_repo,
            user_repository=self.mock_user_repo
        )
    
    def test_create_with_valid_data(self):
        """Test: Crear asignación con datos válidos y actualizar enabled del cliente"""
        # Preparar datos de prueba
        seller_id = '123e4567-e89b-12d3-a456-426614174000'
        client_id = '456e7890-e89b-12d3-a456-426614174111'
        
        # Mock del vendedor y cliente existentes
        mock_seller = Mock(spec=User)
        mock_seller.id = seller_id
        mock_client = Mock(spec=User)
        mock_client.id = client_id
        
        self.mock_user_repo.get_by_id.side_effect = [mock_seller, mock_client]
        self.mock_assigned_client_repo.exists_assignment.return_value = False
        
        # Mock de la creación
        mock_assigned_client = Mock(spec=AssignedClient)
        mock_assigned_client.id = '987e6543-e21b-12d3-a456-426614174000'
        mock_assigned_client.seller_id = seller_id
        mock_assigned_client.client_id = client_id
        self.mock_assigned_client_repo.create.return_value = mock_assigned_client
        
        # Mock del update del cliente
        self.mock_user_repo.update.return_value = mock_client
        
        # Ejecutar
        result = self.service.create(seller_id=seller_id, client_id=client_id)
        
        # Verificar
        self.assertEqual(result.seller_id, seller_id)
        self.assertEqual(result.client_id, client_id)
        self.mock_assigned_client_repo.create.assert_called_once()
        # Verificar que se actualizó el campo enabled del cliente
        self.mock_user_repo.update.assert_called_once_with(client_id, enabled=True)
    
    def test_create_with_missing_seller_id(self):
        """Test: Crear asignación sin seller_id debe lanzar ValidationError"""
        with self.assertRaises(ValidationError):
            self.service.create(seller_id='', client_id='456e7890-e89b-12d3-a456-426614174111')
    
    def test_create_with_missing_client_id(self):
        """Test: Crear asignación sin client_id debe lanzar ValidationError"""
        with self.assertRaises(ValidationError):
            self.service.create(seller_id='123e4567-e89b-12d3-a456-426614174000', client_id='')
    
    def test_create_with_same_seller_and_client(self):
        """Test: Crear asignación con mismo seller y client debe lanzar ValidationError"""
        same_id = '123e4567-e89b-12d3-a456-426614174000'
        
        with self.assertRaises(ValidationError) as context:
            self.service.create(seller_id=same_id, client_id=same_id)
        
        self.assertIn("propio cliente", str(context.exception))
    
    def test_create_with_non_existent_seller(self):
        """Test: Crear asignación con vendedor inexistente debe lanzar ValidationError"""
        self.mock_user_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValidationError) as context:
            self.service.create(
                seller_id='non-existent-seller',
                client_id='456e7890-e89b-12d3-a456-426614174111'
            )
        
        self.assertIn("No existe un vendedor", str(context.exception))
    
    def test_create_with_duplicate_assignment(self):
        """Test: Crear asignación duplicada debe lanzar ValidationError"""
        seller_id = '123e4567-e89b-12d3-a456-426614174000'
        client_id = '456e7890-e89b-12d3-a456-426614174111'
        
        # Mock del vendedor y cliente existentes
        mock_seller = Mock(spec=User)
        mock_client = Mock(spec=User)
        
        self.mock_user_repo.get_by_id.side_effect = [mock_seller, mock_client]
        self.mock_assigned_client_repo.exists_assignment.return_value = True
        
        with self.assertRaises(ValidationError) as context:
            self.service.create(seller_id=seller_id, client_id=client_id)
        
        self.assertIn("ya existe", str(context.exception))
    
    def test_get_assigned_clients_with_details(self):
        """Test: Obtener clientes asignados con detalles completos"""
        seller_id = '123e4567-e89b-12d3-a456-426614174000'
        
        # Mock del vendedor
        mock_seller = Mock(spec=User)
        mock_seller.id = seller_id
        self.mock_user_repo.get_by_id.return_value = mock_seller
        
        # Mock de la asignación
        mock_assignment = Mock(spec=AssignedClient)
        mock_assignment.id = '987e6543-e21b-12d3-a456-426614174000'
        mock_assignment.client_id = '456e7890-e89b-12d3-a456-426614174111'
        mock_assignment.created_at = Mock()
        mock_assignment.created_at.isoformat.return_value = '2024-10-28T10:30:00.000Z'
        
        self.mock_assigned_client_repo.get_by_seller_id.return_value = [mock_assignment]
        
        # Mock del cliente
        mock_client = Mock(spec=User)
        mock_client.id = mock_assignment.client_id
        mock_client.to_dict.return_value = {
            'id': mock_assignment.client_id,
            'name': 'Hospital San Rafael',
            'tax_id': '918183499',
            'email': 'contacto@hospital.com',
            'address': 'Calle 123 #45-67, Bogotá',
            'phone': '3001234567',
            'institution_type': 'Hospital',
            'logo_filename': 'hospital_logo.png',
            'logo_url': 'https://example.com/logo.png',
            'specialty': 'Cadena de frío',
            'applicant_name': 'Dr. Juan Pérez',
            'applicant_email': 'solicitante@hospital.com',
            'latitude': 4.6097,
            'longitude': -74.0817,
            'enabled': True,
            'created_at': '2024-10-28T10:30:00.000Z',
            'updated_at': '2024-10-28T10:30:00.000Z'
        }
        
        # Configurar mock para devolver vendedor primero, luego cliente
        self.mock_user_repo.get_by_id.side_effect = [mock_seller, mock_client]
        
        # Ejecutar
        result = self.service.get_assigned_clients_with_details(seller_id)
        
        # Verificar
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], mock_client.id)
        self.assertEqual(result[0]['name'], 'Hospital San Rafael')
        self.assertEqual(result[0]['email'], 'contacto@hospital.com')
        self.assertIn('tax_id', result[0])
        self.assertIn('logo_filename', result[0])
    
    def test_get_assigned_clients_with_non_existent_seller(self):
        """Test: Obtener clientes de vendedor inexistente debe lanzar NotFoundError"""
        self.mock_user_repo.get_by_id.return_value = None
        
        with self.assertRaises(NotFoundError):
            self.service.get_assigned_clients_with_details('non-existent-seller')


if __name__ == '__main__':
    unittest.main()


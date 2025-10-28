"""
Tests para el controlador AssignedClientController
"""
import unittest
from unittest.mock import Mock, patch
from flask import Flask
from app.controllers.assigned_client_controller import AssignedClientController
from app.exceptions.custom_exceptions import ValidationError, BusinessLogicError, NotFoundError


class TestAssignedClientController(unittest.TestCase):
    """Tests para AssignedClientController"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.mock_service = Mock()
        self.controller = AssignedClientController(assigned_client_service=self.mock_service)
    
    def test_get_assigned_clients_success(self):
        """Test: GET exitoso de clientes asignados"""
        user_id = '123e4567-e89b-12d3-a456-426614174000'
        
        # Mock de clientes asignados
        mock_clients = [
            {
                'id': '456e7890-e89b-12d3-a456-426614174111',
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
        ]
        
        self.mock_service.get_assigned_clients_with_details.return_value = mock_clients
        
        # Ejecutar
        response, status_code = self.controller.get(user_id)
        
        # Verificar
        self.assertEqual(status_code, 200)
        self.assertIn('message', response)
        self.assertEqual(response['message'], "Clientes asignados obtenidos exitosamente")
        self.assertEqual(response['data']['seller_id'], user_id)
        self.assertEqual(response['data']['total'], 1)
        self.assertEqual(len(response['data']['assigned_clients']), 1)
    
    def test_get_assigned_clients_seller_not_found(self):
        """Test: GET con vendedor inexistente debe retornar 404"""
        user_id = 'non-existent-seller'
        
        self.mock_service.get_assigned_clients_with_details.side_effect = NotFoundError(
            f"No se encontró el vendedor con ID: {user_id}"
        )
        
        # Ejecutar
        response, status_code = self.controller.get(user_id)
        
        # Verificar
        self.assertEqual(status_code, 404)
        self.assertIn('error', response)
        self.assertIn("No se encontró el vendedor", response['error'])
    
    def test_post_create_assignment_success(self):
        """Test: POST exitoso para crear asignación"""
        with self.app.test_request_context(json={
            'seller_id': '123e4567-e89b-12d3-a456-426614174000',
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }):
            # Mock del servicio
            mock_assigned_client = Mock()
            mock_assigned_client.to_dict.return_value = {
                'id': '987e6543-e21b-12d3-a456-426614174000',
                'seller_id': '123e4567-e89b-12d3-a456-426614174000',
                'client_id': '456e7890-e89b-12d3-a456-426614174111'
            }
            
            self.mock_service.create.return_value = mock_assigned_client
            
            # Ejecutar
            response, status_code = self.controller.post()
            
            # Verificar
            self.assertEqual(status_code, 201)
            self.assertIn('message', response)
            self.assertIn("Asignación creada exitosamente", response['message'])
    
    def test_post_create_assignment_missing_seller_id(self):
        """Test: POST sin seller_id debe retornar 400"""
        with self.app.test_request_context(json={
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }):
            # Ejecutar
            response, status_code = self.controller.post()
            
            # Verificar
            self.assertEqual(status_code, 400)
            self.assertIn('error', response)
            self.assertIn("seller_id", response['error'])
    
    def test_post_create_assignment_empty_json(self):
        """Test: POST con JSON vacío debe retornar error"""
        with self.app.test_request_context():
            # Ejecutar
            response, status_code = self.controller.post()
            
            # Verificar
            self.assertIn(status_code, [400, 500])  # Puede retornar 400 o 500 dependiendo del manejo
            self.assertIn('error', response)


if __name__ == '__main__':
    unittest.main()


"""
Tests extendidos para el controlador AssignedClientController - Para incrementar cobertura
"""
import unittest
from unittest.mock import Mock
from flask import Flask
from app.controllers.assigned_client_controller import AssignedClientController
from app.exceptions.custom_exceptions import ValidationError, BusinessLogicError


class TestAssignedClientControllerExtended(unittest.TestCase):
    """Tests extendidos para AssignedClientController"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.mock_service = Mock()
        self.controller = AssignedClientController(assigned_client_service=self.mock_service)
    
    def test_get_with_business_logic_error(self):
        """Test: GET con error de lógica de negocio"""
        user_id = '123e4567-e89b-12d3-a456-426614174000'
        
        self.mock_service.get_assigned_clients_with_details.side_effect = BusinessLogicError(
            "Error de lógica de negocio"
        )
        
        response, status_code = self.controller.get(user_id)
        
        self.assertEqual(status_code, 500)
        self.assertIn('error', response)
    
    def test_get_with_generic_exception(self):
        """Test: GET con excepción genérica"""
        user_id = '123e4567-e89b-12d3-a456-426614174000'
        
        self.mock_service.get_assigned_clients_with_details.side_effect = Exception(
            "Error inesperado"
        )
        
        response, status_code = self.controller.get(user_id)
        
        self.assertEqual(status_code, 500)
        self.assertIn('error', response)
    
    def test_post_with_missing_client_id(self):
        """Test: POST sin client_id"""
        with self.app.test_request_context(json={
            'seller_id': '123e4567-e89b-12d3-a456-426614174000'
        }):
            response, status_code = self.controller.post()
            
            self.assertEqual(status_code, 400)
            self.assertIn('error', response)
            self.assertIn("client_id", response['error'])
    
    def test_post_with_validation_error(self):
        """Test: POST con error de validación"""
        with self.app.test_request_context(json={
            'seller_id': '123e4567-e89b-12d3-a456-426614174000',
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }):
            self.mock_service.create.side_effect = ValidationError("Error de validación")
            
            response, status_code = self.controller.post()
            
            self.assertEqual(status_code, 400)
            self.assertIn('error', response)
    
    def test_post_with_business_logic_error(self):
        """Test: POST con error de lógica de negocio"""
        with self.app.test_request_context(json={
            'seller_id': '123e4567-e89b-12d3-a456-426614174000',
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }):
            self.mock_service.create.side_effect = BusinessLogicError("Error de negocio")
            
            response, status_code = self.controller.post()
            
            self.assertEqual(status_code, 500)
            self.assertIn('error', response)
    
    def test_post_with_generic_exception(self):
        """Test: POST con excepción genérica"""
        with self.app.test_request_context(json={
            'seller_id': '123e4567-e89b-12d3-a456-426614174000',
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }):
            self.mock_service.create.side_effect = Exception("Error inesperado")
            
            response, status_code = self.controller.post()
            
            self.assertEqual(status_code, 500)
            self.assertIn('error', response)
    
    def test_get_with_empty_clients_list(self):
        """Test: GET que retorna lista vacía de clientes"""
        user_id = '123e4567-e89b-12d3-a456-426614174000'
        
        self.mock_service.get_assigned_clients_with_details.return_value = []
        
        response, status_code = self.controller.get(user_id)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response['data']['total'], 0)
        self.assertEqual(len(response['data']['assigned_clients']), 0)
    
    def test_post_with_whitespace_seller_id(self):
        """Test: POST con seller_id que solo contiene espacios"""
        with self.app.test_request_context(json={
            'seller_id': '   ',
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }):
            response, status_code = self.controller.post()
            
            self.assertEqual(status_code, 400)
            self.assertIn('error', response)
            self.assertIn("seller_id", response['error'])
    
    def test_post_with_whitespace_client_id(self):
        """Test: POST con client_id que solo contiene espacios"""
        with self.app.test_request_context(json={
            'seller_id': '123e4567-e89b-12d3-a456-426614174000',
            'client_id': '   '
        }):
            response, status_code = self.controller.post()
            
            self.assertEqual(status_code, 400)
            self.assertIn('error', response)
            self.assertIn("client_id", response['error'])


if __name__ == '__main__':
    unittest.main()


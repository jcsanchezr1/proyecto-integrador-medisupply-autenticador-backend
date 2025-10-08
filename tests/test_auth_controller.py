"""
Tests para el controlador de autenticación
"""
import unittest
from unittest.mock import Mock
from flask import Flask
from app.controllers.auth_controller import AuthController
from app.services.auth_service import AuthService
from app.exceptions.custom_exceptions import ValidationError, BusinessLogicError


class TestAuthController(unittest.TestCase):
    """Tests para AuthController"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.mock_auth_service = Mock(spec=AuthService)
        self.auth_controller = AuthController(auth_service=self.mock_auth_service)
    
    def test_post_login_success(self):
        """Test de login exitoso"""
        # Datos de prueba
        user_email = "test@example.com"
        password = "password123"
        
        # Mock de respuesta exitosa del servicio
        keycloak_response = {
            "access_token": "AccessToken",
            "expires_in": 300,
            "refresh_expires_in": 1800,
            "refresh_token": "RefreshToken",
            "token_type": "Bearer",
            "not-before-policy": 0,
            "session_state": "2ea068ec-21b1-4ba7-ab64-44cc50d3080f",
            "scope": "email profile"
        }
        self.mock_auth_service.authenticate_user.return_value = keycloak_response
        
        # Simular request
        with self.app.test_request_context('/auth/token', 
                                         method='POST',
                                         json={'user': user_email, 'password': password}):
            # Ejecutar el método
            response, status_code = self.auth_controller.post()
            
            # Verificaciones
            self.assertEqual(status_code, 200)
            self.assertEqual(response, keycloak_response)
            self.mock_auth_service.authenticate_user.assert_called_once_with(user_email, password)
    
    def test_post_login_validation_error(self):
        """Test de login con error de validación"""
        user_email = "invalid-email"
        password = "password123"
        
        # Mock de error de validación del servicio
        self.mock_auth_service.authenticate_user.side_effect = ValidationError("El campo 'user' debe ser un email válido")
        
        # Simular request
        with self.app.test_request_context('/auth/token', 
                                         method='POST',
                                         json={'user': user_email, 'password': password}):
            # Ejecutar el método
            response, status_code = self.auth_controller.post()
            
            # Verificaciones
            self.assertEqual(status_code, 400)
            self.assertIn('error', response)
            self.assertEqual(response['error'], "El campo 'user' debe ser un email válido")
    
    def test_post_login_business_logic_error(self):
        """Test de login con error de lógica de negocio"""
        user_email = "test@example.com"
        password = "wrongpassword"
        
        # Mock de error de lógica de negocio del servicio
        self.mock_auth_service.authenticate_user.side_effect = BusinessLogicError("Credenciales inválidas")
        
        # Simular request
        with self.app.test_request_context('/auth/token', 
                                         method='POST',
                                         json={'user': user_email, 'password': password}):
            # Ejecutar el método
            response, status_code = self.auth_controller.post()
            
            # Verificaciones
            self.assertEqual(status_code, 401)
            self.assertIn('error', response)
            self.assertEqual(response['error'], "Credenciales inválidas")
    
    def test_post_login_keycloak_error(self):
        """Test de login con error de Keycloak"""
        user_email = "test@example.com"
        password = "wrongpassword"
        
        # Mock de error de Keycloak (dict)
        keycloak_error = {
            "error": "invalid_grant",
            "error_description": "Invalid user credentials"
        }
        self.mock_auth_service.authenticate_user.side_effect = BusinessLogicError(keycloak_error)
        
        # Simular request
        with self.app.test_request_context('/auth/token', 
                                         method='POST',
                                         json={'user': user_email, 'password': password}):
            # Ejecutar el método
            response, status_code = self.auth_controller.post()
            
            # Verificaciones
            self.assertEqual(status_code, 401)
            self.assertIn('error', response)
            self.assertEqual(response['error'], keycloak_error)
    
    def test_post_login_empty_json(self):
        """Test de login con JSON vacío"""
        with self.app.test_request_context('/auth/token', 
                                         method='POST',
                                         data='{}',
                                         content_type='application/json'):
            # Ejecutar el método
            response, status_code = self.auth_controller.post()
            
            # Verificaciones
            self.assertEqual(status_code, 400)
            self.assertIn('error', response)
            self.assertEqual(response['error'], "El cuerpo de la petición JSON está vacío")
    
    def test_post_login_general_exception(self):
        """Test de login con excepción general"""
        user_email = "test@example.com"
        password = "password123"
        
        # Mock de excepción general
        self.mock_auth_service.authenticate_user.side_effect = Exception("Error inesperado")
        
        # Simular request
        with self.app.test_request_context('/auth/token', 
                                         method='POST',
                                         json={'user': user_email, 'password': password}):
            # Ejecutar el método
            response, status_code = self.auth_controller.post()
            
            # Verificaciones
            self.assertEqual(status_code, 500)
            self.assertIn('error', response)


if __name__ == '__main__':
    unittest.main()
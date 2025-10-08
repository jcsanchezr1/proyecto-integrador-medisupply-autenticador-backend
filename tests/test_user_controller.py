"""
Pruebas unitarias para UserController usando unittest
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.controllers.user_controller import UserController, UserHealthController, UserDeleteAllController
from app.exceptions.custom_exceptions import ValidationError, BusinessLogicError, NotFoundError


class TestUserController(unittest.TestCase):
    """Pruebas para UserController"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.mock_user_service = Mock()
        self.controller = UserController(user_service=self.mock_user_service)
    
    def test_init_with_user_service(self):
        """Prueba que el controlador se inicializa con el servicio de usuario"""
        self.assertEqual(self.controller.user_service, self.mock_user_service)
    
    def test_init_without_user_service(self):
        """Prueba que el controlador se inicializa sin servicio de usuario"""
        with patch('app.controllers.user_controller.UserService') as mock_service:
            controller = UserController()
            self.assertIsNotNone(controller.user_service)
    
    def test_get_user_by_id_success(self):
        """Prueba obtener usuario por ID exitosamente"""
        # Configurar mock
        mock_user = Mock()
        mock_user.to_dict.return_value = {"id": "123", "name": "Test"}
        self.mock_user_service.get_by_id.return_value = mock_user
        
        # Ejecutar
        response, status_code = self.controller.get(user_id="123")
        
        # Verificar
        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], "Usuario obtenido exitosamente")
        self.assertEqual(response["data"], {"id": "123", "name": "Test"})
        self.mock_user_service.get_by_id.assert_called_once_with("123")
    
    def test_get_user_by_id_not_found(self):
        """Prueba obtener usuario por ID cuando no existe"""
        # Configurar mock
        self.mock_user_service.get_by_id.return_value = None
        
        # Ejecutar
        response, status_code = self.controller.get(user_id="123")
        
        # Verificar
        self.assertEqual(status_code, 404)
        self.assertEqual(response["error"], "Usuario no encontrado")
    
    def test_get_business_logic_error(self):
        """Prueba manejo de BusinessLogicError en get"""
        # Configurar mock
        self.mock_user_service.get_by_id.side_effect = BusinessLogicError("Error de negocio")
        
        # Ejecutar
        response, status_code = self.controller.get(user_id="123")
        
        # Verificar
        self.assertEqual(status_code, 500)
        self.assertEqual(response["error"], "Error de negocio")
    
    def test_post_success(self):
        """Prueba crear usuario exitosamente"""
        # Configurar mock
        mock_user = Mock()
        mock_user.to_dict.return_value = {"id": "123", "name": "Test Hospital"}
        self.mock_user_service.create_user_with_validation.return_value = mock_user
        
        # Mock del método _process_json_request
        with patch.object(self.controller, '_process_json_request') as mock_process:
            user_data = {
                'institution_name': 'Test Hospital',
                'tax_id': '123456789',
                'email': 'test@hospital.com',
                'address': 'Test Address',
                'phone': '1234567890',
                'institution_type': 'Hospital',
                'specialty': 'Alto valor',
                'applicant_name': 'John Doe',
                'applicant_email': 'john@hospital.com',
                'password': 'password123',
                'confirm_password': 'password123'
            }
            mock_process.return_value = user_data
            
            # Usar contexto de Flask para la prueba
            with self.app.test_request_context():
                response, status_code = self.controller.post()
                
                # Verificar
                self.assertEqual(status_code, 201)
                self.assertEqual(response["message"], "Usuario registrado exitosamente")
                self.assertEqual(response["data"], {"id": "123", "name": "Test Hospital"})
    
    def test_post_validation_error(self):
        """Prueba crear usuario con error de validación"""
        # Configurar mock
        self.mock_user_service.create_user_with_validation.side_effect = ValidationError("Campo obligatorio")
        
        # Mock del método _process_json_request
        with patch.object(self.controller, '_process_json_request') as mock_process:
            user_data = {
                'institution_name': '',  # Campo vacío
                'tax_id': '123456789',
                'email': 'test@hospital.com',
                'address': 'Test Address',
                'phone': '1234567890',
                'institution_type': 'Hospital',
                'specialty': 'Alto valor',
                'applicant_name': 'John Doe',
                'applicant_email': 'john@hospital.com',
                'password': 'password123',
                'confirm_password': 'password123'
            }
            mock_process.return_value = user_data
            
            # Usar contexto de Flask para la prueba
            with self.app.test_request_context():
                response, status_code = self.controller.post()
                
                # Verificar
                self.assertEqual(status_code, 400)
                self.assertEqual(response["error"], "Campo obligatorio")
    
    def test_post_business_logic_error(self):
        """Prueba crear usuario con error de lógica de negocio"""
        # Configurar mock
        self.mock_user_service.create_user_with_validation.side_effect = BusinessLogicError("Error de Keycloak")
        
        # Mock del método _process_json_request
        with patch.object(self.controller, '_process_json_request') as mock_process:
            user_data = {
                'institution_name': 'Test Hospital',
                'tax_id': '123456789',
                'email': 'test@hospital.com',
                'address': 'Test Address',
                'phone': '1234567890',
                'institution_type': 'Hospital',
                'specialty': 'Alto valor',
                'applicant_name': 'John Doe',
                'applicant_email': 'john@hospital.com',
                'password': 'password123',
                'confirm_password': 'password123'
            }
            mock_process.return_value = user_data
            
            # Usar contexto de Flask para la prueba
            with self.app.test_request_context():
                response, status_code = self.controller.post()
                
                # Verificar
                self.assertEqual(status_code, 500)
                self.assertIn("Error de negocio", response["error"])
    
    def test_post_empty_json(self):
        """Prueba crear usuario con JSON vacío"""
        # Mock del método _process_json_request para lanzar ValidationError
        with patch.object(self.controller, '_process_json_request') as mock_process:
            mock_process.side_effect = ValidationError("El cuerpo de la petición JSON está vacío")
            
            # Usar contexto de Flask para la prueba
            with self.app.test_request_context():
                response, status_code = self.controller.post()
                
                # Verificar
                self.assertEqual(status_code, 400)
                self.assertIn("JSON está vacío", response["error"])


class TestUserHealthController(unittest.TestCase):
    """Pruebas para UserHealthController"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.controller = UserHealthController()
    
    def test_get_health_check_success(self):
        """Prueba health check exitoso"""
        response, status_code = self.controller.get()
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], "Servicio de usuarios funcionando correctamente")
        self.assertEqual(response["data"]["service"], "users")
        self.assertEqual(response["data"]["status"], "healthy")
        self.assertEqual(response["data"]["version"], "1.0.0")
    
    def test_get_health_check_exception(self):
        """Prueba health check con excepción"""
        # Simular excepción
        with patch.object(self.controller, 'success_response', side_effect=Exception("Error")):
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 500)
            self.assertIn("error", response)


class TestUserDeleteAllController(unittest.TestCase):
    """Pruebas para UserDeleteAllController"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.mock_user_service = Mock()
        self.controller = UserDeleteAllController(user_service=self.mock_user_service)
    
    def test_init_with_user_service(self):
        """Prueba que el controlador se inicializa con el servicio de usuario"""
        self.assertEqual(self.controller.user_service, self.mock_user_service)
    
    def test_init_without_user_service(self):
        """Prueba que el controlador se inicializa sin servicio de usuario"""
        with patch('app.controllers.user_controller.UserService') as mock_service:
            controller = UserDeleteAllController()
            self.assertIsNotNone(controller.user_service)
    
    def test_delete_all_success(self):
        """Prueba eliminar todos los usuarios exitosamente"""
        # Configurar mock
        self.mock_user_service.delete_all.return_value = 5
        
        # Ejecutar
        response, status_code = self.controller.delete()
        
        # Verificar
        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], "Se eliminaron 5 usuarios exitosamente")
        self.assertEqual(response["data"]["deleted_count"], 5)
        self.mock_user_service.delete_all.assert_called_once()
    
    def test_delete_all_business_logic_error(self):
        """Prueba eliminar todos los usuarios con error de lógica de negocio"""
        # Configurar mock
        self.mock_user_service.delete_all.side_effect = BusinessLogicError("Error de base de datos")
        
        # Ejecutar
        response, status_code = self.controller.delete()
        
        # Verificar
        self.assertEqual(status_code, 500)
        self.assertIn("Error temporal del sistema", response["error"])
    
    def test_delete_all_general_exception(self):
        """Prueba eliminar todos los usuarios con excepción general"""
        # Configurar mock
        self.mock_user_service.delete_all.side_effect = Exception("Error inesperado")
        
        # Ejecutar
        response, status_code = self.controller.delete()
        
        # Verificar
        self.assertEqual(status_code, 500)
        self.assertIn("Error temporal del sistema", response["error"])


if __name__ == '__main__':
    unittest.main()

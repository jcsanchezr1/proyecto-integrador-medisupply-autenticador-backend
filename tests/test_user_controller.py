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

from app.controllers.user_controller import UserController, UserDeleteAllController, AdminUserController
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
                'name': 'Test Hospital',
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
                'name': '',  # Campo vacío
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
                'name': 'Test Hospital',
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


class TestUserControllerExtended(unittest.TestCase):
    """Pruebas adicionales para UserController para aumentar cobertura"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.mock_user_service = Mock()
        self.controller = UserController(user_service=self.mock_user_service)
    
    def test_get_users_list_success(self):
        """Prueba GET para obtener lista de usuarios exitosamente"""
        with self.app.test_request_context('/auth/user?page=1&per_page=10'):
            # Configurar mocks
            mock_users = [
                {'id': '1', 'name': 'Hospital 1', 'email': 'h1@test.com'},
                {'id': '2', 'name': 'Hospital 2', 'email': 'h2@test.com'}
            ]
            self.mock_user_service.get_users_summary.return_value = mock_users
            self.mock_user_service.get_users_count.return_value = 2
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 200)
            self.assertIn('data', response)
            self.assertIn('users', response['data'])
            self.assertIn('pagination', response['data'])
            self.assertEqual(len(response['data']['users']), 2)
    
    def test_get_users_list_invalid_page(self):
        """Prueba GET con página inválida"""
        with self.app.test_request_context('/auth/user?page=0&per_page=10'):
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 400)
            self.assertIn("page", response["error"])
    
    def test_get_users_list_invalid_per_page(self):
        """Prueba GET con per_page inválido"""
        with self.app.test_request_context('/auth/user?page=1&per_page=0'):
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 400)
            self.assertIn("per_page", response["error"])
    
    def test_get_users_list_per_page_too_large(self):
        """Prueba GET con per_page muy grande"""
        with self.app.test_request_context('/auth/user?page=1&per_page=101'):
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 400)
            self.assertIn("per_page", response["error"])
    
    def test_get_users_list_default_params(self):
        """Prueba GET con parámetros por defecto"""
        with self.app.test_request_context('/auth/user'):
            # Configurar mocks
            self.mock_user_service.get_users_summary.return_value = []
            self.mock_user_service.get_users_count.return_value = 0
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 200)
            self.mock_user_service.get_users_summary.assert_called_once_with(limit=10, offset=0)
    
    def test_process_json_request_success(self):
        """Prueba _process_json_request exitoso"""
        with self.app.test_request_context('/auth/user', method='POST', json={
            'name': 'Test Hospital',
            'tax_id': '12345678-9',
            'email': 'test@hospital.com',
            'address': '123 Main St',
            'phone': '+1234567890',
            'institution_type': 'Hospital',
            'specialty': 'Cardiología',
            'applicant_name': 'Dr. Smith',
            'applicant_email': 'dr.smith@hospital.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'logo_filename': 'logo.jpg'
        }):
            result = self.controller._process_json_request()
            
            self.assertEqual(result['name'], 'Test Hospital')
            self.assertEqual(result['email'], 'test@hospital.com')
            self.assertEqual(result['logo_filename'], 'logo.jpg')
    
    def test_process_json_request_missing_field(self):
        """Prueba _process_json_request con campo faltante"""
        with self.app.test_request_context('/auth/user', method='POST', json={
            'name': 'Test Hospital',
            'email': 'test@hospital.com'
            # Faltan otros campos requeridos
        }):
            with self.assertRaises(ValidationError) as context:
                self.controller._process_json_request()
            
            self.assertIn("obligatorio", str(context.exception))
    
    def test_process_multipart_request_success(self):
        """Prueba _process_multipart_request exitoso"""
        with self.app.test_request_context('/auth/user', method='POST', data={
            'name': 'Test Hospital',
            'tax_id': '12345678-9',
            'email': 'test@hospital.com',
            'address': '123 Main St',
            'phone': '+1234567890',
            'institution_type': 'Hospital',
            'specialty': 'Cardiología',
            'applicant_name': 'Dr. Smith',
            'applicant_email': 'dr.smith@hospital.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }):
            result = self.controller._process_multipart_request()
            
            self.assertEqual(result['name'], 'Test Hospital')
            self.assertEqual(result['email'], 'test@hospital.com')
            self.assertIsNone(result['logo_file'])
    
    def test_process_multipart_request_missing_field(self):
        """Prueba _process_multipart_request con campo faltante"""
        with self.app.test_request_context('/auth/user', method='POST', data={
            'name': 'Test Hospital',
            'email': 'test@hospital.com'
            # Faltan otros campos requeridos
        }):
            with self.assertRaises(ValidationError) as context:
                self.controller._process_multipart_request()
            
            self.assertIn("obligatorio", str(context.exception))
    
    def test_post_multipart_request(self):
        """Prueba POST con multipart/form-data"""
        with self.app.test_request_context('/auth/user', method='POST', 
                                         content_type='multipart/form-data',
                                         data={
                                             'name': 'Test Hospital',
                                             'tax_id': '12345678-9',
                                             'email': 'test@hospital.com',
                                             'address': '123 Main St',
                                             'phone': '+1234567890',
                                             'institution_type': 'Hospital',
                                             'specialty': 'Cardiología',
                                             'applicant_name': 'Dr. Smith',
                                             'applicant_email': 'dr.smith@hospital.com',
                                             'password': 'password123',
                                             'confirm_password': 'password123'
                                         }):
            # Configurar mock
            mock_user = Mock()
            mock_user.to_dict.return_value = {'id': '123', 'name': 'Test Hospital'}
            self.mock_user_service.create_user_with_validation.return_value = mock_user
            
            response, status_code = self.controller.post()
            
            self.assertEqual(status_code, 201)
            self.assertIn('data', response)
    
    def test_post_general_exception(self):
        """Prueba POST con excepción general"""
        with self.app.test_request_context('/auth/user', method='POST', json={
            'name': 'Test Hospital',
            'tax_id': '12345678-9',
            'email': 'test@hospital.com',
            'address': '123 Main St',
            'phone': '+1234567890',
            'institution_type': 'Hospital',
            'specialty': 'Cardiología',
            'applicant_name': 'Dr. Smith',
            'applicant_email': 'dr.smith@hospital.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }):
            # Configurar mock para lanzar excepción general
            self.mock_user_service.create_user_with_validation.side_effect = Exception("Error inesperado")
            
            response, status_code = self.controller.post()
            
            self.assertEqual(status_code, 500)
            self.assertIn("Error del sistema", response["error"])


class TestAdminUserController(unittest.TestCase):
    """Pruebas para AdminUserController"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.mock_user_service = Mock()
        self.controller = AdminUserController(user_service=self.mock_user_service)
    
    def test_controller_initialization(self):
        """Test de inicialización del controlador"""
        self.assertIsNotNone(self.controller)
        self.assertEqual(self.controller.user_service, self.mock_user_service)
    
    def test_controller_with_default_service(self):
        """Test de inicialización con servicio por defecto"""
        # Mock del UserService para evitar dependencias de base de datos
        with patch('app.controllers.user_controller.UserService') as mock_service:
            controller = AdminUserController()
            self.assertIsNotNone(controller.user_service)


if __name__ == '__main__':
    unittest.main()

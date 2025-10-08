"""
Pruebas unitarias para KeycloakClient usando unittest
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.external.keycloak_client import KeycloakClient
from app.exceptions.custom_exceptions import BusinessLogicError


class TestKeycloakClient(unittest.TestCase):
    """Pruebas para KeycloakClient"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        with patch.dict(os.environ, {
            'KC_BASE_URL': 'http://test-keycloak:8080',
            'KC_ADMIN_USER': 'test-admin',
            'KC_ADMIN_PASS': 'test-password'
        }):
            self.client = KeycloakClient()
    
    def test_init_with_default_values(self):
        """Prueba inicialización con valores por defecto"""
        with patch.dict(os.environ, {}, clear=True):
            client = KeycloakClient()
            
            self.assertEqual(client.base_url, 'http://localhost:8080')
            self.assertEqual(client.admin_user, 'admin')
            self.assertEqual(client.admin_pass, 'admin')
            self.assertEqual(client.realm, 'medisupply-realm')
    
    def test_init_with_environment_variables(self):
        """Prueba inicialización con variables de entorno"""
        self.assertEqual(self.client.base_url, 'http://test-keycloak:8080')
        self.assertEqual(self.client.admin_user, 'test-admin')
        self.assertEqual(self.client.admin_pass, 'test-password')
        self.assertEqual(self.client.realm, 'medisupply-realm')
    
    @patch('app.external.keycloak_client.requests.post')
    @patch('time.time')
    def test_get_admin_token_success(self, mock_time, mock_post):
        """Prueba obtener token de administrador exitosamente"""
        # Configurar mocks
        mock_time.return_value = 1000  # Tiempo actual
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test-token',
            'expires_in': 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Ejecutar
        token = self.client._get_admin_token()
        
        # Verificar
        self.assertEqual(token, 'test-token')
        self.assertEqual(self.client._admin_token, 'test-token')
        self.assertEqual(self.client._token_expires_at, 1000 + 3600 - 60)
        mock_post.assert_called_once()
    
    @patch('app.external.keycloak_client.requests.post')
    @patch('time.time')
    def test_get_admin_token_reuse_existing(self, mock_time, mock_post):
        """Prueba reutilizar token existente válido"""
        # Configurar mocks
        self.client._admin_token = 'existing-token'
        self.client._token_expires_at = 2000  # Token válido hasta tiempo 2000
        mock_time.return_value = 1000  # Tiempo actual menor al de expiración
        
        # Ejecutar
        token = self.client._get_admin_token()
        
        # Verificar
        self.assertEqual(token, 'existing-token')
        mock_post.assert_not_called()  # No debe hacer nueva petición
    
    @patch('app.external.keycloak_client.requests.post')
    @patch('time.time')
    def test_get_admin_token_expired(self, mock_time, mock_post):
        """Prueba obtener nuevo token cuando el existente expiró"""
        # Configurar mocks
        self.client._admin_token = 'expired-token'
        self.client._token_expires_at = 500  # Token expirado
        mock_time.return_value = 1000  # Tiempo actual mayor al de expiración
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'new-token',
            'expires_in': 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Ejecutar
        token = self.client._get_admin_token()
        
        # Verificar
        self.assertEqual(token, 'new-token')
        self.assertEqual(self.client._admin_token, 'new-token')
        mock_post.assert_called_once()
    
    @patch('app.external.keycloak_client.requests.post')
    def test_get_admin_token_request_exception(self, mock_post):
        """Prueba manejo de excepción en petición de token"""
        # Configurar mock
        mock_post.side_effect = Exception("Connection error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.client._get_admin_token()
        
        self.assertIn("Error inesperado al obtener token de Keycloak", str(context.exception))
    
    @patch('app.external.keycloak_client.requests.post')
    def test_get_admin_token_http_error(self, mock_post):
        """Prueba manejo de error HTTP en petición de token"""
        # Configurar mock
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 401")
        mock_post.return_value = mock_response
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.client._get_admin_token()
        
        self.assertIn("Error inesperado al obtener token de Keycloak", str(context.exception))
    
    @patch.object(KeycloakClient, '_get_admin_token')
    @patch('app.external.keycloak_client.requests.post')
    def test_create_user_success(self, mock_post, mock_get_token):
        """Prueba crear usuario exitosamente"""
        # Configurar mocks
        mock_get_token.return_value = 'test-token'
        mock_response = Mock()
        mock_response.headers = {'Location': '/admin/realms/medisupply-realm/users/user-123'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Ejecutar
        user_id = self.client.create_user(
            email='test@hospital.com',
            password='password123',
            name='Test Hospital'
        )
        
        # Verificar
        self.assertEqual(user_id, 'user-123')
        mock_get_token.assert_called_once()
        mock_post.assert_called_once()
    
    @patch.object(KeycloakClient, '_get_admin_token')
    @patch('app.external.keycloak_client.requests.post')
    def test_create_user_no_location_header(self, mock_post, mock_get_token):
        """Prueba crear usuario sin header Location"""
        # Configurar mocks
        mock_get_token.return_value = 'test-token'
        mock_response = Mock()
        mock_response.headers = {}  # Sin Location header
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.client.create_user(
                email='test@hospital.com',
                password='password123',
                name='Test Hospital'
            )
        
        self.assertIn("No se pudo obtener el ID del usuario creado", str(context.exception))
    
    @patch.object(KeycloakClient, '_get_admin_token')
    @patch('app.external.keycloak_client.requests.post')
    def test_create_user_request_exception(self, mock_post, mock_get_token):
        """Prueba crear usuario con excepción en petición"""
        # Configurar mocks
        mock_get_token.return_value = 'test-token'
        mock_post.side_effect = Exception("Connection error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.client.create_user(
                email='test@hospital.com',
                password='password123',
                name='Test Hospital'
            )
        
        self.assertIn("Error inesperado al crear usuario en Keycloak", str(context.exception))
    
    @patch.object(KeycloakClient, '_get_admin_token')
    @patch('app.external.keycloak_client.requests.post')
    def test_assign_role_to_user_success(self, mock_post, mock_get_token):
        """Prueba asignar rol a usuario exitosamente"""
        # Configurar mocks
        mock_get_token.return_value = 'test-token'
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Ejecutar
        self.client.assign_role_to_user('user-123', 'Cliente')
        
        # Verificar
        mock_get_token.assert_called_once()
        mock_post.assert_called_once()
    
    @patch.object(KeycloakClient, '_get_admin_token')
    @patch('app.external.keycloak_client.requests.post')
    def test_assign_role_to_user_invalid_role(self, mock_post, mock_get_token):
        """Prueba asignar rol inválido a usuario"""
        # Configurar mocks
        mock_get_token.return_value = 'test-token'
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.client.assign_role_to_user('user-123', 'InvalidRole')
        
        self.assertIn("Rol 'InvalidRole' no válido", str(context.exception))
        mock_post.assert_not_called()
    
    @patch.object(KeycloakClient, '_get_admin_token')
    @patch('app.external.keycloak_client.requests.post')
    def test_assign_role_to_user_request_exception(self, mock_post, mock_get_token):
        """Prueba asignar rol con excepción en petición"""
        # Configurar mocks
        mock_get_token.return_value = 'test-token'
        mock_post.side_effect = Exception("Connection error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.client.assign_role_to_user('user-123', 'Cliente')
        
        self.assertIn("Error inesperado al asignar rol en Keycloak", str(context.exception))
    
    @patch.object(KeycloakClient, '_get_admin_token')
    @patch('app.external.keycloak_client.requests.delete')
    def test_delete_user_success(self, mock_delete, mock_get_token):
        """Prueba eliminar usuario exitosamente"""
        # Configurar mocks
        mock_get_token.return_value = 'test-token'
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        # Ejecutar
        self.client.delete_user('user-123')
        
        # Verificar
        mock_get_token.assert_called_once()
        mock_delete.assert_called_once()
    
    @patch.object(KeycloakClient, '_get_admin_token')
    @patch('app.external.keycloak_client.requests.delete')
    def test_delete_user_request_exception(self, mock_delete, mock_get_token):
        """Prueba eliminar usuario con excepción en petición"""
        # Configurar mocks
        mock_get_token.return_value = 'test-token'
        mock_delete.side_effect = Exception("Connection error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.client.delete_user('user-123')
        
        self.assertIn("Error inesperado al eliminar usuario de Keycloak", str(context.exception))
    
    def test_get_available_roles(self):
        """Prueba obtener roles disponibles"""
        roles = self.client.get_available_roles()
        
        expected_roles = ["Administrador", "Compras", "Ventas", "Logistica", "Cliente"]
        self.assertEqual(roles, expected_roles)
    
    def test_role_mapping_structure(self):
        """Prueba que el mapeo de roles tiene la estructura correcta"""
        # Este test verifica que el método assign_role_to_user maneja correctamente
        # los roles definidos en el mapeo interno
        valid_roles = self.client.get_available_roles()
        
        # Verificar que todos los roles esperados están disponibles
        expected_roles = ["Administrador", "Compras", "Ventas", "Logistica", "Cliente"]
        for role in expected_roles:
            self.assertIn(role, valid_roles)
    
    @patch('app.external.keycloak_client.requests.post')
    def test_logout_user_success(self, mock_post):
        """Prueba logout exitoso"""
        # Configurar mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response
        
        # Ejecutar logout
        result = self.client.logout_user("valid_refresh_token")
        
        # Verificaciones
        self.assertEqual(result, {"message": "Logout successful"})
        mock_post.assert_called_once()
        
        # Verificar URL y datos enviados
        call_args = mock_post.call_args
        self.assertIn("/protocol/openid-connect/logout", call_args[0][0])  # URL es el primer argumento posicional
        self.assertEqual(call_args[1]['data']['client_id'], 'medisupply-app')
        self.assertEqual(call_args[1]['data']['refresh_token'], 'valid_refresh_token')
    
    @patch('app.external.keycloak_client.requests.post')
    def test_logout_user_success_200(self, mock_post):
        """Prueba logout exitoso con status 200"""
        # Configurar mock de respuesta exitosa con status 200
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response
        
        # Ejecutar logout
        result = self.client.logout_user("valid_refresh_token")
        
        # Verificaciones
        self.assertEqual(result, {"message": "Logout successful"})
    
    @patch('app.external.keycloak_client.requests.post')
    def test_logout_user_keycloak_error(self, mock_post):
        """Prueba logout con error de Keycloak"""
        # Configurar mock de error de Keycloak
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Invalid refresh token"
        }
        mock_post.return_value = mock_response
        
        # Ejecutar logout
        result = self.client.logout_user("invalid_refresh_token")
        
        # Verificaciones
        self.assertEqual(result["error"], "invalid_grant")
        self.assertEqual(result["error_description"], "Invalid refresh token")
    
    @patch('app.external.keycloak_client.requests.post')
    def test_logout_user_keycloak_error_no_standard_format(self, mock_post):
        """Prueba logout con error de Keycloak sin formato estándar"""
        # Configurar mock de error de Keycloak sin formato estándar
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "message": "Token not found"
        }
        mock_post.return_value = mock_response
        
        # Ejecutar logout
        result = self.client.logout_user("invalid_refresh_token")
        
        # Verificaciones - Keycloak retorna el JSON directamente cuando hay error
        self.assertEqual(result["message"], "Token not found")
    
    @patch('app.external.keycloak_client.requests.post')
    def test_logout_user_json_parse_error(self, mock_post):
        """Prueba logout con error de parsing JSON"""
        # Configurar mock de respuesta con JSON inválido
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        # Ejecutar logout
        result = self.client.logout_user("valid_refresh_token")
        
        # Verificaciones
        self.assertEqual(result["error"], "logout_failed")
        self.assertIn("Status: 500", result["error_description"])
    
    @patch('app.external.keycloak_client.requests.post')
    def test_logout_user_request_exception(self, mock_post):
        """Prueba logout con excepción de requests"""
        # Configurar mock para lanzar excepción
        mock_post.side_effect = Exception("Connection error")
        
        # Ejecutar logout y verificar excepción
        with self.assertRaises(BusinessLogicError) as context:
            self.client.logout_user("valid_refresh_token")
        
        self.assertIn("Error inesperado al cerrar sesión con Keycloak", str(context.exception))
        self.assertIn("Connection error", str(context.exception))
    
    @patch('app.external.keycloak_client.requests.post')
    def test_logout_user_timeout(self, mock_post):
        """Prueba logout con timeout"""
        # Configurar mock para lanzar excepción de timeout
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Ejecutar logout y verificar excepción
        with self.assertRaises(BusinessLogicError) as context:
            self.client.logout_user("valid_refresh_token")
        
        self.assertIn("Error al cerrar sesión con Keycloak", str(context.exception))
        self.assertIn("Request timeout", str(context.exception))


if __name__ == '__main__':
    unittest.main()

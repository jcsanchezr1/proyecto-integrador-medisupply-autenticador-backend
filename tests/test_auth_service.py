"""
Tests para el servicio de autenticación
"""
import unittest
from unittest.mock import Mock, patch
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.external.keycloak_client import KeycloakClient
from app.models.user_model import User
from app.exceptions.custom_exceptions import ValidationError, BusinessLogicError


class TestAuthService(unittest.TestCase):
    """Tests para AuthService"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_user_repository = Mock(spec=UserRepository)
        self.mock_keycloak_client = Mock(spec=KeycloakClient)
        self.auth_service = AuthService(
            user_repository=self.mock_user_repository,
            keycloak_client=self.mock_keycloak_client
        )
    
    def test_authenticate_user_success(self):
        """Test de autenticación exitosa"""
        # Datos de prueba
        user_email = "test@example.com"
        password = "password123"
        
        # Mock del usuario en la base de datos
        mock_user = Mock(spec=User)
        self.mock_user_repository.get_by_email.return_value = mock_user
        
        # Mock de respuesta exitosa de Keycloak
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
        self.mock_keycloak_client.authenticate_user.return_value = keycloak_response
        
        # Ejecutar el método
        result = self.auth_service.authenticate_user(user_email, password)
        
        # Verificaciones
        self.assertEqual(result, keycloak_response)
        self.mock_user_repository.get_by_email.assert_called_once_with(user_email)
        self.mock_keycloak_client.authenticate_user.assert_called_once_with(user_email, password)
    
    def test_authenticate_user_not_found(self):
        """Test cuando el usuario no existe en la base de datos"""
        user_email = "nonexistent@example.com"
        password = "password123"
        
        # Mock de usuario no encontrado
        self.mock_user_repository.get_by_email.return_value = None
        
        # Ejecutar el método y verificar excepción
        with self.assertRaises(BusinessLogicError) as context:
            self.auth_service.authenticate_user(user_email, password)
        
        self.assertEqual(str(context.exception), "Credenciales inválidas")
        self.mock_user_repository.get_by_email.assert_called_once_with(user_email)
        self.mock_keycloak_client.authenticate_user.assert_not_called()
    
    def test_authenticate_user_keycloak_error(self):
        """Test cuando Keycloak retorna error"""
        user_email = "test@example.com"
        password = "wrongpassword"
        
        # Mock del usuario en la base de datos
        mock_user = Mock(spec=User)
        self.mock_user_repository.get_by_email.return_value = mock_user
        
        # Mock de error de Keycloak
        keycloak_error = {
            "error": "invalid_grant",
            "error_description": "Invalid user credentials"
        }
        self.mock_keycloak_client.authenticate_user.return_value = keycloak_error
        
        # Ejecutar el método y verificar excepción
        with self.assertRaises(BusinessLogicError) as context:
            self.auth_service.authenticate_user(user_email, password)
        
        self.assertEqual(context.exception.args[0], keycloak_error)
    
    def test_authenticate_user_empty_user(self):
        """Test con campo user vacío"""
        with self.assertRaises(ValidationError) as context:
            self.auth_service.authenticate_user("", "password123")
        
        self.assertIn("El campo 'user' es obligatorio", str(context.exception))
    
    def test_authenticate_user_empty_password(self):
        """Test con campo password vacío"""
        with self.assertRaises(ValidationError) as context:
            self.auth_service.authenticate_user("test@example.com", "")
        
        self.assertIn("El campo 'password' es obligatorio", str(context.exception))
    
    def test_authenticate_user_invalid_email(self):
        """Test con formato de email inválido"""
        with self.assertRaises(ValidationError) as context:
            self.auth_service.authenticate_user("invalid-email", "password123")
        
        self.assertIn("El campo 'user' debe ser un email válido", str(context.exception))
    
    def test_logout_user_success(self):
        """Test de logout exitoso"""
        # Datos de prueba
        refresh_token = "valid_refresh_token"
        
        # Mock de respuesta exitosa de Keycloak
        keycloak_response = {"message": "Logout successful"}
        self.mock_keycloak_client.logout_user.return_value = keycloak_response
        
        # Ejecutar el método
        result = self.auth_service.logout_user(refresh_token)
        
        # Verificaciones
        self.assertEqual(result, keycloak_response)
        self.mock_keycloak_client.logout_user.assert_called_once_with(refresh_token)
    
    def test_logout_user_empty_token(self):
        """Test de logout con token vacío"""
        with self.assertRaises(ValidationError) as context:
            self.auth_service.logout_user("")
        
        self.assertIn("El refresh_token es requerido", str(context.exception))
        self.mock_keycloak_client.logout_user.assert_not_called()
    
    def test_logout_user_none_token(self):
        """Test de logout con token None"""
        with self.assertRaises(ValidationError) as context:
            self.auth_service.logout_user(None)
        
        self.assertIn("El refresh_token es requerido", str(context.exception))
        self.mock_keycloak_client.logout_user.assert_not_called()
    
    def test_logout_user_whitespace_token(self):
        """Test de logout con token solo espacios en blanco"""
        with self.assertRaises(ValidationError) as context:
            self.auth_service.logout_user("   ")
        
        self.assertIn("El refresh_token es requerido", str(context.exception))
        self.mock_keycloak_client.logout_user.assert_not_called()
    
    def test_logout_user_keycloak_error(self):
        """Test de logout con error de Keycloak"""
        refresh_token = "invalid_refresh_token"
        
        # Mock de error de Keycloak
        keycloak_error = {
            "error": "invalid_grant",
            "error_description": "Invalid refresh token"
        }
        self.mock_keycloak_client.logout_user.return_value = keycloak_error
        
        # Ejecutar el método y verificar excepción
        with self.assertRaises(BusinessLogicError) as context:
            self.auth_service.logout_user(refresh_token)
        
        self.assertEqual(context.exception.args[0], keycloak_error)
        self.mock_keycloak_client.logout_user.assert_called_once_with(refresh_token)
    
    def test_logout_user_keycloak_connection_error(self):
        """Test de logout con error de conexión a Keycloak"""
        refresh_token = "valid_refresh_token"
        
        # Mock de error de conexión
        self.mock_keycloak_client.logout_user.side_effect = BusinessLogicError("Error de conexión con Keycloak")
        
        # Ejecutar el método y verificar excepción
        with self.assertRaises(BusinessLogicError) as context:
            self.auth_service.logout_user(refresh_token)
        
        self.assertEqual(str(context.exception), "Error de conexión con Keycloak")
        self.mock_keycloak_client.logout_user.assert_called_once_with(refresh_token)


if __name__ == '__main__':
    unittest.main()

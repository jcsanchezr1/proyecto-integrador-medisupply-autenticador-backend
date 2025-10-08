"""
Tests para los modelos de autenticación
"""
import unittest
from app.models.auth_model import AuthCredentials, AuthResponse


class TestAuthCredentials(unittest.TestCase):
    """Tests para AuthCredentials"""
    
    def test_init_with_valid_data(self):
        """Test de inicialización con datos válidos"""
        credentials = AuthCredentials(user="test@example.com", password="password123")
        
        self.assertEqual(credentials.user, "test@example.com")
        self.assertEqual(credentials.password, "password123")
    
    def test_to_dict(self):
        """Test del método to_dict"""
        credentials = AuthCredentials(user="test@example.com", password="password123")
        result = credentials.to_dict()
        
        expected = {"user": "test@example.com"}
        self.assertEqual(result, expected)
        # Verificar que no incluye password por seguridad
        self.assertNotIn("password", result)
    
    def test_validate_success(self):
        """Test de validación exitosa"""
        credentials = AuthCredentials(user="test@example.com", password="password123")
        
        # No debería lanzar excepción
        credentials.validate()
    
    def test_validate_empty_user(self):
        """Test de validación con user vacío"""
        credentials = AuthCredentials(user="", password="password123")
        
        with self.assertRaises(ValueError) as context:
            credentials.validate()
        
        self.assertIn("El campo 'user' es obligatorio", str(context.exception))
    
    def test_validate_empty_password(self):
        """Test de validación con password vacío"""
        credentials = AuthCredentials(user="test@example.com", password="")
        
        with self.assertRaises(ValueError) as context:
            credentials.validate()
        
        self.assertIn("El campo 'password' es obligatorio", str(context.exception))
    
    def test_validate_invalid_email(self):
        """Test de validación con email inválido"""
        credentials = AuthCredentials(user="invalid-email", password="password123")
        
        with self.assertRaises(ValueError) as context:
            credentials.validate()
        
        self.assertIn("El campo 'user' debe ser un email válido", str(context.exception))
    
    def test_validate_user_too_long(self):
        """Test de validación con user muy largo"""
        long_email = "a" * 100 + "@example.com"
        credentials = AuthCredentials(user=long_email, password="password123")
        
        with self.assertRaises(ValueError) as context:
            credentials.validate()
        
        self.assertIn("El campo 'user' no puede exceder 100 caracteres", str(context.exception))
    
    def test_is_valid_email(self):
        """Test del método de validación de email"""
        credentials = AuthCredentials()
        
        # Emails válidos
        self.assertTrue(credentials._is_valid_email("test@example.com"))
        self.assertTrue(credentials._is_valid_email("user.name@domain.co.uk"))
        self.assertTrue(credentials._is_valid_email("user+tag@example.org"))
        
        # Emails inválidos
        self.assertFalse(credentials._is_valid_email("invalid-email"))
        self.assertFalse(credentials._is_valid_email("@example.com"))
        self.assertFalse(credentials._is_valid_email("test@"))
        self.assertFalse(credentials._is_valid_email(""))
    
    def test_repr(self):
        """Test del método __repr__"""
        credentials = AuthCredentials(user="test@example.com", password="password123")
        result = repr(credentials)
        
        self.assertIn("AuthCredentials", result)
        self.assertIn("test@example.com", result)


class TestAuthResponse(unittest.TestCase):
    """Tests para AuthResponse"""
    
    def test_init_with_valid_data(self):
        """Test de inicialización con datos válidos"""
        response_data = {
            "access_token": "AccessToken",
            "expires_in": 300,
            "refresh_expires_in": 1800,
            "refresh_token": "RefreshToken",
            "token_type": "Bearer",
            "not-before-policy": 0,
            "session_state": "2ea068ec-21b1-4ba7-ab64-44cc50d3080f",
            "scope": "email profile"
        }
        
        auth_response = AuthResponse(**response_data)
        
        self.assertEqual(auth_response.access_token, "AccessToken")
        self.assertEqual(auth_response.expires_in, 300)
        self.assertEqual(auth_response.token_type, "Bearer")
    
    def test_to_dict(self):
        """Test del método to_dict"""
        response_data = {
            "access_token": "AccessToken",
            "expires_in": 300,
            "refresh_expires_in": 1800,
            "refresh_token": "RefreshToken",
            "token_type": "Bearer",
            "not-before-policy": 0,
            "session_state": "2ea068ec-21b1-4ba7-ab64-44cc50d3080f",
            "scope": "email profile"
        }
        
        auth_response = AuthResponse(**response_data)
        result = auth_response.to_dict()
        
        self.assertEqual(result, response_data)
    
    def test_validate_success(self):
        """Test de validación exitosa"""
        response_data = {
            "access_token": "AccessToken",
            "expires_in": 300,
            "refresh_expires_in": 1800,
            "refresh_token": "RefreshToken",
            "token_type": "Bearer",
            "not-before-policy": 0,
            "session_state": "2ea068ec-21b1-4ba7-ab64-44cc50d3080f",
            "scope": "email profile"
        }
        
        auth_response = AuthResponse(**response_data)
        
        # No debería lanzar excepción
        auth_response.validate()
    
    def test_validate_missing_access_token(self):
        """Test de validación sin access_token"""
        response_data = {
            "expires_in": 300,
            "token_type": "Bearer"
        }
        
        auth_response = AuthResponse(**response_data)
        
        with self.assertRaises(ValueError) as context:
            auth_response.validate()
        
        self.assertIn("El campo 'access_token' es obligatorio", str(context.exception))
    
    def test_validate_missing_token_type(self):
        """Test de validación sin token_type"""
        response_data = {
            "access_token": "AccessToken",
            "expires_in": 300
        }
        
        auth_response = AuthResponse(**response_data)
        
        with self.assertRaises(ValueError) as context:
            auth_response.validate()
        
        self.assertIn("El campo 'token_type' es obligatorio", str(context.exception))
    
    def test_validate_invalid_expires_in(self):
        """Test de validación con expires_in inválido"""
        response_data = {
            "access_token": "AccessToken",
            "expires_in": 0,
            "token_type": "Bearer"
        }
        
        auth_response = AuthResponse(**response_data)
        
        with self.assertRaises(ValueError) as context:
            auth_response.validate()
        
        self.assertIn("El campo 'expires_in' debe ser mayor a 0", str(context.exception))
    
    def test_repr(self):
        """Test del método __repr__"""
        response_data = {
            "access_token": "AccessToken",
            "expires_in": 300,
            "token_type": "Bearer"
        }
        
        auth_response = AuthResponse(**response_data)
        result = repr(auth_response)
        
        self.assertIn("AuthResponse", result)
        self.assertIn("Bearer", result)
        self.assertIn("300", result)


if __name__ == '__main__':
    unittest.main()

"""
Pruebas unitarias para BaseController usando unittest
"""
import unittest
import sys
import os

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.controllers.base_controller import BaseController


class TestBaseController(unittest.TestCase):
    """Pruebas para BaseController"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.controller = BaseController()
    
    def test_handle_exception_returns_error_response(self):
        """Prueba que handle_exception retorna respuesta de error"""
        exception = Exception("Error de prueba")
        response, status_code = self.controller.handle_exception(exception)
        
        self.assertEqual(status_code, 500)
        self.assertIn("error", response)
        self.assertEqual(response["error"], "Error de prueba")
    
    def test_success_response_with_data(self):
        """Prueba que success_response retorna respuesta exitosa con datos"""
        data = {"id": "123", "name": "Test"}
        response, status_code = self.controller.success_response(data, "Success")
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], "Success")
        self.assertEqual(response["data"], data)
    
    def test_success_response_without_data(self):
        """Prueba que success_response retorna respuesta exitosa sin datos"""
        response, status_code = self.controller.success_response(message="Success")
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], "Success")
        self.assertNotIn("data", response)
    
    def test_success_response_with_custom_status_code(self):
        """Prueba que success_response retorna código de estado personalizado"""
        response, status_code = self.controller.success_response(
            data={"id": "123"}, 
            message="Created", 
            status_code=201
        )
        
        self.assertEqual(status_code, 201)
        self.assertEqual(response["message"], "Created")
        self.assertEqual(response["data"], {"id": "123"})
    
    def test_error_response_default_status_code(self):
        """Prueba que error_response retorna código 400 por defecto"""
        response, status_code = self.controller.error_response("Error message")
        
        self.assertEqual(status_code, 400)
        self.assertEqual(response["error"], "Error message")
    
    def test_error_response_custom_status_code(self):
        """Prueba que error_response retorna código de estado personalizado"""
        response, status_code = self.controller.error_response("Not found", 404)
        
        self.assertEqual(status_code, 404)
        self.assertEqual(response["error"], "Not found")


if __name__ == '__main__':
    unittest.main()

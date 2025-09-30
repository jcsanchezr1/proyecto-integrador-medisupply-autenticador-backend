"""
Pruebas de integración para el endpoint de health check
"""
import pytest


class TestHealthEndpoint:
    """Pruebas de integración para el endpoint /auth/ping"""
    
    def test_health_endpoint_returns_pong(self, client):
        """Prueba que el endpoint /auth/ping retorna 'pong'"""
        response = client.get('/auth/ping')
        
        assert response.status_code == 200
        # Flask-RESTful retorna JSON, así que verificamos el contenido JSON
        assert response.get_json() == "pong"
    
    def test_health_endpoint_returns_json(self, client):
        """Prueba que el endpoint retorna content-type application/json"""
        response = client.get('/auth/ping')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    def test_health_endpoint_handles_get_method(self, client):
        """Prueba que el endpoint maneja correctamente el método GET"""
        response = client.get('/auth/ping')
        
        assert response.status_code == 200
        # Verificar que la respuesta es exitosa
        assert response.get_json() == "pong"
    
    def test_health_endpoint_does_not_accept_post(self, client):
        """Prueba que el endpoint no acepta método POST"""
        response = client.post('/auth/ping')
        
        assert response.status_code == 405  # Method Not Allowed

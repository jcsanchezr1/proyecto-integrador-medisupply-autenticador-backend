"""
Pruebas unitarias para el controlador de health check
"""
import pytest
from app.controllers.health_controller import HealthCheckView


class TestHealthController:
    """Pruebas para HealthCheckView"""
    
    def test_health_check_returns_pong(self):
        """Prueba que el health check retorna 'pong'"""
        controller = HealthCheckView()
        result, status_code = controller.get()
        
        assert result == "pong"
        assert status_code == 200
    
    def test_health_check_is_get_method(self):
        """Prueba que el health check responde al método GET"""
        controller = HealthCheckView()
        
        # Verificar que tiene el método get
        assert hasattr(controller, 'get')
        assert callable(getattr(controller, 'get'))

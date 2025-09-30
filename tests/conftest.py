"""
Configuración de pytest para las pruebas
"""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Crea una instancia de la aplicación para testing"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Crea un cliente de prueba"""
    return app.test_client()

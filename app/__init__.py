"""
Aplicación principal del sistema de autenticación MediSupply
"""
import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS


def create_app():
    """Factory function para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Configurar CORS
    cors = CORS(app)
    
    # Configurar rutas
    configure_routes(app)
    
    return app


def configure_routes(app):
    """Configura las rutas de la aplicación"""
    from .controllers.health_controller import HealthCheckView
    from .controllers.user_controller import UserController, UserDeleteAllController, AdminUserController
    from .controllers.auth_controller import AuthController, LogoutController
    
    api = Api(app)
    
    # Health check endpoint
    api.add_resource(HealthCheckView, '/auth/ping')
    
    # Authentication endpoints
    api.add_resource(AuthController, '/auth/token')
    api.add_resource(LogoutController, '/auth/logout')
    
    # User endpoints
    api.add_resource(UserController, '/auth/user', '/auth/user/<string:user_id>')
    api.add_resource(UserDeleteAllController, '/auth/user/all')
    
    # Admin endpoints
    api.add_resource(AdminUserController, '/auth/admin/users')
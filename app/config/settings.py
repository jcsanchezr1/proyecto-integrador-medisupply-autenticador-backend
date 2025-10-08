"""
Configuración de la aplicación - Estructura para manejar configuraciones
"""
import os


class Config:
    """Configuración base de la aplicación"""
    
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8080'))
    
    # Configuración de la aplicación
    APP_NAME = 'MediSupply Authenticator Backend'
    APP_VERSION = '1.0.0'
    
    # Configuración de base de datos PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://medisupply_local_user:medisupply_local_password@medisupply-db:5432/medisupply_local_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Keycloak
    KC_BASE_URL = os.getenv('KC_BASE_URL', 'http://localhost:8080')
    KC_ADMIN_USER = os.getenv('KC_ADMIN_USER', 'admin')
    KC_ADMIN_PASS = os.getenv('KC_ADMIN_PASS', 'admin')
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB máximo para archivos
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    
    # Configuración de Google Cloud Storage
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'soluciones-cloud-2024-02')
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'medisupply-images-bucket')
    BUCKET_FOLDER = os.getenv('BUCKET_FOLDER', 'users')
    BUCKET_LOCATION = os.getenv('BUCKET_LOCATION', 'us-central1')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False


def get_config():
    """Retorna la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()
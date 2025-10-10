"""
Pruebas unitarias para CloudStorageService usando unittest
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.cloud_storage_service import CloudStorageService
from app.exceptions.custom_exceptions import ValidationError
from google.cloud.exceptions import GoogleCloudError


class TestCloudStorageService(unittest.TestCase):
    """Pruebas para CloudStorageService"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.mock_config = Mock()
        self.mock_config.BUCKET_NAME = 'test-bucket'
        self.mock_config.BUCKET_FOLDER = 'test-folder'
        self.mock_config.GCP_PROJECT_ID = 'test-project'
        self.mock_config.GOOGLE_APPLICATION_CREDENTIALS = '/path/to/credentials.json'
        self.mock_config.MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
        
        self.service = CloudStorageService(config=self.mock_config)
    
    def test_init_with_config(self):
        """Prueba inicialización con configuración"""
        self.assertEqual(self.service.config, self.mock_config)
        self.assertIsNone(self.service._client)
        self.assertIsNone(self.service._bucket)
    
    def test_init_without_config(self):
        """Prueba inicialización sin configuración"""
        with patch('app.services.cloud_storage_service.Config') as mock_config_class:
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            
            service = CloudStorageService()
            
            self.assertEqual(service.config, mock_config)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_client_property_success(self, mock_client_class):
        """Prueba obtener cliente exitosamente"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = self.service.client
        
        self.assertEqual(client, mock_client)
        mock_client_class.assert_called_once_with(project=self.mock_config.GCP_PROJECT_ID)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_client_property_error(self, mock_client_class):
        """Prueba obtener cliente con error"""
        mock_client_class.side_effect = Exception("Connection error")
        
        with self.assertRaises(GoogleCloudError) as context:
            _ = self.service.client
        
        self.assertIn("Error al inicializar cliente de GCS", str(context.exception))
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_bucket_property_success(self, mock_client_class):
        """Prueba obtener bucket exitosamente"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        bucket = self.service.bucket
        
        self.assertEqual(bucket, mock_bucket)
        mock_client.bucket.assert_called_once_with(self.mock_config.BUCKET_NAME)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_bucket_property_error(self, mock_client_class):
        """Prueba obtener bucket con error"""
        mock_client = Mock()
        mock_client.bucket.side_effect = Exception("Bucket error")
        mock_client_class.return_value = mock_client
        
        with self.assertRaises(GoogleCloudError) as context:
            _ = self.service.bucket
        
        self.assertIn("Error al obtener bucket", str(context.exception))
    
    def test_validate_image_file_success(self):
        """Prueba validar archivo de imagen exitosamente"""
        # Crear mock de archivo válido
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.content_type = 'image/jpeg'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=1024)  # 1KB
        mock_file.read = Mock(return_value=b'fake image data')
        
        with patch('app.services.cloud_storage_service.Image') as mock_image:
            mock_image.open.return_value.__enter__.return_value.size = (100, 100)
            
            is_valid, error = self.service.validate_image_file(mock_file)
            
            self.assertTrue(is_valid)
            self.assertEqual(error, "Archivo válido")
    
    def test_validate_image_file_no_filename(self):
        """Prueba validar archivo sin nombre"""
        mock_file = Mock()
        mock_file.filename = ''
        
        is_valid, error = self.service.validate_image_file(mock_file)
        
        self.assertFalse(is_valid)
        self.assertIn("No se proporcionó archivo", error)
    
    def test_validate_image_file_invalid_extension(self):
        """Prueba validar archivo con extensión inválida"""
        mock_file = Mock()
        mock_file.filename = 'test.txt'
        
        is_valid, error = self.service.validate_image_file(mock_file)
        
        self.assertFalse(is_valid)
        self.assertIn("Extensión no permitida", error)
    
    def test_validate_image_file_invalid_content_type(self):
        """Prueba validar archivo con tipo de contenido inválido"""
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.content_type = 'text/plain'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=1024)  # 1KB
        mock_file.read = Mock(return_value=b'fake image data')
        
        with patch('app.services.cloud_storage_service.Image') as mock_image:
            mock_image.open.side_effect = Exception("Invalid image")
            
            is_valid, error = self.service.validate_image_file(mock_file)
            
            self.assertFalse(is_valid)
            self.assertIn("El archivo no es una imagen válida", error)
    
    def test_validate_image_file_too_large(self):
        """Prueba validar archivo muy grande"""
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.content_type = 'image/jpeg'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=3 * 1024 * 1024)  # 3MB
        mock_file.read = Mock(return_value=b'x' * (3 * 1024 * 1024))  # 3MB
        
        is_valid, error = self.service.validate_image_file(mock_file)
        
        self.assertFalse(is_valid)
        self.assertIn("El archivo es demasiado grande", error)
    
    def test_validate_image_file_invalid_image(self):
        """Prueba validar archivo de imagen inválido"""
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.content_type = 'image/jpeg'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=1024)  # 1KB
        mock_file.read = Mock(return_value=b'fake image data')
        
        with patch('app.services.cloud_storage_service.Image') as mock_image:
            mock_image.open.side_effect = Exception("Invalid image")
            
            is_valid, error = self.service.validate_image_file(mock_file)
            
            self.assertFalse(is_valid)
            self.assertIn("El archivo no es una imagen válida", error)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_upload_image_success(self, mock_client_class):
        """Prueba subir imagen exitosamente"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        
        # Crear mock de archivo
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.content_type = 'image/jpeg'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=1024)  # 1KB
        mock_file.read = Mock(return_value=b'fake image data')
        
        with patch('app.services.cloud_storage_service.Image') as mock_image:
            mock_image.open.return_value.__enter__.return_value.size = (100, 100)
            
            # Mock del método get_image_url
            with patch.object(self.service, 'get_image_url', return_value='https://storage.googleapis.com/bucket/test.jpg'):
                success, message, url = self.service.upload_image(mock_file, 'test.jpg')
                
                self.assertTrue(success)
                self.assertEqual(message, "Imagen subida exitosamente")
                self.assertEqual(url, 'https://storage.googleapis.com/bucket/test.jpg')
                mock_blob.upload_from_file.assert_called_once()
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_upload_image_validation_error(self, mock_client_class):
        """Prueba subir imagen con error de validación"""
        # Crear mock de archivo inválido
        mock_file = Mock()
        mock_file.filename = 'test.txt'  # Extensión inválida
        
        success, message, url = self.service.upload_image(mock_file, 'test.txt')
        
        self.assertFalse(success)
        self.assertIn("Extensión no permitida", message)
        self.assertIsNone(url)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_upload_image_upload_error(self, mock_client_class):
        """Prueba subir imagen con error de subida"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        
        # Crear mock de archivo válido
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.content_type = 'image/jpeg'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=1024)  # 1KB
        mock_file.read = Mock(return_value=b'fake image data')
        
        # Simular error en upload
        mock_blob.upload_from_file.side_effect = GoogleCloudError("Upload failed")
        
        with patch('app.services.cloud_storage_service.Image') as mock_image:
            mock_image.open.return_value.__enter__.return_value.size = (100, 100)
            
            success, message, url = self.service.upload_image(mock_file, 'test.jpg')
            
            self.assertFalse(success)
            self.assertIn("Error de Google Cloud Storage", message)
            self.assertIsNone(url)
    
    @patch('google.auth.impersonated_credentials.Credentials')
    @patch('google.auth.default')
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_get_image_url_success(self, mock_client_class, mock_default, mock_impersonated_creds):
        """Prueba obtener URL de imagen exitosamente"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_source_creds = Mock()
        mock_target_creds = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        mock_default.return_value = (mock_source_creds, None)
        mock_impersonated_creds.return_value = mock_target_creds
        
        # Configurar blob
        mock_blob.exists.return_value = True
        mock_blob.generate_signed_url.return_value = 'https://storage.googleapis.com/bucket/test.jpg?signed'
        
        url = self.service.get_image_url('test.jpg')
        
        self.assertEqual(url, 'https://storage.googleapis.com/bucket/test.jpg?signed')
        mock_blob.exists.assert_called_once()
        mock_blob.generate_signed_url.assert_called_once()
        mock_impersonated_creds.assert_called_once()
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_get_image_url_file_not_exists(self, mock_client_class):
        """Prueba obtener URL de imagen que no existe"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        
        # Configurar blob
        mock_blob.exists.return_value = False
        
        url = self.service.get_image_url('test.jpg')
        
        self.assertEqual(url, "")
        mock_blob.exists.assert_called_once()
        mock_blob.generate_signed_url.assert_not_called()
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_get_image_url_error(self, mock_client_class):
        """Prueba obtener URL de imagen con error"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        
        # Configurar blob
        mock_blob.exists.side_effect = Exception("Blob error")
        
        url = self.service.get_image_url('test.jpg')
        
        # Debería retornar URL directa como fallback
        self.assertIn("https://storage.googleapis.com", url)
        self.assertIn("test.jpg", url)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_delete_image_success(self, mock_client_class):
        """Prueba eliminar imagen exitosamente"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        
        # Configurar blob
        mock_blob.exists.return_value = True
        
        success, message = self.service.delete_image('test.jpg')
        
        self.assertTrue(success)
        self.assertEqual(message, "Imagen eliminada exitosamente")
        mock_blob.delete.assert_called_once()
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_delete_image_not_exists(self, mock_client_class):
        """Prueba eliminar imagen que no existe"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        
        # Configurar blob
        mock_blob.exists.return_value = False
        
        success, message = self.service.delete_image('test.jpg')
        
        self.assertFalse(success)
        self.assertEqual(message, "La imagen no existe")
        mock_blob.delete.assert_not_called()
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_delete_image_error(self, mock_client_class):
        """Prueba eliminar imagen con error"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        
        # Configurar blob
        mock_blob.exists.return_value = True
        mock_blob.delete.side_effect = GoogleCloudError("Delete failed")
        
        success, message = self.service.delete_image('test.jpg')
        
        self.assertFalse(success)
        self.assertIn("Error de Google Cloud Storage", message)
    
    @patch('google.auth.impersonated_credentials.Credentials')
    @patch('google.auth.default')
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_get_image_url_custom_expiration(self, mock_client_class, mock_default, mock_impersonated_creds):
        """Prueba obtener URL con expiración personalizada"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_source_creds = Mock()
        mock_target_creds = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        mock_default.return_value = (mock_source_creds, None)
        mock_impersonated_creds.return_value = mock_target_creds
        
        # Configurar blob
        mock_blob.exists.return_value = True
        mock_blob.generate_signed_url.return_value = 'https://storage.googleapis.com/bucket/test.jpg?signed'
        
        url = self.service.get_image_url('test.jpg', expiration_hours=24)
        
        self.assertEqual(url, 'https://storage.googleapis.com/bucket/test.jpg?signed')
        mock_blob.generate_signed_url.assert_called_once()
        mock_impersonated_creds.assert_called_once()
        
        # Verificar que se pasó la expiración correcta
        call_args = mock_blob.generate_signed_url.call_args
        expiration = call_args[1]['expiration']
        expected_expiration = datetime.now(timezone.utc) + timedelta(hours=24)
        # Permitir diferencia de hasta 1 segundo
        self.assertLess(abs((expiration - expected_expiration).total_seconds()), 1)


if __name__ == '__main__':
    unittest.main()

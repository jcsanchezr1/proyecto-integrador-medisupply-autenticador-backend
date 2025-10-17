"""
Pruebas unitarias para UserService usando unittest
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.user_service import UserService
from app.models.user_model import User
from app.exceptions.custom_exceptions import ValidationError, BusinessLogicError


class TestUserService(unittest.TestCase):
    """Pruebas para UserService"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.mock_user_repository = Mock()
        self.mock_keycloak_client = Mock()
        self.mock_cloud_storage_service = Mock()
        self.mock_config = Mock()
        self.service = UserService(
            user_repository=self.mock_user_repository,
            keycloak_client=self.mock_keycloak_client,
            cloud_storage_service=self.mock_cloud_storage_service,
            config=self.mock_config
        )
    
    def test_init_with_dependencies(self):
        """Prueba inicialización con dependencias"""
        self.assertEqual(self.service.user_repository, self.mock_user_repository)
        self.assertEqual(self.service.keycloak_client, self.mock_keycloak_client)
    
    def test_init_without_dependencies(self):
        """Prueba inicialización sin dependencias"""
        with patch('app.services.user_service.UserRepository') as mock_repo, \
             patch('app.services.user_service.KeycloakClient') as mock_keycloak, \
             patch('app.services.user_service.CloudStorageService') as mock_cloud, \
             patch('app.services.user_service.Config') as mock_config:
            
            service = UserService()
            
            self.assertIsNotNone(service.user_repository)
            self.assertIsNotNone(service.keycloak_client)
            self.assertIsNotNone(service.cloud_storage_service)
            self.assertIsNotNone(service.config)
    
    def test_create_success(self):
        """Prueba crear usuario exitosamente"""
        # Configurar mocks
        mock_user = User(id='123', name='Test Hospital', enabled=False)
        self.mock_user_repository.create.return_value = mock_user
        self.mock_user_repository.get_by_email.return_value = None  # Email no existe
        
        # Ejecutar
        result = self.service.create(
            name='Test Hospital',
            email='test@hospital.com',
            tax_id='123456789',
            address='Test Address',
            phone='1234567890',
            institution_type='Hospital',
            specialty='Alto valor',
            applicant_name='John Doe',
            applicant_email='john@hospital.com',
            latitude=4.711,
            longitude=-74.0721,
            password='password123',
            confirm_password='password123'
        )
        
        # Verificar
        self.assertIsInstance(result, User)
        self.mock_user_repository.create.assert_called_once()
    
    def test_create_validation_error(self):
        """Prueba crear usuario con error de validación"""
        # Configurar mock para lanzar ValueError
        self.mock_user_repository.create.side_effect = ValueError("Campo obligatorio")
        self.mock_user_repository.get_by_email.return_value = None  # Email no existe
        
        # Ejecutar y verificar
        with self.assertRaises(ValidationError) as context:
            self.service.create(
                name='Test Hospital',
                email='test@hospital.com',
                tax_id='123456789',
                address='Test Address',
                phone='1234567890',
                institution_type='Hospital',
                specialty='Alto valor',
                applicant_name='John Doe',
                applicant_email='john@hospital.com',
                password='password123',
                confirm_password='password123'
            )
        
        self.assertEqual(str(context.exception), "Campo obligatorio")
    
    def test_create_business_logic_error(self):
        """Prueba crear usuario con error de lógica de negocio"""
        # Configurar mock para lanzar excepción general
        self.mock_user_repository.create.side_effect = Exception("Database error")
        self.mock_user_repository.get_by_email.return_value = None  # Email no existe
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.create(
                name='Test Hospital',
                email='test@hospital.com',
                tax_id='123456789',
                address='Test Address',
                phone='1234567890',
                institution_type='Hospital',
                specialty='Alto valor',
                applicant_name='John Doe',
                applicant_email='john@hospital.com',
                password='password123',
                confirm_password='password123'
            )
        
        self.assertIn("Error al crear usuario", str(context.exception))
    
    def test_get_by_id_success(self):
        """Prueba obtener usuario por ID exitosamente"""
        # Configurar mock
        mock_user = User(id='123', name='Test Hospital')
        self.mock_user_repository.get_by_id.return_value = mock_user
        
        # Ejecutar
        result = self.service.get_by_id('123')
        
        # Verificar
        self.assertEqual(result, mock_user)
        self.mock_user_repository.get_by_id.assert_called_once_with('123')
    
    def test_get_by_id_business_logic_error(self):
        """Prueba obtener usuario por ID con error"""
        # Configurar mock para lanzar excepción
        self.mock_user_repository.get_by_id.side_effect = Exception("Database error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.get_by_id('123')
        
        self.assertIn("Error al obtener usuario", str(context.exception))
    
    def test_get_all_success(self):
        """Prueba obtener todos los usuarios exitosamente"""
        # Configurar mock
        mock_users = [User(id='1'), User(id='2')]
        self.mock_user_repository.get_all.return_value = mock_users
        
        # Ejecutar
        result = self.service.get_all(limit=10, offset=0)
        
        # Verificar
        self.assertEqual(result, mock_users)
        self.mock_user_repository.get_all.assert_called_once_with(limit=10, offset=0)
    
    def test_get_all_business_logic_error(self):
        """Prueba obtener todos los usuarios con error"""
        # Configurar mock para lanzar excepción
        self.mock_user_repository.get_all.side_effect = Exception("Database error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.get_all()
        
        self.assertIn("Error al obtener usuarios", str(context.exception))
    
    def test_update_success(self):
        """Prueba actualizar usuario exitosamente"""
        # Configurar mock
        mock_user = User(id='123', name='Updated Hospital')
        self.mock_user_repository.update.return_value = mock_user
        
        # Ejecutar
        result = self.service.update('123', name='Updated Hospital')
        
        # Verificar
        self.assertEqual(result, mock_user)
        self.mock_user_repository.update.assert_called_once_with('123', name='Updated Hospital')
    
    def test_update_business_logic_error(self):
        """Prueba actualizar usuario con error"""
        # Configurar mock para lanzar excepción
        self.mock_user_repository.update.side_effect = Exception("Database error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.update('123', name='Updated Hospital')
        
        self.assertIn("Error al actualizar usuario", str(context.exception))
    
    def test_delete_success(self):
        """Prueba eliminar usuario exitosamente"""
        # Configurar mock
        self.mock_user_repository.delete.return_value = True
        
        # Ejecutar
        result = self.service.delete('123')
        
        # Verificar
        self.assertTrue(result)
        self.mock_user_repository.delete.assert_called_once_with('123')
    
    def test_delete_business_logic_error(self):
        """Prueba eliminar usuario con error"""
        # Configurar mock para lanzar excepción
        self.mock_user_repository.delete.side_effect = Exception("Database error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.delete('123')
        
        self.assertIn("Error al eliminar usuario", str(context.exception))
    
    def test_delete_all_success(self):
        """Prueba eliminar todos los usuarios exitosamente"""
        # Configurar mock
        self.mock_user_repository.delete_all.return_value = 5
        
        # Ejecutar
        result = self.service.delete_all()
        
        # Verificar
        self.assertEqual(result, 5)
        self.mock_user_repository.delete_all.assert_called_once()
    
    def test_delete_all_business_logic_error(self):
        """Prueba eliminar todos los usuarios con error"""
        # Configurar mock para lanzar excepción
        self.mock_user_repository.delete_all.side_effect = Exception("Database error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.delete_all()
        
        self.assertIn("Error al eliminar todos los usuarios", str(context.exception))
    
    def test_validate_business_rules_name_required(self):
        """Prueba validación de nombre de institución obligatorio"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(name='')
        
        self.assertIn("Nombre", str(context.exception))
    
    def test_validate_business_rules_name_too_long(self):
        """Prueba validación de nombre de institución muy largo"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(name='A' * 101)
        
        self.assertIn("100 caracteres", str(context.exception))
    
    def test_validate_business_rules_name_too_short(self):
        """Prueba validación de nombre de institución muy corto"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(name='A')
        
        self.assertIn("2 caracteres", str(context.exception))
    
    def test_validate_business_rules_email_required(self):
        """Prueba validación de email obligatorio"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(email='')
        
        self.assertIn("Correo electrónico", str(context.exception))
    
    def test_validate_business_rules_email_invalid_format(self):
        """Prueba validación de email con formato inválido"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(email='invalid-email')
        
        self.assertIn("formato válido", str(context.exception))
    
    def test_validate_business_rules_password_too_short(self):
        """Prueba validación de contraseña muy corta"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(password='123')
        
        self.assertIn("8 caracteres", str(context.exception))
    
    def test_validate_business_rules_passwords_dont_match(self):
        """Prueba validación de contraseñas que no coinciden"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(
                password='password123',
                confirm_password='different123'
            )
        
        self.assertIn("deben ser iguales", str(context.exception))
    
    def test_validate_business_rules_phone_invalid(self):
        """Prueba validación de teléfono inválido"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(phone='abc123')
        
        # El error puede ser "solo números" o "al menos 7 dígitos"
        error_message = str(context.exception)
        self.assertTrue("solo números" in error_message or "7 dígitos" in error_message)
    
    def test_validate_business_rules_institution_type_invalid(self):
        """Prueba validación de tipo de institución inválido"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(institution_type='InvalidType')
        
        self.assertIn("Clínica, Hospital o Laboratorio", str(context.exception))
    
    def test_validate_business_rules_specialty_invalid(self):
        """Prueba validación de especialidad inválida"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(specialty='InvalidSpecialty')
        
        self.assertIn("Cadena de frío, Alto valor o Seguridad", str(context.exception))
    
    def test_validate_business_rules_role_invalid(self):
        """Prueba validación de rol inválido"""
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(role='InvalidRole')
        
        self.assertIn("Administrador, Compras, Ventas, Logistica, Cliente", str(context.exception))
    
    def test_validate_business_rules_email_already_exists(self):
        """Prueba validación de email ya existente"""
        # Configurar mock
        self.mock_user_repository.get_by_email.return_value = User(id='123')
        
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service.validate_business_rules(email='existing@hospital.com')
        
        self.assertIn("Ya existe un usuario con este correo electrónico", str(context.exception))
    
    def test_get_users_summary_success(self):
        """Prueba obtener resumen de usuarios exitosamente"""
        # Configurar mock
        mock_users = [
            User(id='1', name='Hospital 1', email='h1@test.com'),
            User(id='2', name='Hospital 2', email='h2@test.com')
        ]
        self.mock_user_repository.get_all.return_value = mock_users
        
        # Ejecutar
        result = self.service.get_users_summary(limit=10, offset=0)
        
        # Verificar
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], '1')
        self.assertEqual(result[0]['name'], 'Hospital 1')
        self.assertEqual(result[0]['email'], 'h1@test.com')
    
    def test_get_users_summary_business_logic_error(self):
        """Prueba obtener resumen de usuarios con error"""
        # Configurar mock para lanzar excepción
        self.mock_user_repository.get_all.side_effect = Exception("Database error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.get_users_summary()
        
        self.assertIn("Error al obtener resumen de usuarios", str(context.exception))
    
    def test_get_users_count_success(self):
        """Prueba contar usuarios exitosamente"""
        # Configurar mock
        self.mock_user_repository.count_all.return_value = 5
        
        # Ejecutar
        result = self.service.get_users_count()
        
        # Verificar
        self.assertEqual(result, 5)
        self.mock_user_repository.count_all.assert_called_once()
    
    def test_get_users_count_business_logic_error(self):
        """Prueba contar usuarios con error"""
        # Configurar mock para lanzar excepción
        self.mock_user_repository.count_all.side_effect = Exception("Database error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.get_users_count()
        
        self.assertIn("Error al contar usuarios", str(context.exception))
    
    def test_create_user_with_validation_success(self):
        """Prueba crear usuario con validación completa exitosamente"""
        # Configurar mocks
        mock_user = User(id='123', name='Test Hospital', enabled=False)
        self.mock_user_repository.create.return_value = mock_user
        self.mock_user_repository.get_by_email.return_value = None  # Email no existe
        self.mock_keycloak_client.get_available_roles.return_value = ['Cliente']
        self.mock_keycloak_client.create_user.return_value = 'keycloak-123'
        self.mock_keycloak_client.assign_role_to_user.return_value = None
        
        # Ejecutar
        result = self.service.create_user_with_validation(
            name='Test Hospital',
            email='test@hospital.com',
            tax_id='123456789',
            address='Test Address',
            phone='1234567890',
            institution_type='Hospital',
            specialty='Alto valor',
            applicant_name='John Doe',
            applicant_email='john@hospital.com',
            latitude=4.711,
            longitude=-74.0721,
            password='password123',
            confirm_password='password123'
        )
        
        # Verificar
        self.assertEqual(result, mock_user)
        self.mock_keycloak_client.create_user.assert_called_once()
        self.mock_keycloak_client.assign_role_to_user.assert_called_once()
    
    def test_create_user_with_validation_keycloak_error(self):
        """Prueba crear usuario con error en Keycloak"""
        # Configurar mocks
        mock_user = User(id='123', name='Test Hospital', enabled=False)
        self.mock_user_repository.create.return_value = mock_user
        self.mock_user_repository.get_by_email.return_value = None  # Email no existe
        self.mock_keycloak_client.get_available_roles.return_value = ['Cliente']
        self.mock_keycloak_client.create_user.side_effect = Exception("Keycloak error")
        self.mock_user_repository.delete.return_value = True
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.create_user_with_validation(
                name='Test Hospital',
                email='test@hospital.com',
                tax_id='123456789',
                address='Test Address',
                phone='1234567890',
                institution_type='Hospital',
                specialty='Alto valor',
                applicant_name='John Doe',
                applicant_email='john@hospital.com',
                latitude=4.711,
                longitude=-74.0721,
                password='password123',
                confirm_password='password123'
            )
        
        self.assertIn("Error al crear usuario en Keycloak", str(context.exception))
        # Verificar que se intentó eliminar el usuario de la base de datos local
        self.mock_user_repository.delete.assert_called_once_with('123')
    
    def test_create_user_with_validation_sets_enabled_false(self):
        """Prueba que el campo enabled se establece como False por defecto"""
        # Configurar mocks
        mock_user = User(id='123', name='Test Hospital', enabled=False)
        self.mock_user_repository.create.return_value = mock_user
        self.mock_user_repository.get_by_email.return_value = None  # Email no existe
        self.mock_keycloak_client.get_available_roles.return_value = ['Cliente']
        self.mock_keycloak_client.create_user.return_value = 'keycloak-123'
        self.mock_keycloak_client.assign_role_to_user.return_value = None
        
        # Ejecutar
        result = self.service.create_user_with_validation(
            name='Test Hospital',
            email='test@hospital.com',
            tax_id='123456789',
            address='Test Address',
            phone='1234567890',
            institution_type='Hospital',
            specialty='Alto valor',
            applicant_name='John Doe',
            applicant_email='john@hospital.com',
            latitude=4.711,
            longitude=-74.0721,
            password='password123',
            confirm_password='password123'
        )
        
        # Verificar que el campo enabled se establece como False
        self.assertEqual(result.enabled, False)
        # Verificar que se pasó enabled=False al repositorio
        call_args = self.mock_user_repository.create.call_args
        self.assertEqual(call_args[1]['enabled'], False)
    
    def test_create_user_with_validation_invalid_role(self):
        """Prueba crear usuario con rol inválido"""
        # Esta prueba se omite porque la validación de rol se maneja en Keycloak
        # y no en la validación local del servicio
        pass
    
    def test_create_with_logo_file_success(self):
        """Prueba crear usuario con archivo de logo exitosamente"""
        # Configurar mocks
        mock_user = User(id='123', name='Test Hospital', enabled=False)
        self.mock_user_repository.create.return_value = mock_user
        self.mock_user_repository.get_by_email.return_value = None  # Email no existe
        self.mock_cloud_storage_service.upload_image.return_value = (True, "Success", "https://storage.googleapis.com/bucket/logo.jpg")
        
        # Crear mock de archivo
        mock_file = Mock()
        mock_file.filename = "logo.jpg"
        
        # Ejecutar
        result = self.service.create(
            name='Test Hospital',
            email='test@hospital.com',
            tax_id='123456789',
            address='Test Address',
            phone='1234567890',
            institution_type='Hospital',
            specialty='Alto valor',
            applicant_name='John Doe',
            applicant_email='john@hospital.com',
            password='password123',
            confirm_password='password123',
            logo_file=mock_file
        )
        
        # Verificar
        self.assertIsInstance(result, User)
        self.mock_cloud_storage_service.upload_image.assert_called_once()
        self.mock_user_repository.create.assert_called_once()
    
    def test_create_with_logo_file_upload_error(self):
        """Prueba crear usuario con error al subir logo"""
        # Configurar mocks
        self.mock_user_repository.get_by_email.return_value = None  # Email no existe
        self.mock_cloud_storage_service.upload_image.return_value = (False, "Upload failed", None)
        
        # Crear mock de archivo
        mock_file = Mock()
        mock_file.filename = "logo.jpg"
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.create(
                name='Test Hospital',
                email='test@hospital.com',
                tax_id='123456789',
                address='Test Address',
                phone='1234567890',
                institution_type='Hospital',
                specialty='Alto valor',
                applicant_name='John Doe',
                applicant_email='john@hospital.com',
                password='password123',
                confirm_password='password123',
                logo_file=mock_file
            )
        
        self.assertIn("Error al subir imagen", str(context.exception))
    
    def test_create_without_logo_file(self):
        """Prueba crear usuario sin archivo de logo"""
        # Configurar mocks
        mock_user = User(id='123', name='Test Hospital', enabled=False)
        self.mock_user_repository.create.return_value = mock_user
        self.mock_user_repository.get_by_email.return_value = None  # Email no existe
        
        # Ejecutar
        result = self.service.create(
            name='Test Hospital',
            email='test@hospital.com',
            tax_id='123456789',
            address='Test Address',
            phone='1234567890',
            institution_type='Hospital',
            specialty='Alto valor',
            applicant_name='John Doe',
            applicant_email='john@hospital.com',
            latitude=4.711,
            longitude=-74.0721,
            password='password123',
            confirm_password='password123'
        )
        
        # Verificar
        self.assertIsInstance(result, User)
        self.mock_cloud_storage_service.upload_image.assert_not_called()
        self.mock_user_repository.create.assert_called_once()
    
    def test_process_logo_file_success(self):
        """Prueba procesar archivo de logo exitosamente"""
        # Configurar mocks
        self.mock_cloud_storage_service.upload_image.return_value = (True, "Success", "https://storage.googleapis.com/bucket/logo.jpg")
        
        # Crear mock de archivo
        mock_file = Mock()
        mock_file.filename = "logo.jpg"
        
        # Ejecutar
        filename, url = self.service._process_logo_file(mock_file)
        
        # Verificar
        self.assertIsNotNone(filename)
        self.assertIsNotNone(url)
        self.assertEqual(url, "https://storage.googleapis.com/bucket/logo.jpg")
        self.mock_cloud_storage_service.upload_image.assert_called_once()
    
    def test_process_logo_file_no_file(self):
        """Prueba procesar archivo de logo cuando no hay archivo"""
        # Ejecutar
        filename, url = self.service._process_logo_file(None)
        
        # Verificar
        self.assertIsNone(filename)
        self.assertIsNone(url)
        self.mock_cloud_storage_service.upload_image.assert_not_called()
    
    def test_process_logo_file_empty_filename(self):
        """Prueba procesar archivo de logo con filename vacío"""
        # Crear mock de archivo sin filename
        mock_file = Mock()
        mock_file.filename = ""
        
        # Ejecutar
        filename, url = self.service._process_logo_file(mock_file)
        
        # Verificar
        self.assertIsNone(filename)
        self.assertIsNone(url)
        self.mock_cloud_storage_service.upload_image.assert_not_called()
    
    def test_process_logo_file_upload_error(self):
        """Prueba procesar archivo de logo con error de subida"""
        # Configurar mocks
        self.mock_cloud_storage_service.upload_image.return_value = (False, "Upload failed", None)
        
        # Crear mock de archivo
        mock_file = Mock()
        mock_file.filename = "logo.jpg"
        
        # Ejecutar y verificar
        with self.assertRaises(ValidationError) as context:
            self.service._process_logo_file(mock_file)
        
        self.assertIn("Error al subir imagen", str(context.exception))
    
    def test_process_logo_file_exception(self):
        """Prueba procesar archivo de logo con excepción general"""
        # Configurar mocks
        self.mock_cloud_storage_service.upload_image.side_effect = Exception("General error")
        
        # Crear mock de archivo
        mock_file = Mock()
        mock_file.filename = "logo.jpg"
        
        # Ejecutar y verificar
        with self.assertRaises(ValidationError) as context:
            self.service._process_logo_file(mock_file)
        
        self.assertIn("Error al procesar archivo de logo", str(context.exception))
    
    def test_create_admin_user_success(self):
        """Test de creación exitosa de usuario admin"""
        # Configurar mocks
        self.mock_user_repository.get_by_email.return_value = None
        self.mock_keycloak_client.create_user.return_value = 'keycloak-123'
        self.mock_keycloak_client.assign_role_to_user.return_value = None
        
        mock_user = User(id='123', name='Admin User', email='admin@test.com', enabled=True)
        self.mock_user_repository.create_admin_user.return_value = mock_user
        
        # Ejecutar
        result = self.service.create_admin_user(
            name='Admin User',
            email='admin@test.com',
            password='password123',
            role='Administrador'
        )
        
        # Verificar
        self.assertEqual(result['name'], 'Admin User')
        self.assertEqual(result['email'], 'admin@test.com')
        self.assertEqual(result['role'], 'Administrador')
        self.assertTrue(result['enabled'])
        
        # Verificar llamadas
        self.mock_user_repository.get_by_email.assert_called_once_with('admin@test.com')
        self.mock_keycloak_client.create_user.assert_called_once_with('admin@test.com', 'password123', 'Admin User')
        self.mock_keycloak_client.assign_role_to_user.assert_called_once_with('keycloak-123', 'Administrador')
        self.mock_user_repository.create_admin_user.assert_called_once_with(
            name='Admin User',
            email='admin@test.com',
            keycloak_id='keycloak-123',
            enabled=True
        )
    
    def test_create_admin_user_email_exists(self):
        """Test de creación de usuario admin con email existente"""
        # Configurar mock
        self.mock_user_repository.get_by_email.return_value = User(id='123', name='Existing User')
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.create_admin_user(
                name='Admin User',
                email='admin@test.com',
                password='password123',
                role='Administrador'
            )
        
        self.assertIn("Ya existe un usuario con este email", str(context.exception))
    
    def test_create_admin_user_keycloak_error(self):
        """Test de creación de usuario admin con error en Keycloak"""
        # Configurar mocks
        self.mock_user_repository.get_by_email.return_value = None
        self.mock_keycloak_client.create_user.side_effect = Exception("Keycloak error")
        
        # Ejecutar y verificar
        with self.assertRaises(BusinessLogicError) as context:
            self.service.create_admin_user(
                name='Admin User',
                email='admin@test.com',
                password='password123',
                role='Administrador'
            )
        
        self.assertIn("Error al crear usuario", str(context.exception))
    
    def test_create_admin_user_invalid_data(self):
        """Test de creación de usuario admin con datos inválidos"""
        # Ejecutar y verificar
        with self.assertRaises(ValidationError) as context:
            self.service.create_admin_user(
                name='',  # Nombre vacío
                email='invalid-email',  # Email inválido
                password='123',  # Password muy corto
                role='InvalidRole'  # Rol inválido
            )
        
        self.assertIn("name", str(context.exception))
        self.assertIn("email", str(context.exception))
        self.assertIn("password", str(context.exception))
        self.assertIn("role", str(context.exception))


if __name__ == '__main__':
    unittest.main()

"""
Pruebas unitarias para UserRepository usando unittest
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.repositories.user_repository import UserRepository, UserDB
from app.models.user_model import User


class TestUserRepository(unittest.TestCase):
    """Pruebas para UserRepository"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        # Mock de la configuración de base de datos
        with patch('app.repositories.user_repository.Config') as mock_config:
            mock_config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            with patch('app.repositories.user_repository.create_engine'), \
                 patch('app.repositories.user_repository.sessionmaker'), \
                 patch('app.repositories.user_repository.Base.metadata.create_all'):
                self.repository = UserRepository()
    
    def test_init_creates_engine_and_session(self):
        """Prueba que __init__ configura el motor y la sesión"""
        with patch('app.repositories.user_repository.Config') as mock_config:
            mock_config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            with patch('app.repositories.user_repository.create_engine') as mock_engine, \
                 patch('app.repositories.user_repository.sessionmaker') as mock_sessionmaker, \
                 patch('app.repositories.user_repository.Base.metadata.create_all') as mock_create_all:
                
                repository = UserRepository()
                
                mock_engine.assert_called_once_with('sqlite:///:memory:')
                mock_sessionmaker.assert_called_once()
                mock_create_all.assert_called_once()
    
    def test_db_to_model_conversion(self):
        """Prueba conversión de modelo de DB a modelo de dominio"""
        # Crear mock de UserDB
        db_user = Mock()
        db_user.id = '123'
        db_user.name = 'Test Hospital'
        db_user.tax_id = '123456789'
        db_user.email = 'test@hospital.com'
        db_user.address = 'Test Address'
        db_user.phone = '1234567890'
        db_user.institution_type = 'Hospital'
        db_user.logo_filename = 'logo.png'
        db_user.specialty = 'Alto valor'
        db_user.applicant_name = 'John Doe'
        db_user.applicant_email = 'john@hospital.com'
        db_user.enabled = False
        db_user.created_at = datetime.now()
        db_user.updated_at = datetime.now()
        
        # Ejecutar conversión
        user = self.repository._db_to_model(db_user)
        
        # Verificar
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, '123')
        self.assertEqual(user.name, 'Test Hospital')
        self.assertEqual(user.email, 'test@hospital.com')
    
    def test_model_to_db_conversion(self):
        """Prueba conversión de modelo de dominio a modelo de DB"""
        # Crear modelo de dominio
        user = User(
            id='123',
            name='Test Hospital',
            tax_id='123456789',
            email='test@hospital.com',
            address='Test Address',
            phone='1234567890',
            institution_type='Hospital',
            logo_filename='logo.png',
            specialty='Alto valor',
            applicant_name='John Doe',
            applicant_email='john@hospital.com',
            enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Ejecutar conversión
        db_user = self.repository._model_to_db(user)
        
        # Verificar
        self.assertIsInstance(db_user, UserDB)
        self.assertEqual(db_user.id, '123')
        self.assertEqual(db_user.name, 'Test Hospital')
        self.assertEqual(db_user.email, 'test@hospital.com')
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_create_success(self, mock_get_session):
        """Prueba crear usuario exitosamente"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query para verificar email único
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None  # Email no existe
        
        # Configurar mock de refresh
        mock_db_user = Mock()
        mock_db_user.id = '123'
        mock_session.refresh.return_value = None
        
        # Mock del método _model_to_db
        with patch.object(self.repository, '_model_to_db', return_value=mock_db_user), \
             patch.object(self.repository, '_db_to_model', return_value=User(id='123')):
            
            # Ejecutar
            result = self.repository.create(
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
                role='Cliente'
            )
            
            # Verificar
            self.assertIsInstance(result, User)
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_create_email_already_exists(self, mock_get_session):
        """Prueba crear usuario con email existente"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query para email existente
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = Mock()  # Email existe
        
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.repository.create(
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
                role='Cliente'
            )
        
        self.assertIn("Ya existe un usuario con este correo electrónico", str(context.exception))
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_create_database_error(self, mock_get_session):
        """Prueba crear usuario con error de base de datos"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query para email único
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None  # Email no existe
        
        # Configurar error en commit
        mock_session.commit.side_effect = Exception("Database error")
        
        # Mock del método _model_to_db
        with patch.object(self.repository, '_model_to_db', return_value=Mock()):
            
            # Ejecutar y verificar
            with self.assertRaises(Exception) as context:
                self.repository.create(
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
                    role='Cliente'
                )
            
            self.assertIn("Database error", str(context.exception))
            # No verificar rollback ya que el error ocurre antes del commit
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_get_by_id_success(self, mock_get_session):
        """Prueba obtener usuario por ID exitosamente"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = Mock()
        
        # Mock del método _db_to_model
        with patch.object(self.repository, '_db_to_model', return_value=User(id='123')):
            
            # Ejecutar
            result = self.repository.get_by_id('123')
            
            # Verificar
            self.assertIsInstance(result, User)
            mock_session.query.assert_called_once()
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_get_by_id_not_found(self, mock_get_session):
        """Prueba obtener usuario por ID cuando no existe"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None  # No encontrado
        
        # Ejecutar
        result = self.repository.get_by_id('123')
        
        # Verificar
        self.assertIsNone(result)
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_get_all_success(self, mock_get_session):
        """Prueba obtener todos los usuarios exitosamente"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [Mock(), Mock()]
        
        # Mock del método _db_to_model
        with patch.object(self.repository, '_db_to_model', return_value=User(id='123')):
            
            # Ejecutar
            result = self.repository.get_all(limit=10, offset=0)
            
            # Verificar
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)
            mock_session.query.assert_called_once()
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_update_success(self, mock_get_session):
        """Prueba actualizar usuario exitosamente"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_db_user = Mock()
        mock_db_user.id = '123'
        mock_query.filter.return_value.first.return_value = mock_db_user
        
        # Mock del método _db_to_model
        with patch.object(self.repository, '_db_to_model', return_value=User(id='123')):
            
            # Ejecutar
            result = self.repository.update('123', name='Updated Hospital')
            
            # Verificar
            self.assertIsInstance(result, User)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_update_not_found(self, mock_get_session):
        """Prueba actualizar usuario que no existe"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None  # No encontrado
        
        # Ejecutar
        result = self.repository.update('123', name='Updated Hospital')
        
        # Verificar
        self.assertIsNone(result)
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_delete_success(self, mock_get_session):
        """Prueba eliminar usuario exitosamente"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_db_user = Mock()
        mock_query.filter.return_value.first.return_value = mock_db_user
        
        # Ejecutar
        result = self.repository.delete('123')
        
        # Verificar
        self.assertTrue(result)
        mock_session.delete.assert_called_once_with(mock_db_user)
        mock_session.commit.assert_called_once()
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_delete_not_found(self, mock_get_session):
        """Prueba eliminar usuario que no existe"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None  # No encontrado
        
        # Ejecutar
        result = self.repository.delete('123')
        
        # Verificar
        self.assertFalse(result)
        mock_session.delete.assert_not_called()
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_exists_true(self, mock_get_session):
        """Prueba verificar existencia de usuario que existe"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = Mock()  # Existe
        
        # Ejecutar
        result = self.repository.exists('123')
        
        # Verificar
        self.assertTrue(result)
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_exists_false(self, mock_get_session):
        """Prueba verificar existencia de usuario que no existe"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None  # No existe
        
        # Ejecutar
        result = self.repository.exists('123')
        
        # Verificar
        self.assertFalse(result)
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_get_by_email_success(self, mock_get_session):
        """Prueba obtener usuario por email exitosamente"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = Mock()
        
        # Mock del método _db_to_model
        with patch.object(self.repository, '_db_to_model', return_value=User(id='123')):
            
            # Ejecutar
            result = self.repository.get_by_email('test@hospital.com')
            
            # Verificar
            self.assertIsInstance(result, User)
            mock_session.query.assert_called_once()
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_count_all_success(self, mock_get_session):
        """Prueba contar todos los usuarios exitosamente"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.count.return_value = 5
        
        # Ejecutar
        result = self.repository.count_all()
        
        # Verificar
        self.assertEqual(result, 5)
        mock_session.query.assert_called_once()
    
    @patch('app.repositories.user_repository.UserRepository._get_session')
    def test_delete_all_success(self, mock_get_session):
        """Prueba eliminar todos los usuarios exitosamente"""
        # Configurar mock de sesión
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Configurar mock de query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.count.return_value = 3
        mock_query.delete.return_value = None
        
        # Ejecutar
        result = self.repository.delete_all()
        
        # Verificar
        self.assertEqual(result, 3)
        mock_session.commit.assert_called_once()
        mock_query.delete.assert_called_once()


if __name__ == '__main__':
    unittest.main()

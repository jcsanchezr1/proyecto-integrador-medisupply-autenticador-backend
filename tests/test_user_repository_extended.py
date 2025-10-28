"""
Tests extendidos para UserRepository - Incrementar cobertura
"""
import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import uuid

from app.repositories.user_repository import UserRepository, UserDB
from app.models.user_model import User


class TestUserRepositoryExtended(unittest.TestCase):
    """Tests extendidos para UserRepository"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        with patch('app.repositories.user_repository.create_engine'):
            with patch('app.repositories.user_repository.sessionmaker'):
                self.repository = UserRepository()
                self.mock_session = Mock()
                self.repository._get_session = Mock(return_value=self.mock_session)
    
    def test_create_admin_user_success(self):
        """Test: Crear usuario admin exitosamente"""
        # Mock de consulta que verifica email único
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Mock del objeto DB creado
        mock_db_user = Mock(spec=UserDB)
        mock_db_user.id = str(uuid.uuid4())
        mock_db_user.name = 'Admin User'
        mock_db_user.email = 'admin@test.com'
        mock_db_user.tax_id = None
        mock_db_user.address = None
        mock_db_user.phone = None
        mock_db_user.institution_type = None
        mock_db_user.logo_filename = None
        mock_db_user.logo_url = None
        mock_db_user.specialty = None
        mock_db_user.applicant_name = None
        mock_db_user.applicant_email = None
        mock_db_user.latitude = None
        mock_db_user.longitude = None
        mock_db_user.enabled = True
        mock_db_user.created_at = datetime.utcnow()
        mock_db_user.updated_at = datetime.utcnow()
        
        # Ejecutar
        result = self.repository.create_admin_user(
            name='Admin User',
            email='admin@test.com',
            enabled=True
        )
        
        # Verificar
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.assertIsInstance(result, User)
    
    def test_create_admin_user_without_name(self):
        """Test: Crear usuario admin sin nombre debe fallar"""
        with self.assertRaises(Exception) as context:
            self.repository.create_admin_user(
                name='',
                email='admin@test.com'
            )
        
        self.assertIn("name", str(context.exception).lower())
    
    def test_create_admin_user_without_email(self):
        """Test: Crear usuario admin sin email debe fallar"""
        with self.assertRaises(Exception) as context:
            self.repository.create_admin_user(
                name='Admin User',
                email=''
            )
        
        self.assertIn("email", str(context.exception).lower())
    
    def test_create_admin_user_with_duplicate_email(self):
        """Test: Crear usuario admin con email duplicado debe fallar"""
        # Mock de usuario existente
        mock_existing = Mock(spec=UserDB)
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_existing
        
        with self.assertRaises(Exception) as context:
            self.repository.create_admin_user(
                name='Admin User',
                email='existing@test.com'
            )
        
        self.assertIn("existe", str(context.exception).lower())
    
    def test_get_by_email_found(self):
        """Test: Obtener usuario por email cuando existe"""
        mock_db_user = Mock(spec=UserDB)
        mock_db_user.id = str(uuid.uuid4())
        mock_db_user.name = 'Test User'
        mock_db_user.email = 'test@example.com'
        mock_db_user.tax_id = '123456789'
        mock_db_user.address = 'Test Address'
        mock_db_user.phone = '1234567890'
        mock_db_user.institution_type = 'Hospital'
        mock_db_user.logo_filename = 'logo.png'
        mock_db_user.logo_url = 'http://example.com/logo.png'
        mock_db_user.specialty = 'Cadena de frío'
        mock_db_user.applicant_name = 'Applicant'
        mock_db_user.applicant_email = 'applicant@example.com'
        mock_db_user.latitude = 4.6097
        mock_db_user.longitude = -74.0817
        mock_db_user.enabled = True
        mock_db_user.created_at = datetime.utcnow()
        mock_db_user.updated_at = datetime.utcnow()
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_db_user
        
        result = self.repository.get_by_email('test@example.com')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.email, 'test@example.com')
    
    def test_get_by_email_not_found(self):
        """Test: Obtener usuario por email cuando no existe"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.repository.get_by_email('nonexistent@example.com')
        
        self.assertIsNone(result)
    
    def test_count_all_without_filters(self):
        """Test: Contar todos los usuarios sin filtros"""
        self.mock_session.query.return_value.count.return_value = 10
        
        result = self.repository.count_all()
        
        self.assertEqual(result, 10)
    
    def test_count_all_with_email_filter(self):
        """Test: Contar usuarios con filtro de email"""
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 5
        self.mock_session.query.return_value = mock_query
        
        result = self.repository.count_all(email='test')
        
        self.assertEqual(result, 5)
    
    def test_count_all_with_name_filter(self):
        """Test: Contar usuarios con filtro de nombre"""
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 3
        self.mock_session.query.return_value = mock_query
        
        result = self.repository.count_all(name='Hospital')
        
        self.assertEqual(result, 3)
    
    def test_count_all_with_both_filters(self):
        """Test: Contar usuarios con ambos filtros"""
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.count.return_value = 2
        self.mock_session.query.return_value = mock_query
        
        result = self.repository.count_all(email='test', name='Hospital')
        
        self.assertEqual(result, 2)
    
    def test_delete_all_success(self):
        """Test: Eliminar todos los usuarios exitosamente"""
        self.mock_session.query.return_value.count.return_value = 5
        self.mock_session.query.return_value.delete.return_value = 5
        
        result = self.repository.delete_all()
        
        self.assertEqual(result, 5)
        self.mock_session.commit.assert_called_once()
    
    def test_delete_all_with_sqlalchemy_error(self):
        """Test: Error de SQLAlchemy al eliminar todos"""
        from sqlalchemy.exc import SQLAlchemyError
        
        self.mock_session.query.return_value.count.return_value = 5
        self.mock_session.query.return_value.delete.side_effect = SQLAlchemyError("Database error")
        
        with self.assertRaises(Exception) as context:
            self.repository.delete_all()
        
        self.assertIn("Error al eliminar", str(context.exception))
        self.mock_session.rollback.assert_called()
    
    def test_get_all_with_email_filter(self):
        """Test: Obtener usuarios con filtro de email"""
        mock_db_users = []
        for i in range(2):
            mock_user = Mock(spec=UserDB)
            mock_user.id = str(uuid.uuid4())
            mock_user.name = f'User {i}'
            mock_user.email = f'test{i}@example.com'
            mock_user.tax_id = '123456789'
            mock_user.address = 'Address'
            mock_user.phone = '1234567890'
            mock_user.institution_type = 'Hospital'
            mock_user.logo_filename = 'logo.png'
            mock_user.logo_url = 'http://example.com/logo.png'
            mock_user.specialty = 'Alto valor'
            mock_user.applicant_name = 'Applicant'
            mock_user.applicant_email = 'applicant@example.com'
            mock_user.latitude = 4.6097
            mock_user.longitude = -74.0817
            mock_user.enabled = True
            mock_user.created_at = datetime.utcnow()
            mock_user.updated_at = datetime.utcnow()
            mock_db_users.append(mock_user)
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.offset.return_value.all.return_value = mock_db_users
        self.mock_session.query.return_value = mock_query
        
        result = self.repository.get_all(email='test')
        
        self.assertEqual(len(result), 2)
    
    def test_get_all_with_name_filter(self):
        """Test: Obtener usuarios con filtro de nombre"""
        mock_db_users = []
        for i in range(3):
            mock_user = Mock(spec=UserDB)
            mock_user.id = str(uuid.uuid4())
            mock_user.name = f'Hospital {i}'
            mock_user.email = f'hospital{i}@example.com'
            mock_user.tax_id = '123456789'
            mock_user.address = 'Address'
            mock_user.phone = '1234567890'
            mock_user.institution_type = 'Hospital'
            mock_user.logo_filename = 'logo.png'
            mock_user.logo_url = 'http://example.com/logo.png'
            mock_user.specialty = 'Seguridad'
            mock_user.applicant_name = 'Applicant'
            mock_user.applicant_email = 'applicant@example.com'
            mock_user.latitude = 4.6097
            mock_user.longitude = -74.0817
            mock_user.enabled = False
            mock_user.created_at = datetime.utcnow()
            mock_user.updated_at = datetime.utcnow()
            mock_db_users.append(mock_user)
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.offset.return_value.all.return_value = mock_db_users
        self.mock_session.query.return_value = mock_query
        
        result = self.repository.get_all(name='Hospital')
        
        self.assertEqual(len(result), 3)
    
    def test_exists_true(self):
        """Test: Verificar que usuario existe"""
        mock_db_user = Mock(spec=UserDB)
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_db_user
        
        result = self.repository.exists('some-id')
        
        self.assertTrue(result)
    
    def test_exists_false(self):
        """Test: Verificar que usuario no existe"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.repository.exists('non-existent-id')
        
        self.assertFalse(result)
    
    def test_exists_with_sqlalchemy_error(self):
        """Test: Error de SQLAlchemy al verificar existencia"""
        from sqlalchemy.exc import SQLAlchemyError
        
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with self.assertRaises(Exception) as context:
            self.repository.exists('some-id')
        
        self.assertIn("Error al verificar existencia", str(context.exception))
    
    def test_count_all_with_sqlalchemy_error(self):
        """Test: Error de SQLAlchemy al contar usuarios"""
        from sqlalchemy.exc import SQLAlchemyError
        
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with self.assertRaises(Exception) as context:
            self.repository.count_all()
        
        self.assertIn("Error al contar usuarios", str(context.exception))
    
    def test_get_by_email_with_sqlalchemy_error(self):
        """Test: Error de SQLAlchemy al obtener por email"""
        from sqlalchemy.exc import SQLAlchemyError
        
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with self.assertRaises(Exception) as context:
            self.repository.get_by_email('test@example.com')
        
        self.assertIn("Error al obtener usuario por email", str(context.exception))


if __name__ == '__main__':
    unittest.main()


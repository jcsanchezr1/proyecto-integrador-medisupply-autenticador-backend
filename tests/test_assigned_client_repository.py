"""
Tests para el repositorio AssignedClientRepository
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid

from app.repositories.assigned_client_repository import AssignedClientRepository, AssignedClientDB
from app.models.assigned_client_model import AssignedClient


class TestAssignedClientRepository(unittest.TestCase):
    """Tests para AssignedClientRepository"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        with patch('app.repositories.assigned_client_repository.create_engine'):
            with patch('app.repositories.assigned_client_repository.sessionmaker'):
                self.repository = AssignedClientRepository()
                self.mock_session = Mock()
                self.repository._get_session = Mock(return_value=self.mock_session)
    
    def test_create_with_valid_data(self):
        """Test: Crear asignación con datos válidos"""
        # Preparar datos
        seller_id = str(uuid.uuid4())
        client_id = str(uuid.uuid4())
        
        # Mock de la consulta que verifica duplicados
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Mock del objeto DB creado
        mock_db_obj = Mock(spec=AssignedClientDB)
        mock_db_obj.id = str(uuid.uuid4())
        mock_db_obj.seller_id = seller_id
        mock_db_obj.client_id = client_id
        mock_db_obj.created_at = datetime.utcnow()
        mock_db_obj.updated_at = datetime.utcnow()
        
        # Ejecutar
        result = self.repository.create(seller_id=seller_id, client_id=client_id)
        
        # Verificar
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.assertIsInstance(result, AssignedClient)
    
    def test_create_with_duplicate_assignment(self):
        """Test: Crear asignación duplicada debe lanzar error"""
        # Preparar datos
        seller_id = str(uuid.uuid4())
        client_id = str(uuid.uuid4())
        
        # Mock de asignación existente
        mock_existing = Mock(spec=AssignedClientDB)
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_existing
        
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.repository.create(seller_id=seller_id, client_id=client_id)
        
        self.assertIn("ya existe", str(context.exception))
    
    def test_get_by_id_found(self):
        """Test: Obtener asignación por ID cuando existe"""
        # Preparar datos
        assignment_id = str(uuid.uuid4())
        mock_db_obj = Mock(spec=AssignedClientDB)
        mock_db_obj.id = assignment_id
        mock_db_obj.seller_id = str(uuid.uuid4())
        mock_db_obj.client_id = str(uuid.uuid4())
        mock_db_obj.created_at = datetime.utcnow()
        mock_db_obj.updated_at = datetime.utcnow()
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_db_obj
        
        # Ejecutar
        result = self.repository.get_by_id(assignment_id)
        
        # Verificar
        self.assertIsNotNone(result)
        self.assertIsInstance(result, AssignedClient)
        self.assertEqual(result.id, assignment_id)
    
    def test_get_by_id_not_found(self):
        """Test: Obtener asignación por ID cuando no existe"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.repository.get_by_id('non-existent-id')
        
        self.assertIsNone(result)
    
    def test_get_all_with_limit(self):
        """Test: Obtener todas las asignaciones con límite"""
        # Mock de resultados
        mock_db_objs = []
        for _ in range(5):
            mock_obj = Mock(spec=AssignedClientDB)
            mock_obj.id = str(uuid.uuid4())
            mock_obj.seller_id = str(uuid.uuid4())
            mock_obj.client_id = str(uuid.uuid4())
            mock_obj.created_at = datetime.utcnow()
            mock_obj.updated_at = datetime.utcnow()
            mock_db_objs.append(mock_obj)
        
        mock_query = Mock()
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_db_objs[:3]
        self.mock_session.query.return_value = mock_query
        
        # Ejecutar
        result = self.repository.get_all(limit=3, offset=0)
        
        # Verificar
        self.assertEqual(len(result), 3)
        for item in result:
            self.assertIsInstance(item, AssignedClient)
    
    def test_get_all_without_limit(self):
        """Test: Obtener todas las asignaciones sin límite"""
        mock_db_objs = []
        for _ in range(5):
            mock_obj = Mock(spec=AssignedClientDB)
            mock_obj.id = str(uuid.uuid4())
            mock_obj.seller_id = str(uuid.uuid4())
            mock_obj.client_id = str(uuid.uuid4())
            mock_obj.created_at = datetime.utcnow()
            mock_obj.updated_at = datetime.utcnow()
            mock_db_objs.append(mock_obj)
        
        mock_query = Mock()
        mock_query.order_by.return_value.offset.return_value.all.return_value = mock_db_objs
        self.mock_session.query.return_value = mock_query
        
        result = self.repository.get_all(limit=None, offset=0)
        
        self.assertEqual(len(result), 5)
    
    def test_get_by_seller_id(self):
        """Test: Obtener asignaciones por seller_id"""
        seller_id = str(uuid.uuid4())
        mock_db_objs = []
        for _ in range(3):
            mock_obj = Mock(spec=AssignedClientDB)
            mock_obj.id = str(uuid.uuid4())
            mock_obj.seller_id = seller_id
            mock_obj.client_id = str(uuid.uuid4())
            mock_obj.created_at = datetime.utcnow()
            mock_obj.updated_at = datetime.utcnow()
            mock_db_objs.append(mock_obj)
        
        self.mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_db_objs
        
        result = self.repository.get_by_seller_id(seller_id)
        
        self.assertEqual(len(result), 3)
        for item in result:
            self.assertEqual(item.seller_id, seller_id)
    
    def test_get_by_client_id(self):
        """Test: Obtener asignaciones por client_id"""
        client_id = str(uuid.uuid4())
        mock_db_objs = []
        for _ in range(2):
            mock_obj = Mock(spec=AssignedClientDB)
            mock_obj.id = str(uuid.uuid4())
            mock_obj.seller_id = str(uuid.uuid4())
            mock_obj.client_id = client_id
            mock_obj.created_at = datetime.utcnow()
            mock_obj.updated_at = datetime.utcnow()
            mock_db_objs.append(mock_obj)
        
        self.mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_db_objs
        
        result = self.repository.get_by_client_id(client_id)
        
        self.assertEqual(len(result), 2)
        for item in result:
            self.assertEqual(item.client_id, client_id)
    
    def test_update_success(self):
        """Test: Actualizar asignación exitosamente"""
        assignment_id = str(uuid.uuid4())
        mock_db_obj = Mock(spec=AssignedClientDB)
        mock_db_obj.id = assignment_id
        mock_db_obj.seller_id = str(uuid.uuid4())
        mock_db_obj.client_id = str(uuid.uuid4())
        mock_db_obj.created_at = datetime.utcnow()
        mock_db_obj.updated_at = datetime.utcnow()
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_db_obj
        
        result = self.repository.update(assignment_id, seller_id='new-seller-id')
        
        self.assertIsNotNone(result)
        self.mock_session.commit.assert_called_once()
    
    def test_update_not_found(self):
        """Test: Actualizar asignación que no existe"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.repository.update('non-existent-id', seller_id='new-seller-id')
        
        self.assertIsNone(result)
    
    def test_delete_success(self):
        """Test: Eliminar asignación exitosamente"""
        assignment_id = str(uuid.uuid4())
        mock_db_obj = Mock(spec=AssignedClientDB)
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_db_obj
        
        result = self.repository.delete(assignment_id)
        
        self.assertTrue(result)
        self.mock_session.delete.assert_called_once_with(mock_db_obj)
        self.mock_session.commit.assert_called_once()
    
    def test_delete_not_found(self):
        """Test: Eliminar asignación que no existe"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.repository.delete('non-existent-id')
        
        self.assertFalse(result)
    
    def test_exists_true(self):
        """Test: Verificar que asignación existe"""
        mock_db_obj = Mock(spec=AssignedClientDB)
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_db_obj
        
        result = self.repository.exists('some-id')
        
        self.assertTrue(result)
    
    def test_exists_false(self):
        """Test: Verificar que asignación no existe"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.repository.exists('non-existent-id')
        
        self.assertFalse(result)
    
    def test_exists_assignment_true(self):
        """Test: Verificar que asignación específica existe"""
        mock_db_obj = Mock(spec=AssignedClientDB)
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_db_obj
        
        result = self.repository.exists_assignment('seller-id', 'client-id')
        
        self.assertTrue(result)
    
    def test_exists_assignment_false(self):
        """Test: Verificar que asignación específica no existe"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.repository.exists_assignment('seller-id', 'client-id')
        
        self.assertFalse(result)
    
    def test_create_with_sqlalchemy_error(self):
        """Test: Error de SQLAlchemy al crear"""
        from sqlalchemy.exc import SQLAlchemyError
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        self.mock_session.commit.side_effect = SQLAlchemyError("Database error")
        
        with self.assertRaises(Exception) as context:
            self.repository.create(seller_id='seller', client_id='client')
        
        self.assertIn("Error al crear asignación", str(context.exception))
        self.mock_session.rollback.assert_called()
    
    def test_get_by_id_with_sqlalchemy_error(self):
        """Test: Error de SQLAlchemy al obtener por ID"""
        from sqlalchemy.exc import SQLAlchemyError
        
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with self.assertRaises(Exception) as context:
            self.repository.get_by_id('some-id')
        
        self.assertIn("Error al obtener asignación", str(context.exception))
    
    def test_update_with_sqlalchemy_error(self):
        """Test: Error de SQLAlchemy al actualizar"""
        from sqlalchemy.exc import SQLAlchemyError
        
        mock_db_obj = Mock(spec=AssignedClientDB)
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_db_obj
        self.mock_session.commit.side_effect = SQLAlchemyError("Database error")
        
        with self.assertRaises(Exception) as context:
            self.repository.update('some-id', seller_id='new-seller')
        
        self.assertIn("Error al actualizar asignación", str(context.exception))
        self.mock_session.rollback.assert_called()
    
    def test_delete_with_sqlalchemy_error(self):
        """Test: Error de SQLAlchemy al eliminar"""
        from sqlalchemy.exc import SQLAlchemyError
        
        mock_db_obj = Mock(spec=AssignedClientDB)
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_db_obj
        self.mock_session.commit.side_effect = SQLAlchemyError("Database error")
        
        with self.assertRaises(Exception) as context:
            self.repository.delete('some-id')
        
        self.assertIn("Error al eliminar asignación", str(context.exception))
        self.mock_session.rollback.assert_called()


if __name__ == '__main__':
    unittest.main()


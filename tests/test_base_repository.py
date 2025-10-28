"""
Tests para BaseRepository - Incrementar cobertura
"""
import unittest
from app.repositories.base_repository import BaseRepository


class ConcreteRepository(BaseRepository):
    """Repositorio concreto para testing de BaseRepository"""
    
    def __init__(self):
        self.storage = {}
    
    def create(self, **kwargs):
        """Implementación concreta de create"""
        entity_id = kwargs.get('id', 'generated-id')
        self.storage[entity_id] = kwargs
        return kwargs
    
    def get_by_id(self, entity_id: str):
        """Implementación concreta de get_by_id"""
        return self.storage.get(entity_id)
    
    def get_all(self, limit=None, offset=0):
        """Implementación concreta de get_all"""
        items = list(self.storage.values())
        if limit:
            return items[offset:offset+limit]
        return items[offset:]
    
    def update(self, entity_id: str, **kwargs):
        """Implementación concreta de update"""
        if entity_id in self.storage:
            self.storage[entity_id].update(kwargs)
            return self.storage[entity_id]
        return None
    
    def delete(self, entity_id: str):
        """Implementación concreta de delete"""
        if entity_id in self.storage:
            del self.storage[entity_id]
            return True
        return False
    
    def exists(self, entity_id: str):
        """Implementación concreta de exists"""
        return entity_id in self.storage


class TestBaseRepository(unittest.TestCase):
    """Tests para BaseRepository"""
    
    def setUp(self):
        """Configuración inicial"""
        self.repo = ConcreteRepository()
    
    def test_create(self):
        """Test: create es método abstracto implementado"""
        result = self.repo.create(id='123', name='Test')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], '123')
        self.assertEqual(result['name'], 'Test')
    
    def test_get_by_id_found(self):
        """Test: get_by_id encuentra entidad"""
        self.repo.create(id='123', name='Test')
        result = self.repo.get_by_id('123')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Test')
    
    def test_get_by_id_not_found(self):
        """Test: get_by_id no encuentra entidad"""
        result = self.repo.get_by_id('non-existent')
        
        self.assertIsNone(result)
    
    def test_get_all_without_limit(self):
        """Test: get_all sin límite"""
        self.repo.create(id='1', name='Test1')
        self.repo.create(id='2', name='Test2')
        self.repo.create(id='3', name='Test3')
        
        result = self.repo.get_all()
        
        self.assertEqual(len(result), 3)
    
    def test_get_all_with_limit(self):
        """Test: get_all con límite"""
        self.repo.create(id='1', name='Test1')
        self.repo.create(id='2', name='Test2')
        self.repo.create(id='3', name='Test3')
        
        result = self.repo.get_all(limit=2)
        
        self.assertEqual(len(result), 2)
    
    def test_get_all_with_offset(self):
        """Test: get_all con offset"""
        self.repo.create(id='1', name='Test1')
        self.repo.create(id='2', name='Test2')
        self.repo.create(id='3', name='Test3')
        
        result = self.repo.get_all(offset=1)
        
        self.assertEqual(len(result), 2)
    
    def test_update_existing(self):
        """Test: update entidad existente"""
        self.repo.create(id='123', name='Test')
        result = self.repo.update('123', name='Updated')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Updated')
    
    def test_update_non_existing(self):
        """Test: update entidad no existente"""
        result = self.repo.update('non-existent', name='Updated')
        
        self.assertIsNone(result)
    
    def test_delete_existing(self):
        """Test: delete entidad existente"""
        self.repo.create(id='123', name='Test')
        result = self.repo.delete('123')
        
        self.assertTrue(result)
        self.assertIsNone(self.repo.get_by_id('123'))
    
    def test_delete_non_existing(self):
        """Test: delete entidad no existente"""
        result = self.repo.delete('non-existent')
        
        self.assertFalse(result)
    
    def test_exists_true(self):
        """Test: exists retorna True para entidad existente"""
        self.repo.create(id='123', name='Test')
        result = self.repo.exists('123')
        
        self.assertTrue(result)
    
    def test_exists_false(self):
        """Test: exists retorna False para entidad no existente"""
        result = self.repo.exists('non-existent')
        
        self.assertFalse(result)
    
    def test_cannot_instantiate_abstract_class(self):
        """Test: No se puede instanciar la clase abstracta directamente"""
        from abc import ABCMeta
        
        # Verificar que BaseRepository es abstracta
        self.assertIsInstance(BaseRepository, ABCMeta)
        
        # Intentar instanciar directamente debe fallar
        with self.assertRaises(TypeError):
            BaseRepository()
    
    def test_abstract_methods_exist(self):
        """Test: Verificar que los métodos abstractos existen"""
        # Verificar que los métodos abstractos están definidos
        self.assertTrue(hasattr(BaseRepository, 'create'))
        self.assertTrue(hasattr(BaseRepository, 'get_by_id'))
        self.assertTrue(hasattr(BaseRepository, 'get_all'))
        self.assertTrue(hasattr(BaseRepository, 'update'))
        self.assertTrue(hasattr(BaseRepository, 'delete'))
        self.assertTrue(hasattr(BaseRepository, 'exists'))
    
    def test_concrete_implementation_coverage(self):
        """Test: Asegurar cobertura de métodos implementados"""
        # Crear múltiples operaciones para asegurar cobertura completa
        self.repo.create(id='test1', value='value1')
        self.repo.create(id='test2', value='value2')
        
        # Get by id
        self.assertIsNotNone(self.repo.get_by_id('test1'))
        self.assertIsNone(self.repo.get_by_id('nonexistent'))
        
        # Get all
        all_items = self.repo.get_all()
        self.assertGreater(len(all_items), 0)
        
        # Update
        self.repo.update('test1', value='updated')
        updated = self.repo.get_by_id('test1')
        self.assertEqual(updated['value'], 'updated')
        
        # Exists
        self.assertTrue(self.repo.exists('test1'))
        self.assertFalse(self.repo.exists('nonexistent'))
        
        # Delete
        self.assertTrue(self.repo.delete('test1'))
        self.assertFalse(self.repo.delete('test1'))


if __name__ == '__main__':
    unittest.main()

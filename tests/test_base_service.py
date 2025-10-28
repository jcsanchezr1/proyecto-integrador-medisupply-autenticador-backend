"""
Tests para BaseService - Incrementar cobertura
"""
import unittest
from app.services.base_service import BaseService


class ConcreteService(BaseService):
    """Servicio concreto para testing de BaseService"""
    
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
    
    def validate_business_rules(self, **kwargs):
        """Implementación concreta de validate_business_rules"""
        if 'name' not in kwargs or not kwargs['name']:
            raise ValueError("Name is required")


class TestBaseService(unittest.TestCase):
    """Tests para BaseService"""
    
    def setUp(self):
        """Configuración inicial"""
        self.service = ConcreteService()
    
    def test_create(self):
        """Test: create es método abstracto implementado"""
        result = self.service.create(id='123', name='Test')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], '123')
        self.assertEqual(result['name'], 'Test')
    
    def test_get_by_id_found(self):
        """Test: get_by_id encuentra entidad"""
        self.service.create(id='123', name='Test')
        result = self.service.get_by_id('123')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Test')
    
    def test_get_by_id_not_found(self):
        """Test: get_by_id no encuentra entidad"""
        result = self.service.get_by_id('non-existent')
        
        self.assertIsNone(result)
    
    def test_get_all_without_limit(self):
        """Test: get_all sin límite"""
        self.service.create(id='1', name='Test1')
        self.service.create(id='2', name='Test2')
        self.service.create(id='3', name='Test3')
        
        result = self.service.get_all()
        
        self.assertEqual(len(result), 3)
    
    def test_get_all_with_limit(self):
        """Test: get_all con límite"""
        self.service.create(id='1', name='Test1')
        self.service.create(id='2', name='Test2')
        self.service.create(id='3', name='Test3')
        
        result = self.service.get_all(limit=2)
        
        self.assertEqual(len(result), 2)
    
    def test_get_all_with_offset(self):
        """Test: get_all con offset"""
        self.service.create(id='1', name='Test1')
        self.service.create(id='2', name='Test2')
        self.service.create(id='3', name='Test3')
        
        result = self.service.get_all(offset=1)
        
        self.assertEqual(len(result), 2)
    
    def test_update_existing(self):
        """Test: update entidad existente"""
        self.service.create(id='123', name='Test')
        result = self.service.update('123', name='Updated')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Updated')
    
    def test_update_non_existing(self):
        """Test: update entidad no existente"""
        result = self.service.update('non-existent', name='Updated')
        
        self.assertIsNone(result)
    
    def test_delete_existing(self):
        """Test: delete entidad existente"""
        self.service.create(id='123', name='Test')
        result = self.service.delete('123')
        
        self.assertTrue(result)
        self.assertIsNone(self.service.get_by_id('123'))
    
    def test_delete_non_existing(self):
        """Test: delete entidad no existente"""
        result = self.service.delete('non-existent')
        
        self.assertFalse(result)
    
    def test_validate_business_rules_success(self):
        """Test: validate_business_rules con datos válidos"""
        try:
            self.service.validate_business_rules(name='Test')
        except ValueError:
            self.fail("validate_business_rules raised ValueError unexpectedly")
    
    def test_validate_business_rules_failure(self):
        """Test: validate_business_rules con datos inválidos"""
        with self.assertRaises(ValueError):
            self.service.validate_business_rules(name='')
    
    def test_cannot_instantiate_abstract_class(self):
        """Test: No se puede instanciar la clase abstracta directamente"""
        from abc import ABCMeta
        
        # Verificar que BaseService es abstracta
        self.assertIsInstance(BaseService, ABCMeta)
        
        # Intentar instanciar directamente debe fallar
        with self.assertRaises(TypeError):
            BaseService()
    
    def test_abstract_methods_exist(self):
        """Test: Verificar que los métodos abstractos existen"""
        # Verificar que los métodos abstractos están definidos
        self.assertTrue(hasattr(BaseService, 'create'))
        self.assertTrue(hasattr(BaseService, 'get_by_id'))
        self.assertTrue(hasattr(BaseService, 'get_all'))
        self.assertTrue(hasattr(BaseService, 'update'))
        self.assertTrue(hasattr(BaseService, 'delete'))
        self.assertTrue(hasattr(BaseService, 'validate_business_rules'))
    
    def test_concrete_implementation_coverage(self):
        """Test: Asegurar cobertura de métodos implementados"""
        # Validar reglas de negocio
        self.service.validate_business_rules(name='Valid Name')
        
        # Crear múltiples entidades
        self.service.create(id='test1', name='Test1', value='value1')
        self.service.create(id='test2', name='Test2', value='value2')
        
        # Get by id
        entity = self.service.get_by_id('test1')
        self.assertIsNotNone(entity)
        self.assertEqual(entity['name'], 'Test1')
        
        # Get all con diferentes parámetros
        all_entities = self.service.get_all()
        self.assertEqual(len(all_entities), 2)
        
        limited = self.service.get_all(limit=1)
        self.assertEqual(len(limited), 1)
        
        offset = self.service.get_all(offset=1)
        self.assertEqual(len(offset), 1)
        
        # Update
        updated = self.service.update('test1', name='Updated Name')
        self.assertIsNotNone(updated)
        self.assertEqual(updated['name'], 'Updated Name')
        
        # Delete
        result = self.service.delete('test1')
        self.assertTrue(result)
        
        # Verify deleted
        deleted_entity = self.service.get_by_id('test1')
        self.assertIsNone(deleted_entity)


if __name__ == '__main__':
    unittest.main()

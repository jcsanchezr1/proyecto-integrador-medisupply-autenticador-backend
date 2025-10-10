"""
Pruebas unitarias para BaseRepository usando unittest
"""
import unittest
import sys
import os
from abc import ABC

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.repositories.base_repository import BaseRepository


class TestBaseRepository(unittest.TestCase):
    """Pruebas para BaseRepository"""
    
    def test_base_repository_is_abstract(self):
        """Prueba que BaseRepository es una clase abstracta"""
        self.assertTrue(issubclass(BaseRepository, ABC))
    
    def test_base_repository_has_abstract_methods(self):
        """Prueba que BaseRepository tiene métodos abstractos"""
        # Verificar que los métodos abstractos están definidos
        abstract_methods = BaseRepository.__abstractmethods__
        
        expected_methods = {
            'create', 'get_by_id', 'get_all', 'update', 'delete', 'exists'
        }
        
        self.assertEqual(abstract_methods, expected_methods)
    
    def test_cannot_instantiate_base_repository(self):
        """Prueba que no se puede instanciar BaseRepository directamente"""
        with self.assertRaises(TypeError):
            BaseRepository()
    
    def test_concrete_repository_must_implement_abstract_methods(self):
        """Prueba que una implementación concreta debe implementar todos los métodos abstractos"""
        
        class IncompleteRepository(BaseRepository):
            def create(self, **kwargs):
                pass
            
            def get_by_id(self, entity_id: str):
                pass
            
            def get_all(self, limit=None, offset=0):
                pass
            
            def update(self, entity_id: str, **kwargs):
                pass
            
            def delete(self, entity_id: str):
                pass
            
            # Falta implementar 'exists'
        
        # No se puede instanciar porque no implementa todos los métodos abstractos
        with self.assertRaises(TypeError):
            IncompleteRepository()
    
    def test_complete_repository_can_be_instantiated(self):
        """Prueba que una implementación completa puede ser instanciada"""
        
        class CompleteRepository(BaseRepository):
            def create(self, **kwargs):
                return {"id": "123", "name": "Test"}
            
            def get_by_id(self, entity_id: str):
                return {"id": entity_id, "name": "Test"}
            
            def get_all(self, limit=None, offset=0):
                return [{"id": "123", "name": "Test"}]
            
            def update(self, entity_id: str, **kwargs):
                return {"id": entity_id, "name": "Updated"}
            
            def delete(self, entity_id: str):
                return True
            
            def exists(self, entity_id: str):
                return True
        
        # Debe poder instanciarse sin problemas
        repository = CompleteRepository()
        self.assertIsInstance(repository, BaseRepository)
        self.assertIsInstance(repository, CompleteRepository)
    
    def test_repository_methods_have_correct_signatures(self):
        """Prueba que los métodos abstractos tienen las firmas correctas"""
        import inspect
        
        # Verificar firma de create
        create_sig = inspect.signature(BaseRepository.create)
        self.assertEqual(len(create_sig.parameters), 2)  # self y **kwargs
        self.assertTrue(create_sig.parameters['self'].annotation == inspect.Parameter.empty)
        
        # Verificar firma de get_by_id
        get_by_id_sig = inspect.signature(BaseRepository.get_by_id)
        self.assertEqual(len(get_by_id_sig.parameters), 2)  # self y entity_id
        self.assertEqual(get_by_id_sig.parameters['entity_id'].annotation, str)
        
        # Verificar firma de get_all
        get_all_sig = inspect.signature(BaseRepository.get_all)
        self.assertEqual(len(get_all_sig.parameters), 3)  # self, limit, offset
        from typing import Optional
        self.assertEqual(get_all_sig.parameters['limit'].annotation, Optional[int])
        self.assertEqual(get_all_sig.parameters['offset'].annotation, int)
        
        # Verificar firma de update
        update_sig = inspect.signature(BaseRepository.update)
        self.assertEqual(len(update_sig.parameters), 3)  # self, entity_id y **kwargs
        self.assertEqual(update_sig.parameters['entity_id'].annotation, str)
        
        # Verificar firma de delete
        delete_sig = inspect.signature(BaseRepository.delete)
        self.assertEqual(len(delete_sig.parameters), 2)  # self y entity_id
        self.assertEqual(delete_sig.parameters['entity_id'].annotation, str)
        
        # Verificar firma de exists
        exists_sig = inspect.signature(BaseRepository.exists)
        self.assertEqual(len(exists_sig.parameters), 2)  # self y entity_id
        self.assertEqual(exists_sig.parameters['entity_id'].annotation, str)


if __name__ == '__main__':
    unittest.main()

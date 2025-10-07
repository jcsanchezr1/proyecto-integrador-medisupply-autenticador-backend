"""
Pruebas unitarias para BaseService usando unittest
"""
import unittest
import sys
import os
from abc import ABC

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.base_service import BaseService


class TestBaseService(unittest.TestCase):
    """Pruebas para BaseService"""
    
    def test_base_service_is_abstract(self):
        """Prueba que BaseService es una clase abstracta"""
        self.assertTrue(issubclass(BaseService, ABC))
    
    def test_base_service_has_abstract_methods(self):
        """Prueba que BaseService tiene métodos abstractos"""
        # Verificar que los métodos abstractos están definidos
        abstract_methods = BaseService.__abstractmethods__
        
        expected_methods = {
            'create', 'get_by_id', 'get_all', 'update', 'delete', 'validate_business_rules'
        }
        
        self.assertEqual(abstract_methods, expected_methods)
    
    def test_cannot_instantiate_base_service(self):
        """Prueba que no se puede instanciar BaseService directamente"""
        with self.assertRaises(TypeError):
            BaseService()
    
    def test_concrete_service_must_implement_abstract_methods(self):
        """Prueba que una implementación concreta debe implementar todos los métodos abstractos"""
        
        class IncompleteService(BaseService):
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
            
            # Falta implementar 'validate_business_rules'
        
        # No se puede instanciar porque no implementa todos los métodos abstractos
        with self.assertRaises(TypeError):
            IncompleteService()
    
    def test_complete_service_can_be_instantiated(self):
        """Prueba que una implementación completa puede ser instanciada"""
        
        class CompleteService(BaseService):
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
            
            def validate_business_rules(self, **kwargs):
                pass
        
        # Debe poder instanciarse sin problemas
        service = CompleteService()
        self.assertIsInstance(service, BaseService)
        self.assertIsInstance(service, CompleteService)
    
    def test_service_methods_have_correct_signatures(self):
        """Prueba que los métodos abstractos tienen las firmas correctas"""
        import inspect
        
        # Verificar firma de create
        create_sig = inspect.signature(BaseService.create)
        self.assertEqual(len(create_sig.parameters), 2)  # self y **kwargs
        self.assertTrue(create_sig.parameters['self'].annotation == inspect.Parameter.empty)
        
        # Verificar firma de get_by_id
        get_by_id_sig = inspect.signature(BaseService.get_by_id)
        self.assertEqual(len(get_by_id_sig.parameters), 2)  # self y entity_id
        self.assertEqual(get_by_id_sig.parameters['entity_id'].annotation, str)
        
        # Verificar firma de get_all
        get_all_sig = inspect.signature(BaseService.get_all)
        self.assertEqual(len(get_all_sig.parameters), 3)  # self, limit, offset
        from typing import Optional
        self.assertEqual(get_all_sig.parameters['limit'].annotation, Optional[int])
        self.assertEqual(get_all_sig.parameters['offset'].annotation, int)
        
        # Verificar firma de update
        update_sig = inspect.signature(BaseService.update)
        self.assertEqual(len(update_sig.parameters), 3)  # self, entity_id y **kwargs
        self.assertEqual(update_sig.parameters['entity_id'].annotation, str)
        
        # Verificar firma de delete
        delete_sig = inspect.signature(BaseService.delete)
        self.assertEqual(len(delete_sig.parameters), 2)  # self y entity_id
        self.assertEqual(delete_sig.parameters['entity_id'].annotation, str)
        
        # Verificar firma de validate_business_rules
        validate_sig = inspect.signature(BaseService.validate_business_rules)
        self.assertEqual(len(validate_sig.parameters), 2)  # self y **kwargs
        self.assertTrue(validate_sig.parameters['self'].annotation == inspect.Parameter.empty)


if __name__ == '__main__':
    unittest.main()

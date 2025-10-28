"""
Tests para BaseModel - Incrementar cobertura
"""
import unittest
from app.models.base_model import BaseModel


class ConcreteModel(BaseModel):
    """Modelo concreto para testing de BaseModel"""
    
    def __init__(self, **kwargs):
        self.id = None
        self.name = None
        self.value = None
        super().__init__(**kwargs)
    
    def to_dict(self):
        """Implementación concreta de to_dict"""
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value
        }
    
    def validate(self):
        """Implementación concreta de validate"""
        if not self.name:
            raise ValueError("Name is required")


class TestBaseModel(unittest.TestCase):
    """Tests para BaseModel"""
    
    def test_init_with_valid_attributes(self):
        """Test: Inicializar modelo con atributos válidos"""
        model = ConcreteModel(id='123', name='Test', value=100)
        
        self.assertEqual(model.id, '123')
        self.assertEqual(model.name, 'Test')
        self.assertEqual(model.value, 100)
    
    def test_init_with_invalid_attributes(self):
        """Test: Inicializar modelo con atributos que no existen (deben ser ignorados)"""
        model = ConcreteModel(
            id='123',
            name='Test',
            invalid_attr='should be ignored'
        )
        
        self.assertEqual(model.id, '123')
        self.assertEqual(model.name, 'Test')
        self.assertFalse(hasattr(model, 'invalid_attr'))
    
    def test_to_dict_abstract_method(self):
        """Test: to_dict es método abstracto implementado"""
        model = ConcreteModel(id='123', name='Test')
        result = model.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], '123')
        self.assertEqual(result['name'], 'Test')
    
    def test_validate_abstract_method(self):
        """Test: validate es método abstracto implementado"""
        model = ConcreteModel(id='123', name='Test')
        
        # No debe lanzar excepción con datos válidos
        try:
            model.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly")
    
    def test_validate_with_invalid_data(self):
        """Test: validate lanza excepción con datos inválidos"""
        model = ConcreteModel(id='123', name=None)
        
        with self.assertRaises(ValueError):
            model.validate()
    
    def test_repr(self):
        """Test: __repr__ retorna representación string correcta"""
        model = ConcreteModel(id='123', name='Test')
        repr_str = repr(model)
        
        self.assertIn('ConcreteModel', repr_str)
        self.assertTrue(repr_str.startswith('<'))
        self.assertTrue(repr_str.endswith('>'))
    
    def test_init_with_empty_kwargs(self):
        """Test: Inicializar modelo sin argumentos"""
        model = ConcreteModel()
        
        self.assertIsNone(model.id)
        self.assertIsNone(model.name)
        self.assertIsNone(model.value)
    
    def test_init_with_partial_kwargs(self):
        """Test: Inicializar modelo con algunos argumentos"""
        model = ConcreteModel(name='Test')
        
        self.assertIsNone(model.id)
        self.assertEqual(model.name, 'Test')
        self.assertIsNone(model.value)


if __name__ == '__main__':
    unittest.main()


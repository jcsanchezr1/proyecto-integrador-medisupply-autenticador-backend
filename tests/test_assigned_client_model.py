"""
Tests para el modelo AssignedClient
"""
import unittest
from datetime import datetime
from app.models.assigned_client_model import AssignedClient


class TestAssignedClientModel(unittest.TestCase):
    """Tests para el modelo AssignedClient"""
    
    def test_create_assigned_client_with_valid_data(self):
        """Test: Crear un cliente asignado con datos válidos"""
        data = {
            'seller_id': '123e4567-e89b-12d3-a456-426614174000',
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }
        
        assigned_client = AssignedClient(**data)
        
        self.assertIsNotNone(assigned_client.id)
        self.assertEqual(assigned_client.seller_id, data['seller_id'])
        self.assertEqual(assigned_client.client_id, data['client_id'])
        self.assertIsInstance(assigned_client.created_at, datetime)
        self.assertIsInstance(assigned_client.updated_at, datetime)
    
    def test_validate_with_valid_data(self):
        """Test: Validar con datos correctos no debe lanzar excepción"""
        data = {
            'seller_id': '123e4567-e89b-12d3-a456-426614174000',
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }
        
        assigned_client = AssignedClient(**data)
        
        try:
            assigned_client.validate()
        except ValueError:
            self.fail("validate() lanzó ValueError inesperadamente")
    
    def test_validate_without_seller_id(self):
        """Test: Validar sin seller_id debe lanzar ValueError"""
        data = {
            'seller_id': '',
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }
        
        assigned_client = AssignedClient(**data)
        
        with self.assertRaises(ValueError) as context:
            assigned_client.validate()
        
        self.assertIn("seller_id", str(context.exception))
    
    def test_validate_without_client_id(self):
        """Test: Validar sin client_id debe lanzar ValueError"""
        data = {
            'seller_id': '123e4567-e89b-12d3-a456-426614174000',
            'client_id': ''
        }
        
        assigned_client = AssignedClient(**data)
        
        with self.assertRaises(ValueError) as context:
            assigned_client.validate()
        
        self.assertIn("client_id", str(context.exception))
    
    def test_validate_with_same_seller_and_client(self):
        """Test: Validar con mismo seller_id y client_id debe lanzar ValueError"""
        same_id = '123e4567-e89b-12d3-a456-426614174000'
        data = {
            'seller_id': same_id,
            'client_id': same_id
        }
        
        assigned_client = AssignedClient(**data)
        
        with self.assertRaises(ValueError) as context:
            assigned_client.validate()
        
        self.assertIn("propio cliente", str(context.exception))
    
    def test_to_dict(self):
        """Test: Convertir modelo a diccionario"""
        data = {
            'id': '987e6543-e21b-12d3-a456-426614174000',
            'seller_id': '123e4567-e89b-12d3-a456-426614174000',
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }
        
        assigned_client = AssignedClient(**data)
        result = assigned_client.to_dict()
        
        self.assertEqual(result['id'], data['id'])
        self.assertEqual(result['seller_id'], data['seller_id'])
        self.assertEqual(result['client_id'], data['client_id'])
        self.assertIn('created_at', result)
        self.assertIn('updated_at', result)
    
    def test_repr(self):
        """Test: Representación string del modelo"""
        data = {
            'id': '987e6543-e21b-12d3-a456-426614174000',
            'seller_id': '123e4567-e89b-12d3-a456-426614174000',
            'client_id': '456e7890-e89b-12d3-a456-426614174111'
        }
        
        assigned_client = AssignedClient(**data)
        repr_str = repr(assigned_client)
        
        self.assertIn('AssignedClient', repr_str)
        self.assertIn(data['id'], repr_str)
        self.assertIn(data['seller_id'], repr_str)
        self.assertIn(data['client_id'], repr_str)


if __name__ == '__main__':
    unittest.main()


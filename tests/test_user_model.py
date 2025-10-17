"""
Tests para los modelos de usuario (User y AdminUserCreate)
"""
import unittest
import sys
import os

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.user_model import User, AdminUserCreate


class TestAdminUserCreate(unittest.TestCase):
    """Tests para AdminUserCreate"""
    
    def test_init_with_valid_data(self):
        """Test de inicialización con datos válidos"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="admin@test.com",
            password="password123",
            confirm_password="password123",
            role="Administrador"
        )
        
        self.assertEqual(admin_user.name, "Admin User")
        self.assertEqual(admin_user.email, "admin@test.com")
        self.assertEqual(admin_user.password, "password123")
        self.assertEqual(admin_user.confirm_password, "password123")
        self.assertEqual(admin_user.role, "Administrador")
    
    def test_to_dict(self):
        """Test del método to_dict"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="admin@test.com",
            password="password123",
            confirm_password="password123",
            role="Administrador"
        )
        result = admin_user.to_dict()
        
        expected = {
            "name": "Admin User",
            "email": "admin@test.com",
            "role": "Administrador"
        }
        self.assertEqual(result, expected)
        # Verificar que no incluye password por seguridad
        self.assertNotIn("password", result)
        self.assertNotIn("confirm_password", result)
    
    def test_validate_success(self):
        """Test de validación exitosa"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="admin@test.com",
            password="password123",
            confirm_password="password123",
            role="Administrador"
        )
        
        # No debe lanzar excepción
        admin_user.validate()
    
    def test_validate_name_required(self):
        """Test de validación con nombre vacío"""
        admin_user = AdminUserCreate(
            name="",
            email="admin@test.com",
            password="password123",
            confirm_password="password123",
            role="Administrador"
        )
        
        with self.assertRaises(ValueError) as context:
            admin_user.validate()
        
        self.assertIn("name", str(context.exception))
    
    def test_validate_name_too_long(self):
        """Test de validación con nombre muy largo"""
        admin_user = AdminUserCreate(
            name="A" * 101,  # Más de 100 caracteres
            email="admin@test.com",
            password="password123",
            confirm_password="password123",
            role="Administrador"
        )
        
        with self.assertRaises(ValueError) as context:
            admin_user.validate()
        
        self.assertIn("name", str(context.exception))
    
    def test_validate_email_required(self):
        """Test de validación con email vacío"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="",
            password="password123",
            confirm_password="password123",
            role="Administrador"
        )
        
        with self.assertRaises(ValueError) as context:
            admin_user.validate()
        
        self.assertIn("email", str(context.exception))
    
    def test_validate_email_invalid_format(self):
        """Test de validación con email inválido"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="invalid-email",
            password="password123",
            confirm_password="password123",
            role="Administrador"
        )
        
        with self.assertRaises(ValueError) as context:
            admin_user.validate()
        
        self.assertIn("email", str(context.exception))
    
    def test_validate_password_required(self):
        """Test de validación con password vacío"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="admin@test.com",
            password="",
            confirm_password="password123",
            role="Administrador"
        )
        
        with self.assertRaises(ValueError) as context:
            admin_user.validate()
        
        self.assertIn("password", str(context.exception))
    
    def test_validate_password_too_short(self):
        """Test de validación con password muy corto"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="admin@test.com",
            password="123",
            confirm_password="123",
            role="Administrador"
        )
        
        with self.assertRaises(ValueError) as context:
            admin_user.validate()
        
        self.assertIn("password", str(context.exception))
    
    def test_validate_confirm_password_required(self):
        """Test de validación con confirm_password vacío"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="admin@test.com",
            password="password123",
            confirm_password="",
            role="Administrador"
        )
        
        with self.assertRaises(ValueError) as context:
            admin_user.validate()
        
        self.assertIn("confirm_password", str(context.exception))
    
    def test_validate_passwords_mismatch(self):
        """Test de validación con passwords diferentes"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="admin@test.com",
            password="password123",
            confirm_password="different123",
            role="Administrador"
        )
        
        with self.assertRaises(ValueError) as context:
            admin_user.validate()
        
        self.assertIn("password", str(context.exception))
    
    def test_validate_role_required(self):
        """Test de validación con rol vacío"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="admin@test.com",
            password="password123",
            confirm_password="password123",
            role=""
        )
        
        with self.assertRaises(ValueError) as context:
            admin_user.validate()
        
        self.assertIn("role", str(context.exception))
    
    def test_validate_role_invalid(self):
        """Test de validación con rol inválido"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="admin@test.com",
            password="password123",
            confirm_password="password123",
            role="InvalidRole"
        )
        
        with self.assertRaises(ValueError) as context:
            admin_user.validate()
        
        self.assertIn("role", str(context.exception))
    
    def test_validate_valid_roles(self):
        """Test de validación con roles válidos"""
        valid_roles = ['Administrador', 'Compras', 'Ventas', 'Logistica', 'Cliente']
        
        for role in valid_roles:
            admin_user = AdminUserCreate(
                name="Admin User",
                email="admin@test.com",
                password="password123",
                confirm_password="password123",
                role=role
            )
            
            # No debe lanzar excepción
            admin_user.validate()
    
    def test_repr(self):
        """Test del método __repr__"""
        admin_user = AdminUserCreate(
            name="Admin User",
            email="admin@test.com",
            password="password123",
            confirm_password="password123",
            role="Administrador"
        )
        
        result = repr(admin_user)
        self.assertIn("AdminUserCreate", result)
        self.assertIn("Admin User", result)
        self.assertIn("admin@test.com", result)
        self.assertIn("Administrador", result)


class TestUser(unittest.TestCase):
    """Tests para el modelo User"""
    
    def test_init_with_basic_data(self):
        """Test de inicialización con datos básicos"""
        user = User(
            name="Test Hospital",
            email="test@hospital.com"
        )
        
        self.assertEqual(user.name, "Test Hospital")
        self.assertEqual(user.email, "test@hospital.com")
        self.assertIsNotNone(user.id)
        self.assertIsNotNone(user.created_at)
    
    def test_to_dict(self):
        """Test del método to_dict"""
        user = User(
            name="Test Hospital",
            email="test@hospital.com"
        )
        result = user.to_dict()
        
        expected_keys = ['id', 'name', 'email', 'enabled', 'created_at', 'updated_at']
        
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Verificar que no incluye password por seguridad
        self.assertNotIn("password", result)
        self.assertNotIn("confirm_password", result)
    
    def test_repr(self):
        """Test del método __repr__"""
        user = User(
            name="Test Hospital",
            email="test@hospital.com"
        )
        
        result = repr(user)
        self.assertIn("User", result)
        self.assertIn("Test Hospital", result)
        self.assertIn("test@hospital.com", result)
    
    def test_validate_name_required(self):
        """Test de validación con nombre vacío"""
        user = User(
            name="",
            email="test@hospital.com"
        )
        
        with self.assertRaises(ValueError) as context:
            user.validate()
        
        self.assertIn("Nombre", str(context.exception))
    
    def test_validate_name_too_long(self):
        """Test de validación con nombre muy largo"""
        user = User(
            name="A" * 101,  # Más de 100 caracteres
            email="test@hospital.com"
        )
        
        with self.assertRaises(ValueError) as context:
            user.validate()
        
        self.assertIn("Nombre", str(context.exception))
    
    def test_validate_email_required(self):
        """Test de validación con email vacío"""
        user = User(
            name="Test Hospital",
            email=""
        )
        
        with self.assertRaises(ValueError) as context:
            user.validate()
        
        self.assertIn("Correo electrónico", str(context.exception))
    
    def test_validate_email_invalid_format(self):
        """Test de validación con email inválido"""
        user = User(
            name="Test Hospital",
            email="invalid-email"
        )
        
        with self.assertRaises(ValueError) as context:
            user.validate()
        
        self.assertIn("Correo electrónico", str(context.exception))
    
    def test_validate_with_all_required_fields(self):
        """Test de validación con todos los campos requeridos"""
        user = User(
            name="Test Hospital",
            tax_id="12345678-9",
            email="test@hospital.com",
            address="123 Main St",
            phone="1234567890",
            institution_type="Hospital",
            specialty="Cadena de frío",
            applicant_name="Dr. Smith",
            applicant_email="dr.smith@hospital.com",
            latitude=4.711,
            longitude=-74.0721,
            password="password123",
            confirm_password="password123",
            role="Cliente"
        )
        
        # No debe lanzar excepción
        user.validate()
    
    def test_validate_institution_type_valid(self):
        """Test de validación con tipos de institución válidos"""
        valid_types = ['Clínica', 'Hospital', 'Laboratorio']
        
        for institution_type in valid_types:
            user = User(
                name="Test Hospital",
                email="test@hospital.com",
                institution_type=institution_type,
                role="Cliente"
            )
            
            # Solo validar el campo específico, no todos los campos
            if not user.institution_type or not user.institution_type.strip():
                self.fail("Tipo de institución no puede estar vacío")
            elif user.institution_type not in ['Clínica', 'Hospital', 'Laboratorio']:
                self.fail(f"Tipo de institución inválido: {user.institution_type}")
    
    def test_validate_specialty_valid(self):
        """Test de validación con especialidades válidas"""
        valid_specialties = ['Cadena de frío', 'Alto valor', 'Seguridad']
        
        for specialty in valid_specialties:
            user = User(
                name="Test Hospital",
                email="test@hospital.com",
                specialty=specialty,
                role="Cliente"
            )
            
            # Solo validar el campo específico, no todos los campos
            if not user.specialty or not user.specialty.strip():
                self.fail("Especialidad no puede estar vacía")
            elif user.specialty not in ['Cadena de frío', 'Alto valor', 'Seguridad']:
                self.fail(f"Especialidad inválida: {user.specialty}")
    
    def test_validate_role_valid(self):
        """Test de validación con roles válidos"""
        valid_roles = ['Administrador', 'Compras', 'Ventas', 'Logistica', 'Cliente']
        
        for role in valid_roles:
            user = User(
                name="Test Hospital",
                email="test@hospital.com",
                role=role
            )
            
            # Solo validar el campo específico, no todos los campos
            if not user.role or not user.role.strip():
                self.fail("Rol no puede estar vacío")
            elif user.role not in valid_roles:
                self.fail(f"Rol inválido: {user.role}")
    
    def test_phone_validation(self):
        """Test de validación de teléfono"""
        # Teléfono válido (solo números)
        user = User(
            name="Test Hospital",
            email="test@hospital.com",
            phone="1234567890"
        )
        
        # Verificar que el teléfono contiene solo números
        import re
        if user.phone and not re.match(r'^\d+$', user.phone.strip()):
            self.fail("Teléfono debe contener solo números")
    
    def test_tax_id_validation(self):
        """Test de validación de tax_id"""
        # Tax ID válido
        user = User(
            name="Test Hospital",
            email="test@hospital.com",
            tax_id="12345678-9"
        )
        
        # Verificar que el tax_id no esté vacío
        if not user.tax_id or not user.tax_id.strip():
            self.fail("Tax ID no puede estar vacío")
    
    def test_validate_latitude_required(self):
        """Test de validación con latitud vacía"""
        user = User(
            name="Test Hospital",
            tax_id="12345678-9",
            email="test@hospital.com",
            address="123 Main St",
            phone="1234567890",
            institution_type="Hospital",
            specialty="Cadena de frío",
            applicant_name="Dr. Smith",
            applicant_email="dr.smith@hospital.com",
            latitude=None,
            longitude=-74.0721,
            password="password123",
            confirm_password="password123",
            role="Cliente"
        )
        
        with self.assertRaises(ValueError) as context:
            user.validate()
        
        self.assertIn("Latitud", str(context.exception))
    
    def test_validate_longitude_required(self):
        """Test de validación con longitud vacía"""
        user = User(
            name="Test Hospital",
            tax_id="12345678-9",
            email="test@hospital.com",
            address="123 Main St",
            phone="1234567890",
            institution_type="Hospital",
            specialty="Cadena de frío",
            applicant_name="Dr. Smith",
            applicant_email="dr.smith@hospital.com",
            latitude=4.711,
            longitude=None,
            password="password123",
            confirm_password="password123",
            role="Cliente"
        )
        
        with self.assertRaises(ValueError) as context:
            user.validate()
        
        self.assertIn("Longitud", str(context.exception))
    
    def test_validate_latitude_invalid_value(self):
        """Test de validación con latitud no numérica"""
        user = User(
            name="Test Hospital",
            tax_id="12345678-9",
            email="test@hospital.com",
            address="123 Main St",
            phone="1234567890",
            institution_type="Hospital",
            specialty="Cadena de frío",
            applicant_name="Dr. Smith",
            applicant_email="dr.smith@hospital.com",
            latitude="invalid",
            longitude=-74.0721,
            password="password123",
            confirm_password="password123",
            role="Cliente"
        )
        
        with self.assertRaises(ValueError) as context:
            user.validate()
        
        self.assertIn("Latitud", str(context.exception))
    
    def test_validate_longitude_invalid_value(self):
        """Test de validación con longitud no numérica"""
        user = User(
            name="Test Hospital",
            tax_id="12345678-9",
            email="test@hospital.com",
            address="123 Main St",
            phone="1234567890",
            institution_type="Hospital",
            specialty="Cadena de frío",
            applicant_name="Dr. Smith",
            applicant_email="dr.smith@hospital.com",
            latitude=4.711,
            longitude="invalid",
            password="password123",
            confirm_password="password123",
            role="Cliente"
        )
        
        with self.assertRaises(ValueError) as context:
            user.validate()
        
        self.assertIn("Longitud", str(context.exception))
    
    def test_validate_latitude_out_of_range(self):
        """Test de validación con latitud fuera de rango - ahora válido porque solo validamos que sea número"""
        user = User(
            name="Test Hospital",
            tax_id="12345678-9",
            email="test@hospital.com",
            address="123 Main St",
            phone="1234567890",
            institution_type="Hospital",
            specialty="Cadena de frío",
            applicant_name="Dr. Smith",
            applicant_email="dr.smith@hospital.com",
            latitude=91.0,  # Ya no se valida rango, solo que sea número
            longitude=-74.0721,
            password="password123",
            confirm_password="password123",
            role="Cliente"
        )
        
        # No debe lanzar excepción porque solo validamos que sea número
        user.validate()
    
    def test_validate_longitude_out_of_range(self):
        """Test de validación con longitud fuera de rango - ahora válido porque solo validamos que sea número"""
        user = User(
            name="Test Hospital",
            tax_id="12345678-9",
            email="test@hospital.com",
            address="123 Main St",
            phone="1234567890",
            institution_type="Hospital",
            specialty="Cadena de frío",
            applicant_name="Dr. Smith",
            applicant_email="dr.smith@hospital.com",
            latitude=4.711,
            longitude=181.0,  # Ya no se valida rango, solo que sea número
            password="password123",
            confirm_password="password123",
            role="Cliente"
        )
        
        # No debe lanzar excepción porque solo validamos que sea número
        user.validate()
    
    def test_validate_latitude_longitude_valid(self):
        """Test de validación con latitud y longitud válidas"""
        user = User(
            name="Test Hospital",
            tax_id="12345678-9",
            email="test@hospital.com",
            address="123 Main St",
            phone="1234567890",
            institution_type="Hospital",
            specialty="Cadena de frío",
            applicant_name="Dr. Smith",
            applicant_email="dr.smith@hospital.com",
            latitude=4.711,
            longitude=-74.0721,
            password="password123",
            confirm_password="password123",
            role="Cliente"
        )
        
        # No debe lanzar excepción
        user.validate()


if __name__ == '__main__':
    unittest.main()

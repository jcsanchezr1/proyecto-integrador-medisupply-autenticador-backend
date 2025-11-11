"""
Servicio de Autenticación - Lógica de negocio para autenticación
"""
from typing import Dict, Any, Tuple, Optional
from ..repositories.user_repository import UserRepository
from ..external.keycloak_client import KeycloakClient
from ..models.auth_model import AuthCredentials, AuthResponse
from ..exceptions.custom_exceptions import ValidationError, BusinessLogicError


class AuthService:
    """Servicio para operaciones de autenticación"""
    
    def __init__(self, user_repository=None, keycloak_client=None):
        self.user_repository = user_repository or UserRepository()
        self.keycloak_client = keycloak_client or KeycloakClient()
    
    def authenticate_user(self, user_email: str, password: str) -> Dict[str, Any]:
        """
        Autentica un usuario validando su existencia y credenciales con Keycloak
        
        Args:
            user_email: Email del usuario
            password: Contraseña del usuario
            
        Returns:
            Dict con la respuesta de Keycloak más información adicional del usuario
            
        Raises:
            ValidationError: Si los datos de entrada son inválidos
            BusinessLogicError: Si hay error en la lógica de negocio
        """
        # Crear modelo de credenciales y validar
        try:
            credentials = AuthCredentials(user=user_email, password=password)
            credentials.validate()
        except ValueError as e:
            raise ValidationError(str(e))
        
        # Verificar que el usuario existe en la base de datos
        user = self.user_repository.get_by_email(user_email)
        if not user:
            raise BusinessLogicError("Credenciales inválidas")
        
        # Verificar que el usuario esté habilitado
        if not user.enabled:
            raise BusinessLogicError("La cuenta no está habilitada. Contacte al administrador")
        
        # Autenticar con Keycloak
        auth_result = self.keycloak_client.authenticate_user(user_email, password)
        
        # Si hay error en la respuesta de Keycloak
        if 'error' in auth_result:
            raise BusinessLogicError(auth_result)
        
        # Obtener el rol del usuario desde Keycloak
        try:
            user_role = self.keycloak_client.get_user_role(user_email)
        except Exception:
            # Si hay error obteniendo el rol, usar "Cliente" por defecto
            user_role = "Cliente"
        
        # Crear modelo de respuesta y validar
        try:
            auth_response = AuthResponse(**auth_result)
            auth_response.validate()
            
            # Obtener el diccionario base de la respuesta
            response_dict = auth_response.to_dict()
            
            # Agregar información adicional del usuario
            response_dict.update({
                'email': user.email,
                'name': user.name,
                'role': user_role,
                'id': user.id
            })
            
            return response_dict
        except ValueError as e:
            raise BusinessLogicError(f"Error en la respuesta de autenticación: {str(e)}")
    
    def logout_user(self, refresh_token: str) -> Dict[str, Any]:
        """
        Cierra la sesión de un usuario invalidando el token en Keycloak
        
        Args:
            refresh_token: Token de refresh para invalidar
            
        Returns:
            Dict con la respuesta de Keycloak o error
            
        Raises:
            ValidationError: Si los datos de entrada son inválidos
            BusinessLogicError: Si hay error en la lógica de negocio
        """
        # Validar que el refresh_token no esté vacío
        if not refresh_token or not refresh_token.strip():
            raise ValidationError("El refresh_token es requerido")
        
        # Cerrar sesión con Keycloak
        logout_result = self.keycloak_client.logout_user(refresh_token.strip())
        
        # Si hay error en la respuesta de Keycloak
        if 'error' in logout_result:
            raise BusinessLogicError(logout_result)
        
        # Retornar la respuesta de Keycloak
        return logout_result
    

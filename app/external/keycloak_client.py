"""
Cliente para integración con Keycloak - Servicios de autenticación y gestión de usuarios
"""
import requests
import json
import os
from typing import Dict, Any, Optional
from ..exceptions.custom_exceptions import BusinessLogicError


class KeycloakClient:
    """Cliente para interactuar con Keycloak"""
    
    def __init__(self):
        self.base_url = os.getenv('KC_BASE_URL', 'http://localhost:8080')
        self.admin_user = os.getenv('KC_ADMIN_USER', 'admin')
        self.admin_pass = os.getenv('KC_ADMIN_PASS', 'admin')
        self.realm = 'medisupply-realm'
        self._admin_token = None
        self._token_expires_at = None
    
    def _get_admin_token(self) -> str:
        """Obtiene el token de administrador de Keycloak"""
        try:
            # Si ya tenemos un token válido, lo retornamos
            if self._admin_token and self._token_expires_at:
                import time
                if time.time() < self._token_expires_at:
                    return self._admin_token
            
            # Solicitar nuevo token
            url = f"{self.base_url}/realms/master/protocol/openid-connect/token"
            data = {
                'grant_type': 'password',
                'client_id': 'admin-cli',
                'username': self.admin_user,
                'password': self.admin_pass
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self._admin_token = token_data['access_token']
            
            # Calcular tiempo de expiración (restar 60 segundos para margen)
            expires_in = token_data.get('expires_in', 3600)
            import time
            self._token_expires_at = time.time() + expires_in - 60
            
            return self._admin_token
            
        except requests.exceptions.RequestException as e:
            raise BusinessLogicError(f"Error al obtener token de Keycloak: {str(e)}")
        except Exception as e:
            raise BusinessLogicError(f"Error inesperado al obtener token de Keycloak: {str(e)}")
    
    def create_user(self, email: str, password: str, institution_name: str) -> str:
        """Crea un usuario en Keycloak"""
        try:
            token = self._get_admin_token()
            url = f"{self.base_url}/admin/realms/{self.realm}/users"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            user_data = {
                "username": email,
                "email": email,
                "firstName": institution_name,
                "enabled": True,
                "emailVerified": True,
                "credentials": [
                    {
                        "type": "password",
                        "value": password,
                        "temporary": False
                    }
                ]
            }
            
            response = requests.post(url, json=user_data, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Obtener el ID del usuario creado desde el header Location
            location_header = response.headers.get('Location')
            if location_header:
                # Extraer el ID del usuario de la URL
                user_id = location_header.split('/')[-1]
                return user_id
            else:
                raise BusinessLogicError("No se pudo obtener el ID del usuario creado")
                
        except requests.exceptions.RequestException as e:
            raise BusinessLogicError(f"Error al crear usuario en Keycloak: {str(e)}")
        except Exception as e:
            raise BusinessLogicError(f"Error inesperado al crear usuario en Keycloak: {str(e)}")
    
    def assign_role_to_user(self, user_id: str, role_name: str) -> None:
        """Asigna un rol a un usuario en Keycloak"""
        try:
            token = self._get_admin_token()
            url = f"{self.base_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/realm"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            # Mapeo de roles según medisupply-realm-realm.json
            role_mapping = {
                "Administrador": {
                    "id": "7f3a2d1e-6b0b-4f32-9c96-6a2a2b5f5a11",
                    "name": "Administrador",
                    "description": "Rol administrador del realm para la app Medisupply",
                    "composite": False,
                    "clientRole": False,
                    "containerId": "medisupply-realm"
                },
                "Compras": {
                    "id": "2b1c5e42-9d3a-4a0f-8f3c-3c7e6f2a1b22",
                    "name": "Compras",
                    "description": "Rol departamento de compras del realm para la app Medisupply",
                    "composite": False,
                    "clientRole": False,
                    "containerId": "medisupply-realm"
                },
                "Ventas": {
                    "id": "a6e5c3b1-2d4f-4c7a-9b8e-1f2a3d4e5f33",
                    "name": "Ventas",
                    "description": "Rol gerente de cuenta / vendedor del realm para la app Medisupply",
                    "composite": False,
                    "clientRole": False,
                    "containerId": "medisupply-realm"
                },
                "Logistica": {
                    "id": "c4d3e2f1-a5b6-4c7d-8e9f-0a1b2c3d4e44",
                    "name": "Logistica",
                    "description": "Rol personal logístico del realm para la app Medisupply",
                    "composite": False,
                    "clientRole": False,
                    "containerId": "medisupply-realm"
                },
                "Cliente": {
                    "id": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a55",
                    "name": "Cliente",
                    "description": "Rol cliente institucional del realm para la app Medisupply",
                    "composite": False,
                    "clientRole": False,
                    "containerId": "medisupply-realm"
                }
            }
            
            if role_name not in role_mapping:
                raise BusinessLogicError(f"Rol '{role_name}' no válido. Roles disponibles: {', '.join(role_mapping.keys())}")
            
            role_data = [role_mapping[role_name]]
            
            response = requests.post(url, json=role_data, headers=headers, timeout=30)
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise BusinessLogicError(f"Error al asignar rol en Keycloak: {str(e)}")
        except Exception as e:
            raise BusinessLogicError(f"Error inesperado al asignar rol en Keycloak: {str(e)}")
    
    def delete_user(self, user_id: str) -> None:
        """Elimina un usuario de Keycloak"""
        try:
            token = self._get_admin_token()
            url = f"{self.base_url}/admin/realms/{self.realm}/users/{user_id}"
            
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.delete(url, headers=headers, timeout=30)
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise BusinessLogicError(f"Error al eliminar usuario de Keycloak: {str(e)}")
        except Exception as e:
            raise BusinessLogicError(f"Error inesperado al eliminar usuario de Keycloak: {str(e)}")
    
    def get_available_roles(self) -> list:
        """Retorna la lista de roles disponibles en Keycloak"""
        return ["Administrador", "Compras", "Ventas", "Logistica", "Cliente"]

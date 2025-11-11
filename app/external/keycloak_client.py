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
    
    def create_user(self, email: str, password: str, name: str) -> str:
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
                "firstName": name,
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
    
    def get_user_role(self, email: str) -> str:
        """Obtiene el rol de un usuario por email"""
        try:
            token = self._get_admin_token()

            search_url = f"{self.base_url}/admin/realms/{self.realm}/users"
            headers = {
                'Authorization': f'Bearer {token}'
            }
            params = {
                'email': email,
                'exact': 'true'
            }
            
            response = requests.get(search_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            users = response.json()
            if not users:
                return "Cliente"
            
            user_id = users[0]['id']

            roles_url = f"{self.base_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/realm"
            roles_response = requests.get(roles_url, headers=headers, timeout=30)
            roles_response.raise_for_status()
            
            roles = roles_response.json()
            if roles:
                # Filtrar roles específicos de la aplicación, ignorando el rol por defecto
                app_roles = ["Administrador", "Compras", "Ventas", "Logistica", "Cliente"]
                for role in roles:
                    if role['name'] in app_roles:
                        return role['name']

                return roles[0]['name']
            
            return "Cliente"
            
        except requests.exceptions.RequestException as e:
            return "Cliente"
        except Exception as e:
            return "Cliente"
    
    def get_users_by_role(self, role_name: str) -> list:
        """
        Obtiene la lista de emails de usuarios que tienen un rol específico en Keycloak.
        Esto es más eficiente que obtener el rol de cada usuario individualmente.
        
        Args:
            role_name: Nombre del rol a buscar
            
        Returns:
            Lista de emails de usuarios con ese rol
        """
        try:
            token = self._get_admin_token()
            
            # Mapeo de nombres de roles a nombres exactos en Keycloak
            role_name_mapping = {
                "Administrador": "Administrador",
                "Compras": "Compras",
                "Ventas": "Ventas",
                "Logistica": "Logistica",
                "Cliente": "Cliente"
            }
            
            # Normalizar el nombre del rol
            normalized_role = role_name_mapping.get(role_name, role_name)
            
            # Obtener usuarios con ese rol usando la API de Keycloak
            url = f"{self.base_url}/admin/realms/{self.realm}/roles/{normalized_role}/users"
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            # Keycloak puede paginar los resultados, así que necesitamos obtener todos
            all_users = []
            first = 0
            max_results = 100  # Keycloak permite hasta 100 por defecto
            
            while True:
                params = {
                    'first': first,
                    'max': max_results
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                
                users = response.json()
                if not users:
                    break
                
                # Extraer emails de los usuarios
                for user in users:
                    if 'email' in user and user['email']:
                        all_users.append(user['email'])
                
                # Si obtenemos menos resultados que el máximo, significa que ya obtuvimos todos
                if len(users) < max_results:
                    break
                
                first += max_results
            
            return all_users
            
        except requests.exceptions.RequestException as e:
            # Si hay error, retornar lista vacía para que el sistema pueda continuar
            # pero sin el filtro de rol optimizado
            return []
        except Exception as e:
            return []
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Autentica un usuario con Keycloak y retorna el token"""
        try:
            url = f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/token"
            
            data = {
                'grant_type': 'password',
                'client_id': 'medisupply-app',
                'username': username,
                'password': password
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=30)
            
            # Si la respuesta es exitosa, retornar el JSON
            if response.status_code == 200:
                return response.json()
            
            # Si hay error, retornar el error de Keycloak
            try:
                error_data = response.json()
                return error_data
            except:
                # Si no se puede parsear el JSON, crear un error genérico
                return {
                    "error": "authentication_failed",
                    "error_description": "Error de autenticación"
                }
                
        except requests.exceptions.RequestException as e:
            raise BusinessLogicError(f"Error al autenticar con Keycloak: {str(e)}")
        except Exception as e:
            raise BusinessLogicError(f"Error inesperado al autenticar con Keycloak: {str(e)}")
    
    def logout_user(self, refresh_token: str) -> Dict[str, Any]:
        """Cierra la sesión de un usuario invalidando el token en Keycloak"""
        try:
            url = f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/logout"
            
            data = {
                'client_id': 'medisupply-app',
                'refresh_token': refresh_token
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=30)
            
            # Si la respuesta es exitosa (200 o 204), retornar éxito
            if response.status_code in [200, 204]:
                return {"message": "Logout successful"}
            
            # Si hay error, retornar el error de Keycloak
            try:
                error_data = response.json()
                return error_data
            except:
                # Si no se puede parsear el JSON, crear un error genérico
                return {
                    "error": "logout_failed",
                    "error_description": f"Error al cerrar sesión. Status: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            raise BusinessLogicError(f"Error al cerrar sesión con Keycloak: {str(e)}")
        except Exception as e:
            raise BusinessLogicError(f"Error inesperado al cerrar sesión con Keycloak: {str(e)}")
"""
Repositorio de Cliente Asignado - Implementación con SQLAlchemy
"""
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import uuid

from .base_repository import BaseRepository
from ..models.assigned_client_model import AssignedClient
from ..config.settings import Config

# Configuración de SQLAlchemy
Base = declarative_base()


class AssignedClientDB(Base):
    """Modelo de base de datos para clientes asignados"""
    __tablename__ = 'assigned_clients'
    
    id = Column(String(36), primary_key=True)
    seller_id = Column(String(36), nullable=False)
    client_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AssignedClientRepository(BaseRepository):
    """Repositorio para operaciones CRUD de clientes asignados"""
    
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        """Crea las tablas si no existen"""
        try:
            Base.metadata.create_all(bind=self.engine)
        except SQLAlchemyError as e:
            print(f"Error creando tablas: {e}")
    
    def _get_session(self) -> Session:
        """Obtiene una sesión de base de datos"""
        return self.SessionLocal()
    
    def _db_to_model(self, db_assigned_client: AssignedClientDB) -> AssignedClient:
        """Convierte un modelo de DB a modelo de dominio"""
        return AssignedClient(
            id=db_assigned_client.id,
            seller_id=db_assigned_client.seller_id,
            client_id=db_assigned_client.client_id,
            created_at=db_assigned_client.created_at,
            updated_at=db_assigned_client.updated_at
        )
    
    def _model_to_db(self, assigned_client: AssignedClient) -> AssignedClientDB:
        """Convierte un modelo de dominio a modelo de DB"""
        return AssignedClientDB(
            id=assigned_client.id,
            seller_id=assigned_client.seller_id,
            client_id=assigned_client.client_id,
            created_at=assigned_client.created_at,
            updated_at=assigned_client.updated_at
        )
    
    def create(self, **kwargs) -> AssignedClient:
        """Crea una nueva asignación de cliente"""
        session = self._get_session()
        try:
            # Crear modelo de dominio
            assigned_client = AssignedClient(**kwargs)
            assigned_client.validate()  # Validar antes de guardar
            
            # Verificar que la asignación no exista ya
            existing = session.query(AssignedClientDB).filter(
                AssignedClientDB.seller_id == assigned_client.seller_id,
                AssignedClientDB.client_id == assigned_client.client_id
            ).first()
            if existing:
                raise ValueError("Esta asignación vendedor-cliente ya existe")
            
            # Convertir a modelo de DB y guardar
            db_assigned_client = self._model_to_db(assigned_client)
            session.add(db_assigned_client)
            session.commit()
            session.refresh(db_assigned_client)
            
            return self._db_to_model(db_assigned_client)
            
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al crear asignación de cliente: {str(e)}")
        finally:
            session.close()
    
    def get_by_id(self, assigned_client_id: str) -> Optional[AssignedClient]:
        """Obtiene una asignación por ID"""
        session = self._get_session()
        try:
            db_assigned_client = session.query(AssignedClientDB).filter(
                AssignedClientDB.id == assigned_client_id
            ).first()
            if db_assigned_client:
                return self._db_to_model(db_assigned_client)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener asignación: {str(e)}")
        finally:
            session.close()
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[AssignedClient]:
        """Obtiene todas las asignaciones"""
        session = self._get_session()
        try:
            query = session.query(AssignedClientDB).order_by(AssignedClientDB.created_at.desc()).offset(offset)
            if limit:
                query = query.limit(limit)
            
            db_assigned_clients = query.all()
            return [self._db_to_model(db_ac) for db_ac in db_assigned_clients]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener asignaciones: {str(e)}")
        finally:
            session.close()
    
    def get_by_seller_id(self, seller_id: str) -> List[AssignedClient]:
        """Obtiene todas las asignaciones de un vendedor específico"""
        session = self._get_session()
        try:
            db_assigned_clients = session.query(AssignedClientDB).filter(
                AssignedClientDB.seller_id == seller_id
            ).order_by(AssignedClientDB.created_at.desc()).all()
            
            return [self._db_to_model(db_ac) for db_ac in db_assigned_clients]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener clientes asignados: {str(e)}")
        finally:
            session.close()
    
    def get_by_client_id(self, client_id: str) -> List[AssignedClient]:
        """Obtiene todas las asignaciones para un cliente específico"""
        session = self._get_session()
        try:
            db_assigned_clients = session.query(AssignedClientDB).filter(
                AssignedClientDB.client_id == client_id
            ).order_by(AssignedClientDB.created_at.desc()).all()
            
            return [self._db_to_model(db_ac) for db_ac in db_assigned_clients]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener vendedores asignados: {str(e)}")
        finally:
            session.close()
    
    def update(self, assigned_client_id: str, **kwargs) -> Optional[AssignedClient]:
        """Actualiza una asignación"""
        session = self._get_session()
        try:
            db_assigned_client = session.query(AssignedClientDB).filter(
                AssignedClientDB.id == assigned_client_id
            ).first()
            if not db_assigned_client:
                return None
            
            # Actualizar campos
            for key, value in kwargs.items():
                if hasattr(db_assigned_client, key):
                    setattr(db_assigned_client, key, value)
            
            db_assigned_client.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(db_assigned_client)
            
            return self._db_to_model(db_assigned_client)
            
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al actualizar asignación: {str(e)}")
        finally:
            session.close()
    
    def delete(self, assigned_client_id: str) -> bool:
        """Elimina una asignación"""
        session = self._get_session()
        try:
            db_assigned_client = session.query(AssignedClientDB).filter(
                AssignedClientDB.id == assigned_client_id
            ).first()
            if not db_assigned_client:
                return False
            
            session.delete(db_assigned_client)
            session.commit()
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al eliminar asignación: {str(e)}")
        finally:
            session.close()
    
    def exists(self, assigned_client_id: str) -> bool:
        """Verifica si una asignación existe"""
        session = self._get_session()
        try:
            db_assigned_client = session.query(AssignedClientDB).filter(
                AssignedClientDB.id == assigned_client_id
            ).first()
            return db_assigned_client is not None
        except SQLAlchemyError as e:
            raise Exception(f"Error al verificar existencia de asignación: {str(e)}")
        finally:
            session.close()
    
    def exists_assignment(self, seller_id: str, client_id: str) -> bool:
        """Verifica si existe una asignación específica vendedor-cliente"""
        session = self._get_session()
        try:
            db_assigned_client = session.query(AssignedClientDB).filter(
                AssignedClientDB.seller_id == seller_id,
                AssignedClientDB.client_id == client_id
            ).first()
            return db_assigned_client is not None
        except SQLAlchemyError as e:
            raise Exception(f"Error al verificar existencia de asignación: {str(e)}")
        finally:
            session.close()


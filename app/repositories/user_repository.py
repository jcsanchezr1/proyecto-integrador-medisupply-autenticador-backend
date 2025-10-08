"""
Repositorio de Usuario - Implementación con SQLAlchemy
"""
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid

from .base_repository import BaseRepository
from ..models.user_model import User
from ..config.settings import Config

# Configuración de SQLAlchemy
Base = declarative_base()


class UserDB(Base):
    """Modelo de base de datos para usuarios"""
    __tablename__ = 'users_medisupply'
    
    id = Column(String(36), primary_key=True)
    institution_name = Column(String(100), nullable=False)
    tax_id = Column(String(50), nullable=True)
    email = Column(String(100), nullable=False, unique=True)
    address = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    institution_type = Column(String(20), nullable=True)
    logo_filename = Column(String(255), nullable=True)
    logo_url = Column(Text, nullable=True)
    specialty = Column(String(20), nullable=True)
    applicant_name = Column(String(80), nullable=True)
    applicant_email = Column(String(100), nullable=True)
    enabled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserRepository(BaseRepository):
    """Repositorio para operaciones CRUD de usuarios"""
    
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
    
    def _db_to_model(self, db_user: UserDB) -> User:
        """Convierte un modelo de DB a modelo de dominio"""
        return User(
            id=db_user.id,
            institution_name=db_user.institution_name,
            tax_id=db_user.tax_id,
            email=db_user.email,
            address=db_user.address,
            phone=db_user.phone,
            institution_type=db_user.institution_type,
            logo_filename=db_user.logo_filename,
            logo_url=db_user.logo_url,
            specialty=db_user.specialty,
            applicant_name=db_user.applicant_name,
            applicant_email=db_user.applicant_email,
            enabled=db_user.enabled,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    def _model_to_db(self, user: User) -> UserDB:
        """Convierte un modelo de dominio a modelo de DB"""
        return UserDB(
            id=user.id,
            institution_name=user.institution_name,
            tax_id=user.tax_id,
            email=user.email,
            address=user.address,
            phone=user.phone,
            institution_type=user.institution_type,
            logo_filename=user.logo_filename,
            logo_url=user.logo_url,
            specialty=user.specialty,
            applicant_name=user.applicant_name,
            applicant_email=user.applicant_email,
            enabled=user.enabled,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    def create(self, **kwargs) -> User:
        """Crea un nuevo usuario"""
        session = self._get_session()
        try:
            # Crear modelo de dominio
            user = User(**kwargs)
            user.validate()  # Validar antes de guardar
            
            # Verificar que el email no exista
            existing = session.query(UserDB).filter(UserDB.email == user.email).first()
            if existing:
                raise ValueError("Ya existe un usuario con este correo electrónico")
            
            # Convertir a modelo de DB y guardar
            db_user = self._model_to_db(user)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            
            return self._db_to_model(db_user)
            
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al crear usuario: {str(e)}")
        finally:
            session.close()
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Obtiene un usuario por ID"""
        session = self._get_session()
        try:
            db_user = session.query(UserDB).filter(UserDB.id == user_id).first()
            if db_user:
                return self._db_to_model(db_user)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener usuario: {str(e)}")
        finally:
            session.close()
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[User]:
        """Obtiene todos los usuarios ordenados por nombre de institución"""
        session = self._get_session()
        try:
            query = session.query(UserDB).order_by(UserDB.institution_name.asc()).offset(offset)
            if limit:
                query = query.limit(limit)
            
            db_users = query.all()
            return [self._db_to_model(db_user) for db_user in db_users]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener usuarios: {str(e)}")
        finally:
            session.close()
    
    def update(self, user_id: str, **kwargs) -> Optional[User]:
        """Actualiza un usuario"""
        session = self._get_session()
        try:
            db_user = session.query(UserDB).filter(UserDB.id == user_id).first()
            if not db_user:
                return None
            
            # Actualizar campos
            for key, value in kwargs.items():
                if hasattr(db_user, key):
                    setattr(db_user, key, value)
            
            db_user.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(db_user)
            
            return self._db_to_model(db_user)
            
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al actualizar usuario: {str(e)}")
        finally:
            session.close()
    
    def delete(self, user_id: str) -> bool:
        """Elimina un usuario"""
        session = self._get_session()
        try:
            db_user = session.query(UserDB).filter(UserDB.id == user_id).first()
            if not db_user:
                return False
            
            session.delete(db_user)
            session.commit()
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al eliminar usuario: {str(e)}")
        finally:
            session.close()
    
    def exists(self, user_id: str) -> bool:
        """Verifica si un usuario existe"""
        session = self._get_session()
        try:
            db_user = session.query(UserDB).filter(UserDB.id == user_id).first()
            return db_user is not None
        except SQLAlchemyError as e:
            raise Exception(f"Error al verificar existencia de usuario: {str(e)}")
        finally:
            session.close()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        session = self._get_session()
        try:
            db_user = session.query(UserDB).filter(UserDB.email == email).first()
            if db_user:
                return self._db_to_model(db_user)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener usuario por email: {str(e)}")
        finally:
            session.close()
    
    def count_all(self) -> int:
        """Cuenta el total de usuarios"""
        session = self._get_session()
        try:
            return session.query(UserDB).count()
        except SQLAlchemyError as e:
            raise Exception(f"Error al contar usuarios: {str(e)}")
        finally:
            session.close()
    
    def delete_all(self) -> int:
        """Elimina todos los usuarios de la base de datos"""
        session = self._get_session()
        try:
            # Contar registros antes de eliminar
            count = session.query(UserDB).count()
            
            # Eliminar todos los registros
            session.query(UserDB).delete()
            session.commit()
            
            return count
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al eliminar todos los usuarios: {str(e)}")
        finally:
            session.close()
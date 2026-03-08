"""
Kudos System - Task 2
PostgreSQL Version - FIXED
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    department = Column(String(50))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    sent_kudos = relationship("Kudos", foreign_keys="Kudos.sender_id", back_populates="sender")
    received_kudos = relationship("Kudos", foreign_keys="Kudos.receiver_id", back_populates="receiver")
    moderation_actions = relationship("ModerationLog", back_populates="moderator")

class Kudos(Base):
    __tablename__ = 'kudos'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_visible = Column(Boolean, default=True)
    moderated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    moderation_reason = Column(String(200), nullable=True)
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_kudos")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_kudos")
    moderator = relationship("User", foreign_keys=[moderated_by])

class ModerationLog(Base):
    __tablename__ = 'moderation_log'
    
    id = Column(Integer, primary_key=True)
    kudos_id = Column(Integer, ForeignKey('kudos.id'), nullable=False)
    moderator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(20), nullable=False)
    reason = Column(String(200))
    created_at = Column(DateTime, default=func.now())
    
    kudos = relationship("Kudos")
    moderator = relationship("User", back_populates="moderation_actions")

class KudosSystem:
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kudos_db')
        
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
        self.engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False
        )
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        self.Session = sessionmaker(bind=self.engine)
        logger.info("KudosSystem initialized")
    
    def get_session(self):
        return self.Session()
    
    def create_user(self, username, email, full_name, department=None, is_admin=False):
        session = self.get_session()
        try:
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                department=department,
                is_admin=is_admin
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def send_kudos(self, sender_id, receiver_id, message):
        if len(message) > 500:
            raise ValueError("Message too long (max 500 characters)")
        
        if sender_id == receiver_id:
            raise ValueError("Cannot send kudos to yourself")
        
        session = self.get_session()
        try:
            kudos = Kudos(
                sender_id=sender_id,
                receiver_id=receiver_id,
                message=message.strip(),
                is_visible=True
            )
            session.add(kudos)
            session.commit()
            session.refresh(kudos)
            return kudos
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_users_list(self):
        session = self.get_session()
        try:
            users = session.query(User).order_by(User.full_name).all()
            return [
                {
                    'id': u.id,
                    'full_name': u.full_name,
                    'email': u.email,
                    'department': u.department,
                    'is_admin': u.is_admin
                }
                for u in users
            ]
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
        finally:
            session.close()
    
    def get_public_feed(self, limit=50):
        session = self.get_session()
        try:
            kudos_list = session.query(Kudos).filter(
                Kudos.is_visible == True
            ).order_by(
                Kudos.created_at.desc()
            ).limit(limit).all()
            
            result = []
            for k in kudos_list:
                result.append({
                    'id': k.id,
                    'sender': k.sender.full_name if k.sender else 'Unknown',
                    'receiver': k.receiver.full_name if k.receiver else 'Unknown',
                    'message': k.message,
                    'created_at': k.created_at.isoformat() if k.created_at else '',
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching feed: {e}")
            return []
        finally:
            session.close()
    
    def moderate_kudos(self, kudos_id, moderator_id, action, reason=None):
        session = self.get_session()
        try:
            kudos = session.query(Kudos).filter(Kudos.id == kudos_id).first()
            moderator = session.query(User).filter(User.id == moderator_id).first()
            
            if not kudos:
                raise ValueError(f"Kudos {kudos_id} not found")
            
            if not moderator or not moderator.is_admin:
                raise PermissionError("Not authorized")
            
            if action == 'hide':
                kudos.is_visible = False
                kudos.moderated_by = moderator_id
                kudos.moderated_at = datetime.now()
                kudos.moderation_reason = reason
            elif action == 'delete':
                session.delete(kudos)
            elif action == 'restore':
                kudos.is_visible = True
                kudos.moderated_by = moderator_id
                kudos.moderated_at = datetime.now()
                kudos.moderation_reason = reason
            
            # Log moderation
            log = ModerationLog(
                kudos_id=kudos_id,
                moderator_id=moderator_id,
                action=action,
                reason=reason
            )
            session.add(log)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
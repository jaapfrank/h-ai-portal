"""
SQLAlchemy models voor user context en memory management
Ondersteunt Letta memory integratie en Entra ID authenticatie
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import json

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, 
    Boolean, JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class UserContext(Base):
    """
    Hoofd user context model
    Slaat gebruikersinformatie op gekoppeld aan Entra ID en Letta agents
    """
    __tablename__ = "user_contexts"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Entra ID (Azure AD) identifiers
    azure_object_id = Column(String(255), unique=True, nullable=False, index=True)
    azure_user_principal_name = Column(String(255), unique=True, nullable=False)
    
    # User profile information
    display_name = Column(String(255), nullable=False)
    given_name = Column(String(255))
    surname = Column(String(255))
    email = Column(String(255), nullable=False, index=True)
    department = Column(String(255))
    job_title = Column(String(255))
    manager_id = Column(String(255))  # Azure Object ID van manager
    
    # Letta agent integration
    letta_agent_id = Column(String(255), unique=True, index=True)
    agent_created_at = Column(DateTime(timezone=True))
    agent_last_interaction = Column(DateTime(timezone=True))
    
    # System timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True))
    
    # Status and permissions
    is_active = Column(Boolean, default=True)
    access_level = Column(String(50), default="user")  # user, admin, manager, readonly
    
    # JSON fields voor flexibele data
    azure_claims = Column(JSON)  # Claims van Azure AD token
    custom_attributes = Column(JSON)  # Aangepaste attributen
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserContext(azure_object_id='{self.azure_object_id}', email='{self.email}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert naar dictionary voor JSON responses"""
        return {
            "id": self.id,
            "azure_object_id": self.azure_object_id,
            "azure_user_principal_name": self.azure_user_principal_name,
            "display_name": self.display_name,
            "given_name": self.given_name,
            "surname": self.surname,
            "email": self.email,
            "department": self.department,
            "job_title": self.job_title,
            "manager_id": self.manager_id,
            "letta_agent_id": self.letta_agent_id,
            "agent_created_at": self.agent_created_at.isoformat() if self.agent_created_at else None,
            "agent_last_interaction": self.agent_last_interaction.isoformat() if self.agent_last_interaction else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
            "access_level": self.access_level,
            "azure_claims": self.azure_claims,
            "custom_attributes": self.custom_attributes
        }
    
    def get_user_profile_for_letta(self) -> Dict[str, Any]:
        """Format user profile voor Letta memory agent"""
        return {
            "user_id": self.azure_object_id,
            "name": self.display_name,
            "email": self.email,
            "role": self.job_title or "Medewerker",
            "department": self.department,
            "manager": self.manager_id,
            "access_level": self.access_level,
            "preferences": self.preferences.to_dict() if self.preferences else {}
        }


class UserSession(Base):
    """
    User sessie tracking voor audit en analytics
    """
    __tablename__ = "user_sessions"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Foreign key naar user
    user_id = Column(Integer, ForeignKey("user_contexts.id"), nullable=False)
    
    # Session details
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True))
    last_activity = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Session metadata
    ip_address = Column(String(45))  # Ondersteunt IPv6
    user_agent = Column(Text)
    device_type = Column(String(50))  # desktop, mobile, tablet
    browser = Column(String(100))
    
    # Activity counters
    message_count = Column(Integer, default=0)
    query_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # JSON fields
    session_data = Column(JSON)  # Flexibele session data
    
    # Relationships
    user = relationship("UserContext", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(session_id='{self.session_id}', user_id={self.user_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert naar dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "last_activity": self.last_activity.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device_type": self.device_type,
            "browser": self.browser,
            "message_count": self.message_count,
            "query_count": self.query_count,
            "error_count": self.error_count,
            "is_active": self.is_active,
            "session_data": self.session_data
        }


class UserPreferences(Base):
    """
    Gebruikersvoorkeuren voor personalisatie
    """
    __tablename__ = "user_preferences"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key naar user (one-to-one relationship)
    user_id = Column(Integer, ForeignKey("user_contexts.id"), nullable=False, unique=True)
    
    # Language and localization
    language = Column(String(10), default="nl-NL")
    timezone = Column(String(50), default="Europe/Amsterdam")
    date_format = Column(String(20), default="DD-MM-YYYY")
    number_format = Column(String(20), default="nl-NL")
    
    # Interface preferences
    theme = Column(String(20), default="light")  # light, dark, auto
    sidebar_collapsed = Column(Boolean, default=False)
    dashboard_layout = Column(String(20), default="grid")  # grid, list, compact
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    browser_notifications = Column(Boolean, default=True)
    notification_frequency = Column(String(20), default="immediate")  # immediate, hourly, daily, weekly
    
    # Data preferences
    default_database = Column(String(50))  # ridder_erp, hoeflon_bv, hoeflon_int
    preferred_chart_types = Column(JSON)  # Array van chart types
    dashboard_widgets = Column(JSON)  # Array van widget configuraties
    
    # Query preferences
    auto_execute_queries = Column(Boolean, default=False)
    query_timeout_seconds = Column(Integer, default=30)
    max_results_per_query = Column(Integer, default=1000)
    
    # Memory and AI preferences
    enable_memory = Column(Boolean, default=True)
    memory_retention_days = Column(Integer, default=30)
    ai_response_style = Column(String(20), default="professional")  # casual, professional, technical
    
    # Privacy preferences
    analytics_opt_in = Column(Boolean, default=True)
    data_sharing_opt_in = Column(Boolean, default=False)
    
    # System timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # JSON field voor custom preferences
    custom_preferences = Column(JSON)
    
    # Relationships
    user = relationship("UserContext", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id}, language='{self.language}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert naar dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "language": self.language,
            "timezone": self.timezone,
            "date_format": self.date_format,
            "number_format": self.number_format,
            "theme": self.theme,
            "sidebar_collapsed": self.sidebar_collapsed,
            "dashboard_layout": self.dashboard_layout,
            "email_notifications": self.email_notifications,
            "browser_notifications": self.browser_notifications,
            "notification_frequency": self.notification_frequency,
            "default_database": self.default_database,
            "preferred_chart_types": self.preferred_chart_types,
            "dashboard_widgets": self.dashboard_widgets,
            "auto_execute_queries": self.auto_execute_queries,
            "query_timeout_seconds": self.query_timeout_seconds,
            "max_results_per_query": self.max_results_per_query,
            "enable_memory": self.enable_memory,
            "memory_retention_days": self.memory_retention_days,
            "ai_response_style": self.ai_response_style,
            "analytics_opt_in": self.analytics_opt_in,
            "data_sharing_opt_in": self.data_sharing_opt_in,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "custom_preferences": self.custom_preferences
        }


# Database indexes voor performance
Index("idx_user_azure_object_id", UserContext.azure_object_id)
Index("idx_user_email", UserContext.email)
Index("idx_user_letta_agent", UserContext.letta_agent_id)
Index("idx_session_user_id", UserSession.user_id)
Index("idx_session_active", UserSession.is_active)
Index("idx_session_last_activity", UserSession.last_activity)


# Database helper functions
def create_user_from_azure_claims(claims: Dict[str, Any], session: Session) -> UserContext:
    """
    Creëer nieuwe user van Azure AD claims
    
    Args:
        claims: Azure AD JWT claims
        session: SQLAlchemy session
        
    Returns:
        UserContext object
    """
    user = UserContext(
        azure_object_id=claims.get("oid"),
        azure_user_principal_name=claims.get("upn"),
        display_name=claims.get("name"),
        given_name=claims.get("given_name"),
        surname=claims.get("family_name"),
        email=claims.get("email") or claims.get("preferred_username"),
        department=claims.get("department"),
        job_title=claims.get("jobTitle"),
        azure_claims=claims,
        last_login=datetime.now(timezone.utc)
    )
    
    # Creëer default preferences
    preferences = UserPreferences(user=user)
    
    session.add(user)
    session.add(preferences)
    session.commit()
    
    return user


def get_or_create_user_by_azure_id(azure_object_id: str, session: Session, claims: Dict[str, Any] = None) -> UserContext:
    """
    Verkrijg bestaande user of creëer nieuwe van Azure claims
    
    Args:
        azure_object_id: Azure AD Object ID
        session: SQLAlchemy session
        claims: Azure AD claims (voor nieuwe users)
        
    Returns:
        UserContext object
    """
    user = session.query(UserContext).filter_by(azure_object_id=azure_object_id).first()
    
    if user:
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        if claims:
            # Update claims en basic info
            user.azure_claims = claims
            user.display_name = claims.get("name", user.display_name)
            user.email = claims.get("email") or claims.get("preferred_username", user.email)
        session.commit()
        return user
    
    if not claims:
        raise ValueError("Claims required for new user creation")
    
    return create_user_from_azure_claims(claims, session)


def update_user_letta_agent(user_id: int, letta_agent_id: str, session: Session) -> bool:
    """
    Update Letta agent ID voor user
    
    Args:
        user_id: User ID
        letta_agent_id: Letta agent ID
        session: SQLAlchemy session
        
    Returns:
        Success status
    """
    try:
        user = session.query(UserContext).filter_by(id=user_id).first()
        if user:
            user.letta_agent_id = letta_agent_id
            user.agent_created_at = datetime.now(timezone.utc)
            user.agent_last_interaction = datetime.now(timezone.utc)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        return False
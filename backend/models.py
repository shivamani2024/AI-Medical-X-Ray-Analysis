# ============================================
# AI Medical Image Analysis
# Database Models
# ============================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from datetime import datetime

from .database import Base


# ============================================
# USER TABLE
# ============================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # ----------------------------------------
    # User → Patient
    # One user has one patient profile
    # ----------------------------------------

    patient = relationship(
        "Patient",
        back_populates="user",
        uselist=False
    )


# ============================================
# PATIENT TABLE
# ============================================

class Patient(Base):

    __tablename__ = "patients"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    patient_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    age = Column(
        Integer,
        nullable=True
    )

    gender = Column(
        String,
        nullable=True
    )

    phone = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # ----------------------------------------
    # Patient → User
    # ----------------------------------------

    user = relationship(
        "User",
        back_populates="patient"
    )

    # ----------------------------------------
    # Patient → Analyses
    # One patient can have many analyses
    # ----------------------------------------

    analyses = relationship(
        "Analysis",
        back_populates="patient",
        cascade="all, delete-orphan"
    )


# ============================================
# ANALYSIS TABLE
# ============================================

class Analysis(Base):

    __tablename__ = "analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    image_filename = Column(
        String,
        nullable=False
    )

    prediction = Column(
        String,
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=False
    )

    # ----------------------------------------
    # User's question/prompt
    # ----------------------------------------

    user_prompt = Column(
        String,
        nullable=True
    )

    # ----------------------------------------
    # Gemini explanation
    # ----------------------------------------

    ai_explanation = Column(
        String,
        nullable=True
    )

    gradcam_explanation = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # ----------------------------------------
    # Analysis → Patient
    # ----------------------------------------

    patient = relationship(
        "Patient",
        back_populates="analyses"
    )

    # ----------------------------------------
    # Analysis → Chat Messages
    # One analysis can have many chat messages
    # ----------------------------------------

    chat_messages = relationship(
        "ChatMessage",
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )


# ============================================
# CHAT MESSAGE TABLE
# ============================================

class ChatMessage(Base):

    __tablename__ = "chat_messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ----------------------------------------
    # Which X-ray analysis this conversation
    # belongs to
    # ----------------------------------------

    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id"),
        nullable=False,
        index=True
    )

    # ----------------------------------------
    # Message sender
    #
    # "user" = patient
    # "ai"   = Gemini
    # ----------------------------------------

    sender = Column(
        String,
        nullable=False
    )

    # ----------------------------------------
    # Actual conversation message
    # ----------------------------------------

    message = Column(
        String,
        nullable=False
    )

    # ----------------------------------------
    # Message creation time
    # ----------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # ----------------------------------------
    # ChatMessage → Analysis
    # ----------------------------------------

    analysis = relationship(
        "Analysis",
        back_populates="chat_messages"
    )


# ============================================
# PASSWORD RESET OTP TABLE
# ============================================

class PasswordResetOTP(Base):

    __tablename__ = "password_reset_otps"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ----------------------------------------
    # Hashed OTP
    # ----------------------------------------

    otp_hash = Column(
        String,
        nullable=False
    )

    # ----------------------------------------
    # OTP expiration time
    # ----------------------------------------

    expires_at = Column(
        DateTime,
        nullable=False
    )

    # ----------------------------------------
    # Number of verification attempts
    # ----------------------------------------

    attempts = Column(
        Integer,
        default=0,
        nullable=False
    )

    # ----------------------------------------
    # 0 = unused
    # 1 = already used
    # ----------------------------------------

    used = Column(
        Integer,
        default=0,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
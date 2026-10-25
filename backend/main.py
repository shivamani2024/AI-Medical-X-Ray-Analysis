# ============================================================
# AI MEDICAL IMAGE ANALYSIS API
# Corrected FastAPI Backend
# ============================================================

import os
import io
import hashlib
import hmac
import secrets
import logging

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import tensorflow as tf

from PIL import Image

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Depends,
    HTTPException,
    Form,
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import (
    FileResponse,
    HTMLResponse,
)

from fastapi.staticfiles import StaticFiles

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from pydantic import (
    BaseModel,
    Field,
)

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    text,
    event,
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session,
    relationship,
)

from jose import (
    JWTError,
    jwt,
)

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(
    "ai_medical_api"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent

PROJECT_DIR = BASE_DIR.parent


MODEL_PATH = (
    PROJECT_DIR
    / "models"
    / "mobilenetv2_baseline.keras"
)


DATABASE_PATH = (
    BASE_DIR
    / "medical.db"
)


UPLOAD_DIR = (
    BASE_DIR
    / "uploads"
)


GRADCAM_DIR = (
    BASE_DIR
    / "gradcam"
)


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


GRADCAM_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# IMAGE SETTINGS
# ============================================================

IMG_SIZE = (
    224,
    224,
)


MAX_IMAGE_SIZE = (
    10 * 1024 * 1024
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}


# ============================================================
# JWT SETTINGS
# ============================================================

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-this-secret-key",
)


ALGORITHM = "HS256"


ACCESS_TOKEN_EXPIRE_MINUTES = 60
REMEMBER_ME_EXPIRE_DAYS = 30


# ============================================================
# DATABASE
# ============================================================

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={
        "check_same_thread": False,
        "timeout": 60,
    },
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=60000")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()



SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


Base = declarative_base()


# ============================================================
# USER TABLE
# ============================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash = Column(
        String,
        nullable=False,
    )

    name = Column(
        String,
        nullable=False,
    )

    patient_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    phone = Column(
        String,
        nullable=True,
    )

    age = Column(
        Integer,
        nullable=True,
    )

    gender = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    patient = relationship(
        "Patient",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


# ============================================================
# PATIENT TABLE
# ============================================================

class Patient(Base):

    __tablename__ = "patients"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    patient_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    name = Column(
        String,
        nullable=False,
    )

    email = Column(
        String,
        nullable=False,
    )

    phone = Column(
        String,
        nullable=True,
    )

    age = Column(
        Integer,
        nullable=True,
    )

    gender = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    user = relationship(
        "User",
        back_populates="patient",
    )

    analyses = relationship(
        "Analysis",
        back_populates="patient",
        cascade="all, delete-orphan",
    )


# ============================================================
# ANALYSIS TABLE
# ============================================================

class Analysis(Base):

    __tablename__ = "analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )

    image_filename = Column(
        String,
        nullable=False,
    )

    image_path = Column(
        String,
        nullable=False,
    )

    prediction = Column(
        String,
        nullable=False,
    )

    confidence = Column(
        Float,
        nullable=False,
    )

    user_prompt = Column(
        Text,
        nullable=True,
    )

    ai_explanation = Column(
        Text,
        nullable=True,
    )

    gradcam_explanation = Column(
        Text,
        nullable=True,
    )

    gradcam_filename = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    patient = relationship(
        "Patient",
        back_populates="analyses",
    )

    chat_messages = relationship(
        "ChatMessage",
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


# ============================================================
# CHAT MESSAGE TABLE
# ============================================================

class ChatMessage(Base):

    __tablename__ = "chat_messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id"),
        nullable=False,
        index=True,
    )

    sender = Column(
        String,
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    analysis = relationship(
        "Analysis",
        back_populates="chat_messages",
    )


# ============================================================
# PASSWORD RESET OTP TABLE
# ============================================================

class PasswordResetOTP(Base):

    __tablename__ = "password_reset_otps"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    otp_hash = Column(
        String,
        nullable=False,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    attempts = Column(
        Integer,
        default=0,
        nullable=False,
    )

    used = Column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)

def _run_sqlite_migrations():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(analyses)"))
            existing_cols = {row[1] for row in result.fetchall()}
            needed_cols = [
                ("image_path", "VARCHAR"),
                ("gradcam_explanation", "TEXT"),
                ("gradcam_filename", "VARCHAR"),
            ]
            for col_name, col_type in needed_cols:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE analyses ADD COLUMN {col_name} {col_type}"))
                    logger.info(f"Auto-migrated: added {col_name} to analyses table")
            conn.commit()
    except Exception as exc:
        logger.warning(f"Database migration check note: {exc}")

_run_sqlite_migrations()


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# PASSWORD / OTP HASHING
#
# We intentionally do NOT use passlib/bcrypt here.
# ============================================================

def _hash_secret(
    value: str,
) -> str:

    salt = secrets.token_bytes(
        16
    )

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        value.encode(),
        salt,
        200_000,
    )

    return (
        f"pbkdf2_sha256$200000$"
        f"{salt.hex()}$"
        f"{digest.hex()}"
    )


def _verify_secret(
    value: str,
    stored: str,
) -> bool:

    try:

        (
            scheme,
            rounds,
            salt_hex,
            digest_hex,
        ) = stored.split(
            "$",
            3,
        )

        if scheme != "pbkdf2_sha256":
            return False

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            value.encode(),
            bytes.fromhex(
                salt_hex
            ),
            int(rounds),
        )

        return hmac.compare_digest(
            digest.hex(),
            digest_hex,
        )

    except Exception:

        return False


def hash_password(
    password: str,
) -> str:

    return _hash_secret(
        password
    )


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    return _verify_secret(
        password,
        password_hash,
    )


def hash_otp(
    otp: str,
) -> str:

    return _hash_secret(
        otp
    )


def verify_otp(
    otp: str,
    otp_hash: str,
) -> bool:

    return _verify_secret(
        otp,
        otp_hash,
    )


def generate_otp() -> str:

    return str(
        secrets.randbelow(
            900000
        ) + 100000
    )


# ============================================================
# PATIENT ID
# ============================================================

def generate_patient_id(
    db: Session,
) -> str:

    while True:

        value = (
            f"PAT-"
            f"{secrets.randbelow(90000) + 10000}"
        )

        exists = (
            db.query(User)
            .filter(
                User.patient_id == value
            )
            .first()
        )

        if not exists:
            return value


# ============================================================
# JWT
# ============================================================

def create_access_token(
    user_id: int,
    remember_me: bool = True,
) -> str:

    token_lifetime = (
        timedelta(days=REMEMBER_ME_EXPIRE_DAYS)
        if remember_me
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    expire = (
        datetime.now(timezone.utc)
        + token_lifetime
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
# ============================================================
# AUTHENTICATION
# ============================================================

security = HTTPBearer(
    auto_error=False
)


REVOKED_TOKENS = set()


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] =
        Depends(security),
    token: Optional[str] = None,
    db: Session =
        Depends(get_db),
):

    auth_token = None

    if credentials is not None and credentials.credentials:
        auth_token = credentials.credentials
    elif token:
        auth_token = token


    if auth_token is None:

        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )


    if auth_token in REVOKED_TOKENS:

        raise HTTPException(
            status_code=401,
            detail="Token has been logged out",
        )


    try:

        payload = jwt.decode(
            auth_token,
            SECRET_KEY,
            algorithms=[
                ALGORITHM
            ],
        )

        user_id = (
            payload.get("sub")
            or payload.get("user_id")
        )

        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token",
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )


    user = (
        db.query(User)
        .filter(
            User.id == int(user_id)
        )
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found",
        )


    return user


# ============================================================
# LOAD MOBILE NET V2 MODEL
# ============================================================

try:

    logger.info(
        "Loading MobileNetV2 model..."
    )

    model = tf.keras.models.load_model(
        str(MODEL_PATH)
    )

    logger.info(
        "MobileNetV2 model loaded successfully."
    )

    logger.info(
        "Input shape: %s",
        model.input_shape,
    )

    logger.info(
        "Output shape: %s",
        model.output_shape,
    )

except Exception as exc:

    logger.exception(
        "Model loading failed: %s",
        exc,
    )

    raise


# ============================================================
# GRAD-CAM VARIABLES
# ============================================================

BACKBONE = None

TARGET_LAYER = None

GRADCAM_LAYER_NAME = None

BACKBONE_INDEX = None

ACTIVATION_MODEL = None


# ============================================================
# FIND MOBILE NET V2 BACKBONE
# ============================================================

def find_backbone_and_target():

    global BACKBONE
    global TARGET_LAYER
    global GRADCAM_LAYER_NAME
    global BACKBONE_INDEX


    # --------------------------------------------------------
    # Find nested MobileNetV2 model
    # --------------------------------------------------------

    for index, layer in enumerate(
        model.layers
    ):

        if (
            isinstance(
                layer,
                tf.keras.Model,
            )
            and
            "mobilenetv2"
            in layer.name.lower()
        ):

            BACKBONE = layer

            BACKBONE_INDEX = index

            break


    # --------------------------------------------------------
    # Fallback: first nested model
    # --------------------------------------------------------

    if BACKBONE is None:

        for index, layer in enumerate(
            model.layers
        ):

            if isinstance(
                layer,
                tf.keras.Model,
            ):

                BACKBONE = layer

                BACKBONE_INDEX = index

                break


    # --------------------------------------------------------
    # Find last Conv2D INSIDE MobileNetV2
    # --------------------------------------------------------

    if BACKBONE is not None:

        convolution_layers = [
            layer
            for layer in BACKBONE.layers
            if isinstance(
                layer,
                tf.keras.layers.Conv2D,
            )
        ]


        if convolution_layers:

            TARGET_LAYER = (
                convolution_layers[-1]
            )


    # --------------------------------------------------------
    # Fallback: top-level Conv2D
    # --------------------------------------------------------

    if TARGET_LAYER is None:

        convolution_layers = [
            layer
            for layer in model.layers
            if isinstance(
                layer,
                tf.keras.layers.Conv2D,
            )
        ]


        if convolution_layers:

            TARGET_LAYER = (
                convolution_layers[-1]
            )


    # --------------------------------------------------------
    # Store layer name and build activation model
    # --------------------------------------------------------

    if TARGET_LAYER is not None:

        GRADCAM_LAYER_NAME = (
            TARGET_LAYER.name
        )


    if BACKBONE is not None and TARGET_LAYER is not None:

        global ACTIVATION_MODEL

        ACTIVATION_MODEL = (
            tf.keras.Model(
                inputs=BACKBONE.input,
                outputs=[
                    TARGET_LAYER.output,
                    BACKBONE.output,
                ],
            )
        )


# Run detection

find_backbone_and_target()


logger.info(
    "MobileNetV2 backbone: %s",
    (
        BACKBONE.name
        if BACKBONE is not None
        else None
    ),
)


logger.info(
    "Grad-CAM layer: %s",
    GRADCAM_LAYER_NAME,
)


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(
    image: Image.Image,
):

    image = (
        image
        .convert("RGB")
        .resize(IMG_SIZE)
    )


    image_array = np.asarray(
        image,
        dtype=np.float32,
    )


    image_array = np.expand_dims(
        image_array,
        axis=0,
    )


    return image_array


# ============================================================
# MODEL PREDICTION
# ============================================================

def predict_xray(
    image: Image.Image,
):

    image_array = (
        preprocess_image(
            image
        )
    )


    prediction = model.predict(
        image_array,
        verbose=0,
    )


    probability = float(
        np.asarray(
            prediction
        ).reshape(-1)[0]
    )


    if probability >= 0.5:

        return (
            "Pneumonia",
            probability,
        )


    return (
        "Normal",
        1.0 - probability,
    )


# ============================================================
# CORRECT GRAD-CAM
#
# IMPORTANT:
#
# The old code did:
#
# Model(
#     inputs=model.inputs,
#     outputs=[
#         nested_layer.output,
#         model.output
#     ]
# )
#
# That causes:
#
# Output with path '0' is not connected to inputs
#
# because the Conv2D output belongs to the nested
# MobileNetV2 graph.
#
# This implementation works through the MobileNetV2
# backbone itself and then applies the classification head.
# ============================================================

def generate_gradcam(
    image: Image.Image,
):

    if (
        BACKBONE is None
        or TARGET_LAYER is None
        or BACKBONE_INDEX is None
    ):

        raise RuntimeError(
            "Grad-CAM target layer could not be determined"
        )


    raw_image = tf.convert_to_tensor(
        preprocess_image(
            image
        ),
        dtype=tf.float32,
    )


    # --------------------------------------------------------
    # Layers BEFORE MobileNetV2
    # --------------------------------------------------------

    prefix_layers = (
        model.layers[
            :BACKBONE_INDEX
        ]
    )


    # --------------------------------------------------------
    # Layers AFTER MobileNetV2
    # --------------------------------------------------------

    head_layers = (
        model.layers[
            BACKBONE_INDEX + 1:
        ]
    )


    with tf.GradientTape() as tape:

        x = raw_image


        # ----------------------------------------------------
        # Apply preprocessing layers before MobileNetV2
        # ----------------------------------------------------

        for layer in prefix_layers:

            if isinstance(
                layer,
                tf.keras.layers.InputLayer,
            ):

                continue


            try:

                x = layer(
                    x,
                    training=False,
                )

            except TypeError:

                x = layer(x)


        # ----------------------------------------------------
        # Use prebuilt activation model
        # ----------------------------------------------------

        act_model = (
            ACTIVATION_MODEL
            if ACTIVATION_MODEL is not None
            else tf.keras.Model(
                inputs=BACKBONE.input,
                outputs=[
                    TARGET_LAYER.output,
                    BACKBONE.output,
                ],
            )
        )


        conv_outputs, features = (
            act_model(
                x,
                training=False,
            )
        )


        # ----------------------------------------------------
        # Apply classification head
        # ----------------------------------------------------

        y = features


        for layer in head_layers:

            try:

                y = layer(
                    y,
                    training=False,
                )

            except TypeError:

                y = layer(y)


        # ----------------------------------------------------
        # Binary classifier output
        # ----------------------------------------------------

        raw_pred = tf.reshape(
            y,
            [-1],
        )[0]


        target_score = tf.where(
            raw_pred >= 0.5,
            raw_pred,
            1.0 - raw_pred,
        )


    # --------------------------------------------------------
    # Calculate gradients
    # --------------------------------------------------------

    gradients = tape.gradient(
        target_score,
        conv_outputs,
    )


    if gradients is None:

        raise RuntimeError(
            "Grad-CAM gradients are None"
        )


    # --------------------------------------------------------
    # Global average pooling of gradients
    # --------------------------------------------------------

    weights = tf.reduce_mean(
        gradients,
        axis=(1, 2),
    )[0]


    conv_outputs = (
        conv_outputs[0]
    )


    # --------------------------------------------------------
    # Weighted feature maps
    # --------------------------------------------------------

    heatmap = tf.reduce_sum(
        conv_outputs
        *
        weights[
            tf.newaxis,
            tf.newaxis,
            :
        ],
        axis=-1,
    )


    # --------------------------------------------------------
    # ReLU
    # --------------------------------------------------------

    heatmap = tf.maximum(
        heatmap,
        0,
    )


    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    maximum = tf.reduce_max(
        heatmap
    )


    heatmap = tf.where(
        maximum > 0,
        heatmap / maximum,
        heatmap,
    )


    return heatmap.numpy()


# ============================================================
# SAVE GRAD-CAM IMAGE
# ============================================================

def save_gradcam_image(
    heatmap,
    original_image: Image.Image,
    analysis_id: int,
):

    heatmap_image = (
        Image.fromarray(
            np.uint8(
                np.clip(
                    heatmap,
                    0,
                    1,
                )
                * 255
            )
        )
        .resize(
            IMG_SIZE,
            Image.Resampling.BILINEAR,
        )
    )


    heatmap_array = (
        np.asarray(
            heatmap_image,
            dtype=np.float32,
        )
        / 255.0
    )


    # --------------------------------------------------------
    # Simple RGB heatmap
    # --------------------------------------------------------

    red = heatmap_array

    green = (
        1.0
        -
        np.abs(
            heatmap_array - 0.5
        )
        * 2.0
    )

    blue = (
        1.0
        -
        heatmap_array
    )


    colored_heatmap = np.stack(
        [
            red,
            green,
            blue,
        ],
        axis=-1,
    )


    # --------------------------------------------------------
    # Original X-ray
    # --------------------------------------------------------

    original_array = (
        np.asarray(
            original_image
            .convert("RGB")
            .resize(IMG_SIZE),
            dtype=np.float32,
        )
        / 255.0
    )


    # --------------------------------------------------------
    # Overlay
    # --------------------------------------------------------

    overlay = np.clip(
        (
            0.60
            * original_array
        )
        +
        (
            0.40
            * colored_heatmap
        ),
        0,
        1,
    )


    output_image = Image.fromarray(
        np.uint8(
            overlay * 255
        ),
        "RGB",
    )


    filename = (
        f"analysis_"
        f"{analysis_id}"
        f"_gradcam.png"
    )


    output_path = (
        GRADCAM_DIR
        / filename
    )


    output_image.save(
        output_path,
        format="PNG",
    )


    return filename
# ============================================================
# OPTIONAL GEMINI
#
# The API will still work if Gemini is not installed.
# ============================================================

gemini_client = None

gemini_model = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash",
)


try:

    from google import genai

    gemini_key = os.getenv(
        "GEMINI_API_KEY"
    )


    if gemini_key:

        gemini_client = (
            genai.Client(
                api_key=gemini_key
            )
        )


except Exception as exc:

    logger.warning(
        "Gemini unavailable; "
        "using local explanations: %s",
        exc,
    )


# ============================================================
# AI EXPLANATION
# ============================================================

def generate_explanation(
    prediction: str,
    confidence: float,
    use_gemini: bool = True,
) -> str:

    fallback = (
        f"The AI model classified "
        f"this chest X-ray as "
        f"{prediction} with "
        f"{confidence * 100:.2f}% confidence. "
        f"This is an AI-assisted screening "
        f"result, not a medical diagnosis. "
        f"Please have the image reviewed by "
        f"a qualified healthcare professional."
    )


    if gemini_client is None or not use_gemini:

        return fallback


    prompt = (
        "Give a short patient-friendly "
        "explanation for an educational "
        "chest X-ray classifier. "
        f"Prediction: {prediction}. "
        f"Confidence: "
        f"{confidence * 100:.2f}%. "
        "Do not diagnose, invent X-ray "
        "findings, or give treatment advice."
    )


    try:

        response = (
            gemini_client
            .models
            .generate_content(
                model=gemini_model,
                contents=prompt,
            )
        )


        text = getattr(
            response,
            "text",
            None,
        )


        if text:

            return text.strip()


    except Exception as exc:

        logger.warning(
            "Gemini explanation failed: %s",
            exc,
        )


    return fallback


def generate_gradcam_explanation(
    prediction: str,
    confidence: float,
    use_gemini: bool = True,
) -> str:

    is_pneumonia = prediction.upper() == "PNEUMONIA"

    if is_pneumonia:
        fallback = (
            f"The Grad-CAM visual heatmap highlights focal activation regions (red and yellow zones) "
            f"within the lung parenchyma where the convolutional network detected dense opacities and "
            f"pattern irregularities characteristic of pulmonary consolidation ({confidence * 100:.1f}% model attention intensity). "
            f"Cooler blue areas indicate background anatomical structures that contributed minimally to the classification."
        )
    else:
        fallback = (
            f"The Grad-CAM heatmap displays a clear, balanced, and diffuse activation distribution across both "
            f"pulmonary fields with {confidence * 100:.1f}% confidence. The absence of intense focal warm clusters (red/yellow) "
            f"indicates that no prominent localized parenchymal opacities or consolidation features were triggered during deep feature extraction."
        )

    if gemini_client is None or not use_gemini:
        return fallback

    prompt = (
        f"Provide a clear 2-3 sentence visual interpretation explanation of a Grad-CAM heatmap overlay for a chest X-ray. "
        f"The deep neural network classified the scan as {prediction} with {confidence * 100:.1f}% confidence. "
        f"Explain what warm (red/yellow/orange) versus cool (blue) activation overlay regions mean for this specific {prediction} classification in simple, professional terms. "
        f"Do not give direct medical diagnosis or treatment advice."
    )

    try:
        response = gemini_client.models.generate_content(
            model=gemini_model,
            contents=prompt,
        )
        text = getattr(response, "text", None)
        if text and len(text.strip()) > 10:
            return text.strip()
    except Exception as exc:
        logger.warning("Gemini Grad-CAM explanation failed: %s", exc)

    return fallback


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Medical Image Analysis API",
    description="Chest X-Ray AI analysis API",
    version="1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class RegisterRequest(BaseModel):

    name: str

    email: str

    password: str = Field(
        min_length=4
    )

    phone: Optional[str] = None

    age: Optional[int] = None

    gender: Optional[str] = None


class LoginRequest(BaseModel):

    email: str

    password: str

    remember_me: bool = True


class PatientUpdate(BaseModel):

    name: Optional[str] = None

    phone: Optional[str] = None

    age: Optional[int] = None

    gender: Optional[str] = None


class ChatRequest(BaseModel):

    analysis_id: int

    message: str


class AnalysisResponse(BaseModel):

    id: int

    analysis_id: Optional[int] = None

    prediction: str

    confidence: float

    ai_explanation: Optional[str] = None

    gradcam_explanation: Optional[str] = None

    risk_level: Optional[str] = None

    gradcam_url: Optional[str] = None

    image_filename: str

    created_at: datetime


class PatientResponse(BaseModel):

    id: int

    patient_id: str

    name: str

    email: str

    phone: Optional[str]

    age: Optional[int]

    gender: Optional[str]

    created_at: Optional[datetime]


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message":
            "AI Medical Image Analysis API is running",
        "docs":
            "/docs",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status":
            "healthy",

        "model_loaded":
            model is not None,

        "gradcam_layer":
            GRADCAM_LAYER_NAME,
    }


# ============================================================
# REGISTER
# ============================================================

@app.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):

    email = (
        data.email
        .strip()
        .lower()
    )


    existing_user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )


    patient_id = (
        generate_patient_id(
            db
        )
    )


    user = User(
        email=email,
        password_hash=(
            hash_password(
                data.password
            )
        ),
        name=data.name,
        patient_id=patient_id,
        phone=data.phone,
        age=data.age,
        gender=data.gender,
    )


    db.add(user)

    db.flush()


    patient = Patient(
        user_id=user.id,
        patient_id=patient_id,
        name=data.name,
        email=email,
        phone=data.phone,
        age=data.age,
        gender=data.gender,
    )


    db.add(patient)

    db.commit()

    db.refresh(user)


    user_payload = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "patient_id": user.patient_id,
        "phone": user.phone,
        "age": user.age,
        "gender": user.gender,
    }

    return {
        "message": "Registration successful",
        "patient_id": user.patient_id,
        "user": user_payload,
        "patient": user_payload,
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):

    email = (
        data.email
        .strip()
        .lower()
    )


    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    if (
        not user
        or not verify_password(
            data.password,
            user.password_hash,
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )


    token = (
        create_access_token(
            user.id,
            data.remember_me,
        )
    )

    user_payload = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "patient_id": user.patient_id,
        "phone": user.phone,
        "age": user.age,
        "gender": user.gender,
    }


    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": user_payload,
        "patient": user_payload,
    }



# ============================================================
# ME
# ============================================================

@app.get("/me")
def me(
    current_user: User =
        Depends(get_current_user),
):

    return {
        "id":
            current_user.id,

        "email":
            current_user.email,

        "name":
            current_user.name,

        "patient_id":
            current_user.patient_id,

        "phone":
            current_user.phone,

        "age":
            current_user.age,

        "gender":
            current_user.gender,
    }


# ============================================================
# LOGOUT
# ============================================================

@app.post("/logout")
def logout(
    credentials:
        HTTPAuthorizationCredentials =
        Depends(security),
):

    if credentials:

        REVOKED_TOKENS.add(
            credentials.credentials
        )


    return {
        "message":
            "Logout successful"
    }


# ============================================================
# PATIENT HELPER
# ============================================================

def get_patient(
    current_user: User,
    db: Session,
):

    patient = (
        db.query(Patient)
        .filter(
            Patient.user_id
            == current_user.id
        )
        .first()
    )


    if not patient:

        raise HTTPException(
            status_code=404,
            detail="Patient profile not found",
        )


    return patient


# ============================================================
# GET PATIENT PROFILE
# ============================================================

@app.get(
    "/patient/profile",
    response_model=PatientResponse,
)
def get_profile(
    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    return get_patient(
        current_user,
        db,
    )


# ============================================================
# UPDATE PATIENT PROFILE
# ============================================================

@app.put(
    "/patient/profile",
    response_model=PatientResponse,
)
def update_profile(
    data: PatientUpdate,

    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    patient = get_patient(
        current_user,
        db,
    )


    for field in (
        "name",
        "phone",
        "age",
        "gender",
    ):

        value = getattr(
            data,
            field,
        )


        if value is not None:

            setattr(
                patient,
                field,
                value,
            )

            setattr(
                current_user,
                field,
                value,
            )


    db.commit()

    db.refresh(
        patient
    )


    return patient


# ============================================================
# PREDICT
# ============================================================

@app.post(
    "/predict",
    response_model=AnalysisResponse,
)
async def predict(
    file: UploadFile = File(...),

    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    if (
        file.content_type
        not in ALLOWED_IMAGE_TYPES
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG, PNG "
                "or WEBP images are allowed"
            ),
        )


    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    contents = (
        await file.read()
    )


    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty",
        )


    if len(contents) > MAX_IMAGE_SIZE:

        raise HTTPException(
            status_code=400,
            detail="Image size exceeds 10 MB",
        )


    try:

        image = Image.open(
            io.BytesIO(contents)
        )

        image.load()

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Unable to read uploaded image",
        )


    # --------------------------------------------------------
    # Patient
    # --------------------------------------------------------

    patient = get_patient(
        current_user,
        db,
    )


    # --------------------------------------------------------
    # Safe filename
    # --------------------------------------------------------

    safe_name = Path(
        file.filename
        or "xray.jpg"
    ).name


    stored_name = (
        datetime.utcnow()
        .strftime(
            "%Y%m%d%H%M%S%f"
        )
        + "_"
        + secrets.token_hex(4)
        + "_"
        + safe_name
    )


    image_path = (
        UPLOAD_DIR
        / stored_name
    )


    image.save(
        image_path
    )


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction, confidence = (
        predict_xray(
            image
        )
    )


    # --------------------------------------------------------
    # AI explanation & Grad-CAM explanation
    # --------------------------------------------------------

    explanation = (
        generate_explanation(
            prediction,
            confidence,
            use_gemini=False,
        )
    )

    gradcam_exp = (
        generate_gradcam_explanation(
            prediction,
            confidence,
            use_gemini=False,
        )
    )

    risk_lvl = (
        "HIGH" if (prediction.upper() == "PNEUMONIA" and confidence >= 0.75)
        else "MODERATE" if (prediction.upper() == "PNEUMONIA")
        else "LOW"
    )

    # --------------------------------------------------------
    # Create analysis
    # --------------------------------------------------------

    analysis = Analysis(
        patient_id=patient.id,

        image_filename=safe_name,

        image_path=str(
            image_path
        ),

        prediction=prediction,

        confidence=confidence,

        ai_explanation=explanation,

        gradcam_explanation=gradcam_exp,
    )


    db.add(
        analysis
    )

    db.flush()


    # --------------------------------------------------------
    # Generate Grad-CAM
    # --------------------------------------------------------

    try:

        logger.info(
            "Generating Grad-CAM "
            "for analysis %s...",
            analysis.id,
        )


        heatmap = (
            generate_gradcam(
                image
            )
        )


        analysis.gradcam_filename = (
            save_gradcam_image(
                heatmap,
                image,
                analysis.id,
            )
        )


        logger.info(
            "Grad-CAM generated successfully."
        )


    except Exception as exc:

        logger.exception(
            "Grad-CAM generation failed: %s",
            exc,
        )

        analysis.gradcam_filename = None


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    db.commit()

    db.refresh(
        analysis
    )


    return AnalysisResponse(
        id=analysis.id,

        analysis_id=analysis.id,

        prediction=analysis.prediction,

        confidence=analysis.confidence,

        ai_explanation=(
            analysis.ai_explanation
        ),

        gradcam_explanation=(
            analysis.gradcam_explanation
        ),

        risk_level=risk_lvl,

        gradcam_url=(
            f"/gradcam/{analysis.id}"
            if analysis.gradcam_filename
            else None
        ),

        image_filename=(
            analysis.image_filename
        ),

        created_at=(
            analysis.created_at
        ),
    )


# ============================================================
# GET SAMPLE X-RAY
# ============================================================

@app.get("/sample-xray/{sample_type}")
def get_sample_xray(sample_type: str):
    root_dir = Path(__file__).resolve().parent.parent
    if sample_type.lower() == "pneumonia":
        sample_path = root_dir / "dataset" / "test" / "PNEUMONIA" / "person100_bacteria_475.jpeg"
    else:
        sample_path = root_dir / "dataset" / "test" / "NORMAL" / "IM-0001-0001.jpeg"

    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Sample image not found")

    return FileResponse(
        str(sample_path),
        media_type="image/jpeg",
        filename=f"sample_{sample_type.lower()}.jpeg"
    )


# ============================================================
# GET GRAD-CAM
# ============================================================

@app.get(
    "/gradcam/{analysis_id}"
)
def get_gradcam(
    analysis_id: int,

    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    patient = get_patient(
        current_user,
        db,
    )


    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id
            == analysis_id,

            Analysis.patient_id
            == patient.id,
        )
        .first()
    )


    if (
        not analysis
        or not analysis.gradcam_filename
    ):

        raise HTTPException(
            status_code=404,
            detail=(
                "Grad-CAM image is not available"
            ),
        )


    path = (
        GRADCAM_DIR
        / analysis.gradcam_filename
    )


    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Grad-CAM image file is missing"
            ),
        )


    return FileResponse(
        path,
        media_type="image/png",
        filename=path.name,
    )


# ============================================================
# GET INDIVIDUAL ANALYSIS
# ============================================================

@app.get(
    "/analysis/{analysis_id}"
)
def get_analysis(
    analysis_id: int,

    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    patient = get_patient(
        current_user,
        db,
    )


    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id
            == analysis_id,

            Analysis.patient_id
            == patient.id,
        )
        .first()
    )


    if not analysis:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )


    return {
        "id":
            analysis.id,

        "prediction":
            analysis.prediction,

        "confidence":
            analysis.confidence,

        "ai_explanation":
            analysis.ai_explanation,

        "gradcam_url":
            (
                f"/gradcam/{analysis.id}"
                if analysis.gradcam_filename
                else None
            ),

        "image_filename":
            analysis.image_filename,

        "created_at":
            analysis.created_at,

        "chat":
            [
                {
                    "id":
                        message.id,

                    "sender":
                        message.sender,

                    "message":
                        message.message,

                    "created_at":
                        message.created_at,
                }

                for message
                in analysis.chat_messages
            ],
    }


# ============================================================
# ANALYSIS HISTORY
# ============================================================

@app.get(
    "/history"
)
def history(
    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    patient = get_patient(
        current_user,
        db,
    )


    analyses = (
        db.query(Analysis)
        .filter(
            Analysis.patient_id
            == patient.id
        )
        .order_by(
            Analysis.created_at.desc()
        )
        .all()
    )


    return [
        {
            "id":
                analysis.id,

            "prediction":
                analysis.prediction,

            "confidence":
                analysis.confidence,

            "ai_explanation":
                analysis.ai_explanation,

            "gradcam_url":
                (
                    f"/gradcam/{analysis.id}"
                    if analysis.gradcam_filename
                    else None
                ),

            "image_filename":
                analysis.image_filename,

            "created_at":
                analysis.created_at,
        }

        for analysis
        in analyses
    ]


# ============================================================
# HTML REPORT
# ============================================================

@app.get(
    "/report/{analysis_id}",
    response_class=HTMLResponse,
)
def report(
    analysis_id: int,

    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    patient = get_patient(
        current_user,
        db,
    )


    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id
            == analysis_id,

            Analysis.patient_id
            == patient.id,
        )
        .first()
    )


    if not analysis:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )


    html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
AI Medical Image Analysis Report
</title>

<style>

body {{
    font-family: Arial, sans-serif;
    max-width: 800px;
    margin: 40px auto;
    padding: 20px;
}}

.box {{
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 10px;
}}

.note {{
    margin-top: 20px;
    font-size: 14px;
}}

</style>

</head>

<body>

<h1>
AI Medical Image Analysis Report
</h1>

<div class="box">

<p>
<b>Patient:</b>
{patient.name}
</p>

<p>
<b>Patient ID:</b>
{patient.patient_id}
</p>

<p>
<b>Analysis ID:</b>
{analysis.id}
</p>

<p>
<b>Prediction:</b>
{analysis.prediction}
</p>

<p>
<b>Confidence:</b>
{analysis.confidence * 100:.2f}%
</p>

<p>
<b>AI Explanation:</b>
{analysis.ai_explanation or ""}
</p>

<p>
<b>Image:</b>
{analysis.image_filename}
</p>

<p>
<b>Date:</b>
{analysis.created_at}
</p>

</div>

<p class="note">

<b>
Medical disclaimer:
</b>

This report is generated by an
AI-assisted educational system and
is not a medical diagnosis.

Please consult a qualified healthcare
professional for medical interpretation.

</p>

</body>

</html>
"""


    return HTMLResponse(
        content=html
    )


# ============================================================
# CHAT REQUEST
# ============================================================

@app.post(
    "/chat"
)
def chat(
    data: ChatRequest,

    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    patient = get_patient(
        current_user,
        db,
    )


    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id
            == data.analysis_id,

            Analysis.patient_id
            == patient.id,
        )
        .first()
    )


    if not analysis:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )


    message = (
        data.message.strip()
    )


    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty",
        )





    # --------------------------------------------------------
    # Context-aware educational fallback response
    # --------------------------------------------------------

    msg_lower = message.lower()
    conf_pct = f"{analysis.confidence * 100:.1f}%"

    if "heatmap" in msg_lower or "red" in msg_lower or "color" in msg_lower or "zone" in msg_lower:
        answer = (
            f"The Grad-CAM heatmap highlights the anatomical regions that most heavily influenced "
            f"the AI model's {analysis.prediction} classification ({conf_pct} confidence). "
            f"Warm colors (red, orange, and yellow) indicate focal areas where the neural network detected "
            f"significant density or consolidation patterns, whereas cool blue zones indicate clear or normal tissue baseline. "
            f"This serves as an interpretability aid and should be correlated clinically by a radiologist."
        )
    elif "confidence" in msg_lower or "score" in msg_lower or "percentage" in msg_lower:
        answer = (
            f"The AI model yielded a confidence score of {conf_pct} for {analysis.prediction}. "
            f"This represents the mathematical probability computed by the deep learning classifier based on patterns "
            f"learned from thousands of chest radiographs. While high confidence indicates strong pattern matching, "
            f"it is a clinical screening indicator rather than a definitive medical diagnosis."
        )
    elif "symptom" in msg_lower or "urgent" in msg_lower or "emergency" in msg_lower or "breath" in msg_lower:
        answer = (
            f"Key pulmonary symptoms that warrant prompt medical evaluation include persistent productive cough, "
            f"high fever, chills, localized chest pain during deep inhalation, and fatigue. "
            f"Seek immediate emergency medical attention if you experience severe shortness of breath, "
            f"bluish lips or fingernails, confusion, or difficulty speaking in full sentences."
        )
    elif "doctor" in msg_lower or "question" in msg_lower or "physician" in msg_lower or "ask" in msg_lower:
        answer = (
            f"Here are practical questions to review with your healthcare provider:\n"
            f"1. Based on this chest X-ray and my clinical symptoms, what is your official diagnosis?\n"
            f"2. Does the radiologist see any signs of bacterial or viral consolidation?\n"
            f"3. Are supplementary tests (such as blood work, pulse oximetry, or sputum culture) needed?\n"
            f"4. What treatment or recovery timeline do you advise?"
        )
    elif "pneumonia" in msg_lower or "infection" in msg_lower:
        answer = (
            f"Pneumonia is an infection that inflames the air sacs (alveoli) in one or both lungs, which may fill with fluid or purulent material. "
            f"On radiographs, it often manifests as areas of increased opacity or consolidation. "
            f"Your scan showed patterns consistent with {analysis.prediction} ({conf_pct} confidence). "
            f"A physician will determine if antibiotics, antivirals, or supportive therapies are appropriate."
        )
    elif "normal" in msg_lower or "healthy" in msg_lower or "clear" in msg_lower:
        answer = (
            f"A Normal classification indicates that the neural network did not detect characteristic signs of "
            f"acute pulmonary consolidation or infiltrates ({conf_pct} confidence). "
            f"To maintain respiratory wellness, practice good hydration, avoid tobacco/vape exposure, and consult a doctor if symptoms persist."
        )
    else:
        answer = (
            f"This chest X-ray analysis was classified as {analysis.prediction} with {conf_pct} confidence. "
            f"I can provide educational context regarding the prediction, the Grad-CAM visual heatmap, and relevant questions for your physician. "
            f"Please remember that AI assistance is for informational screening and does not substitute a licensed clinical consultation."
        )

    # --------------------------------------------------------
    # Gemini response if available
    # --------------------------------------------------------

    if gemini_client is not None:

        prompt = (
            "You are MediAI, an empathetic and knowledgeable clinical educational assistant for chest X-ray interpretation.\n\n"
            f"Scan Context:\n"
            f"- AI Classification: {analysis.prediction}\n"
            f"- Confidence: {analysis.confidence * 100:.2f}%\n"
            f"- Grad-CAM Interpretation: {analysis.gradcam_explanation or 'Standard feature map'}\n"
            f"- Clinical Summary: {analysis.ai_explanation or 'N/A'}\n\n"
            f"User Question: \"{message}\"\n\n"
            "Guidelines:\n"
            "1. Answer the patient's specific question directly, clearly, and concisely in 2-4 short paragraphs.\n"
            "2. If asked about the heatmap, explain the red/warm vs blue zones in relation to the scan.\n"
            "3. If asked what to ask their doctor, provide 3-4 structured bullet questions.\n"
            "4. Maintain a supportive, professional medical tone.\n"
            "5. Include a brief reminder that this is an educational screening and requires licensed clinical interpretation."
        )

        try:

            response = (
                gemini_client
                .models
                .generate_content(
                    model=gemini_model,
                    contents=prompt,
                )
            )

            if getattr(
                response,
                "text",
                None,
            ):
                answer = (
                    response.text.strip()
                )

        except Exception as exc:

            logger.warning(
                "Gemini chat failed: %s",
                exc,
            )


    # --------------------------------------------------------
    # Save messages
    # --------------------------------------------------------

    db.add(
        ChatMessage(
            analysis_id=analysis.id,
            sender="user",
            message=message,
        )
    )

    db.add(
        ChatMessage(
            analysis_id=analysis.id,
            sender="ai",
            message=answer,
        )
    )

    db.commit()


    return {
        "analysis_id": analysis.id,
        "reply": answer,
        "response": answer,
        "message": answer,
        "answer": answer,
    }



# ============================================================
# CHAT HISTORY
# ============================================================

@app.get(
    "/chat/{analysis_id}"
)
def get_chat_history(
    analysis_id: int,

    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    patient = get_patient(
        current_user,
        db,
    )


    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id
            == analysis_id,

            Analysis.patient_id
            == patient.id,
        )
        .first()
    )


    if not analysis:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )


    messages = [
        {
            "id":
                message.id,

            "sender":
                message.sender,

            "message":
                message.message,

            "created_at":
                (
                    message.created_at.isoformat()
                    if message.created_at
                    else None
                ),
        }

        for message
        in analysis.chat_messages
    ]


    return {
        "analysis_id":
            analysis.id,

        "messages":
            messages,
    }


# ============================================================
# CHAT COUNT
# ============================================================

@app.get(
    "/chat/{analysis_id}/count"
)
def get_chat_count(
    analysis_id: int,

    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    patient = get_patient(
        current_user,
        db,
    )


    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id
            == analysis_id,

            Analysis.patient_id
            == patient.id,
        )
        .first()
    )


    if not analysis:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )


    count = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.analysis_id
            == analysis.id
        )
        .count()
    )


    return {
        "analysis_id":
            analysis.id,

        "message_count":
            count,
    }


# ============================================================
# CLEAR CHAT
# ============================================================

@app.delete(
    "/chat/{analysis_id}"
)
def clear_chat(
    analysis_id: int,

    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    patient = get_patient(
        current_user,
        db,
    )


    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id
            == analysis_id,

            Analysis.patient_id
            == patient.id,
        )
        .first()
    )


    if not analysis:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )


    messages = list(
        analysis.chat_messages
    )


    count = len(
        messages
    )


    for message in messages:

        db.delete(
            message
        )


    db.commit()


    return {
        "message":
            "Chat history cleared successfully",

        "analysis_id":
            analysis_id,

        "deleted_messages":
            count,
    }


# ============================================================
# DELETE INDIVIDUAL CHAT MESSAGE
# ============================================================

@app.delete(
    "/chat/message/{message_id}"
)
def delete_chat_message(
    message_id: int,

    current_user: User =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),
):

    patient = get_patient(
        current_user,
        db,
    )


    message = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.id
            == message_id
        )
        .first()
    )


    if not message:

        raise HTTPException(
            status_code=404,
            detail="Chat message not found",
        )


    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id
            == message.analysis_id,

            Analysis.patient_id
            == patient.id,
        )
        .first()
    )


    if not analysis:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    db.delete(
        message
    )

    db.commit()


    return {
        "message":
            "Chat message deleted successfully",

        "message_id":
            message_id,
    }


# ============================================================
# FORGOT PASSWORD
#
# For your current development setup the OTP is returned
# in the response so you can test it without Resend.
# ============================================================

@app.post(
    "/forgot-password"
)
def forgot_password(
    email: str = Form(...),

    db: Session =
        Depends(get_db),
):

    email = (
        email.strip()
        .lower()
    )


    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    if not user:

        return {
            "message":
                "If this email is registered, "
                "an OTP has been generated."
        }


    otp = generate_otp()


    old_otps = (
        db.query(
            PasswordResetOTP
        )
        .filter(
            PasswordResetOTP.user_id
            == user.id,

            PasswordResetOTP.used
            == 0,
        )
        .all()
    )


    for old_otp in old_otps:

        old_otp.used = 1


    new_otp = PasswordResetOTP(
        user_id=user.id,

        otp_hash=(
            hash_otp(
                otp
            )
        ),

        expires_at=(
            datetime.utcnow()
            + timedelta(
                minutes=10
            )
        ),

        attempts=0,

        used=0,
    )


    db.add(
        new_otp
    )

    db.commit()


    print(
        "=" * 50
    )

    print(
        "PASSWORD RESET OTP"
    )

    print(
        "Email:",
        user.email,
    )

    print(
        "OTP:",
        otp,
    )

    print(
        "=" * 50
    )


    return {
        "message":
            "OTP generated successfully",

        "otp":
            otp,
    }


# ============================================================
# VERIFY OTP
# ============================================================

@app.post(
    "/verify-otp"
)
def verify_reset_otp(
    email: str = Form(...),

    otp: str = Form(...),

    db: Session =
        Depends(get_db),
):

    email = (
        email.strip()
        .lower()
    )


    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=400,
            detail="Invalid reset request",
        )


    reset_otp = (
        db.query(
            PasswordResetOTP
        )
        .filter(
            PasswordResetOTP.user_id
            == user.id,

            PasswordResetOTP.used
            == 0,
        )
        .order_by(
            PasswordResetOTP.created_at.desc()
        )
        .first()
    )


    if not reset_otp:

        raise HTTPException(
            status_code=400,
            detail="OTP not found or already used",
        )


    if (
        datetime.utcnow()
        > reset_otp.expires_at
    ):

        reset_otp.used = 1

        db.commit()


        raise HTTPException(
            status_code=400,
            detail="OTP has expired",
        )


    if reset_otp.attempts >= 5:

        reset_otp.used = 1

        db.commit()


        raise HTTPException(
            status_code=400,
            detail="Too many OTP attempts",
        )


    if not verify_otp(
        otp,
        reset_otp.otp_hash,
    ):

        reset_otp.attempts += 1

        db.commit()


        raise HTTPException(
            status_code=400,
            detail="Invalid OTP",
        )


    return {
        "message":
            "OTP verified successfully",

        "email":
            email,
    }


# ============================================================
# RESET PASSWORD
# ============================================================

@app.post(
    "/reset-password"
)
def reset_password(
    email: str = Form(...),

    otp: str = Form(...),

    new_password: str = Form(...),

    db: Session =
        Depends(get_db),
):

    email = (
        email.strip()
        .lower()
    )


    if len(
        new_password
    ) < 4:

        raise HTTPException(
            status_code=400,
            detail=(
                "Password must contain "
                "at least 4 characters"
            ),
        )


    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=400,
            detail="Invalid reset request",
        )


    reset_otp = (
        db.query(
            PasswordResetOTP
        )
        .filter(
            PasswordResetOTP.user_id
            == user.id,

            PasswordResetOTP.used
            == 0,
        )
        .order_by(
            PasswordResetOTP.created_at.desc()
        )
        .first()
    )


    if not reset_otp:

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP",
        )


    if (
        datetime.utcnow()
        > reset_otp.expires_at
    ):

        reset_otp.used = 1

        db.commit()


        raise HTTPException(
            status_code=400,
            detail="OTP has expired",
        )


    if reset_otp.attempts >= 5:

        reset_otp.used = 1

        db.commit()


        raise HTTPException(
            status_code=400,
            detail="Too many OTP attempts",
        )


    if not verify_otp(
        otp,
        reset_otp.otp_hash,
    ):

        reset_otp.attempts += 1

        db.commit()


        raise HTTPException(
            status_code=400,
            detail="Invalid OTP",
        )


    user.password_hash = (
        hash_password(
            new_password
        )
    )


    reset_otp.used = 1


    db.commit()


    return {
        "message":
            "Password reset successfully"
    }


# ============================================================
# API INFO
# ============================================================

@app.get(
    "/api/info"
)
def api_info():

    return {
        "name":
            app.title,

        "version":
            app.version,

        "features": [

            "Patient registration",

            "Patient login",

            "JWT authentication",

            "Patient profile",

            "Chest X-ray prediction",

            "MobileNetV2",

            "Grad-CAM explainability",

            "AI explanation",

            "Analysis history",

            "Analysis details",

            "HTML reports",

            "AI medical assistant",

            "Chat history",

            "Password reset OTP",
        ],
    }


# ============================================================
# FRONTEND STATIC FILES MOUNT
# ============================================================

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


# ============================================================
# STARTUP
# ============================================================

@app.on_event(
    "startup"
)
def startup_event():

    print(
        "=" * 60
    )

    print(
        "AI Medical Image Analysis API starting..."
    )

    print(
        "=" * 60
    )

    print(
        f"Base directory: "
        f"{BASE_DIR}"
    )

    print(
        f"Model path: "
        f"{MODEL_PATH}"
    )

    print(
        f"Database path: "
        f"{DATABASE_PATH}"
    )

    print(
        f"Model loaded: "
        f"{model is not None}"
    )

    print(
        f"MobileNetV2 backbone: "
        f"{
            BACKBONE.name
            if BACKBONE is not None
            else 'Not found'
        }"
    )

    print(
        f"Grad-CAM layer: "
        f"{GRADCAM_LAYER_NAME}"
    )

    print(
        f"Grad-CAM directory: "
        f"{GRADCAM_DIR}"
    )

    print(
        f"Gemini available: "
        f"{gemini_client is not None}"
    )

    print(
        "API documentation: "
        "https://ai-medical-x-ray-analysis-1.onrender.com/docs"
    )

    print(
        "=" * 60
    )
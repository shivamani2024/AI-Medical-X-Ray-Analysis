# ============================================
# Initialize Database
# ============================================

from .database import engine, Base

from .models import (
    User,
    Patient,
    Analysis,
    PasswordResetOTP
)


print("Creating database tables...")


Base.metadata.create_all(
    bind=engine
)


print("Database created successfully!")
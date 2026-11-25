import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://support_user:support_pass@localhost:5432/ecommerce_support")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-dev-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
AUTO_REFUND_LIMIT = float(os.getenv("AUTO_REFUND_LIMIT", "5000"))
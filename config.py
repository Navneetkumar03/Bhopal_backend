import os 
from dotenv import load_dotenv

load_dotenv()

class setting:
    """
    Application configuration loaded from environment variables.
    """
    app_env: str = os.getenv("APP_ENV","Development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
     # ============ PRIMARY DATABASE (BHOPAL) ============
    db_host: str = os.getenv("DB_HOST")
    db_port: int = os.getenv("DB_PORT")
    db_user: str = os.getenv("DB_USER")
    db_name: str = os.getenv("DB_NAME")
    db_password: str = os.getenv("DB_PASSWORD")
    
    
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    
    
    @property
    def database_url(self) -> str:
        """SQLAlchemy connection string (psycopg2 driver)."""
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        
        
setting = setting()
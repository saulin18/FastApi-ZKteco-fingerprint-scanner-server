from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
import sys
from config import DATABASE_URL

sys.dont_write_bytecode = True  # don't create __pycache__

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

class Fingerprint(Base):
    """Model for storing fingerprint capture data"""
    __tablename__ = "fingerprints"
    
    id = Column(Integer, primary_key=True, index=True)
    fingerprint_id = Column(Integer, nullable=True, index=True)
    score = Column(Integer, nullable=True)
    image_base64 = Column(Text, nullable=False)
    template_data = Column(Text, nullable=False)
    device_serial = Column(String(100), nullable=False, index=True)
    image_width = Column(Integer, nullable=False)
    image_height = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Fingerprint(id={self.id}, fingerprint_id={self.fingerprint_id}, timestamp={self.timestamp})>"

class DeviceInfo(Base):
    """Model for storing device information"""
    __tablename__ = "device_info"
    
    id = Column(Integer, primary_key=True, index=True)
    device_serial = Column(String(100), unique=True, nullable=False, index=True)
    device_type = Column(String(50), nullable=True)
    last_connected = Column(DateTime, default=datetime.utcnow)
    image_width = Column(Integer, nullable=False)
    image_height = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DeviceInfo(serial={self.device_serial}, type={self.device_type})>"

class FingerprintTemplate(Base):
    """Model for storing registered fingerprint templates"""
    __tablename__ = "fingerprint_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    fingerprint_id = Column(Integer, unique=True, nullable=False, index=True)
    template_data = Column(Text, nullable=False)
    device_serial = Column(String(100), nullable=False, index=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<FingerprintTemplate(id={self.fingerprint_id}, registered_at={self.registered_at})>"

# Database dependency
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database initialization
def init_database():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# Database cleanup
def close_database():
    """Close database connections"""
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

if __name__ == "__main__":
    init_database()

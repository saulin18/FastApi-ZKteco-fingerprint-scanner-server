

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from .models import get_db, init_database, close_database
from .fingerprint_service import FingerprintService
from .database_service import DatabaseService

# Import configuration
from config import API_TITLE, API_DESCRIPTION, API_VERSION, LOG_LEVEL
# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Global instances
fingerprint_service = None
db_service = DatabaseService()

# Pydantic models
class FingerprintResponse(BaseModel):
    id: Optional[int] = None
    fingerprint_id: Optional[int] = None
    score: Optional[int] = None
    image_base64: str
    template_data: str
    timestamp: str
    device_serial: str
    image_width: int
    image_height: int

class DeviceStatus(BaseModel):
    device_count: int
    is_connected: bool
    device_serial: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None

class DatabaseStats(BaseModel):
    total_fingerprints: int
    unique_devices: int
    latest_capture: Optional[str] = None

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global fingerprint_service
    try:
        # Initialize database
        init_database()
        logger.info("Database initialized successfully")
        
        # Initialize fingerprint service
        fingerprint_service = FingerprintService()
        fingerprint_service.init_device()
        logger.info("Fingerprint service initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Don't raise exception to allow API to start without device

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    global fingerprint_service
    try:
        if fingerprint_service:
            fingerprint_service.cleanup()
        close_database()
        logger.info("Services cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fingerprint API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/device/status", response_model=DeviceStatus)
async def get_device_status():
    """Get the current status of the fingerprint device"""
    global fingerprint_service
    if not fingerprint_service:
        raise HTTPException(status_code=503, detail="Fingerprint service not initialized")
    
    try:
        device_count = fingerprint_service.get_device_count()
        is_connected = fingerprint_service.is_device_connected()
        device_serial = fingerprint_service.get_device_serial() if is_connected else None
        width = fingerprint_service.get_image_width() if is_connected else None
        height = fingerprint_service.get_image_height() if is_connected else None
        
        return DeviceStatus(
            device_count=device_count,
            is_connected=is_connected,
            device_serial=device_serial,
            image_width=width,
            image_height=height
        )
    except Exception as e:
        logger.error(f"Error getting device status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting device status: {str(e)}")

@app.get("/fingerprint/capture", response_model=FingerprintResponse)
async def capture_fingerprint(db=Depends(get_db)):
    """Capture a fingerprint and return image and template data"""
    global fingerprint_service
    if not fingerprint_service:
        raise HTTPException(status_code=503, detail="Fingerprint service not initialized")
    
    try:
        # Capture fingerprint
        result = fingerprint_service.capture_fingerprint()
        if not result:
            raise HTTPException(status_code=408, detail="No fingerprint detected. Please try again.")
        
        template, image_data = result
        
        # Convert image to base64 using improved method
        image_base64 = fingerprint_service.image_to_base64(image_data)
        
        # Convert template to base64 for storage
        template_base64 = fingerprint_service.template_to_base64(template)
        
        # Get device information
        device_serial = fingerprint_service.get_device_serial()
        width = fingerprint_service.get_image_width()
        height = fingerprint_service.get_image_height()
        
        # Create response
        response = FingerprintResponse(
            fingerprint_id=None,
            score=None,
            image_base64=image_base64,
            template_data=template_base64,
            timestamp=datetime.now().isoformat(),
            device_serial=device_serial,
            image_width=width,
            image_height=height
        )
        
        # Store in database
        stored_fingerprint = db_service.store_fingerprint_data(
            db=db,
            fingerprint_id=None,
            score=None,
            image_base64=image_base64,
            template_data=template_base64,
            device_serial=device_serial,
            width=width,
            height=height
        )
        
        response.id = stored_fingerprint.id
        
        return response
        
    except Exception as e:
        logger.error(f"Error capturing fingerprint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error capturing fingerprint: {str(e)}")

@app.get("/fingerprint/latest")
async def get_latest_fingerprint(db=Depends(get_db)):
    """Get the latest captured fingerprint data from database"""
    try:
        latest_data = db_service.get_latest_fingerprint(db)
        if not latest_data:
            raise HTTPException(status_code=404, detail="No fingerprint data found")
        
        return latest_data
    except Exception as e:
        logger.error(f"Error retrieving latest fingerprint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving latest fingerprint: {str(e)}")

@app.get("/fingerprint/history")
async def get_fingerprint_history(limit: int = 10, db=Depends(get_db)):
    """Get fingerprint capture history"""
    try:
        history = db_service.get_fingerprint_history(db, limit)
        return {"history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Error retrieving fingerprint history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving fingerprint history: {str(e)}")

@app.get("/fingerprint/stats", response_model=DatabaseStats)
async def get_database_stats(db=Depends(get_db)):
    """Get database statistics"""
    try:
        stats = db_service.get_database_stats(db)
        return DatabaseStats(**stats)
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")

@app.post("/fingerprint/light/{color}")
async def control_light(color: str, duration: float = 0.5):
    """Control the device light"""
    global fingerprint_service
    if not fingerprint_service:
        raise HTTPException(status_code=503, detail="Fingerprint service not initialized")
    
    if color not in ["white", "green", "red"]:
        raise HTTPException(status_code=400, detail="Invalid color. Use: white, green, or red")
    
    try:
        fingerprint_service.light_device(color, duration)
        return {"message": f"Light turned {color} for {duration} seconds"}
    except Exception as e:
        logger.error(f"Error controlling light: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error controlling light: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global fingerprint_service
    return {
        "status": "healthy",
        "fingerprint_service": fingerprint_service is not None,
        "timestamp": datetime.now().isoformat()
    }

# Main function for running the app
def main():
    """Main function to run the FastAPI application"""
    import uvicorn
    from config import HOST, PORT

    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)

if __name__ == "__main__":
    main()

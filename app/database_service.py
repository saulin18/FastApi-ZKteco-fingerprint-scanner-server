import sys
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .models import Fingerprint, DeviceInfo
sys.dont_write_bytecode = True 


logger = logging.getLogger(__name__)


class DatabaseService:
    

    def __init__(self):
        self.logger = logging.getLogger("database_service")

    def store_fingerprint_data(
        self,
        db: Session,
        fingerprint_id: Optional[int],
        score: Optional[int],
        image_base64: str,
        template_data: str,
        device_serial: str,
        width: int,
        height: int,
    ) -> Fingerprint:
        
        try:
          
            fingerprint = Fingerprint(
                fingerprint_id=fingerprint_id,
                score=score,
                image_base64=image_base64,
                template_data=template_data,
                device_serial=device_serial,
                image_width=width,
                image_height=height,
                timestamp=datetime.utcnow(),
            )

            db.add(fingerprint)

          
            device_info = (
                db.query(DeviceInfo)
                .filter(DeviceInfo.device_serial == device_serial)
                .first()
            )

            if device_info:
                device_info.last_connected = datetime.utcnow()
                device_info.image_width = width
                device_info.image_height = height
                device_info.updated_at = datetime.utcnow()
            else:
                device_info = DeviceInfo(
                    device_serial=device_serial,
                    image_width=width,
                    image_height=height,
                    last_connected=datetime.utcnow(),
                )
                db.add(device_info)

            db.commit()
            db.refresh(fingerprint)

            self.logger.info(
                f"Fingerprint data stored successfully: ID {fingerprint.id}"
            )
            return fingerprint

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error storing fingerprint data: {str(e)}")
            raise Exception(f"Error storing fingerprint data: {str(e)}")

    def get_latest_fingerprint(self, db: Session) -> Optional[Dict[str, Any]]:
        
        try:
            fingerprint = (
                db.query(Fingerprint).order_by(desc(Fingerprint.timestamp)).first()
            )

            if fingerprint:
                return {
                    "id": fingerprint.id,
                    "fingerprint_id": fingerprint.fingerprint_id,
                    "score": fingerprint.score,
                    "image_base64": fingerprint.image_base64,
                    "template_data": fingerprint.template_data,
                    "device_serial": fingerprint.device_serial,
                    "image_width": fingerprint.image_width,
                    "image_height": fingerprint.image_height,
                    "timestamp": fingerprint.timestamp.isoformat(),
                }
            return None

        except Exception as e:
            self.logger.error(f"Error getting latest fingerprint: {str(e)}")
            raise Exception(f"Error getting latest fingerprint: {str(e)}")

    def get_fingerprint_history(
        self, db: Session, limit: int = 10
    ) -> List[Dict[str, Any]]:
       
        try:
            fingerprints = (
                db.query(Fingerprint)
                .order_by(desc(Fingerprint.timestamp))
                .limit(limit)
                .all()
            )

            return [
                {
                    "id": fp.id,
                    "fingerprint_id": fp.fingerprint_id,
                    "score": fp.score,
                    "image_base64": fp.image_base64,
                    "template_data": fp.template_data,
                    "device_serial": fp.device_serial,
                    "image_width": fp.image_width,
                    "image_height": fp.image_height,
                    "timestamp": fp.timestamp.isoformat(),
                }
                for fp in fingerprints
            ]

        except Exception as e:
            self.logger.error(f"Error getting fingerprint history: {str(e)}")
            raise Exception(f"Error getting fingerprint history: {str(e)}")

    def get_device_info(
        self, db: Session, device_serial: str
    ) -> Optional[Dict[str, Any]]:
        
        try:
            device_info = (
                db.query(DeviceInfo)
                .filter(DeviceInfo.device_serial == device_serial)
                .first()
            )

            if device_info:
                return {
                    "id": device_info.id,
                    "device_serial": device_info.device_serial,
                    "device_type": device_info.device_type,
                    "last_connected": device_info.last_connected.isoformat(),
                    "image_width": device_info.image_width,
                    "image_height": device_info.image_height,
                    "is_active": device_info.is_active,
                    "created_at": device_info.created_at.isoformat(),
                    "updated_at": device_info.updated_at.isoformat(),
                }
            return None

        except Exception as e:
            self.logger.error(f"Error getting device info: {str(e)}")
            raise Exception(f"Error getting device info: {str(e)}")


    def get_database_stats(self, db: Session) -> Dict[str, Any]:
        
        try:
            # Count total fingerprints
            total_fingerprints = db.query(Fingerprint).count()

            # Count unique devices
            unique_devices = db.query(
                func.count(func.distinct(Fingerprint.device_serial))
            ).scalar()

           

            # Get latest capture time
            latest_capture = (
                db.query(Fingerprint.timestamp)
                .order_by(desc(Fingerprint.timestamp))
                .first()
            )

            return {
                "total_fingerprints": total_fingerprints,
                "unique_devices": unique_devices,
                "latest_capture": latest_capture[0].isoformat()
                if latest_capture
                else None,
            }

        except Exception as e:
            self.logger.error(f"Error getting database stats: {str(e)}")
            raise Exception(f"Error getting database stats: {str(e)}")


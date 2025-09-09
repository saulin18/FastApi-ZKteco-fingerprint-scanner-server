
from io import BytesIO
# Import configuration
from config import LOG_LEVEL, LOG_FILE

import base64
import logging
from typing import Optional, Tuple

# pyzkfp includes its own DLL files, no need to add custom dll path

try:
    from PIL import Image
except ImportError:
    Image = None

# Use pyzkfp directly as in the official example
try:
    from pyzkfp import ZKFP2
    from pyzkfp._construct.errors_handler import *  # noqa: F403
    from System import Array, Byte  # Import .NET types
except ImportError:
    raise ImportError("pyzkfp not found. Please install with: pip install pyzkfp")



# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FingerprintService:
    """Service class for handling fingerprint device operations with improved logging"""
    
    def __init__(self):
        """Initialize the fingerprint service"""
        self.logger = logging.getLogger('fingerprint_service')
        
        # Add file handler for logging
        fh = logging.FileHandler(LOG_FILE)
        fh.setLevel(getattr(logging, LOG_LEVEL))
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)
        
        # Use ZKFP2 directly as in the official example
        self.zkfp2 = ZKFP2()
        self.devHandle: Optional[int] = None
        self.dbHandle: Optional[int] = None
        self.dev_serial_number: Optional[str] = None
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self._is_initialized = False
        
    
    def _handle_error(self, err_code: int):
        """Handle error codes from the fingerprint device"""
        error_mapping = {
            -25: (DeviceAlreadyConnectedError, "The device is already connected"),  # noqa: F405
            -24: (DeviceNotInitializedError, "The device is not initialized"),  # noqa: F405
            -23: (DeviceNotStartedError, "The device is not started"),  # noqa: F405
            -22: (FailedToCombineTemplatesError, "Failed to combine the registered fingerprint templates"),  # noqa: F405
            -20: (FingerprintComparisonFailedError, "Fingerprint comparison failed"),  # noqa: F405
            -18: (CaptureCancelledError, "Capture cancelled"),  # noqa: F405
            -17: (OperationFailedError, "Operation failed"),  # noqa: F405
            -14: (FailedToDeleteTemplateError, "Failed to delete the fingerprint template"),  # noqa: F405
            -13: (FailedToAddTemplateError, "Failed to add the fingerprint template"),  # noqa: F405
            -12: (FingerprintCapturedError, "The fingerprint is being captured"),  # noqa: F405
            -11: (InsufficientMemoryError, "Insufficient memory"),  # noqa: F405
            -10: (AbortedError, "Aborted"),  # noqa: F405
            -9: (FailedToExtractTemplateError, "Failed to extract the fingerprint template"),  # noqa: F405
            -8: (FailedToCaptureImageError, "Failed to capture the image"),  # noqa: F405
            -7: (InvalidHandleError, "Invalid Handle"),  # noqa: F405
            -6: (FailedToStartDeviceError, "Failed to start the device"),  # noqa: F405
            -5: (InvalidParameterError, "Invalid parameter"),  # noqa: F405
            -4: (NotSupportedError, "Not supported by the interface"),  # noqa: F405
            -3: (NoDeviceConnectedError, "No device connected"),  # noqa: F405
            -2: (CaptureLibraryInitializationError, "Failed to initialize the capture library"),  # noqa: F405
            -1: (AlgorithmLibraryInitializationError, "Failed to initialize the algorithm library"),  # noqa: F405
        }
        
        if err_code in error_mapping:
            error_class, error_message = error_mapping[err_code]
            self.logger.error(f"Device error {err_code}: {error_message}")
            raise error_class(error_message)
    
    def init_device(self) -> None:
        """Initialize the fingerprint device"""
        try:
            # Initialize the SDK
            self.zkfp2.Init()
            
            # Get device count
            device_count = self.zkfp2.GetDeviceCount()
            self.logger.info(f"{device_count} devices found. Connecting to the first device.")
            
            if device_count == 0:
                raise NoDeviceConnectedError("No fingerprint devices found")  # noqa: F405
            
            # Open the first device
            self.devHandle = self.zkfp2.OpenDevice(0)
            
            # Get device information
            self.dev_serial_number = self.zkfp2.dev_serial_number
            self.width = self.zkfp2.width
            self.height = self.zkfp2.height
            
            # Initialize database
            self.dbHandle = self.zkfp2.DBInit()
            
            self._is_initialized = True
            self.logger.info(f"Device initialized successfully. Serial: {self.dev_serial_number}")
            
            # Turn on green light to indicate ready
            self.light_device("green", 0.5)
            
        except Exception as e:
            self._is_initialized = False
            self.logger.error(f"Failed to initialize device: {str(e)}")
            raise Exception(f"Failed to initialize device: {str(e)}")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            if self.dbHandle:
                self.zkfp2.DBFree(self.dbHandle)
            if self.devHandle is not None:
                self.zkfp2.CloseDevice(self.devHandle)
            self.zkfp2.Terminate()
            self._is_initialized = False
            self.logger.info("Device cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def get_device_count(self) -> int:
        """Get the number of connected devices"""
        return self.zkfp2.GetDeviceCount()
    
    def is_device_connected(self) -> bool:
        """Check if device is connected and initialized"""
        return self._is_initialized and self.devHandle is not None
    
    def get_device_serial(self) -> Optional[str]:
        """Get device serial number"""
        return self.dev_serial_number
    
    def get_image_width(self) -> Optional[int]:
        """Get image width"""
        return self.width
    
    def get_image_height(self) -> Optional[int]:
        """Get image height"""
        return self.height
    
    def capture_fingerprint(self) -> Optional[Tuple[Array[Byte], bytes]]:
        """Capture a fingerprint and return template and image data"""
        if not self._is_initialized or self.devHandle is None:
            raise DeviceNotInitializedError("Device not initialized")  # noqa: F405
        
        try:
            # Use ZKFP2's AcquireFingerprint method as in the example
            capture = self.zkfp2.AcquireFingerprint()
            
            if capture:
                template, img = capture
                self.logger.info("Fingerprint captured successfully")
                return template, bytes(img)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error capturing fingerprint: {str(e)}")
            raise Exception(f"Error capturing fingerprint: {str(e)}")
    
    def capture_fingerprint_image(self) -> Optional[bytes]:
        """Capture only the fingerprint image"""
        if not self._is_initialized or self.devHandle is None:
            raise DeviceNotInitializedError("Device not initialized")
        
        try:
            imgBuffer = Array[Byte](self.width * self.height)
            ret = self.zkfp2.AcquireFingerprintImage(self.devHandle, imgBuffer)
            
            if ret == 0:  # Success
                self.logger.info("Fingerprint image captured successfully")
                return bytes(imgBuffer)
            elif ret == -8:  # No fingerprint detected
                return None
            else:
                self._handle_error(ret)
                
        except Exception as e:
            self.logger.error(f"Error capturing fingerprint image: {str(e)}")
            raise Exception(f"Error capturing fingerprint image: {str(e)}")
    

    
    def image_to_base64(self, image_data: bytes) -> str:
        """Convert image data to base64 string using ZKFP2's Blob2Base64String method"""
        try:
            if not isinstance(image_data, bytes):
                image_data = bytes(image_data)
            
            # Use ZKFP2's built-in method for better compatibility
            return self.zkfp2.Blob2Base64String(image_data)
                
        except Exception as e:
            self.logger.error(f"Error converting image to base64: {str(e)}")
            # Fallback to PIL method
            return self._image_to_base64_pil(image_data)
    
    def _image_to_base64_pil(self, image_data: bytes) -> str:
        """Fallback method using PIL for image to base64 conversion"""
        if Image is None:
            raise ImportError("PIL (Pillow) is required for image processing")
        
        try:
            # Create PIL image from bytes
            image = Image.frombytes("L", (self.width, self.height), image_data)
            
            # Convert to base64
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
            
        except Exception as e:
            raise Exception(f"Error converting image to base64 with PIL: {str(e)}")
    
    def template_to_base64(self, template: Array[Byte]) -> str:
        """Convert template data to base64 string"""
        try:
            if not isinstance(template, bytes):
                template = bytes(template)
            
            return base64.b64encode(template).decode("utf-8")
            
        except Exception as e:
            self.logger.error(f"Error converting template to base64: {str(e)}")
            raise Exception(f"Error converting template to base64: {str(e)}")
    
    def light_device(self, color: str, duration: float = 0.5) -> None:
        """Control device light"""
        if not self._is_initialized:
            raise DeviceNotInitializedError("Device not initialized")  # noqa: F405
        
        try:
            # Use ZKFP2's Light method as in the example
            self.zkfp2.Light(color, duration)
            
        except Exception as e:
            self.logger.error(f"Error controlling light: {str(e)}")
            raise Exception(f"Error controlling light: {str(e)}")
    
    def int_to_byte_array(self, value: int) -> bytes:
        """Convert integer to byte array"""
        buf = Array[Byte](4)
        result = self.zkfp2.Int2ByteArray(value, buf)
        if result:
            return buf
        else:
            raise Exception("Failed to convert integer to byte array")
    

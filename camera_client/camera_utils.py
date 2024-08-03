import cv2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def configure_camera(cap):
    """Configure camera settings."""
    try:
        if not cap.set(cv2.CAP_PROP_EXPOSURE, -6):
            logging.warning("Failed to set exposure to -6")
        if not cap.set(cv2.CAP_PROP_GAIN, 0):
            logging.warning("Failed to set gain to 0")
        
        # Verify settings
        actual_exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
        actual_gain = cap.get(cv2.CAP_PROP_GAIN)
        logging.info(f"Camera configured. Exposure: {actual_exposure}, Gain: {actual_gain}")
    except Exception as e:
        logging.error(f"Error in configure_camera: {str(e)}")
        raise

def init_camera(device_index):
    """Initialize and configure the camera."""
    try:
        cap = cv2.VideoCapture(device_index, cv2.CAP_AVFOUNDATION)
        if not cap.isOpened():
            raise IOError(f"Could not open camera with index {device_index}")
        
        configure_camera(cap)
        
        # Log camera properties
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        logging.info(f"Camera initialized. Resolution: {width}x{height}, FPS: {fps}")
        
        return cap
    except Exception as e:
        logging.error(f"Error in init_camera: {str(e)}")
        if 'cap' in locals() and cap is not None:
            cap.release()
        raise

def release_camera(cap):
    """Safely release camera resources."""
    if cap is not None:
        try:
            cap.release()
            logging.info("Camera released successfully")
        except Exception as e:
            logging.error(f"Error in release_camera: {str(e)}")
        finally:
            cv2.destroyAllWindows()
            logging.info("All OpenCV windows destroyed")
    else:
        logging.warning("Attempted to release a None camera object")
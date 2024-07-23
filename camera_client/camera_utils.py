import cv2

def configure_camera(cap):
    cap.set(cv2.CAP_PROP_EXPOSURE, -6)
    cap.set(cv2.CAP_PROP_GAIN, 0)

def init_camera(device_index):
    cap = cv2.VideoCapture(device_index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        raise Exception(f"Error: Could not open camera with index {device_index}.")
    configure_camera(cap)
    return cap

def release_camera(cap):
    cap.release()
    cv2.destroyAllWindows()

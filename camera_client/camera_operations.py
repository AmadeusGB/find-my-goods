import time
import cv2
import os
from datetime import datetime
from camera_utils import init_camera, release_camera
from image_processing import detect_motion, is_similar
from upload import upload_image

def capture_images(device_index, interval, duration, save_dir, threshold, min_contour_area, detection_interval, location, image_format):
    os.makedirs(save_dir, exist_ok=True)

    cap = init_camera(device_index)
    device_name = 'computer' if device_index == 1 else 'iphone'
    start_time = time.time()
    last_capture_time = 0
    last_detection_time = 0
    image_count = 0
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=100, detectShadows=True)
    prev_saved_image = None

    try:
        motion_frames = 0
        required_motion_frames = 3

        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"Error: Could not read frame from camera with index {device_index}.")
                break

            current_time = time.time()
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            if current_time - last_detection_time >= detection_interval:
                motion_detected = detect_motion(gray_frame, bg_subtractor, threshold=threshold, min_contour_area=min_contour_area)
                last_detection_time = current_time

                if motion_detected:
                    motion_frames += 1
                    if motion_frames >= required_motion_frames:
                        if prev_saved_image is None or not is_similar(prev_saved_image, frame):
                            image_path = os.path.join(save_dir, f'{location}_{device_name}_motion_photo_{image_count}.{image_format}')
                            cv2.imwrite(image_path, frame)  # Save image to disk
                            upload_image(image_path)  # Upload image
                            prev_saved_image = frame
                            image_count += 1
                        motion_frames = 0
                else:
                    motion_frames = 0

            if current_time - last_capture_time >= interval:
                if prev_saved_image is None or not is_similar(prev_saved_image, frame):
                    image_path = os.path.join(save_dir, f'{location}_{device_name}_interval_photo_{image_count}.{image_format}')
                    cv2.imwrite(image_path, frame)  # Save image to disk
                    upload_image(image_path)  # Upload image
                    prev_saved_image = frame
                    image_count += 1
                last_capture_time = current_time

            cv2.imshow(f'Camera {device_index}', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if current_time - start_time >= duration:
                break
    except KeyboardInterrupt:
        print("Capture interrupted by user.")
    finally:
        release_camera(cap)

def record_video(device_index, duration, save_dir, location):
    os.makedirs(save_dir, exist_ok=True)
    cap = init_camera(device_index)

    device_name = 'computer' if device_index == 1 else 'iphone'
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_path = os.path.join(save_dir, f'{location}_{device_name}_video_{timestamp}.mp4')

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(save_path, fourcc, 20.0, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    if not out.isOpened():
        print(f"Error: Could not open video writer with path {save_path}.")
        release_camera(cap)
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"Error: Could not read frame from camera with index {device_index}.")
                break

            out.write(frame)
            cv2.imshow(f'Camera {device_index}', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if time.time() - start_time >= duration:
                break
    except KeyboardInterrupt:
        print("Recording interrupted by user.")
    finally:
        out.release()
        release_camera(cap)
        print(f"Video saved as {save_path}")

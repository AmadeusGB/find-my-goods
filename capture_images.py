import cv2
import time
import os
import argparse
from datetime import datetime

def add_timestamp(frame, timestamp, sequence_number, location):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f'Time: {timestamp}', (10, 30), font, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, f'Seq: {sequence_number}', (10, 60), font, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, f'Location: {location}', (10, 90), font, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    return frame

def detect_motion(prev_gray, curr_gray, threshold=60, min_contour_area=4000):
    # 计算帧之间的差异
    frame_diff = cv2.absdiff(prev_gray, curr_gray)
    blurred_diff = cv2.GaussianBlur(frame_diff, (5, 5), 0)
    _, thresh = cv2.threshold(blurred_diff, threshold, 255, cv2.THRESH_BINARY)
    dilated_thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(dilated_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 检测是否有足够大的运动
    motion_detected = any(cv2.contourArea(contour) > min_contour_area for contour in contours)
    return motion_detected

def capture_images(device_index, interval=60, duration=600, save_dir='photos', threshold=60, min_contour_area=4000, detection_interval=1, location='unknown'):
    # 确保 photos 目录存在
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(device_index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {device_index}.")
        return

    device_name = 'computer' if device_index == 1 else 'iphone'
    start_time = time.time()
    last_capture_time = 0
    last_detection_time = 0
    image_count = 0

    ret, prev_frame = cap.read()
    if not ret:
        print("Error: Could not read initial frame from camera.")
        return

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Could not read frame from camera with index {device_index}.")
            break

        current_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if current_time - last_detection_time >= detection_interval:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
            motion_detected = detect_motion(prev_gray, gray_frame, threshold=threshold, min_contour_area=min_contour_area)
            last_detection_time = current_time

            if motion_detected:
                frame_with_timestamp = add_timestamp(frame.copy(), timestamp, image_count, location)
                save_path = os.path.join(save_dir, f'{location}_{device_name}_motion_photo_{image_count}.jpg')
                cv2.imwrite(save_path, frame_with_timestamp)
                print(f"Motion detected. Photo saved as {save_path}")
                image_count += 1

        if current_time - last_capture_time >= interval:
            frame_with_timestamp = add_timestamp(frame.copy(), timestamp, image_count, location)
            save_path = os.path.join(save_dir, f'{location}_{device_name}_interval_photo_{image_count}.jpg')
            cv2.imwrite(save_path, frame_with_timestamp)
            print(f"Interval capture. Photo saved as {save_path}")
            image_count += 1
            last_capture_time = current_time

        cv2.imshow(f'Camera {device_index}', frame)

        # 更新上一帧
        prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

        # 按 'q' 键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 运行到指定时长后退出
        if current_time - start_time >= duration:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture images from camera.')
    parser.add_argument('--device', type=int, required=True, help='Device index for the camera (e.g., 0 for iPhone, 1 for computer).')
    parser.add_argument('--interval', type=int, default=60, help='Interval between captures in seconds.')
    parser.add_argument('--duration', type=int, default=600, help='Total duration of capturing in seconds.')
    parser.add_argument('--threshold', type=int, default=60, help='Threshold for frame difference in motion detection.')
    parser.add_argument('--min_contour_area', type=int, default=4000, help='Minimum contour area for motion detection.')
    parser.add_argument('--detection_interval', type=int, default=1, help='Interval between motion detection checks in seconds.')
    parser.add_argument('--location', type=str, default='unknown', help='Location where the images are captured (e.g., bedroom, living_room).')
    args = parser.parse_args()

    capture_images(device_index=args.device, interval=args.interval, duration=args.duration, threshold=args.threshold, min_contour_area=args.min_contour_area, detection_interval=args.detection_interval, location=args.location)

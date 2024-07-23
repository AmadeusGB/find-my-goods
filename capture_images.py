import cv2
import time
import os
import argparse
from datetime import datetime

def add_timestamp(frame, timestamp, sequence_number, location):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0  # 增大字体大小
    font_thickness = 2  # 增加描边宽度
    text_color = (0, 255, 0)  # 文字颜色
    line_type = cv2.LINE_AA  # 线条类型

    cv2.putText(frame, f'Time: {timestamp}', (10, 30), font, font_scale, text_color, font_thickness, line_type)
    cv2.putText(frame, f'Seq: {sequence_number}', (10, 60), font, font_scale, text_color, font_thickness, line_type)
    cv2.putText(frame, f'Location: {location}', (10, 90), font, font_scale, text_color, font_thickness, line_type)
    return frame

def detect_motion(prev_gray, curr_gray, bg_subtractor, min_contour_area=4000):
    # 使用背景减除算法
    fg_mask = bg_subtractor.apply(curr_gray)
    blurred_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)
    _, thresh = cv2.threshold(blurred_mask, 200, 255, cv2.THRESH_BINARY)
    dilated_thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(dilated_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 检测是否有足够大的运动
    motion_detected = any(cv2.contourArea(contour) > min_contour_area for contour in contours)
    return motion_detected

def configure_camera(cap):
    # 设置曝光值（快门速度）和ISO值
    cap.set(cv2.CAP_PROP_EXPOSURE, -6)  # 尝试设置一个较低的曝光值
    cap.set(cv2.CAP_PROP_GAIN, 0)  # ISO值通常通过增益来控制

def capture_images(device_index, interval=60, duration=600, save_dir='photos', min_contour_area=4000, detection_interval=1, location='unknown', image_format='webp'):
    # 确保 photos 目录存在
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(device_index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {device_index}.")
        return

    configure_camera(cap)

    device_name = 'computer' if device_index == 1 else 'iphone'
    start_time = time.time()
    last_capture_time = 0
    last_detection_time = 0
    image_count = 0

    # 初始化背景减除器
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

    ret, prev_frame = cap.read()
    if not ret:
        print("Error: Could not read initial frame from camera.")
        return

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    try:
        motion_frames = 0
        required_motion_frames = 3  # 需要连续检测到运动的帧数

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
                motion_detected = detect_motion(prev_gray, gray_frame, bg_subtractor, min_contour_area=min_contour_area)
                last_detection_time = current_time

                if motion_detected:
                    motion_frames += 1
                    if motion_frames >= required_motion_frames:
                        frame_with_timestamp = add_timestamp(frame.copy(), timestamp, image_count, location)
                        save_path = os.path.join(save_dir, f'{location}_{device_name}_motion_photo_{image_count}.{image_format}')
                        cv2.imwrite(save_path, frame_with_timestamp)
                        print(f"Motion detected. Photo saved as {save_path}")
                        image_count += 1
                        motion_frames = 0  # 重置计数
                else:
                    motion_frames = 0

            if current_time - last_capture_time >= interval:
                frame_with_timestamp = add_timestamp(frame.copy(), timestamp, image_count, location)
                save_path = os.path.join(save_dir, f'{location}_{device_name}_interval_photo_{image_count}.{image_format}')
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
    except KeyboardInterrupt:
        print("Capture interrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def record_video(device_index, duration=600, save_dir='videos', location='unknown'):
    os.makedirs(save_dir, exist_ok=True)
    cap = cv2.VideoCapture(device_index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {device_index}.")
        return

    configure_camera(cap)

    device_name = 'computer' if device_index == 1 else 'iphone'
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_path = os.path.join(save_dir, f'{location}_{device_name}_video_{timestamp}.mp4')

    # 使用MP4编码器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(save_path, fourcc, 20.0, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    if not out.isOpened():
        print(f"Error: Could not open video writer with path {save_path}.")
        cap.release()
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
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"Video saved as {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture images or record video from camera.')
    parser.add_argument('--device', type=int, required=True, help='Device index for the camera (e.g., 0 for iPhone, 1 for computer).')
    parser.add_argument('--mode', type=str, required=True, choices=['photo', 'video'], help='Mode of operation: photo or video.')
    parser.add_argument('--interval', type=int, default=60, help='Interval between captures in seconds (only for photo mode).')
    parser.add_argument('--duration', type=int, default=600, help='Total duration of capturing/recording in seconds.')
    parser.add_argument('--threshold', type=int, default=60, help='Threshold for frame difference in motion detection (only for photo mode).')
    parser.add_argument('--min_contour_area', type=int, default=4000, help='Minimum contour area for motion detection (only for photo mode).')
    parser.add_argument('--detection_interval', type=int, default=1, help='Interval between motion detection checks in seconds (only for photo mode).')
    parser.add_argument('--location', type=str, default='unknown', help='Location where the images or video are captured (e.g., bedroom, living_room).')
    parser.add_argument('--image_format', type=str, default='webp', help='Format to save images (e.g., jpg, webp).')
    args = parser.parse_args()

    if args.mode == 'photo':
        capture_images(device_index=args.device, interval=args.interval, duration=args.duration, min_contour_area=args.min_contour_area, detection_interval=args.detection_interval, location=args.location, image_format=args.image_format)
    elif args.mode == 'video':
        record_video(device_index=args.device, duration=args.duration, location=args.location)

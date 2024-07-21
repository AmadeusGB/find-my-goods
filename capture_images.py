import cv2
import time
import os
import argparse

def capture_images(device_index, interval=1, duration=10, save_dir='photos'):
    # 确保 photos 目录存在
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(device_index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {device_index}.")
        return

    start_time = time.time()
    last_capture_time = 0
    image_count = 0

    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow(f'Camera {device_index}', frame)
            current_time = time.time()

            if current_time - last_capture_time >= interval:
                # 每秒钟拍摄一张图片
                device_name = 'computer' if device_index == 1 else 'iphone'
                save_path = os.path.join(save_dir, f'{device_name}_photo_{image_count}.jpg')
                cv2.imwrite(save_path, frame)
                print(f"Photo saved as {save_path}")
                image_count += 1
                last_capture_time = current_time

            # 按 'q' 键退出循环
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # 运行到指定时长后退出
            if current_time - start_time >= duration:
                break
        else:
            print(f"Error: Could not read frame from camera with index {device_index}.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture images from camera.')
    parser.add_argument('--device', type=int, required=True, help='Device index for the camera (e.g., 0 for iPhone, 1 for computer).')
    parser.add_argument('--interval', type=int, default=1, help='Interval between captures in seconds.')
    parser.add_argument('--duration', type=int, default=10, help='Total duration of capturing in seconds.')
    args = parser.parse_args()

    capture_images(device_index=args.device, interval=args.interval, duration=args.duration)

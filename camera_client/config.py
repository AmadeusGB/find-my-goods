import argparse

def parse_args():
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
    return parser.parse_args()

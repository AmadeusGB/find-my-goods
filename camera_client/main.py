from config import parse_args
from camera_operations import capture_images, record_video

if __name__ == "__main__":
    args = parse_args()

    if args.mode == 'photo':
        capture_images(device_index=args.device, interval=args.interval, duration=args.duration, save_dir='photos',
                       threshold=args.threshold, min_contour_area=args.min_contour_area,
                       detection_interval=args.detection_interval, location=args.location,
                       image_format=args.image_format)
    elif args.mode == 'video':
        record_video(device_index=args.device, duration=args.duration, save_dir='videos', location=args.location)

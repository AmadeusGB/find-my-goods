import sys
import logging
from config import parse_args
from camera_operations import capture_images, record_video

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        args = parse_args()
        
        if args.mode == 'photo':
            logging.info("Starting photo capture mode")
            capture_images(
                device_index=args.device,
                interval=args.interval,
                duration=args.duration,
                save_dir='photos',
                threshold=args.threshold,
                min_contour_area=args.min_contour_area,
                detection_interval=args.detection_interval,
                location=args.location,
                image_format=args.image_format
            )
        elif args.mode == 'video':
            logging.info("Starting video recording mode")
            record_video(
                device_index=args.device,
                duration=args.duration,
                save_dir='videos',
                location=args.location
            )
        else:
            raise ValueError(f"Invalid mode: {args.mode}")

    except ValueError as ve:
        logging.error(f"Value Error: {ve}")
        sys.exit(1)
    except IOError as ioe:
        logging.error(f"IO Error: {ioe}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
    else:
        logging.info("Operation completed successfully")

if __name__ == "__main__":
    main()
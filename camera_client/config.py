import argparse

def parse_args():
    """Parse command line arguments efficiently."""
    parser = argparse.ArgumentParser(description='Capture images or record video from camera.')
    
    # Use a dictionary to define arguments for more efficient setup
    args_config = {
        'device': {'type': int, 'required': True, 'help': 'Device index for the camera (e.g., 0 for iPhone, 1 for computer).'},
        'mode': {'type': str, 'required': True, 'choices': ['photo', 'video'], 'help': 'Mode of operation: photo or video.'},
        'interval': {'type': int, 'default': 60, 'help': 'Interval between captures in seconds (only for photo mode).'},
        'duration': {'type': int, 'default': 600, 'help': 'Total duration of capturing/recording in seconds.'},
        'threshold': {'type': int, 'default': 60, 'help': 'Threshold for frame difference in motion detection (only for photo mode).'},
        'min_contour_area': {'type': int, 'default': 4000, 'help': 'Minimum contour area for motion detection (only for photo mode).'},
        'detection_interval': {'type': int, 'default': 1, 'help': 'Interval between motion detection checks in seconds (only for photo mode).'},
        'location': {'type': str, 'default': 'unknown', 'help': 'Location where the images or video are captured (e.g., bedroom, living_room).'},
        'image_format': {'type': str, 'default': 'webp', 'help': 'Format to save images (e.g., jpg, webp).'}
    }
    
    # Add arguments efficiently
    for arg, config in args_config.items():
        parser.add_argument(f'--{arg}', **config)
    
    try:
        args = parser.parse_args()
        
        # Basic type checking and validation
        if args.interval <= 0 or args.duration <= 0 or args.threshold <= 0 or args.min_contour_area <= 0 or args.detection_interval <= 0:
            raise ValueError("All numeric arguments must be positive.")
        
        return args
    except argparse.ArgumentError as e:
        print(f"Error: {str(e)}")
        parser.print_help()
        raise
    except ValueError as e:
        print(f"Error: {str(e)}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        raise
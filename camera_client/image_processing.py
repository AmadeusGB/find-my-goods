import cv2
from datetime import datetime
from skimage.metrics import structural_similarity as ssim
import os

def add_timestamp(frame, timestamp, sequence_number, location):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    font_thickness = 2
    text_color = (0, 255, 0)
    line_type = cv2.LINE_AA

    cv2.putText(frame, f'Time: {timestamp}', (10, 30), font, font_scale, text_color, font_thickness, line_type)
    cv2.putText(frame, f'Seq: {sequence_number}', (10, 60), font, font_scale, text_color, font_thickness, line_type)
    cv2.putText(frame, f'Location: {location}', (10, 90), font, font_scale, text_color, font_thickness, line_type)
    return frame

def detect_motion(curr_gray, bg_subtractor, threshold=60, min_contour_area=4000):
    fg_mask = bg_subtractor.apply(curr_gray)
    blurred_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)
    _, thresh = cv2.threshold(blurred_mask, threshold, 255, cv2.THRESH_BINARY)
    dilated_thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(dilated_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = any(cv2.contourArea(contour) > min_contour_area for contour in contours)
    return motion_detected

def is_similar(image1, image2, similarity_threshold=0.85):
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(gray1, gray2, full=True)
    return score > similarity_threshold

def save_image(frame, save_dir, location, device_name, image_count, image_format, motion_type):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    frame_with_timestamp = add_timestamp(frame.copy(), timestamp, image_count, location)
    save_path = os.path.join(save_dir, f'{location}_{device_name}_{motion_type}_photo_{image_count}.{image_format}')
    cv2.imwrite(save_path, frame_with_timestamp)
    print(f"Photo saved as {save_path}")
    return frame_with_timestamp

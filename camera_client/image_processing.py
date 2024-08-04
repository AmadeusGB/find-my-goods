import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def detect_motion(curr_gray, bg_subtractor, threshold=60, min_contour_area=4000):
    try:
        fg_mask = bg_subtractor.apply(curr_gray)
        
        # 使用 NumPy 操作替代 OpenCV 函数以提高效率
        blurred_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)
        thresh = np.where(blurred_mask > threshold, 255, 0).astype(np.uint8)
        
        # 使用更高效的形态学操作
        kernel = np.ones((3,3), np.uint8)
        dilated_thresh = cv2.dilate(thresh, kernel, iterations=2)
        
        # 使用 RETR_EXTERNAL 为 findContours 提供更好的性能
        contours, _ = cv2.findContours(dilated_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 使用 any 和生成器表达式提高效率
        motion_detected = any(cv2.contourArea(contour) > min_contour_area for contour in contours)
        
        return motion_detected
    except Exception as e:
        logging.error(f"Error in detect_motion: {str(e)}")
        return False

def is_similar(image1, image2, similarity_threshold=0.85):
    try:
        # 预先转换为灰度可能会提高 SSIM 的速度
        if len(image1.shape) == 3:
            gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        else:
            gray1 = image1
        
        if len(image2.shape) == 3:
            gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        else:
            gray2 = image2
        
        score, _ = ssim(gray1, gray2, full=True)
        return score > similarity_threshold
    except Exception as e:
        logging.error(f"Error in is_similar: {str(e)}")
        return False

def save_image(frame, save_dir, location, device_name, image_count, image_format, motion_type):
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        save_path = os.path.join(save_dir, f'{location}_{device_name}_{motion_type}_photo_{image_count}.{image_format}')
        
        # 使用 IMWRITE_JPEG_QUALITY 参数来控制 JPEG 压缩质量，可能会提高保存速度
        if image_format.lower() == 'jpg':
            cv2.imwrite(save_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        else:
            cv2.imwrite(save_path, frame)
        
        logging.info(f"Photo saved as {save_path}")
        return frame
    except Exception as e:
        logging.error(f"Error saving image: {str(e)}")
        return None
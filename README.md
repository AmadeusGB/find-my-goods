# find-my-goods

[English](README.md) | [中文](README_ZH.md)

## Project Overview

The aim of the `find-my-goods` project is to build a distributed camera monitoring and analysis system based on Python and OpenCV. By leveraging cloud storage and the GPT-4o API, it can analyze images to answer user queries. The system comprises four main modules: the Camera Client (`camera_client`), the GPT Dialogue Client (`gpt_client`), the Photo Storage and Management Server (`photos_api_server`), and the GPT Processing Server (`gpt_processing_server`).

### Features Overview

1. **Real-Time Monitoring and Recording**:
   - Utilize multiple cameras to continuously monitor and record different rooms in the house in real-time. The system can capture and store high-definition images and videos, ensuring users can check the home environment anytime.
   - Use Cases: Home security monitoring, real-time care for the elderly and children.

2. **Intelligent Query and Response**:
   - Users can ask the system about the location of items or other events in the home via voice or text. The system analyzes historical videos and key images to provide accurate answers.
   - Example Questions: “Where is my water bottle?”, “Who moved my pizza yesterday?”. The system can accurately locate items or events through image recognition and event detection.
   - Use Cases: Item tracking, event review.

3. **Event Push and Reporting**:
   - The system can identify and report various events happening in the home, such as item movements, stranger intrusions, animal disturbances, etc.
   - Example Scenarios: The system can inform the user, “Your shoes were taken to the bathroom for washing yesterday” or “A wild cat entered the house and took the pizza”.
   - Use Cases: Home security, pet monitoring.

4. **Fridge Inventory Management**:
   - Install a camera inside the fridge, and the system will periodically report the usage of food items, reminding users to replenish necessary items.
   - Example Functionality: The system can notify the user, “The milk in the fridge is running low, consider buying new milk”.
   - Use Cases: Smart home management, food inventory management.

5. **Baby Behavior Monitoring**:
   - Install a camera in the baby’s room, and the system will analyze and push alerts to the user if the baby exhibits dangerous behavior.
   - Example Functionality: The system can immediately send an alert to parents' phones if the baby falls from the bed.
   - Use Cases: Baby safety monitoring, child care.

6. **Yard Monitoring**:
   - Install cameras around the yard, and the system can summarize and report events happening around the yard during the week, such as strangers passing by or animal disturbances.
   - Example Functionality: The system can inform the user, “Several kittens played in your backyard this week” or “A bear turned over the trash bin”.
   - Use Cases: Home perimeter security monitoring, animal activity monitoring.

7. **Data Privacy and Security**:
   - The system prioritizes user privacy and data security when processing data. All image data is stored in the cloud, accessible only to authorized users.
   - The system supports future local model processing, ensuring complete offline data analysis when computing power is sufficient, further enhancing privacy.

8. **User Friendliness**:
   - The system offers a simple and easy-to-use interface, allowing users to interact with the system via voice or text to obtain the needed information.
   - Supports multi-device access, enabling users to view and manage home monitoring data anytime via phone, tablet, or computer.

This project not only provides efficient monitoring and management tools for the home but also enhances the safety and convenience of home life through intelligent analysis and push mechanisms.

## Directory Structure

```
.
├── camera_client
│   ├── main.py
│   ├── camera_utils.py
│   ├── image_processing.py
│   ├── upload.py
│   ├── config.py
│   └── logger.py
├── gpt_client
│   ├── main.py
│   ├── audio_processing.py
│   ├── request_handler.py
│   ├── config.py
│   └── logger.py
├── photos_api_server
│   ├── app.py
│   ├── storage.py
│   ├── models.py
│   ├── config.py
│   ├── logger.py
│   └── monitor.py
├── gpt_processing_server
│   ├── app.py
│   ├── gpt_api.py
│   ├── config.py
│   ├── logger.py
│   └── monitor.py
├── README.md
└── requirements.txt
```

## Installation Dependencies

Before running the code, please ensure the following dependencies are installed:

- Python 3.9
- OpenCV
- Flask
- Boto3
- SQLAlchemy
- skimage
- requests
- python-dotenv

You can install all dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Module Descriptions

### Camera Client (camera_client)

Handles camera-related operations, including capturing images or videos and uploading them to the server.

- **Main Functions**:
  - Capture images or videos
  - Preprocess images (e.g., add timestamps, motion detection)
  - Upload processed images to cloud storage

- **File Descriptions**:
  - `main.py`: Main entry point, handles command-line arguments and invokes corresponding functions.
  - `camera_utils.py`: Handles camera-related operations such as initializing and configuring the camera.
  - `image_processing.py`: Contains image processing functions such as motion detection and image similarity detection.
  - `upload.py`: Uploads processed images to cloud storage.
  - `config.py`: Configuration file.
  - `logger.py`: Logging module.

- **Usage Examples**:
  - Capture photos using a computer camera:
    ```bash
    python3.9 camera_client/main.py --device 0 --mode photo --interval 60 --duration 600 --location bedroom
    ```

  - Record videos using an iPhone 11 camera:
    ```bash
    python3.9 camera_client/main.py --device 1 --mode video --duration 600 --location living_room
    ```

### GPT Dialogue Client (gpt_client)

Handles user input (text or voice), sends requests to the server, and receives processing results.

- **Main Functions**:
  - Accept user input (text or voice)
  - Send input requests to the GPT processing server
  - Receive and display processing results

- **File Descriptions**:
  - `main.py`: Main entry point, handles command-line arguments and invokes corresponding functions.
  - `audio_processing.py`: Handles voice processing functions such as speech recognition and speech-to-text conversion.
  - `request_handler.py`: Handles user requests, sends requests to the server, and receives responses.
  - `config.py`: Configuration file.
  - `logger.py`: Logging module.

- **Usage Examples**:
  - Ask a question via text and get image analysis results:
    ```bash
    python3.9 gpt_client/v1.py
    ```

### Photo Storage and Management Server (photos_api_server)

Handles receiving images from clients, storing them in the cloud, and providing API interfaces to query and retrieve images.

- **Main Functions**:
  - Receive and store images
  - Provide API interfaces to query and retrieve images
  - Manage image metadata

- **File Descriptions**:
  - `app.py`: Main entry point, starts the Flask server.
  - `storage.py`: Handles image storage functions such as uploading, downloading, and deleting images.
  - `models.py`: Manages image metadata using SQLAlchemy.
  - `config.py`: Configuration file.
  - `logger.py`: Logging module.
  - `monitor.py`: Monitoring module, monitors the server's running status.

- **Running Example**:
  - Start the photo storage and management server:
    ```bash
    uvicorn gpt_processing_server.v6:app --reload
    ```

### GPT Processing Server (gpt_processing_server)

Handles receiving requests from clients, retrieving required images, calling the GPT-4 API for processing, and returning results.

- **Main Functions**:
  - Receive requests from clients
  - Retrieve images from the photo storage server
  - Call the GPT-4 API for image analysis
  - Return processing results

- **File Descriptions**:
  - `app.py`: Main entry point, starts the Flask server.
  - `gpt_api.py`: GPT-4 API call module, handles image analysis requests.
  - `config.py`: Configuration file.
  - `logger.py`: Logging module.
  - `monitor.py`: Monitoring module, monitors the server's running status.

- **Running Example**:
  - Start the GPT processing server:
    ```bash
    python3.9 gpt_processing_server/app.py
    ```

## Command-Line Parameters

Below is a detailed explanation of the command-line parameters:

- `--device`: Specifies the camera device index (0 for computer camera, 1 for iPhone 11 camera, 2 for iPhone 13 camera).
  
  **Explanation**: This parameter is used to select which camera device to use for capturing photos or videos.
  
  **Advantages**: Allows flexible selection of different camera devices for capturing photos or videos.
  
  **Disadvantages**: Requires knowing the device index, otherwise the correct camera may not be selected.

- `--mode`: Specifies the operation mode, `photo` for photo mode, `video` for video recording mode.
  
  **Explanation**: This parameter is used to specify the tool's operation mode, whether to capture photos or record videos.
  
  **Advantages**:

 Allows choosing between photo capture and video recording based on needs.
  
  **Disadvantages**: Requires specifying the operation mode clearly.

- `--interval`: Specifies the interval between captures in seconds (only applicable for photo mode, default is 60 seconds).
  
  **Explanation**: This parameter is used to set the time interval between each photo capture.
  
  **Advantages**: Timed captures ensure photos are taken at fixed intervals, facilitating time-series analysis.
  
  **Disadvantages**: If set too short, it may generate a large number of photos, occupying storage space; if set too long, important changes may be missed.

- `--duration`: Specifies the total duration of capturing/recording in seconds (default is 600 seconds).
  
  **Explanation**: This parameter is used to set the total duration for capturing photos or recording videos.
  
  **Advantages**: Controls the total capturing or recording time, making it convenient for testing and management.
  
  **Disadvantages**: If set too long, it may generate a large amount of data, occupying storage space.

- `--threshold`: Specifies the frame difference threshold for motion detection (only applicable for photo mode, default is 60).
  
  **Explanation**: This parameter is used to set the frame difference threshold for detecting motion.
  
  **Advantages**: Allows adjusting the sensitivity of motion detection; the higher the threshold, the less sensitive the motion detection.
  
  **Disadvantages**: If set too high, subtle motions may be missed; if set too low, it may be too sensitive to slight changes.

- `--min_contour_area`: Specifies the minimum contour area for motion detection (only applicable for photo mode, default is 4000).
  
  **Explanation**: This parameter is used to set the minimum contour area for detecting motion.
  
  **Advantages**: Allows adjusting the sensitivity of motion detection; the larger the contour area threshold, the less sensitive the motion detection.
  
  **Disadvantages**: If set too high, small area motions may be missed; if set too low, it may be too sensitive to small area changes.

- `--detection_interval`: Specifies the interval between motion detection checks in seconds (only applicable for photo mode, default is 1 second).
  
  **Explanation**: This parameter is used to set the time interval for each motion detection check.
  
  **Advantages**: Reduces the frequency of motion detection, thus reducing computation and resource usage.
  
  **Disadvantages**: If set too long, quickly occurring motions may be missed.

- `--location`: Specifies the location where the photos or videos are captured (default is 'unknown').
  
  **Explanation**: This parameter is used to add location information to the images or videos.
  
  **Advantages**: Allows adding location information to images and videos, making it convenient for subsequent location-based classification and analysis.
  
  **Disadvantages**: If the location is set inaccurately, it may mislead the analysis.

- `--image_format`: Specifies the format to save images (only applicable for photo mode, default is 'jpg').
  
  **Explanation**: This parameter is used to set the file format for saving images.
  
  **Advantages**: Allows choosing more efficient image formats like WebP to save storage space and provide better image quality.
  
  **Disadvantages**: Some older devices or software may not support modern image formats like WebP.

## Examples

Here are some usage examples:

- Capture photos using a computer camera with a minimum contour area of 4000, frame difference threshold of 60, and detection interval of 1 second:

  ```bash
  python3.9 camera_client/main.py --device 0 --mode photo --interval 60 --duration 600 --threshold 60 --min_contour_area 4000 --detection_interval 1 --location bedroom --image_format jpg
  ```

- Capture photos using an iPhone 11 camera with a minimum contour area of 5000, frame difference threshold of 70, and detection interval of 2 seconds:

  ```bash
  python3.9 camera_client/main.py --device 1 --mode photo --interval 60 --duration 600 --threshold 70 --min_contour_area 5000 --detection_interval 2 --location living_room --image_format jpg
  ```

- Capture photos using an iPhone 13 camera with a minimum contour area of 5000, frame difference threshold of 70, and detection interval of 2 seconds:

  ```bash
  python3.9 camera_client/main.py --device 2 --mode photo --interval 60 --duration 600 --threshold 70 --min_contour_area 5000 --detection_interval 2 --location living_room --image_format jpg
  ```

- Record videos using a computer camera for 600 seconds, location set to bedroom:

  ```bash
  python3.9 camera_client/main.py --device 0 --mode video --duration 600 --location bedroom
  ```

- Record videos using an iPhone 11 camera for 600 seconds, location set to living_room:

  ```bash
  python3.9 camera_client/main.py --device 1 --mode video --duration 600 --location living_room
  ```

- Record videos using an iPhone 13 camera for 600 seconds, location set to living_room:

  ```bash
  python3.9 camera_client/main.py --device 2 --mode video --duration 600 --location living_room
  ```

## Architecture Description

### Camera Client (camera_client)

Handles camera-related operations, including capturing images or videos and uploading them to the server.

- **Architecture Diagram**:

  ```
  +-----------------+
  |  main.py        |
  +-----------------+
          |
          v
  +-----------------+
  |  camera_utils.py|
  +-----------------+
          |
          v
  +-----------------+
  |image_processing.py|
  +-----------------+
          |
          v
  +-----------------+
  |  upload.py      |
  +-----------------+
  ```

- **Interaction Process**:
  1. `main.py` processes command-line arguments and calls `camera_utils.py` to start the camera.
  2. `camera_utils.py` is responsible for initializing and configuring the camera, capturing images, and passing them to `image_processing.py`.
  3. `image_processing.py` performs image preprocessing, such as motion detection and image similarity detection.
  4. Processed images are uploaded to cloud storage through `upload.py`.

### GPT Dialogue Client (gpt_client)

Handles user input (text or voice), sends requests to the server, and receives processing results.

- **Architecture Diagram**:

  ```
  +-----------------+
  |  main.py        |
  +-----------------+
          |
          v
  +-----------------+
  |audio_processing.py|
  +-----------------+
          |
          v
  +-----------------+
  |request_handler.py|
  +-----------------+
  ```

- **Interaction Process**:
  1. `main.py` processes command-line arguments and user input, calling `audio_processing.py` for speech recognition if needed.
  2. `audio_processing.py` converts speech to text and passes it to `request_handler.py`.
  3. `request_handler.py` sends user questions and image requests to the GPT processing server and receives processing results.

### Photo Storage and Management Server (photos_api_server)

Handles receiving images from clients, storing them in the cloud, and providing API interfaces to query and retrieve images.

- **Architecture Diagram**:

  ```
  +-----------------+
  |  app.py         |
  +-----------------+
          |
          v
  +-----------------+
  |  storage.py     |
  +-----------------+
          |
          v
  +-----------------+
  |  models.py      |
  +-----------------+
  ```

- **Interaction Process**:
  1. `app.py` starts the Flask server and receives image upload requests from clients.
  2. `storage.py` handles image storage and management.
  3. `models.py` uses SQLAlchemy to manage image metadata and provides query interfaces.

### GPT Processing Server (gpt_processing_server)

Handles receiving requests from clients, retrieving required images, calling the GPT-4 API for processing, and returning results.

- **Architecture Diagram**:

  ```
  +-----------------+
  |  app.py         |
  +-----------------+
          |
          v
  +-----------------+
  |  gpt_api.py     |
  +-----------------+
  ```

- **Interaction Process**:
  1. `app.py` starts the Flask server and receives requests from clients.
  2. `gpt_api.py` handles the requests, calls the GPT-4 API for image analysis, and returns the results.

## Considerations

- Ensure that the Python interpreter has camera access permissions when running the camera client script. This can be set in macOS “System Preferences” -> “Security & Privacy” -> “Privacy” -> “Camera”.
- Close other applications that might be using the camera (e.g., Photo Booth) before running the code.
- Adjust parameters as needed to achieve the best results.

## Feedback

If you encounter any issues while using the system, please provide detailed error information for further analysis and troubleshooting.

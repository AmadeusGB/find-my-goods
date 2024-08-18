# find-my-goods

[English](README.md) | [中文](README_ZH.md)

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Use Cases](#use-cases)
4. [System Architecture](#system-architecture)
5. [Installation](#installation)
6. [Usage](#usage)
   - [Camera Client](#camera-client)
   - [GPT Client](#gpt-client)
   - [GPT Processing Server](#gpt-processing-server)
7. [Configuration](#configuration)
8. [Database Schema](#database-schema)
9. [API Endpoints](#api-endpoints)
10. [Image Processing](#image-processing)
11. [Performance Considerations](#performance-considerations)
12. [Security and Privacy](#security-and-privacy)
13. [Troubleshooting](#troubleshooting)
14. [Contributing](#contributing)
15. [License](#license)

## Project Overview

find-my-goods is an advanced, distributed camera monitoring and analysis system built with Python. It leverages cloud storage, computer vision techniques, and the power of GPT-4 API to provide real-time monitoring, intelligent querying, and comprehensive analysis of home environments.

The system is designed to capture images or videos from multiple camera sources, process them for motion detection and other relevant features, store them efficiently, and allow users to query about objects, events, or situations in their home using natural language.

## Features

1. **Multi-Camera Support**: 
   - Compatible with computer webcams, iPhone 11, and iPhone 13 cameras.
   - Extensible architecture for easy addition of new camera types.

2. **Flexible Capture Modes**:
   - Photo mode with customizable interval and duration.
   - Video mode with adjustable recording length.

3. **Intelligent Motion Detection**:
   - Utilizes OpenCV for efficient frame differencing and contour analysis.
   - Customizable thresholds for motion sensitivity and minimum contour area.

4. **Cloud Storage Integration**:
   - Seamless upload of captured images to cloud storage.
   - Efficient metadata management using PostgreSQL.

5. **Advanced Image Analysis**:
   - Integration with GPT-4 API for sophisticated image understanding and question answering.
   - CLIP model integration for generating image feature vectors, enabling semantic search capabilities.

6. **Natural Language Querying**:
   - User-friendly interface for asking questions about the home environment.
   - Intelligent retrieval of relevant images based on query content.

7. **Real-time Processing**:
   - Asynchronous handling of image uploads and processing tasks.
   - Event-driven architecture using PostgreSQL notifications for real-time updates.

8. **Scalable Architecture**:
   - Designed to handle multiple cameras and high volumes of data.
   - Separation of concerns between client, processing server, and database for improved scalability.

## Use Cases

1. **Real-Time Monitoring and Recording**:
   - Continuously monitor and record different rooms in the house using multiple cameras.
   - Capture and store high-definition images and videos for anytime access.
   - Use cases: Home security monitoring, real-time care for the elderly and children.

2. **Intelligent Query and Response**:
   - Ask the system about the location of items or events in the home via voice or text.
   - The system analyzes historical videos and key images to provide accurate answers.
   - Example questions: "Where is my water bottle?", "Who moved my pizza yesterday?"
   - Use cases: Item tracking, event review.

3. **Event Push and Reporting**:
   - Identify and report various events happening in the home, such as item movements, stranger intrusions, or animal disturbances.
   - Example scenarios: "Your shoes were taken to the bathroom for washing yesterday" or "A wild cat entered the house and took the pizza".
   - Use cases: Home security, pet monitoring.

4. **Fridge Inventory Management**:
   - Install a camera inside the fridge to periodically report on food item usage and remind users to replenish necessary items.
   - Example functionality: "The milk in the fridge is running low, consider buying new milk".
   - Use cases: Smart home management, food inventory management.

5. **Baby Behavior Monitoring**:
   - Install a camera in the baby's room to analyze and push alerts for dangerous behavior in real-time.
   - Example functionality: Immediately send an alert to parents' phones if the baby falls from the bed.
   - Use cases: Baby safety monitoring, child care.

6. **Yard Monitoring**:
   - Install cameras around the yard to summarize and report events happening around the yard during the week.
   - Example functionality: "Several kittens played in your backyard this week" or "A bear turned over the trash bin".
   - Use cases: Home perimeter security monitoring, animal activity monitoring.

## System Architecture

The system consists of four main components:

1. **Camera Client (camera_client)**:
   - Responsible for capturing images or videos from various camera sources.
   - Handles motion detection and initial image processing.
   - Uploads captured data to the cloud storage.

2. **GPT Client (gpt_client)**:
   - Provides a user interface for submitting queries about the home environment.
   - Communicates with the GPT Processing Server to get responses.

3. **GPT Processing Server (gpt_processing_server)**:
   - Serves as the central hub for processing user queries.
   - Integrates with the GPT-4 API for advanced image analysis.
   - Manages image retrieval and ranking based on relevance to the query.

4. **PostgreSQL Database**:
   - Stores metadata about captured images, including timestamps, locations, and feature vectors.
   - Enables efficient querying and retrieval of relevant images.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/find-my-goods.git
   cd find-my-goods
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database:
   - Install PostgreSQL if not already installed.
   - Create a new database for the project.
   - Run the initialization script:
     ```
     psql -d your_database_name -f sql/init.sql
     ```

5. Set up environment variables:
   - Create a `.env` file in the project root directory:
     ```
     touch .env
     ```
   - Open the `.env` file in a text editor and add the following variables:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     DATABASE_URL=postgres://username:password@localhost:5432/database_name
     PGUSER=your_postgres_username
     PGPASSWORD=your_postgres_password
     PGDATABASE=your_postgres_database_name
     PGSSLMODE=disable
     PHOTOS_API_URL=http://localhost:5001/api/photos
     PHOTOS_DIR=photos
     LOG_LEVEL=INFO
     DB_POOL_MIN_SIZE=1
     DB_POOL_MAX_SIZE=10
     ```
   - Replace the placeholder values with your actual configuration details:
     - `your_openai_api_key_here`: Your OpenAI API key for GPT-4 access
     - `username`: Your PostgreSQL username
     - `password`: Your PostgreSQL password
     - `database_name`: Your PostgreSQL database name
     - Adjust other values as needed for your setup

   Note: Keep your `.env` file secure and never commit it to version control.

## Usage

### Camera Client

The camera client can be run with various options to customize the capture process:

```bash
python camera_client/main.py --device 0 --mode photo --interval 60 --duration 600 --location bedroom --threshold 60 --min_contour_area 4000 --detection_interval 1 --image_format jpg
```

Options:
- `--device`: Camera device index (0 for computer, 1 for iPhone 11, 2 for iPhone 13)
- `--mode`: 'photo' or 'video'
- `--interval`: Interval between captures in seconds (photo mode only)
- `--duration`: Total duration of capturing/recording in seconds
- `--location`: Location of capture (e.g., bedroom, living_room)
- `--threshold`: Frame difference threshold for motion detection
- `--min_contour_area`: Minimum contour area for motion detection
- `--detection_interval`: Interval between motion detection checks in seconds
- `--image_format`: Format to save images (e.g., jpg, webp)

### GPT Client

To ask a question about your home environment:

```bash
python gpt_client/main.py "Where is my water bottle?"
```

The client will send the query to the GPT Processing Server and display the response.

### GPT Processing Server

Start the GPT processing server:

```bash
uvicorn gpt_processing_server.main:app --reload
```

This will start the server on `http://localhost:8000`. The server provides API endpoints for image upload, querying, and analysis.

## Configuration

The system uses environment variables for configuration. Key variables include:

- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4 access.
- `DATABASE_URL`: PostgreSQL database connection string.
- `PHOTOS_DIR`: Directory for storing uploaded photos (default: 'photos').

Additional configuration options can be found in the `config.py` files within each component.

## Database Schema

The main table `image_data` stores information about captured images:

- `id`: Serial primary key
- `image_id`: UUID for the image
- `s3_url`: URL or path to the stored image
- `status`: Processing status of the image
- `timestamp`: Capture timestamp
- `location`: Capture location
- `vector`: CLIP-generated feature vector for semantic search
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

The table is partitioned by `timestamp` for improved query performance.

## API Endpoints

The GPT Processing Server provides the following main endpoints:

- `POST /api/upload`: Upload a new image
- `GET /api/image_vector/{image_id}`: Retrieve the feature vector for a specific image
- `POST /api/ask`: Submit a question for analysis
- `GET /api/ping`: Health check endpoint

Detailed API documentation can be generated using FastAPI's built-in Swagger UI.

## Image Processing

The system uses several techniques for image processing:

1. **Motion Detection**: Utilizes frame differencing and contour analysis to detect significant changes between frames.
2. **Feature Extraction**: Uses the CLIP model to generate feature vectors for semantic understanding of image content.
3. **Image Similarity**: Compares images using structural similarity index (SSIM) to avoid storing duplicate or very similar images.

## Performance Considerations

- The system uses asynchronous programming (asyncio, aiohttp) for improved concurrency.
- Database queries are optimized with appropriate indexes.
- Image vectors are stored using the `pgvector` extension for efficient similarity searches.
- Partitioning is employed on the `image_data` table to improve query performance for large datasets.

## Security and Privacy

- All API endpoints should be secured with appropriate authentication and authorization mechanisms (not implemented in the current version).
- Image data is stored securely, with access controlled through the application.
- The system is designed to be run on a private network or with proper security measures if exposed to the internet.

## Troubleshooting

Common issues and their solutions:

1. **Camera access denied**: Ensure that your Python environment has permission to access the camera. On macOS, check System Preferences > Security & Privacy > Privacy > Camera.
2. **Database connection issues**: Verify that PostgreSQL is running and that the `DATABASE_URL` is correctly set in your `.env` file.
3. **GPT-4 API errors**: Check that your `OPENAI_API_KEY` is valid and has sufficient credits.

For more detailed troubleshooting, refer to the logs generated by each component.

## Contributing

Contributions to find-my-goods are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Write tests for your changes.
4. Ensure all tests pass and the code adheres to the project's style guide.
5. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
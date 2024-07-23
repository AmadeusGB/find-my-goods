# find-my-goods

## 项目简介

本项目旨在构建一个基于 Python 和 OpenCV 的分布式摄像头监控和分析系统，通过云端存储和 GPT-4 API，实现对用户提出的问题进行图像分析和回答。该系统包含四个主要模块：摄像头客户端（camera_client）、GPT 对话客户端（gpt_client）、图片存储和管理服务器（photos_api_server）以及 GPT 处理服务器（gpt_processing_server）。

## 目录结构

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

## 安装依赖

在运行该代码之前，请确保已安装以下依赖：

- Python 3.9
- OpenCV
- Flask
- Boto3
- SQLAlchemy
- skimage
- requests

您可以使用以下命令安装所有依赖：

```bash
pip install -r requirements.txt
```

## 模块说明

### 摄像头客户端（camera_client）

负责处理摄像头相关操作，包括捕获图片或视频，将其上传到服务器。

- **主要功能**：
  - 捕获图片或视频
  - 对图片进行预处理（如加时间戳、运动检测等）
  - 将处理后的图片上传到云端存储

- **文件说明**：
  - `main.py`：主程序入口，处理命令行参数并调用相应功能。
  - `camera_utils.py`：摄像头相关操作，如启动摄像头、配置摄像头参数。
  - `image_processing.py`：图像处理功能，如运动检测、图像相似性检测。
  - `upload.py`：将处理后的图片上传到云端存储。
  - `config.py`：配置文件。
  - `logger.py`：日志记录模块。

- **使用示例**：
  - 使用电脑摄像头拍照：
    ```bash
    python3.9 camera_client/main.py --device 0 --mode photo --interval 60 --duration 600 --location bedroom
    ```

  - 使用 iPhone 11 摄像头录制视频：
    ```bash
    python3.9 camera_client/main.py --device 1 --mode video --duration 600 --location living_room
    ```

### GPT 对话客户端（gpt_client）

负责接受用户输入（文字或语音），将请求发送到服务器并接收处理结果。

- **主要功能**：
  - 接受用户输入（文字或语音）
  - 将输入请求发送到 GPT 处理服务器
  - 接收并显示处理结果

- **文件说明**：
  - `main.py`：主程序入口，处理命令行参数并调用相应功能。
  - `audio_processing.py`：语音处理功能，如语音识别、语音转文字。
  - `request_handler.py`：处理用户请求，发送请求到服务器并接收响应。
  - `config.py`：配置文件。
  - `logger.py`：日志记录模块。

- **使用示例**：
  - 通过文字询问问题并获取图片分析结果：
    ```bash
    python3.9 gpt_client/main.py --question "红色的袋子在哪里？" --count 5
    ```

### 图片存储和管理服务器（photos_api_server）

负责接收来自客户端的图片，将其存储在云端，并对外提供 API 接口来查询和获取图片。

- **主要功能**：
  - 接收并存储图片
  - 提供 API 接口查询和获取图片
  - 管理图片元数据

- **文件说明**：
  - `app.py`：主程序入口，启动 Flask 服务器。
  - `storage.py`：图片存储功能，实现图片上传、下载、删除等操作。
  - `models.py`：图片元数据模型，使用 SQLAlchemy 管理。
  - `config.py`：配置文件。
  - `logger.py`：日志记录模块。
  - `monitor.py`：监控模块，监控服务器运行状态。

- **运行示例**：
  - 启动图片存储和管理服务器：
    ```bash
    python3.9 photos_api_server/app.py
    ```

### GPT 处理服务器（gpt_processing_server）

负责接受来自客户端的请求，获取所需图片，调用 GPT-4 API 进行处理，并返回结果。

- **主要功能**：
  - 接受来自客户端的请求
  - 从图片存储服务器获取图片
  - 调用 GPT-4 API 进行处理
  - 返回处理结果

- **文件说明**：
  - `app.py`：主程序入口，启动 Flask 服务器。
  - `gpt_api.py`：GPT-4 API 调用模块，处理图像分析请求。
  - `config.py`：配置文件。
  - `logger.py`：日志记录模块。
  - `monitor.py`：监控模块，监控服务器运行状态。

- **运行示例**：
  - 启动 GPT 处理服务器：
    ```bash
    python3.9 gpt_processing_server/app.py
    ```

## 参数说明

以下是命令行参数的详细解析和介绍：

- `--device`：指定摄像头设备索引（0 表示电脑摄像头，1 表示 iPhone 11 摄像头，2 表示 iPhone 13 摄像头）。
  
  **解析**：此参数用于选择哪个摄像头设备将用于拍照或录制视频。
  
  **优点**：可以灵活选择不同的摄像头设备进行拍照或录视频。
  
  **缺点**：必须知道设备索引，否则可能无法正确选择摄像头。

- `--mode`：指定操作模式，`photo` 表示拍照模式，`video` 表示录视频模式。
  
  **解析**：此参数用于指定工具的操作模式，是拍照还是录制视频。
  
  **优点**：可以根据需要选择拍照或录视频。
  
  **缺点**：需要明确指定操作模式。

- `--interval`：指定定时拍摄的间隔时间，单位为秒（仅适用于拍照模式，默认值为60秒）。
  
  **解析**：此参数用于设置每次拍照之间的时间间隔。
  
  **优点**：定时拍摄可以保证在固定时间间隔内拍摄照片，便于时间序列分析。
  
  **缺点**：如果设置过短，可能会生成大量照片，占用存储空间；如果设置过长，可能会漏掉重要的变化。

- `--duration`：指定总拍摄或录制时长，单位为秒（默认值为600秒）。
  
  **解析**：此参数用于设置拍照或录制视频的总时长。
  
  **优点**：可以控制总拍摄或录制时间，便于测试和管理。
  
  **缺点**：如果设置过长，可能会生成大量数据，占用存储空间。

- `--threshold`：指定帧差阈值，用于运动检测（仅适用于拍照模式，默认值为60）。
  
  **解析**：此参数用于设置帧之间差异的阈值，用于检测运动。
  
  **优点**：可以调整运动检测的灵敏度，帧差阈值越高，运动检测越不敏感。
  
  **缺点**：如果设置过高，可能会漏掉细微的运动；如果设置过低，可能会对轻微的变化过于敏感。

- `--min_contour_area`：指定运动检测的最小轮廓面积（仅适用于拍照模式，默认值为4000）。
  
  **解析**：此参数用于设置检测运动时的最小轮廓面积。
  
  **优点**：可以调整运动检测的灵敏度，轮廓面积阈值越大，运动检测越不敏感。
  
  **缺点**：如果设置过高，可能会漏掉小面积的运动；如果设置过低，可能会对小面积的变化过于敏感。

- `--detection_interval`：指定运动检测检查之间的间隔时间，单位为秒（仅适用于拍照模式，默认值为1秒）。
  
  **解析**：此参数用于设置每次进行运动检测的时间间隔。
  
  **优点**

：可以减少运动检测的频率，从而减少计算量和资源占用。
  
  **缺点**：如果设置过长，可能会漏掉快速发生的运动。

- `--location`：指定拍摄照片或录制视频的位置（默认值为 'unknown'）。
  
  **解析**：此参数用于在图片或视频上添加位置信息。
  
  **优点**：可以在图片和视频上添加位置信息，便于后续位置分类和分析。
  
  **缺点**：如果位置设置不准确，可能会导致位置信息误导分析。

- `--image_format`：指定保存图片的格式（仅适用于拍照模式，默认值为 'jpg'）。
  
  **解析**：此参数用于设置保存图片的文件格式。
  
  **优点**：可以选择更高效的图片格式，如 WebP，以节省存储空间并提供更好的图像质量。
  
  **缺点**：某些旧设备或软件可能不支持现代图片格式，如 WebP。

## 示例

以下是一些使用示例：

- 使用电脑摄像头拍照，最小轮廓面积为 4000，帧差阈值为 60，检测间隔为 1 秒：

  ```bash
  python3.9 camera_client/main.py --device 0 --mode photo --interval 60 --duration 600 --threshold 60 --min_contour_area 4000 --detection_interval 1 --location bedroom --image_format jpg
  ```

- 使用 iPhone 11 摄像头拍照，最小轮廓面积为 5000，帧差阈值为 70，检测间隔为 2 秒：

  ```bash
  python3.9 camera_client/main.py --device 1 --mode photo --interval 60 --duration 600 --threshold 70 --min_contour_area 5000 --detection_interval 2 --location living_room --image_format jpg
  ```

- 使用 iPhone 13 摄像头拍照，最小轮廓面积为 5000，帧差阈值为 70，检测间隔为 2 秒：

  ```bash
  python3.9 camera_client/main.py --device 2 --mode photo --interval 60 --duration 600 --threshold 70 --min_contour_area 5000 --detection_interval 2 --location living_room --image_format jpg
  ```

- 使用电脑摄像头录制视频，时长 600 秒，位置为 bedroom：

  ```bash
  python3.9 camera_client/main.py --device 0 --mode video --duration 600 --location bedroom
  ```

- 使用 iPhone 11 摄像头录制视频，时长 600 秒，位置为 living_room：

  ```bash
  python3.9 camera_client/main.py --device 1 --mode video --duration 600 --location living_room
  ```

- 使用 iPhone 13 摄像头录制视频，时长 600 秒，位置为 living_room：

  ```bash
  python3.9 camera_client/main.py --device 2 --mode video --duration 600 --location living_room
  ```

## 架构说明

### 摄像头客户端（camera_client）

负责处理摄像头相关操作，包括捕获图片或视频，将其上传到服务器。

- **架构图**：

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

- **交互流程**：
  1. `main.py` 处理命令行参数，调用 `camera_utils.py` 启动摄像头。
  2. `camera_utils.py` 负责摄像头的初始化和配置，捕获图像并传递给 `image_processing.py`。
  3. `image_processing.py` 对图像进行预处理，如运动检测和图像相似性检测。
  4. 预处理后的图像通过 `upload.py` 上传到云端存储。

### GPT 对话客户端（gpt_client）

负责接受用户输入（文字或语音），将请求发送到服务器并接收处理结果。

- **架构图**：

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

- **交互流程**：
  1. `main.py` 处理命令行参数和用户输入，调用 `audio_processing.py` 进行语音识别（如有需要）。
  2. `audio_processing.py` 将语音转化为文字，并传递给 `request_handler.py`。
  3. `request_handler.py` 将用户问题和图片请求发送到 GPT 处理服务器，并接收处理结果。

### 图片存储和管理服务器（photos_api_server）

负责接收来自客户端的图片，将其存储在云端，并对外提供 API 接口来查询和获取图片。

- **架构图**：

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

- **交互流程**：
  1. `app.py` 负责启动 Flask 服务器，接收来自客户端的图片上传请求。
  2. `storage.py` 处理图片的存储和管理。
  3. `models.py` 使用 SQLAlchemy 管理图片的元数据，并提供查询接口。

### GPT 处理服务器（gpt_processing_server）

负责接受来自客户端的请求，获取所需图片，调用 GPT-4 API 进行处理，并返回结果。

- **架构图**：

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

- **交互流程**：
  1. `app.py` 负责启动 Flask 服务器，接收来自客户端的请求。
  2. `gpt_api.py` 处理请求，调用 GPT-4 API 进行图像分析，并返回处理结果。

## 注意事项

- 请确保运行摄像头客户端脚本时，Python 解释器有摄像头访问权限。可以在 macOS 的“系统偏好设置” -> “安全性与隐私” -> “隐私” -> “相机”中进行设置。
- 运行代码前，请关闭其他可能占用摄像头的应用程序（如 Photo Booth）。
- 根据需求调整各参数，以达到最佳效果。

## 问题反馈

如果在使用过程中遇到任何问题，请提供详细的错误信息，以便进一步分析和排查。
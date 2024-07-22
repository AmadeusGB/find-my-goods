### README

#### 项目简介

`capture_images.py` 是一个使用 Python 和 OpenCV 实现的摄像头拍照和录制视频工具，可以通过命令行参数指定使用电脑内置摄像头或 iPhone 11 摄像头进行拍照或录制视频。拍照功能可以每分钟拍摄一张关键帧，并在检测到运动时增加拍摄频率。录制视频功能支持录制指定时长的视频，并保存为 MP4 格式。每张图片都会添加时间戳和序列号，方便后续对图片进行时间序列分析。

#### 目录结构

```
.
├── README.md
├── capture_images.py
├── photos
└── videos
```

#### 安装依赖

在运行该代码之前，请确保已安装以下依赖：

- Python 3.9
- OpenCV
- argparse

您可以使用以下命令安装 OpenCV：

```bash
pip install opencv-python
```

#### 使用说明

1. **保存代码**

   将 `capture_images.py` 代码保存到项目目录中。

2. **运行代码**

   - 使用电脑摄像头拍照：

     ```bash
     python3.9 capture_images.py --device 0 --mode photo --interval 60 --duration 600 --threshold 60 --min_contour_area 4000 --detection_interval 1 --location bedroom --image_format jpg
     ```

   - 使用 iPhone 11 摄像头拍照：

     ```bash
     python3.9 capture_images.py --device 1 --mode photo --interval 60 --duration 600 --threshold 70 --min_contour_area 5000 --detection_interval 2 --location living_room --image_format jpg
     ```

   - 使用 iPhone 13 摄像头拍照：

     ```bash
     python3.9 capture_images.py --device 2 --mode photo --interval 60 --duration 600 --threshold 70 --min_contour_area 5000 --detection_interval 2 --location living_room --image_format jpg
     ```

   - 使用电脑摄像头录制视频：

     ```bash
     python3.9 capture_images.py --device 0 --mode video --duration 600 --location bedroom
     ```

   - 使用 iPhone 11 摄像头录制视频：

     ```bash
     python3.9 capture_images.py --device 1 --mode video --duration 600 --location living_room
     ```

   - 使用 iPhone 13 摄像头录制视频：

     ```bash
     python3.9 capture_images.py --device 2 --mode video --duration 600 --location living_room
     ```

#### 参数说明

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
  
  **优点**：可以减少运动检测的频率，从而减少计算量和资源占用。
  
  **缺点**：如果设置过长，可能会漏掉快速发生的运动。

- `--location`：指定拍摄照片或录制视频的位置（默认值为 'unknown'）。
  
  **解析**：此参数用于在图片或视频上添加位置信息。
  
  **优点**：可以在图片和视频上添加位置信息，便于后续位置分类和分析。
  
  **缺点**：如果位置设置不准确，可能会导致位置信息误导分析。

- `--image_format`：指定保存图片的格式（仅适用于拍照模式，默认值为 'jpg'）。
  
  **解析**：此参数用于设置保存图片的文件格式。
  
  **优点**：可以选择更高效的图片格式，如 WebP，以节省存储空间并提供更好的图像质量。
  
  **缺点**：某些旧设备或软件可能不支持现代图片格式，如 WebP。

#### 示例

以下是一些使用示例：

- 使用电脑摄像头拍照，最小轮廓面积为 4000，帧差阈值为 60，检测间隔为 1 秒：

  ```bash
  python3.9 capture_images.py --device 0 --mode photo --interval 60 --duration 600 --threshold 60 --min_contour_area 4000 --detection_interval 1 --location bedroom --image_format jpg
  ```

- 使用 iPhone 11 摄像头拍照，最小轮廓面积为 5000，帧差阈值为 70，检测间隔为 2 秒：

  ```bash
  python3.9 capture_images.py --device 1 --mode photo --interval 60 --duration 600 --threshold 70 --min_contour_area 5000 --detection_interval 2 --location living_room --image_format jpg
  ```

- 使用 iPhone 13 摄像头拍照，最小轮廓面积为 5000，帧差阈值为 70，检测间隔为 2 秒：

  ```bash
  python3.9 capture_images.py --device 2 --mode photo --interval 60 --duration 600 --threshold 70 --min_contour_area 5000 --detection_interval 2 --location living_room --image_format jpg
  ```

- 使用电脑摄像头录制视频，时长 600 秒，位置为 bedroom：

  ```bash
  python3.9 capture_images.py --device 0 --mode video --duration 600 --location bedroom
  ```

- 使用 iPhone 11 摄像头录制视频，时长 600 秒，位置为 living_room：

  ```bash
  python3.9 capture_images.py --device 1 --mode video --duration 600 --location living_room
  ```

- 使用 iPhone 13 摄像头录制视频，时长 600 秒，位置为 living_room：

  ```bash
  python3.9 capture_images.py --device 2 --mode video --duration 600 --location living_room
  ```

#### 注意事项

- 请确保运行该脚本时，Python 解释器有摄像头访问权限。可以在 macOS 的“系统偏好设置” -> “安全性与隐私” -> “隐私” -> “相机”中进行设置。
- 运行代码前，请关闭其他可能占用摄像头的应用程序（如 Photo Booth）。
- 根据需求调整各参数，以达到最佳效果。

#### 问题反馈

如果在使用过程中遇到任何问题，请提供详细的错误信息，以便进一步分析和排查。
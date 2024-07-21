### README

#### 项目简介

`capture_images.py` 是一个使用 Python 和 OpenCV 实现的摄像头拍照工具，可以通过命令行参数指定使用电脑内置摄像头或 iPhone 11 摄像头进行拍照。该工具每秒拍摄一张照片，并将照片保存到指定的 `photos` 文件夹中。

#### 目录结构

```
.
├── README.md
├── capture_images.py
└── photos
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
     python3.9 capture_images.py --device 1 --interval 1 --duration 10
     ```

   - 使用 iPhone 11 摄像头拍照：

     ```bash
     python3.9 capture_images.py --device 0 --interval 1 --duration 10
     ```

3. **参数说明**

   - `--device`：指定摄像头设备索引（0 表示 iPhone 11 摄像头，1 表示电脑摄像头）。
   - `--interval`：指定拍摄间隔时间，单位为秒（默认值为1秒）。
   - `--duration`：指定总拍摄时长，单位为秒（默认值为10秒）。

#### 示例

以下是一些使用示例：

- 使用电脑摄像头每秒拍摄一张照片，持续10秒：

  ```bash
  python3.9 capture_images.py --device 1 --interval 1 --duration 10
  ```

- 使用 iPhone 11 摄像头每2秒拍摄一张照片，持续20秒：

  ```bash
  python3.9 capture_images.py --device 0 --interval 2 --duration 20
  ```

#### 注意事项

- 请确保运行该脚本时，Python 解释器有摄像头访问权限。可以在 macOS 的“系统偏好设置” -> “安全性与隐私” -> “隐私” -> “相机”中进行设置。
- 运行代码前，请关闭其他可能占用摄像头的应用程序（如 Photo Booth）。

#### 问题反馈

如果在使用过程中遇到任何问题，请提供详细的错误信息，以便进一步分析和排查。
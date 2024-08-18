# find-my-goods

[English](README.md) | [中文](README_ZH.md)

## 目录
1. [项目概述](#项目概述)
2. [功能特性](#功能特性)
3. [系统架构](#系统架构)
4. [安装说明](#安装说明)
5. [使用方法](#使用方法)
   - [摄像头客户端](#摄像头客户端)
   - [GPT客户端](#gpt客户端)
   - [GPT处理服务器](#gpt处理服务器)
6. [配置说明](#配置说明)
7. [数据库模式](#数据库模式)
8. [API接口](#api接口)
9. [图像处理](#图像处理)
10. [性能考虑](#性能考虑)
11. [安全性和隐私](#安全性和隐私)
12. [故障排除](#故障排除)
13. [贡献指南](#贡献指南)
14. [许可证](#许可证)

## 项目概述

find-my-goods 是一个先进的、分布式的摄像头监控和分析系统，采用 Python 开发。它利用云存储、计算机视觉技术和 GPT-4 API 的强大功能，提供实时监控、智能查询和对家庭环境的全面分析。

该系统设计用于从多个摄像头源捕获图像或视频，对其进行运动检测和其他相关特征的处理，高效存储，并允许用户使用自然语言查询有关家中物品、事件或情况的信息。

## 功能特性

1. **多摄像头支持**：
   - 兼容电脑网络摄像头、iPhone 11 和 iPhone 13 摄像头。
   - 可扩展架构，方便添加新的摄像头类型。

2. **灵活的捕获模式**：
   - 照片模式，可自定义间隔和持续时间。
   - 视频模式，可调整录制长度。

3. **智能运动检测**：
   - 利用 OpenCV 进行高效的帧差分和轮廓分析。
   - 可自定义运动敏感度和最小轮廓面积的阈值。

4. **云存储集成**：
   - 无缝上传捕获的图像到云存储。
   - 使用 PostgreSQL 进行高效的元数据管理。

5. **高级图像分析**：
   - 集成 GPT-4 API 进行复杂的图像理解和问答。
   - 集成 CLIP 模型生成图像特征向量，实现语义搜索功能。

6. **自然语言查询**：
   - 用户友好的界面，可询问关于家庭环境的问题。
   - 根据查询内容智能检索相关图像。

7. **实时处理**：
   - 异步处理图像上传和处理任务。
   - 使用 PostgreSQL 通知的事件驱动架构，实现实时更新。

8. **可扩展架构**：
   - 设计用于处理多个摄像头和大量数据。
   - 客户端、处理服务器和数据库之间的关注点分离，提高可扩展性。

## 系统架构

系统由四个主要组件组成：

1. **摄像头客户端（camera_client）**：
   - 负责从各种摄像头源捕获图像或视频。
   - 处理运动检测和初始图像处理。
   - 将捕获的数据上传到云存储。

2. **GPT客户端（gpt_client）**：
   - 提供用户界面，用于提交关于家庭环境的查询。
   - 与GPT处理服务器通信以获取响应。

3. **GPT处理服务器（gpt_processing_server）**：
   - 作为处理用户查询的中心枢纽。
   - 集成GPT-4 API进行高级图像分析。
   - 管理图像检索和基于查询相关性的排序。

4. **PostgreSQL数据库**：
   - 存储捕获图像的元数据，包括时间戳、位置和特征向量。
   - 实现高效的相关图像查询和检索。

## 安装说明

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/find-my-goods.git
   cd find-my-goods
   ```

2. 设置虚拟环境（可选但推荐）：
   ```
   python -m venv venv
   source venv/bin/activate  # 在Windows上，使用 `venv\Scripts\activate`
   ```

3. 安装所需依赖：
   ```
   pip install -r requirements.txt
   ```

4. 设置PostgreSQL数据库：
   - 如果尚未安装，请安装PostgreSQL。
   - 为项目创建一个新数据库。
   - 运行初始化脚本：
     ```
     psql -d your_database_name -f sql/init.sql
     ```

5. 设置环境变量：
   - 在项目根目录创建一个 `.env` 文件：
     ```
     touch .env
     ```
   - 使用文本编辑器打开 `.env` 文件，并添加以下变量：
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
   - 将占位符值替换为您的实际配置详情：
     - `your_openai_api_key_here`：您用于访问GPT-4的OpenAI API密钥
     - `username`：您的PostgreSQL用户名
     - `password`：您的PostgreSQL密码
     - `database_name`：您的PostgreSQL数据库名称
     - 根据您的设置需要调整其他值

   注意：请保持您的 `.env` 文件安全，切勿将其提交到版本控制系统中。

## 使用方法

### 摄像头客户端

摄像头客户端可以通过各种选项来自定义捕获过程：

```bash
python camera_client/main.py --device 0 --mode photo --interval 60 --duration 600 --location bedroom --threshold 60 --min_contour_area 4000 --detection_interval 1 --image_format jpg
```

选项说明：
- `--device`：摄像头设备索引（0表示电脑，1表示iPhone 11，2表示iPhone 13）
- `--mode`：'photo' 或 'video'
- `--interval`：拍摄间隔，单位为秒（仅适用于照片模式）
- `--duration`：总拍摄/录制时长，单位为秒
- `--location`：拍摄位置（如 bedroom、living_room）
- `--threshold`：运动检测的帧差阈值
- `--min_contour_area`：运动检测的最小轮廓面积
- `--detection_interval`：运动检测检查间隔，单位为秒
- `--image_format`：保存图像的格式（如 jpg、webp）

### GPT客户端

要询问关于您家庭环境的问题：

```bash
python gpt_client/main.py "我的水杯在哪里？"
```

客户端将把查询发送到GPT处理服务器并显示响应。

### GPT处理服务器

启动GPT处理服务器：

```bash
uvicorn gpt_processing_server.main:app --reload
```

这将在 `http://localhost:8000` 上启动服务器。服务器提供用于图像上传、查询和分析的API接口。

## 配置说明

系统使用环境变量进行配置。主要变量包括：

- `OPENAI_API_KEY`：用于访问GPT-4的OpenAI API密钥。
- `DATABASE_URL`：PostgreSQL数据库连接字符串。
- `PHOTOS_DIR`：存储上传照片的目录（默认：'photos'）。

其他配置选项可以在每个组件的 `config.py` 文件中找到。

## 数据库模式

主表 `image_data` 存储捕获图像的信息：

- `id`：序列主键
- `image_id`：图像的UUID
- `s3_url`：存储图像的URL或路径
- `status`：图像的处理状态
- `timestamp`：捕获时间戳
- `location`：捕获位置
- `vector`：CLIP生成的特征向量，用于语义搜索
- `created_at`：记录创建时间戳
- `updated_at`：记录更新时间戳

该表按 `timestamp` 进行分区，以提高查询性能。

## API接口

GPT处理服务器提供以下主要接口：

- `POST /api/upload`：上传新图像
- `GET /api/image_vector/{image_id}`：检索特定图像的特征向量
- `POST /api/ask`：提交问题进行分析
- `GET /api/ping`：健康检查接口

详细的API文档可以使用FastAPI的内置Swagger UI生成。

## 图像处理

系统使用几种技术进行图像处理：

1. **运动检测**：利用帧差分和轮廓分析来检测帧之间的显著变化。
2. **特征提取**：使用CLIP模型生成特征向量，用于图像内容的语义理解。
3. **图像相似性**：使用结构相似性指数（SSIM）比较图像，以避免存储重复或非常相似的图像。

## 性能考虑

- 系统使用异步编程（asyncio、aiohttp）以提高并发性。
- 数据库查询通过适当的索引进行优化。
- 图像向量使用 `pgvector` 扩展存储，以实现高效的相似性搜索。
- 在 `image_data` 表上使用分区来提高大型数据集的查询性能。

## 安全性和隐私

- 所有API接口都应该使用适当的身份验证和授权机制进行安全保护（当前版本中未实现）。
- 图像数据安全存储，通过应用程序控制访问。
- 系统设计为在私有网络上运行，或在暴露到互联网时采取适当的安全措施。

## 故障排除

常见问题及其解决方案：

1. **摄像头访问被拒绝**：确保您的Python环境有权限访问摄像头。在macOS上，检查系统偏好设置 > 安全性与隐私 > 隐私 > 相机。
2. **数据库连接问题**：验证PostgreSQL正在运行，并且 `.env` 文件中的 `DATABASE_URL` 设置正确。
3. **GPT-4 API错误**：检查您的 `OPENAI_API_KEY` 是否有效并具有足够的额度。

要获取更详细的故障排除信息，请参阅每个组件生成的日志。

## 贡献指南

欢迎对find-my-goods项目做出贡献！请遵循以下步骤：

1. Fork 该仓库。
2. 为您的功能或错误修复创建一个新分支。
3. 为您的更改编写测试。
4. 确保所有测试都通过，并且代码符合项目的风格指南。
5. 提交一个清晰描述您更改的拉取请求。

## 许可证

本项目采用MIT许可证。有关详细信息，请参阅 [LICENSE](LICENSE) 文件。
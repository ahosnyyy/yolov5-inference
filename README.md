# YOLOv5 Inference API with FastAPI and Docker

This project provides a Docker-based REST API for running YOLOv5 object detection inference on images using FastAPI.

## Setup

1. Make sure you have Docker and Docker Compose installed on your system.
2. Place your YOLOv5 model weights in the `models` directory (default is yolov5s.pt).

## Usage

### Building and Running the Docker Container

```bash
# Build and run the container
docker-compose up --build
```

This will:
1. Build the Docker image with all necessary dependencies
2. Start a FastAPI server on port 8000
3. Mount the output and models directories as volumes

### API Endpoints

#### 1. Object Detection

**Endpoint:** `POST /detect`

**Parameters:**
- `file`: Image file (multipart/form-data)
- `weights`: Model weights path (default: yolov5s.pt)
- `img_size`: Inference size in pixels (default: 640)
- `conf_thres`: Object confidence threshold (default: 0.25)
- `iou_thres`: IOU threshold for NMS (default: 0.45)
- `device`: CUDA device, i.e., 0 or 0,1,2,3 or cpu (default: auto-detect)

**Response:**
```json
{
  "filename": "processed_image.jpg",
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.92,
      "bbox": [x1, y1, x2, y2]
    }
  ],
  "image_base64": "base64_encoded_image_data"
}
```

#### 2. Get Processed Image

**Endpoint:** `GET /output/{filename}`

**Response:** The processed image file

### Using the Test Client

A simple HTML test client is included in the project. To use it:

1. Start the Docker container using `docker-compose up --build`
2. Open the `test_client.html` file in your web browser
3. Upload an image and set the detection parameters
4. Click "Detect Objects" to see the results

## Download YOLOv5 Weights

If you don't have the YOLOv5 weights, you can download them from the official repository:

- YOLOv5s (small): https://github.com/ultralytics/yolov5/releases/download/v6.1/yolov5s.pt
- YOLOv5m (medium): https://github.com/ultralytics/yolov5/releases/download/v6.1/yolov5m.pt
- YOLOv5l (large): https://github.com/ultralytics/yolov5/releases/download/v6.1/yolov5l.pt
- YOLOv5x (xlarge): https://github.com/ultralytics/yolov5/releases/download/v6.1/yolov5x.pt

Download your preferred model and place it in the `models` directory.

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

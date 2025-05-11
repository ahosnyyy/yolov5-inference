import os
import sys
import io
import uuid
import torch
import base64
import numpy as np
import cv2
from PIL import Image
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import aiofiles
from pydantic import BaseModel

# Import CLO value processing functions
from clo_processor import map_detections_to_clo

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

# Initialize FastAPI app
app = FastAPI(title="YOLOv5 Inference API", description="API for object detection using YOLOv5")

# Model configuration
class ModelConfig(BaseModel):
    weights: str = "models/merged_clothing.pt"
    img_size: int = 640
    conf_thres: float = 0.25
    iou_thres: float = 0.45
    device: str = ""
    max_det: int = 1000
    classes: Optional[List[int]] = None
    yaml_file: str = "merged_clothing.yaml"

# Detection result
class DetectionResult(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    clo_value: Optional[float] = None

# Response model
class InferenceResponse(BaseModel):
    detections: List[DetectionResult]
    total_clo_value: Optional[float] = None

# Global model variable
model = None

# Load class names from YAML file
def load_class_names(yaml_file):
    try:
        import yaml
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            if 'names' in data:
                return data['names']
            else:
                raise ValueError(f"No 'names' field found in {yaml_file}")
    except Exception as e:
        print(f"Error loading class names from YAML: {str(e)}")
        return None

# Load YOLOv5 model
def load_model(config: ModelConfig):
    global model
    if model is None:
        try:
            # Check if the model file exists
            model_path = os.path.join('models', config.weights) if not os.path.exists(config.weights) else config.weights
            if not os.path.exists(model_path):
                raise HTTPException(status_code=404, detail=f"Model file not found: {config.weights}")
                
            # Load the model
            sys.path.append('./yolov5')
            model = torch.hub.load('yolov5', 'custom', path=model_path, source='local')
            
            # Set device
            if config.device:
                model.to(config.device)
                
            # Set model parameters
            model.conf = config.conf_thres
            model.iou = config.iou_thres
            model.classes = config.classes
            model.max_det = config.max_det
            
            # Load custom class names from YAML if available
            if os.path.exists(config.yaml_file):
                class_names = load_class_names(config.yaml_file)
                if class_names:
                    model.names = class_names
                    print(f"Loaded {len(class_names)} class names from {config.yaml_file}")
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
    else:
        # Update model parameters if model is already loaded
        model.conf = config.conf_thres
        model.iou = config.iou_thres
        model.classes = config.classes
        model.max_det = config.max_det
    return model

# Process image for inference
async def process_image(image_bytes, config: ModelConfig):
    try:
        # Load image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Load model
        model = load_model(config)
        
        # Perform inference
        # Set image size
        model.img_size = config.img_size
        results = model(img)
        
        # Process results
        detections = []
        for pred in results.xyxy[0].cpu().numpy():
            x1, y1, x2, y2, conf, cls = pred
            class_id = int(cls)
            class_name = results.names[class_id]
            
            detections.append(DetectionResult(
                class_id=class_id,
                class_name=class_name,
                confidence=float(conf),
                bbox=[float(x1), float(y1), float(x2), float(y2)]
            ))
        
        # Apply CLO value mapping post-processing
        detections, total_clo_value = map_detections_to_clo(detections)
        
        return InferenceResponse(
            detections=detections,
            total_clo_value=total_clo_value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

# API endpoints
@app.get("/")
async def root():
    return {"message": "YOLOv5 Inference API is running. Use /docs for API documentation."}

@app.get("/detect-default", response_model=InferenceResponse)
async def detect_default(weights: str = "models/merged_clothing.pt",
                      img_size: int = 640,
                      conf_thres: float = 0.25,
                      iou_thres: float = 0.45,
                      device: str = "",
                      yaml_file: str = "merged_clothing.yaml"):
    
    # Use default image
    default_image_path = 'input/man-driving-car.jpg'
    if os.path.exists(default_image_path):
        with open(default_image_path, 'rb') as f:
            contents = f.read()
    else:
        raise HTTPException(status_code=404, detail=f"Default image not found: {default_image_path}")
    
    # Create model config
    config = ModelConfig(
        weights=weights,
        img_size=img_size,
        conf_thres=conf_thres,
        iou_thres=iou_thres,
        device=device,
        yaml_file=yaml_file
    )
    
    # Process image
    result = await process_image(contents, config)
    return result

@app.post("/detect", response_model=InferenceResponse)
async def detect(file: Optional[UploadFile] = None, 
                weights: str = Form("models/merged_clothing.pt"),
                img_size: int = Form(640),
                conf_thres: float = Form(0.25),
                iou_thres: float = Form(0.45),
                device: str = Form(""),
                yaml_file: str = Form("merged_clothing.yaml")):
    
    # Read image file or use default image
    if file is not None:
        try:
            contents = await file.read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading uploaded file: {str(e)}")
    else:
        # Use default image
        default_image_path = 'input/man-driving-car.jpg'
        if os.path.exists(default_image_path):
            with open(default_image_path, 'rb') as f:
                contents = f.read()
        else:
            raise HTTPException(status_code=404, detail=f"Default image not found: {default_image_path}")
    
    # Create model config
    config = ModelConfig(
        weights=weights,
        img_size=img_size,
        conf_thres=conf_thres,
        iou_thres=iou_thres,
        device=device,
        yaml_file=yaml_file
    )
    
    # Process image
    result = await process_image(contents, config)
    return result

# Output route removed as we no longer save or serve images

if __name__ == "__main__":
    uvicorn.run("inference:app", host="0.0.0.0", port=8000, reload=True)

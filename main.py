import os
import shutil
import tempfile
import uuid
import atexit
from typing import List
from contextlib import asynccontextmanager

import nibabel as nib
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from totalsegmentator.python_api import totalsegmentator
import plotly.graph_objects as go
from starlette.responses import JSONResponse

from totalsegmentator.nifti_ext_header import load_multilabel_nifti

# Setup temp directory for file storage
TEMP_DIR = os.path.join(tempfile.gettempdir(), "totalsegmentator_api")
os.makedirs(TEMP_DIR, exist_ok=True)

# Clean up on exit
def cleanup():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

app = FastAPI(title="TotalSegmentator API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    a_ = 1
    yield
    cleanup()


@app.post("/segment/")
async def segment_image(
    file: UploadFile = File(...),
    image_type: str = Form("MR")
):
    """Segment a medical image using TotalSegmentator."""
    # Create unique session directory
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_DIR, session_id)
    input_path = os.path.join(session_dir, "input.nii.gz")
    output_dir = os.path.join(session_dir, "segmented_image")
    
    os.makedirs(session_dir, exist_ok=True)
    
    # Save uploaded file
    with open(input_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Load the input image
        input_img = nib.load(input_path)
        
        # Set task based on image type
        if image_type.upper() == "MR":
            task = "total_mr"
        else:
            task = "total"
        
        # Run segmentation
        output_img = totalsegmentator(input_img, fast=True, task=task)
        
        # Save the output
        os.makedirs(output_dir, exist_ok=True)
        nib.save(output_img, output_dir)
        
        # Load the segmentation results
        segmentation_nifti_img, label_map_dict = load_multilabel_nifti(output_dir + ".nii")
        
        return {
            "status": "success",
            "session_id": session_id,
            "download_url": f"/download/{session_id}/segmentation.nii",
            "segmentation_type": str(type(segmentation_nifti_img)),
            "label_map": label_map_dict
        }
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")

@app.get("/example/")
async def segment_example(
):
    """Segment a medical image using TotalSegmentator."""
    # Create unique session directory
    input_path = "./mri.nii.gz"
    
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_DIR, session_id)

    os.makedirs(session_dir, exist_ok=True)
    output_dir = os.path.join(session_dir, "segmented_image")
    

    try:
        input_img = nib.load(input_path)
        output_img = totalsegmentator(input_img, fast=True, task="total_mr")

        os.makedirs(output_dir, exist_ok=True)
        nib.save(output_img, output_dir)

        segmentation_nifti_img, label_map_dict = load_multilabel_nifti(output_dir + ".nii")

        return {
            "status": "success",
            "session_id": session_id,
            "download_url": f"/download/{session_id}/segmentation.nii",
            "segmentation_type": str(type(segmentation_nifti_img)),
            "label_map": label_map_dict
        }
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")

@app.get("/download/{session_id}/segmentation.nii")
async def download_segmentation(session_id: str):
    """Download the segmentation result file."""
    file_path = os.path.join(TEMP_DIR, session_id, "segmented_image.nii")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Segmentation not found")
    
    return FileResponse(file_path, media_type="application/octet-stream", filename="segmentation.nii")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Simple HTML interface."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TotalSegmentator API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            form { margin: 20px 0; }
            .field { margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>TotalSegmentator API</h1>
        <p>Upload a medical image (NIfTI format) for segmentation.</p>
        
        <form action="/segment/" method="post" enctype="multipart/form-data">
            <div class="field">
                <label for="file">Select NIfTI file:</label>
                <input type="file" id="file" name="file" accept=".nii,.nii.gz" required>
            </div>
            <div class="field">
                <label for="image_type">Image Type:</label>
                <select id="image_type" name="image_type">
                    <option value="MR">MR</option>
                    <option value="CT">CT</option>
                </select>
            </div>
            <div class="field">
                <button type="submit">Upload and Segment</button>
            </div>
        </form>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=5000)
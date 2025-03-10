# TotalSegmentator FastAPI

A web API for [TotalSegmentator](https://github.com/wasserth/TotalSegmentator), a tool for automatic segmentation of anatomical structures in CT and MR images.

## Overview

This application provides a RESTful API and web interface for TotalSegmentator, allowing users to upload medical images and receive segmentation results through a simple HTTP interface. It wraps the core functionality of TotalSegmentator in a web service that's easy to integrate with other applications.

## Features

- **Simple Web UI**: Upload and process images through a browser
- **RESTful API**: Programmatically upload images and retrieve segmentations
- **Support for CT and MR Images**: Process both CT and MR scans
- **Automatic Task Selection**: Automatically selects the appropriate segmentation task based on image type
- **NIfTI Format Support**: Works with standard medical imaging formats (.nii, .nii.gz)
- **Segmentation Download**: Easily download the resulting segmentation files
- **Label Map Information**: Returns detailed information about the segmented structures

## Installation

### Prerequisites

- Python >= 3.9
- [Pytorch](http://pytorch.org/) >= 2.0.0 and <2.6.0 (and <2.4 for Windows)

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/totalsegmentator-fastapi.git
   cd totalsegmentator-fastapi
   ```

2. Install the required dependencies:
   ```
   pip install fastapi uvicorn python-multipart TotalSegmentator
   ```

## Usage

### Start the server

```
python app.py
```

Or using uvicorn directly:

```
uvicorn app:app --reload
```

The server will start on http://localhost:8000

### Using the Web Interface

1. Open your browser and navigate to http://localhost:8000
2. Upload a NIfTI (.nii or .nii.gz) file
3. Select the image type (CT or MR)
4. Click "Upload and Segment"
5. Once processing is complete, you'll receive a download link for the segmentation results

### Using the API

To segment an image programmatically:

```python
import requests

url = "http://localhost:8000/segment/"
files = {
    "file": ("image.nii.gz", open("path/to/your/image.nii.gz", "rb"), "application/octet-stream")
}
data = {
    "image_type": "MR"  # or "CT"
}

response = requests.post(url, files=files, data=data)
result = response.json()

# Download the segmentation
if result["status"] == "success":
    segmentation_url = f"http://localhost:8000{result['download_url']}"
    segmentation = requests.get(segmentation_url)
    with open("segmentation.nii", "wb") as f:
        f.write(segmentation.content)
```

## API Documentation

Once the server is running, visit http://localhost:8000/docs for interactive API documentation.

### Endpoints

- `GET /`: Web interface for uploading images
- `POST /segment/`: Upload and segment an image
- `GET /download/{session_id}/segmentation.nii`: Download a segmentation result

## About TotalSegmentator

TotalSegmentator is a tool for segmentation of anatomical structures in CT and MR images. It was trained on a wide range of different CT and MR images (different scanners, institutions, protocols) and therefore works well on most images.

### Citation

If you use this tool in your research, please cite the original TotalSegmentator papers:

For CT images:
```
Wasserthal, J., Breit, H.-C., Meyer, M.T., Pradella, M., Hinck, D., Sauter, A.W., Heye, T., Boll, D., Cyriac, J., Yang, S., Bach, M., Segeroth, M., 2023. TotalSegmentator: Robust Segmentation of 104 Anatomic Structures in CT Images. Radiology: Artificial Intelligence. https://doi.org/10.1148/ryai.230024
```

For MR images:
```
TotalSegmentator MRI Radiology paper (https://pubs.rsna.org/doi/10.1148/radiol.241613)
```

Please also cite [nnUNet](https://github.com/MIC-DKFZ/nnUNet) since TotalSegmentator is heavily based on it.

## License

This FastAPI wrapper is provided under the same license as TotalSegmentator. Please refer to the [TotalSegmentator repository](https://github.com/wasserth/TotalSegmentator) for license information.

## Disclaimer

This is not a medical device and is not intended for clinical usage.
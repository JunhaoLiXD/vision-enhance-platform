# Vision Enhance Platform

A local web-based image enhancement platform built with a **FastAPI backend** and a **React + TypeScript frontend**.

This project is designed as an **engineering-oriented image processing system** rather than a single script or notebook. It uses a **plugin-style pipeline architecture** so that enhancement algorithms can be added, composed, and tested more easily. The current implementation focuses on classical image enhancement methods, while leaving room for future ML-based models and astronomy-specific extensions.

## Project Overview

The goal of this project is to build a production-style image enhancement platform that supports:

* image upload and local processing
* pipeline-based algorithm execution
* downloadable enhancement results
* a modular backend architecture for adding new algorithms
* future support for presets, custom algorithm selection, ML models, and astronomy image workflows

At the current stage, the platform already supports the main local workflow:

1. upload an image
2. send it to the backend for processing
3. generate an enhanced output
4. preview the result in the frontend
5. download the processed image to the local machine

## Current Features

### Implemented

* FastAPI backend for image processing tasks
* React + TypeScript frontend for local interaction
* plugin/pipeline-style processing architecture
* unified internal image processing workflow
* local upload -> process -> preview -> download flow
* workspace-based job/output management
* manifest/log style support for tracking processing steps
* several classical enhancement algorithms integrated into the backend

### Available / Integrated Algorithms

* Gamma Correction
* CLAHE
* Retinex
* Bilateral Filter
* Unsharp Mask

> Note: the exact set of enabled algorithms may depend on the current backend registry and API configuration.

### In Progress / Planned

* preset selection from the UI
* custom algorithm selection from the UI
* richer job polling / status feedback in the frontend
* ML-based enhancement models such as Zero-DCE or DnCNN
* astronomy plugin extensions such as FITS input, calibration, and specialized stretch methods

## Tech Stack

### Backend

* Python 3.11
* FastAPI
* Uvicorn
* NumPy
* OpenCV
* Pillow

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS

## Project Structure

A typical project layout looks like this:

```text
vision-enhance-platform/
├── README.md
├── requirements.txt
├── src/
│   ├── backend/
│   │   ├── app/
│   │   ├── engine/
│   │   └── ...
│   └── frontend/
├── assets/
├── sample_data/
├── tests/
└── docs/
```

Depending on your current implementation, the exact folders may differ slightly.

## How It Works

The platform follows an engineering-style processing flow:

* the frontend sends an image or job request to the backend
* the backend constructs or selects a processing pipeline
* each pipeline step applies one enhancement operation
* outputs are saved locally in the project workspace
* the frontend displays the processed result
* the user can download the final image

This design makes it easier to:

* add new enhancement algorithms
* test pipelines step by step
* keep the backend extensible for future presets and ML models

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/JunhaoLiXD/vision-enhance-platform.git
cd vision-enhance-platform
```

### 2. Create and activate a Python environment

Using **conda**:

```bash
conda create -n vision-enhance python=3.11 -y
conda activate vision-enhance
```

Or using **venv**:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. Install backend dependencies

If you already have a `requirements.txt`, run:

```bash
pip install -r requirements.txt
```

If your environment is still being assembled manually, make sure the backend has at least:

```bash
pip install fastapi uvicorn numpy opencv-python pillow python-multipart
```

If your backend uses additional libraries, install those as needed.

### 4. Install frontend dependencies

Go to the frontend directory and install Node dependencies:

```bash
cd src/frontend
npm install
```

If your frontend is stored in a different directory, replace `src/frontend` with your actual frontend path.

## Running the Project Locally

Because this project is **not deployed to a public server yet**, it must currently be run **locally**.

You need to start the backend and frontend separately.

### Start the backend

From the project root, run something similar to:

```bash
uvicorn src.backend.app.main:app --reload
```

If your FastAPI entry point is different, replace the module path with your actual one.

A successful startup usually looks like this:

```text
Uvicorn running on http://127.0.0.1:8000
```

### Start the frontend

Open a second terminal and run:

```bash
cd src/frontend
npm run dev
```

Vite will usually provide a local address such as:

```text
http://127.0.0.1:5173
```

Open that address in your browser.

## Typical Local Usage

After both services are running:

1. open the frontend in your browser
2. upload an image
3. let the frontend send the request to the backend
4. wait for processing to complete
5. preview the enhanced result
6. click the download button to save the output locally

## API Notes

The backend is designed around a job/pipeline style API. Depending on your current implementation, endpoints may include routes such as:

* `POST /api/jobs` — create a processing job
* `GET /api/jobs/{id}` — query job status
* `GET /api/jobs/{id}/artifacts` — list generated files
* `GET /api/jobs/{id}/download/{name}` — download the result
* `GET /api/algorithms` — list available processing algorithms

The exact route names may vary slightly based on your current codebase.

## Current Limitations

At this stage:

* the platform is intended for **local development and testing**
* it is **not deployed** as an online production service
* UI support for **preset selection** is not fully finished yet
* UI support for **manual algorithm selection** is not fully finished yet
* some features described in the long-term roadmap are still under development

## Development Roadmap

### Phase 1

* pipeline core
* basic backend API
* minimal frontend
* upload / process / download workflow

### Phase 2

* stronger enhancement depth
* Retinex / denoise / sharpen integration
* manifest and step logging
* preset pipeline support

### Phase 3

* ML model integration
* model caching and device selection
* faster inference workflow

### Phase 4

* astronomy image extension
* FITS support
* calibration and stacking tools
* astronomy-specific stretch operations

## Why This Project

This project is meant to demonstrate more than just image processing algorithms. It also shows:

* backend service design
* frontend/backend integration
* modular software architecture
* extensible plugin-style development
* practical engineering workflow for computer vision applications

It is especially suitable as a portfolio project for software engineering, computer vision, and ML-related internships.

## Recommended Environment

For the smoothest local setup, use:

* Python 3.11
* Node.js 18+ (or a recent LTS version)
* npm 9+

## Future Improvements

Some useful future additions include:

* better UI controls for choosing pipelines
* side-by-side before/after comparison
* real-time job status polling
* Docker support
* deployment to a cloud or VPS environment
* batch image processing
* ML enhancement inference
* astronomy workflow plugins

## Author

**Junhao Li**
Computer Science @ University of Florida
Image Processing / Computer Vision / Software Engineering

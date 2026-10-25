# AI Medical X-Ray Analysis

An AI-powered medical image analysis application that uses deep learning and MobileNetV2 to assist with pneumonia detection from chest X-ray images.

## Overview

Pneumonia detection from chest X-rays can require careful examination by medical professionals. This project explores how deep learning can support image classification and provide visual explanations of model predictions.

The application combines a trained MobileNetV2 model, a web-based frontend, and a FastAPI backend to provide an interactive medical image analysis workflow.

## Features

- **Deep Learning Classification:** Uses MobileNetV2 for chest X-ray image classification.
- **Web Interface:** Provides pages for user access and an analysis dashboard.
- **FastAPI Backend:** Handles backend application functionality and model integration.
- **Model Explainability:** Includes Grad-CAM-related functionality to help visualize regions influencing predictions.
- **Model Development:** Includes Jupyter notebooks for dataset exploration and model training.
- **Analysis Workflow:** Organizes prediction-related functionality through the application interface.

## Tech Stack

- **Language:** Python, JavaScript, HTML, CSS
- **Deep Learning:** TensorFlow / Keras, MobileNetV2
- **Backend:** FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **Development:** Jupyter Notebook, VS Code, Git, GitHub

## Project Structure

```text
AI-Medical-Image-Analysis/
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── email_service.py
│   ├── init_db.py
│   └── models.py
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── dashboard.js
│   └── style.css
├── models/
│   ├── best_mobilenetv2.keras
│   ├── mobilenetv2_baseline.keras
│   └── mobilenetv2_finetuned.keras
├── notebooks/
│   ├── 01_dataset_exploration.ipynb
│   └── 02_model_training.ipynb
├── results/
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/shivamani2024/AI-Medical-X-Ray-Analysis.git
cd AI-Medical-X-Ray-Analysis
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Once a `requirements.txt` file is available, install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Run the application

Follow the backend startup instructions after configuring the required environment variables and dependencies.

## Model Development

The `notebooks/` directory contains notebooks for dataset exploration and model training. The `models/` directory contains the saved MobileNetV2 model files used for experimentation and inference.

## Responsible Use

This project is intended for educational and research purposes. Its predictions are not a substitute for professional medical diagnosis, clinical judgment, or advice from a qualified healthcare professional.

## Future Improvements

- Deploy the application for public demonstration.
- Add automated testing and clearer setup instructions.
- Document model evaluation metrics and limitations.
- Improve reproducibility of model training and inference.
- Provide a public demo with sample X-ray images, where appropriate.

## Author

**Shivamani Rao**

GitHub: [@shivamani2024](https://github.com/shivamani2024)

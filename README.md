# Custom Data Generator Web App

A Flask web application that allows users to generate custom CSV datasets for various use cases like finance, e-commerce, and personal information.

## Features
- Interactive web interface to select desired columns.
- Generate up to 100,000 records at a time.
- Download the generated dataset as a CSV file.

## How to Run Locally
1. Clone the repository: `git clone https://github.com/Indra1806/dataset_generator.git`
2. Navigate to the project directory: `cd dataset_generator`
3. Create and activate a virtual environment:
   - `python -m venv venv`
   - `source venv/bin/activate` (macOS/Linux) or `.\venv\Scripts\activate` (Windows)
4. Install the required packages: `pip install -r requirements.txt`
5. Run the application: `python app.py`
6. Open your browser and go to `http://127.0.0.1:5000`.
# ==============================================================================
# ADVANCED CUSTOM DATA GENERATOR - FLASK WEB APPLICATION
#
# This is the backend server code for the advanced DataForge UI.
# It handles requests from the feature-rich HTML frontend, generates
# complex datasets with user-selected columns, and serves them for download.
#
# To run this application:
# 1. Save this entire file as `app.py`.
# 2. Ensure you have the `templates` folder with the advanced `index.html`.
# 3. Run `pip install -r requirements.txt`.
# 4. Run `python app.py` in your terminal.
# 5. Open your browser and go to http://127.0.0.1:5000
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IMPORT LIBRARIES
# ------------------------------------------------------------------------------
from flask import Flask, render_template, request, make_response
import pandas as pd
from faker import Faker
import random
import io
import json
import xml.etree.ElementTree as ET

# ------------------------------------------------------------------------------
# 2. INITIALIZE FLASK APP AND FAKER
# ------------------------------------------------------------------------------
app = Flask(__name__)
fake = Faker()

# ------------------------------------------------------------------------------
# 3. MODULAR DATA GENERATION LOGIC
# ------------------------------------------------------------------------------

# This registry contains a function for every possible column in the UI.
COLUMN_GENERATORS = {
    # Personal Info
    'firstName': lambda: fake.first_name(),
    'lastName': lambda: fake.last_name(),
    'email': lambda: fake.email(),
    'phone': lambda: fake.phone_number(),
    'dateOfBirth': lambda: fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
    'address': lambda: fake.address().replace('\n', ', '),

    # Business Data
    'companyName': lambda: fake.company(),
    'jobTitle': lambda: fake.job(),
    'department': lambda: random.choice(['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']),
    'salary': lambda: round(random.uniform(40000, 150000), 2),
    'startDate': lambda: fake.date_between(start_date='-10y', end_date='today').isoformat(),

    # Technical Data
    'ipAddress': lambda: fake.ipv4(),
    'userAgent': lambda: fake.user_agent(),
    'apiKey': lambda: fake.uuid4(),
    'uuid': lambda: fake.uuid4(),
    'timestamp': lambda: fake.iso8601(),
}

def generate_custom_data(num_records, selected_columns):
    """
    Generates a DataFrame with user-selected columns.
    """
    records = []
    for _ in range(num_records):
        record = {}
        for col_name in selected_columns:
            if col_name in COLUMN_GENERATORS:
                record[col_name] = COLUMN_GENERATORS[col_name]()
        records.append(record)
    
    # Ensure DataFrame columns are in the user-selected order
    return pd.DataFrame(records, columns=selected_columns)

# ------------------------------------------------------------------------------
# 4. DATA FORMATTING HELPERS
# ------------------------------------------------------------------------------

def to_json(df):
    return df.to_json(orient='records', indent=4)

def to_xml(df):
    root = ET.Element("data")
    for _, row in df.iterrows():
        record_elem = ET.SubElement(root, "record")
        for col, val in row.items():
            child = ET.SubElement(record_elem, str(col))
            child.text = str(val)
    return ET.tostring(root, encoding='unicode')

def to_sql(df):
    table_name = "generated_data"
    sql_statements = [f"CREATE TABLE {table_name} ({', '.join([f'{col} TEXT' for col in df.columns])});"]
    for _, row in df.iterrows():
        cols = ', '.join(row.index)
        vals = ', '.join(["'" + str(v).replace("'", "''") + "'" for v in row.values])
        sql_statements.append(f"INSERT INTO {table_name} ({cols}) VALUES ({vals});")
    return "\n".join(sql_statements)


# ------------------------------------------------------------------------------
# 5. FLASK ROUTES
# ------------------------------------------------------------------------------

@app.route('/')
def index():
    """Renders the main page of the application."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_and_download():
    """
    Handles form submission, generates data based on selected columns and format,
    and serves the resulting file for download.
    """
    try:
        # Get form data from the advanced UI
        num_records = int(request.form.get('recordCount', 1000))
        output_format = request.form.get('outputFormat', 'csv')
        selected_columns = request.form.getlist('columns')

        # Validate inputs
        if not (1 <= num_records <= 1000000):
            num_records = 1000
        if not selected_columns:
            return "Please select at least one column to generate.", 400

        # Generate the data
        df = generate_custom_data(num_records, selected_columns)

        # Prepare the file for download based on the selected format
        if output_format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            file_data = output.getvalue()
            mimetype = 'text/csv'
            filename = 'custom_data.csv'
        elif output_format == 'json':
            file_data = to_json(df)
            mimetype = 'application/json'
            filename = 'custom_data.json'
        elif output_format == 'xml':
            file_data = to_xml(df)
            mimetype = 'application/xml'
            filename = 'custom_data.xml'
        elif output_format == 'sql':
            file_data = to_sql(df)
            mimetype = 'application/sql'
            filename = 'custom_data.sql'
        else:
            return "Invalid format selected.", 400

        # Create and return the response to trigger a file download
        response = make_response(file_data)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-type"] = mimetype
        return response

    except Exception as e:
        # Basic error handling
        return str(e), 500

# ------------------------------------------------------------------------------
# 6. RUN THE APPLICATION
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # Set debug=False when deploying to a production server.
    app.run(debug=True)

# ==============================================================================
# CUSTOM DATA GENERATOR - FLASK WEB APPLICATION (V2)
#
# This version allows users to select specific columns to generate.
#
# To run this application:
# 1. Save this entire file as `app.py`.
# 2. Create a folder named `templates` in the same directory.
# 3. Create a file named `index.html` inside the `templates` folder.
# 4. Copy the HTML code (provided at the bottom) into `templates/index.html`.
# 5. Run `pip install Flask Faker pandas`.
# 6. Run `python app.py` in your terminal.
# 7. Open your browser and go to http://127.0.0.1:5000
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IMPORT LIBRARIES
# ------------------------------------------------------------------------------
from flask import Flask, render_template, request, make_response
import pandas as pd
from faker import Faker
import random
import io

# ------------------------------------------------------------------------------
# 2. INITIALIZE FLASK APP AND FAKER
# ------------------------------------------------------------------------------
app = Flask(__name__)
fake = Faker()

# ------------------------------------------------------------------------------
# 3. MODULAR DATA GENERATION LOGIC
#    This section defines how to generate data for each possible column.
# ------------------------------------------------------------------------------

# A registry of functions, where each function knows how to generate one column.
# This makes the system modular and easy to extend.
COLUMN_GENERATORS = {
    # Personal Info
    'person_age': lambda: random.randint(18, 70),
    'person_gender': lambda: random.choice(['Male', 'Female']),
    'person_name': lambda: fake.name(),
    'person_email': lambda: fake.email(),
    'person_address': lambda: fake.address().replace('\n', ', '),
    'person_education': lambda: random.choice(['High School', 'Bachelor', 'Master', 'PhD', 'Associate']),
    'person_income': lambda: round(random.uniform(20000, 250000), 2),
    'person_emp_exp': lambda age: random.randint(0, age - 16 if age > 16 else 0), # Depends on age

    # Financial / Loan Info
    'loan_amnt': lambda: round(random.uniform(500, 50000), 2),
    'loan_intent': lambda: random.choice(['Personal', 'Medical', 'Home', 'Debt Consolidation', 'Venture']),
    'loan_int_rate': lambda: round(random.uniform(5.0, 25.0), 2),
    'credit_score': lambda: random.randint(300, 850),
    'previous_loan_defaults_on_file': lambda: random.choice(['Y', 'N']),
    'cb_person_cred_hist_length': lambda age: random.randint(1, min(age - 1, 35)), # Depends on age

    # E-commerce Info
    'product_id': lambda: fake.uuid4(),
    'product_category': lambda: random.choice(['Electronics', 'Apparel', 'Home Goods', 'Books', 'Groceries']),
    'quantity': lambda: random.randint(1, 5),
    'unit_price': lambda: round(random.uniform(5.0, 500.0), 2),
}

def generate_custom_data(num_records, selected_columns):
    """
    Generates a DataFrame with user-selected columns.
    """
    records = []
    for _ in range(num_records):
        record = {}
        
        # --- Handle Dependent Columns First ---
        # Generate age first if it or its dependent columns are needed.
        age_needed = 'person_age' in selected_columns or \
                     'person_emp_exp' in selected_columns or \
                     'cb_person_cred_hist_length' in selected_columns
        
        if age_needed:
            age = COLUMN_GENERATORS['person_age']()
            if 'person_age' in selected_columns:
                record['person_age'] = age

        # --- Generate All Other Selected Columns ---
        for col_name in selected_columns:
            if col_name in record:  # Skip if already generated (like age)
                continue

            # Check for special dependencies
            if col_name == 'person_emp_exp':
                record[col_name] = COLUMN_GENERATORS[col_name](age)
            elif col_name == 'cb_person_cred_hist_length':
                record[col_name] = COLUMN_GENERATORS[col_name](age)
            # For all other columns, call their generator function
            elif col_name in COLUMN_GENERATORS:
                record[col_name] = COLUMN_GENERATORS[col_name]()
        
        records.append(record)
    
    # Ensure the DataFrame columns are in the same order as selected by the user
    return pd.DataFrame(records, columns=selected_columns)


# ------------------------------------------------------------------------------
# 4. FLASK ROUTES
# ------------------------------------------------------------------------------

@app.route('/')
def index():
    """Renders the main page with the form."""
    # We can pass the list of available columns to the template
    # to dynamically generate the checkboxes.
    column_groups = {
        "Personal Info": ['person_name', 'person_age', 'person_gender', 'person_email', 'person_address', 'person_education', 'person_income', 'person_emp_exp'],
        "Financial & Loan Info": ['loan_amnt', 'loan_intent', 'loan_int_rate', 'credit_score', 'previous_loan_defaults_on_file', 'cb_person_cred_hist_length'],
        "E-commerce Info": ['product_id', 'product_category', 'quantity', 'unit_price']
    }
    return render_template('index.html', column_groups=column_groups)

@app.route('/generate', methods=['POST'])
def generate_and_download():
    """Handles form submission, generates data, and serves the CSV."""
    try:
        num_records = int(request.form.get('num_records', 100))
        if not (1 <= num_records <= 100000):
            num_records = 100
    except (ValueError, TypeError):
        num_records = 100
    
    # Get the list of all selected column checkboxes
    selected_columns = request.form.getlist('columns')
    
    if not selected_columns:
        # Handle case where no columns are selected (optional)
        return "Please select at least one column to generate.", 400

    # Generate the data using our new flexible function
    df = generate_custom_data(num_records, selected_columns)

    # Convert DataFrame to a CSV string in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    csv_data = output.getvalue()

    # Create and return the response
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=custom_synthetic_data.csv"
    response.headers["Content-type"] = "text/csv"
    return response

# ------------------------------------------------------------------------------
# 5. RUN THE APPLICATION
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)

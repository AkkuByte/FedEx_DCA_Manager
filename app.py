import os
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- DATA STRUCTURES ---
agencies = [
    {'id': 1, 'name': 'Alpha Collections', 'rating': 9.5, 'assigned_cases': []},
    {'id': 2, 'name': 'Beta Recovery', 'rating': 7.0, 'assigned_cases': []},
    {'id': 3, 'name': 'Gamma Agency', 'rating': 5.5, 'assigned_cases': []}
]

debt_cases = [] 

# --- LOGIC: Weighted Allocation ---
def smart_allocate():
    # Reset
    for agency in agencies:
        agency['assigned_cases'] = []
    
    unallocated = [c for c in debt_cases]
    if not unallocated:
        return

    # Calculate Priority and Sort Cases
    for case in unallocated:
        case['score'] = case['amount'] * (case['days_overdue'] / 30) / 1000
    unallocated.sort(key=lambda x: x['score'], reverse=True)
    
    # Sort Agencies by Rating
    sorted_agencies = sorted(agencies, key=lambda x: x['rating'], reverse=True)

    # Calculate Capacity Weights
    total_rating = sum(a['rating'] for a in agencies)
    total_cases = len(unallocated)
    
    current_allocated_count = 0
    for ag in sorted_agencies:
        ag['capacity'] = int((ag['rating'] / total_rating) * total_cases)
        current_allocated_count += ag['capacity']
    
    # Assign remainder to top agency
    remainder = total_cases - current_allocated_count
    if remainder > 0:
        sorted_agencies[0]['capacity'] += remainder

    # Distribute Cases
    case_idx = 0
    for ag in sorted_agencies:
        count = ag['capacity']
        batch = unallocated[case_idx : case_idx + count]
        
        for case in batch:
            case['status'] = 'Assigned'
            for original in agencies:
                if original['id'] == ag['id']:
                    original['assigned_cases'].append(case)
                    break
        
        case_idx += count

# --- ROUTES ---

@app.route('/')
def dashboard():
    total_debt = sum(c['amount'] for c in debt_cases)
    pending_count = sum(1 for c in debt_cases if c.get('status') == 'Pending')
    
    return render_template('dashboard.html', 
                           cases=debt_cases, 
                           agencies=agencies, 
                           total_debt=total_debt,
                           pending_count=pending_count)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if not file or file.filename == '':
        return redirect(url_for('dashboard'))

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        try:
            df = pd.read_csv(filepath)
            df.columns = df.columns.str.strip().str.lower()
            
            required_cols = {'id', 'customer', 'amount', 'days_overdue'}
            if not required_cols.issubset(df.columns):
                return redirect(url_for('dashboard'))

            if df['amount'].dtype == 'object':
                df['amount'] = df['amount'].astype(str).str.replace('$', '', regex=False)
                df['amount'] = df['amount'].str.replace(',', '', regex=False)
            
            df = df.fillna(0)

            global debt_cases
            debt_cases = [] 
            
            for index, row in df.iterrows():
                debt_cases.append({
                    'id': int(row['id']),
                    'customer': str(row['customer']),
                    'amount': float(row['amount']),
                    'days_overdue': int(row['days_overdue']),
                    'status': 'Pending'
                })

        except Exception as e:
            print(f"Error: {e}")

    return redirect(url_for('dashboard'))

@app.route('/allocate')
def trigger_allocation():
    smart_allocate()
    return redirect(url_for('dashboard'))

@app.route('/reset')
def reset():
    global debt_cases
    debt_cases = [] 
    for ag in agencies:
        ag['assigned_cases'] = []
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
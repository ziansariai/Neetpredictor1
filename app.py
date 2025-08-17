from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key' # In a real app, use a proper secret key
app.config['UPLOAD_FOLDER'] = 'data'
ALLOWED_EXTENSIONS = {'json'}

DATA_FILE = os.path.join(app.config['UPLOAD_FOLDER'], '2024_MCC_Cuttoff_details.json')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_states_from_data():
    """Extracts unique state names from the data file."""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        states = set()
        for item in data:
            try:
                state = item.get('institute_name', '').split(',')[-1].strip()
                if state:
                    states.add(state)
            except:
                pass
        return sorted(list(states))
    except (IOError, json.JSONDecodeError):
        return []

@app.route('/')
def index():
    """Renders the main page with the list of states."""
    states = get_states_from_data()
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        quota_names = sorted(list(set(item.get('quota_name') for item in data if item.get('quota_name'))))
        categories = sorted(list(set(item.get('category') for item in data if item.get('category'))))
        sub_categories = sorted(list(set(item.get('sub_category') for item in data if item.get('sub_category'))))
        courses = sorted(list(set(item.get('course') for item in data if item.get('course'))))
        domicile_states = states
    except (IOError, json.JSONDecodeError):
        quota_names, categories, sub_categories, courses, domicile_states = [], [], [], [], []

    return render_template('index.html',
                           states=states,
                           quota_names=quota_names,
                           categories=categories,
                           sub_categories=sub_categories,
                           courses=courses,
                           domicile_states=domicile_states)

@app.route('/predict', methods=['POST'])
def predict():
    """Handles the prediction request."""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except (IOError, json.JSONDecodeError):
        return jsonify({'error': 'Could not read data file.'}), 500

    try:
        student_air = int(request.form.get('air'))
        domicile_state = request.form.get('domicile_state')
        counselling_authority = request.form.get('counselling_authority')

        quota_names = request.form.getlist('quota_name')
        category = request.form.get('category')
        sub_category = request.form.get('sub_category')
        preferred_states = request.form.getlist('preferred_states')
        course = request.form.get('course')
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {e}'}), 400

    results = []
    if counselling_authority == 'mcc':
        for entry in data:
            entry_state = entry.get('institute_name', '').split(',')[-1].strip()

            is_quota_match = not quota_names or 'all' in quota_names or entry.get('quota_name') in quota_names
            is_category_match = not category or entry.get('category') == category
            is_sub_category_match = not sub_category or entry.get('sub_category') == sub_category
            is_course_match = not course or entry.get('course') == course
            is_state_match = not preferred_states or 'all' in preferred_states or entry_state in preferred_states

            try:
                air_open = int(entry.get('air_open', 0))
                air_close = int(entry.get('air_close', 0))
                is_air_match = air_open <= student_air <= air_close
            except (ValueError, TypeError):
                is_air_match = False

            if is_quota_match and is_category_match and is_sub_category_match and is_course_match and is_state_match and is_air_match:
                results.append(entry)

    return jsonify({
        'results': results,
        'student_info': {
            'air': student_air,
            'domicile': domicile_state,
            'category': category,
            'sub_category': sub_category,
            'quota_name': ', '.join(quota_names),
            'course': course
        }
    })

@app.route('/admin')
def admin():
    """Renders the admin page."""
    return render_template('admin.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file upload."""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('admin'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'warning')
        return redirect(url_for('admin'))
    if file and allowed_file(file.filename):
        # Overwrite the existing file
        file.save(DATA_FILE)
        flash('File successfully uploaded and data has been updated.', 'success')
        return redirect(url_for('admin'))
    else:
        flash('Invalid file type. Please upload a JSON file.', 'danger')
        return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

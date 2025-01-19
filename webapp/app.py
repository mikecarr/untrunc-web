from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for, flash
import subprocess
import os
import re
import time
import shutil

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages
UPLOAD_FOLDER = "/mnt/nfs"
FIXED_FOLDER = os.path.join(UPLOAD_FOLDER, "fixed")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FIXED_FOLDER'] = FIXED_FOLDER

# Ensure the upload and fixed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FIXED_FOLDER, exist_ok=True)

# Function to clean the upload directory
def clean_upload_folder():
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove file or symbolic link
            elif os.path.isdir(file_path) and filename != "fixed":
                shutil.rmtree(file_path)  # Remove directory except 'fixed'
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

@app.route('/')
def index():
    # List all files in the FIXED_FOLDER with metadata
    files = []
    for filename in os.listdir(app.config['FIXED_FOLDER']):
        file_path = os.path.join(app.config['FIXED_FOLDER'], filename)
        if os.path.isfile(file_path):
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
            creation_time = time.ctime(os.path.getctime(file_path))  # Human-readable date
            files.append({
                'name': filename,
                'size': round(file_size_mb, 2),
                'creation_time': creation_time
            })
    return render_template('upload_form.html', files=files)

@app.route('/untrunc', methods=['POST'])
def untrunc():
    clean_upload_folder()
    
    good_file = request.files.get('good')
    bad_file = request.files.get('bad')
    
    if not good_file or not bad_file:
        flash('Both good and bad files are required.', 'error')
        return redirect(url_for('index'))

    good_path = os.path.join(app.config['UPLOAD_FOLDER'], good_file.filename)
    bad_path = os.path.join(app.config['UPLOAD_FOLDER'], bad_file.filename)

    good_file.save(good_path)
    bad_file.save(bad_path)

    try:
        result = subprocess.run(
            ['untrunc', good_path, bad_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        match = re.search(r"Info: saving (.+)", result.stdout)
        if match:
            fixed_file_path = match.group(1)
            os.makedirs(app.config['FIXED_FOLDER'], exist_ok=True)
            fixed_file_name = os.path.basename(fixed_file_path)
            new_fixed_file_path = os.path.join(app.config['FIXED_FOLDER'], fixed_file_name)
            shutil.move(fixed_file_path, new_fixed_file_path)
            flash(f'Conversion successful! Fixed file saved as {fixed_file_name}.', 'success')
        else:
            flash('Conversion failed: Fixed filename not found in output.', 'error')
    except subprocess.CalledProcessError as e:
        flash(f'Conversion failed: {e.stderr.strip()}', 'error')

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['FIXED_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['FIXED_FOLDER'], filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
        return jsonify({'status': 'success', 'message': f'{filename} deleted successfully.'})
    else:
        return jsonify({'status': 'fail', 'message': f'{filename} not found.'}), 404

@app.route('/view/<filename>')
def view_file(filename):
    file_path = os.path.join(app.config['FIXED_FOLDER'], filename)
    if not os.path.isfile(file_path):
        flash(f"The file {filename} does not exist.", "error")
        return redirect(url_for('index'))

    # Get the file extension in lowercase
    file_extension = os.path.splitext(filename)[1].lower()

    return render_template('viewer.html', filename=filename, file_extension=file_extension)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

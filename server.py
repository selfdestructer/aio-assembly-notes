from flask import Flask, render_template, request, jsonify
import os
import glob
from processor import process_audio

app = Flask(__name__)

# CONFIGURATION
# TODO: Set this to the directory where AIO Launcher saves recordings
# For Termux, standard paths might be:
# /sdcard/Music/Recordings/
# /sdcard/Android/data/ ... (might be restricted)
# For now, we default to a 'recordings' folder in the current directory for testing
RECORDINGS_DIR = os.path.join(os.getcwd(), "recordings")

# Create dir if it doesn't exist for testing
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)

def get_latest_recording():
    # patterns to look for audio files
    patterns = ["*.mp3", "*.wav", "*.m4a", "*.ogg"]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(RECORDINGS_DIR, pattern)))
    
    if not files:
        return None
    
    # Sort by modification time, newest first
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

@app.route('/')
def index():
    latest_file = get_latest_recording()
    filename = os.path.basename(latest_file) if latest_file else "No recordings found"
    return render_template('index.html', filename=filename)

@app.route('/process/<mode>', methods=['POST'])
def process(mode):
    latest_file = get_latest_recording()
    if not latest_file:
        return jsonify({"status": "error", "message": "No audio file found to process"})
    
    try:
        output_file = process_audio(latest_file, mode)
        if "Error" in output_file:
             return jsonify({"status": "error", "message": output_file})
             
        return jsonify({
            "status": "success", 
            "message": f"Processed {os.path.basename(latest_file)}", 
            "output": output_file
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

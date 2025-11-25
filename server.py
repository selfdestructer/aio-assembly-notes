from flask import Flask, render_template, request, jsonify
import os
import glob
from werkzeug.utils import secure_filename
from flask_basicauth import BasicAuth
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import posthog
from processor import process_audio
from context_manager import get_context, log_decision
from ghost_ship import get_ghost_ship_prompt

# Initialize Sentry
if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# Initialize PostHog
if os.getenv("POSTHOG_API_KEY"):
    posthog.project_api_key = os.getenv("POSTHOG_API_KEY")
    posthog.host = os.getenv("POSTHOG_HOST", "https://app.posthog.com")

app = Flask(__name__)

# Security: Basic Auth
app.config['BASIC_AUTH_USERNAME'] = os.getenv("AUTH_USER", "admin")
app.config['BASIC_AUTH_PASSWORD'] = os.getenv("AUTH_PASS", "password")
# Only force auth if env vars are set (to avoid locking out local dev if not configured)
if os.getenv("AUTH_PASS"):
    app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

# CONFIGURATION
# AIO Launcher usually saves to internal storage. Update this to your actual path.
# Common paths: /sdcard/AIO Launcher/recordings or /sdcard/Music/Recordings
RECORDINGS_DIR = "/sdcard/Music/Recordings" 
if not os.path.exists(RECORDINGS_DIR):
    # Fallback for Cloud Run or testing
    RECORDINGS_DIR = os.path.join(os.getcwd(), "Life_OS", "01_Inbox")
    if not os.path.exists(RECORDINGS_DIR):
        os.makedirs(RECORDINGS_DIR)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    if os.getenv("POSTHOG_API_KEY"):
        posthog.capture('user_web', 'view_dashboard')
    return render_template('index.html', filename=filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(RECORDINGS_DIR, filename)
        file.save(save_path)
        
        if os.getenv("POSTHOG_API_KEY"):
            posthog.capture('user_web', 'upload_file', {'filename': filename})
            
        return jsonify({"status": "success", "message": "File uploaded successfully", "filename": filename})
    else:
        return jsonify({"status": "error", "message": "Invalid file type"})

@app.route('/process/<mode>', methods=['POST'])
def process(mode):
    latest_file = get_latest_recording()
    if not latest_file:
        return jsonify({"status": "error", "message": "No audio file found to process"})
    
    try:
        # Capture arguments like "show_ghost_ship" from the request
        options = request.json or {}
        
        if os.getenv("POSTHOG_API_KEY"):
            posthog.capture('user_web', 'process_audio', {'mode': mode, 'options': options})

        output_file = process_audio(latest_file, mode, options)
        
        if "Error" in output_file:
             return jsonify({"status": "error", "message": output_file})
             
        return jsonify({
            "status": "success", 
            "message": f"Processed {os.path.basename(latest_file)}", 
            "output": output_file
        })
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, render_template, Response, redirect, session, request, url_for
import cv2
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_in_production'

# Global list to store logs in memory
detection_logs = []

# Load face cascade
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# Use 'cap' to avoid naming conflicts with the 'camera' route
cap = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        # 1. DETECT FACES (using grayscale)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # 2. LOG DETECTION
        if len(faces) > 0:
            log_entry = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'faces': len(faces),
                'details': "Face detected in live stream"
            }
            # Only log if it's a new "event" (preventing thousands of logs per second)
            if not detection_logs or detection_logs[-1]['time'] != log_entry['time']:
                detection_logs.append(log_entry)

        # 3. DRAW RECTANGLES
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # 4. FIX BLUE TINT (Ensure we are sending BGR to the encoder properly)
        # Flask/Browsers usually expect the byte stream from imencode to be handled correctly,
        # but if it's still blue, ensure your webcam isn't using a weird color space.
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# ====================== ROUTES ======================

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect(url_for('dashboard'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera')
def camera():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('camera.html')

@app.route('/analytics')
def analytics():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Pass the global detection_logs to the template
    return render_template('analytics.html', logs=detection_logs)

if __name__ == '__main__':
    # Use 5001 to avoid the blocked port
    import webbrowser; webbrowser.open("http://127.0.0.1:5001")
    app.run(debug=True, port=5001)
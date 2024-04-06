from flask import Flask, render_template, request, redirect, url_for, flash
import cv2
import os
import numpy as np
from werkzeug.utils import secure_filename
app = Flask(__name__)

UPLOAD_FOLDER = 'upload'
PROCESSED_FOLDER = 'static/processed/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'png', 'bmp', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '13041e5e95e6e69331e30c8f4e579162'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about', methods=['GET','POST'])
def about():
    return render_template('about.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/edit-image', methods=['GET','POST'])
def edit_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file')
            return redirect(request.url)

        file = request.files['image']

        if file.filename == '':
            flash('No file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            operation = request.form.get('operation')

            img = cv2.imread(filepath)

            if operation == 'grayscale':
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            elif operation == 'blur':
                img = cv2.blur(img, (10, 10))
            elif operation == 'removebg':
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            elif operation == 'remove_noise':
                img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 15) 
            elif operation == 'contour':
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            elif operation == 'detail':
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                img = cv2.filter2D(img, -1, kernel)
            elif operation == 'edge_enhance':
                kernel = np.array([[-1,-1,-1,-1,-1], [-1,2,2,2,-1], [-1,2,8,2,-1], [-1,2,2,2,-1], [-1,-1,-1,-1,-1]]) / 8.0
                img = cv2.filter2D(img, -1, kernel)
            elif operation == 'emboss':
                kernel = np.array([[-2,-1,0], [-1,1,1], [0,1,2]])
                img = cv2.filter2D(img, -1, kernel)
            elif operation == 'find_edges':
                img = cv2.Canny(img, 100, 200)
            elif operation == 'sharpen':
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                img = cv2.filter2D(img, -1, kernel)
            elif operation == 'smooth':
                img = cv2.GaussianBlur(img, (5, 5), 0)
            elif operation == 'smooth_more':
                img = cv2.GaussianBlur(img, (15, 15), 0)
           

            edited_filename = f"edited_{filename}"
            edited_filepath = os.path.join(PROCESSED_FOLDER, edited_filename)
            cv2.imwrite(edited_filepath, img)
            flash(f"Your file has been processed and is available <a href='{edited_filepath}' target='_blank'>here</a>")

            return render_template('image.html', image=url_for('static', filename=os.path.join(edited_filepath)))

    return render_template('image.html', image=None)

@app.route('/edit-video', methods=['GET','POST'])
def edit_video():
    return render_template('video.html')

if __name__ == '__main__':
    app.run(debug=True)
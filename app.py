import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
import cv2
import pytesseract

# Specify the path to the Tesseract executable if necessary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust this path based on your installation

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def read_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def read_image(file_path):
    # Read the image using OpenCV
    image = cv2.imread(file_path)
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Use Tesseract to extract text
    text = pytesseract.image_to_string(gray_image)
    return text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            ext = filename.rsplit('.', 1)[1].lower()
            if ext == 'pdf':
                text = read_pdf(file_path)
            elif ext == 'docx':
                text = read_docx(file_path)
            elif ext in ['png', 'jpg', 'jpeg']:
                text = read_image(file_path)
            else:
                text = "Unsupported file type"
            
            return render_template('index.html', text=text)
    return render_template('index.html', text='')

if __name__ == '__main__':
    app.run()


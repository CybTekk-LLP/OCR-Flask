from flask import Flask, render_template, request, redirect, url_for
import os
import cv2
import pytesseract
from PIL import Image
import re

app = Flask(__name__)

# Configure the path where uploaded images will be stored temporarily
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresholded = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresholded


def ocr(image_path):
    try:
        processed_image = preprocess_image(image_path)
        pil_image = Image.fromarray(processed_image)
        text = pytesseract.image_to_string(pil_image)
        # Filter out non-numeric characters and handle common misinterpretations
        # Keep only digits and dot
        cleaned_text = text.replace(' ', '')
        cleaned_text = cleaned_text.replace('i', '1')  # Replace 'i' with '1'
        cleaned_text = cleaned_text.replace('S', '5')  # Replace 'S' with '5'
        cleaned_text = cleaned_text.replace('l', '1')  # Replace 'l' with '1'
        cleaned_text = cleaned_text.replace('o', '0')  # Replace 'o' with '0'
        cleaned_text = cleaned_text.replace('O', '0')  # Replace 'O' with '0'
        cleaned_text = cleaned_text.replace('B', '8')  # Replace 'B' with '8'
        cleaned_text = cleaned_text.replace('D', '0')  # Replace 'D' with '0'
        cleaned_text = cleaned_text.replace('(', '1')
        cleaned_text = cleaned_text.replace(')', '1')
        cleaned_text = cleaned_text.replace('|', '1')
        # Add more replacements as needed
        return cleaned_text
    except Exception as e:
        print("OCR Error:", e)
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return redirect(request.url)
        if file:
            # Save the uploaded file
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Perform OCR on the uploaded file
            extracted_text = ocr(filepath)
            # Pass the extracted text to the result page
            return redirect(url_for('result', text=extracted_text))


@app.route('/result')
def result():
    # Get the extracted text from the URL parameters
    extracted_text = request.args.get('text', '')
    return render_template('result.html', extracted_text=extracted_text)


if __name__ == '__main__':
    app.run(debug=True)

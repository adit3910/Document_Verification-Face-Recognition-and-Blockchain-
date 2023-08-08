from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import cv2
import time
from fpdf import FPDF
from PIL import Image
import face_recognition

app = Flask(__name__, static_folder='F:\project_possible\static')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def capture_images(num_images):
    video_capture = cv2.VideoCapture(0)
    capture_gap = 2  # Time gap between captures in seconds
    captured_images = []

    for i in range(num_images):
        time.sleep(capture_gap)
        ret, frame = video_capture.read()
        if ret:
            image_path = os.path.join('static/uploads', f'live_image_{i}.jpg')
            cv2.imwrite(image_path, frame)
            captured_images.append(image_path)

    video_capture.release()
    return captured_images

# Function to compare the captured image with uploaded images
def compare_images(captured_image_path, document_paths):

    captured_image = face_recognition.load_image_file(captured_image_path)
    captured_encoding = face_recognition.face_encodings(captured_image)

    if len(captured_encoding) == 0:
        # No faces detected in the captured image
        return False, []

    matched_images = []

    for document_path in document_paths:
        document_image = face_recognition.load_image_file(document_path)
        document_encoding = face_recognition.face_encodings(document_image)

        if len(document_encoding) == 0:
            # No faces detected in the document image
            continue

        # Compare the face encodings
        match = face_recognition.compare_faces(document_encoding, captured_encoding[0])
        if match[0]:
            matched_images.append(os.path.basename(document_path))


    return len(matched_images) > 0, matched_images

# Function to create a PDF with watermarked images
def create_pdf(images,phone_number):
    pdf = FPDF()
    directory =os.getcwd()
    directory= directory+'\\'+phone_number
    count =0
    for image in images:
        count += 1
        if count < 5:
            image_path = os.path.join(directory, image)

            # Open the image and get its dimensions
            img = Image.open(image_path)
            img_w, img_h = img.size
            pdf.add_page()

            # Calculate the page dimensions and image position
            page_w, page_h = pdf.w, pdf.h
            if img_w > img_h:  # Landscape image
                img_ratio = img_w / img_h
                page_ratio = page_w / page_h
                if img_ratio > page_ratio:
                    img_new_w = page_w
                    img_new_h = img_new_w / img_ratio
                else:
                    img_new_h = page_h
                    img_new_w = img_new_h * img_ratio
                img_x = (page_w - img_new_w) / 2
                img_y = (page_h - img_new_h) / 2
            else:  # Portrait image
                img_ratio = img_h / img_w
                page_ratio = page_h / page_w
                if img_ratio > page_ratio:
                    img_new_h = page_h
                    img_new_w = img_new_h / img_ratio
                else:
                    img_new_w = page_w
                    img_new_h = img_new_w * img_ratio
                img_x = (page_w - img_new_w) / 2
                img_y = (page_h - img_new_h) / 2

            # Add image to PDF
            pdf.image(image_path, x=img_x, y=img_y, w=img_new_w, h=img_new_h)

            # Add watermark text
            watermark_font_size = min(img_new_w, img_new_h) * 0.02
            pdf.set_font('Arial', 'B', int(watermark_font_size))
            pdf.set_text_color(128)  # Set the color to gray
            watermark_text = 'Verified'
            watermark_text_width = pdf.get_string_width(watermark_text)
            watermark_text_height = watermark_font_size
            watermark_x = (page_w - watermark_text_width) / 2
            watermark_y = (page_h - watermark_text_height) / 2
            pdf.text(watermark_x, watermark_y, watermark_text)

                       # Add digital signature image
            signature_image_path = 'static//signature_t.png'  # Replace with the path to your digital signature image
            signature_image = Image.open(signature_image_path)
            signature_image_w, signature_image_h = signature_image.size
            signature_image_scale = 0.05  # Adjust the scale to reduce the size of the image
            signature_image_new_w = signature_image_w * signature_image_scale
            signature_image_new_h = signature_image_h * signature_image_scale
            signature_image_x = page_w - signature_image_new_w - 10  # Adjust the position as per your requirement
            signature_image_y = page_h - signature_image_new_h - 10  # Adjust the position as per your requirement
            pdf.image(signature_image_path, x=signature_image_x, y=signature_image_y, w=signature_image_new_w,
                      h=signature_image_new_h)
    pdf.output(directory+'\\result.pdf')
    return(directory+'\\result.pdf')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    aadhar_file = request.files['aadhar']
    driving_license_file = request.files['driving_license']
    pan_file = request.files['pan']
    voter_id_file = request.files['voter_id']
    phone_number = request.form.get('phone')
    pdf_path=None
    # Check if any documents were uploaded
    if aadhar_file and allowed_file(aadhar_file.filename) and \
       driving_license_file and allowed_file(driving_license_file.filename) and \
       pan_file and allowed_file(pan_file.filename) and \
       voter_id_file and allowed_file(voter_id_file.filename):

        directory =os.getcwd()
        directory= directory+'\\'+ phone_number
        if not os.path.exists(directory):
             os.mkdir(directory)

        # Save the uploaded files
        aadhar_filename = secure_filename(aadhar_file.filename)
        aadhar_path = os.path.join(directory, aadhar_filename)
        aadhar_file.save(aadhar_path)

        driving_license_filename = secure_filename(driving_license_file.filename)
        driving_license_path = os.path.join(directory, driving_license_filename)
        driving_license_file.save(driving_license_path)

        pan_filename = secure_filename(pan_file.filename)
        pan_path = os.path.join(directory, pan_filename)
        pan_file.save(pan_path)

        voter_id_filename = secure_filename(voter_id_file.filename)
        voter_id_path = os.path.join(directory, voter_id_filename)
        voter_id_file.save(voter_id_path)

        document_paths = [aadhar_path, driving_license_path, pan_path, voter_id_path]

        captured_images = sorted(os.listdir(app.config['UPLOAD_FOLDER']))
        #matched_images = []

        for captured_image in captured_images:
            print(captured_image)
            captured_image_path = os.path.join(app.config['UPLOAD_FOLDER'], captured_image)
            match, matched_images = compare_images(captured_image_path, document_paths)
            if match:
                #print('match print',matched)
                #matched_images.extend(matched)
                print(matched_images)
                print(len(matched_images))
        verification_successful = len(matched_images) == 4        
        if  verification_successful:
            pdf_path=create_pdf(matched_images,phone_number)
            return redirect(url_for('result',pdf_path=pdf_path,status=1))
        else:
            res = 'Verification failed, only '+str(len(matched_images)) +' documents verified'
    # No match found or incomplete file uploads
    if pdf_path:
        return render_template('result.html', message=res, pdf_path=pdf_path,status=1)
    else:
        # Handle the case when pdf_path is not generated
        return render_template('result.html', message=res, pdf_path=None, status=0)
    

@app.route('/capture')
def capture():
    # Modify the number of images you want to capture
    num_images = 3
    captured_images = capture_images(num_images)
    print(captured_images)
    return render_template('capture.html', images=captured_images)


 
@app.route('/result')
def result():
    pdf_path = request.args.get('pdf_path')
    status = request.args.get('status')
    message = request.args.get('message')
    if status == '1':
        message="Verification Successful"
        return render_template('result.html', message=message, pdf_path=pdf_path, status=1)
    else:
        return render_template('result.html', message=message, pdf_path=None, status=0)
   

@app.route('/download_pdf/<path:pdf_path>')
def download_pdf(pdf_path):
    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run()

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os
import zipfile
import tempfile
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

def generate_certificate(name, certificate_date=None):
    """Generate a single certificate for the given name"""
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    certificate_template = Image.open(os.path.join(current_dir, 'certificate_2.png'))
    draw = ImageDraw.Draw(certificate_template)
    
    # Name on certificate
    font = ImageFont.truetype(os.path.join(current_dir, 'DancingScript-Regular.ttf'), 100)
    text_position = (553, 420)
    draw.text(text_position, name, font=font, fill=(0, 6, 31))
    
    # Date on certificate (if provided)
    if certificate_date:
        try:
            # Parse the date and format it nicely
            date_obj = datetime.strptime(certificate_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
            
            # Add date to certificate
            date_font = ImageFont.truetype(os.path.join(current_dir, 'MrDeHaviland-Regular.ttf'), 35)
            date_position = (350, 900)  # Adjust position as needed
            draw.text(date_position, formatted_date, font=date_font, fill=(0, 0, 0))
        except ValueError:
            pass  # Skip if date format is invalid
    
    return certificate_template

def create_zip_with_certificates(names, certificate_date=None):
    """Create a zip file containing certificates for all names"""
    # Create a temporary file for the zip
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    
    with zipfile.ZipFile(temp_zip.name, 'w') as zip_file:
        for name in names:
            # Generate certificate
            certificate = generate_certificate(name.strip(), certificate_date)
            
            # Save certificate to bytes
            img_bytes = io.BytesIO()
            certificate.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Add to zip
            filename = f"{name.strip()}_certificate.png"
            zip_file.writestr(filename, img_bytes.getvalue())
    
    return temp_zip.name

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return generate_certificate_handler()
    return render_template('index.html')

def generate_certificate_handler():
    try:
        option = request.form.get('option')
        certificate_date = request.form.get('certificate_date', '')
        
        # Validate date
        if not certificate_date:
            flash('Please select a certificate date.', 'error')
            return redirect(url_for('index'))
        
        if option == 'single':
            name = request.form.get('single_name', '').strip()
            if not name:
                flash('Please enter a name for single certificate generation.', 'error')
                return redirect(url_for('index'))
            
            # Generate single certificate and return PNG directly
            certificate = generate_certificate(name, certificate_date)
            
            # Save certificate to bytes
            img_bytes = io.BytesIO()
            certificate.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"{name}_{timestamp}.png"
            
            return send_file(
                img_bytes,
                as_attachment=True,
                download_name=download_filename,
                mimetype='image/png'
            )
            
        elif option == 'multiple':
            names_input = request.form.get('multiple_names', '').strip()
            if not names_input:
                flash('Please enter names for multiple certificate generation.', 'error')
                return redirect(url_for('index'))
            
            names = [name.strip() for name in names_input.split(',') if name.strip()]
            if not names:
                flash('Please enter valid names separated by commas.', 'error')
                return redirect(url_for('index'))
            
            # Create zip file with multiple certificates
            zip_path = create_zip_with_certificates(names, certificate_date)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"certificates_{timestamp}.zip"
            
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=download_filename,
                mimetype='application/zip'
            )
        else:
            flash('Please select an option (Single or Multiple).', 'error')
            return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure Certificates directory exists
    os.makedirs('Certificates', exist_ok=True)
    app.run(debug=True)

# For Vercel deployment
application = app

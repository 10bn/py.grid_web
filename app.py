import os
import inspect
import sqlite3
from flask import Flask, render_template, request, send_file, redirect, url_for

from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.units import mm
from io import BytesIO

app = Flask(__name__)

DATABASE = 'statistics.db'

def init_db():
    """Initialize the database and create the statistics table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY,
            pdf_count INTEGER DEFAULT 0
        )
    ''')
    # Ensure there's a row in the table
    c.execute('SELECT COUNT(*) FROM statistics')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO statistics (pdf_count) VALUES (0)')
    conn.commit()
    conn.close()

def increment_pdf_count():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE statistics SET pdf_count = pdf_count + 1 WHERE id = 1')
    conn.commit()
    conn.close()

def get_pdf_count():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT pdf_count FROM statistics WHERE id = 1')
    count = c.fetchone()[0]
    conn.close()
    return count

def get_available_paper_sizes():
    """
    Retrieve all available paper sizes from reportlab.lib.pagesizes.
    
    Returns:
        dict: A dictionary mapping paper size names to their (width, height) in points.
    """
    available_sizes = {}
    for name, size in inspect.getmembers(pagesizes):
        if name.isupper() and isinstance(size, tuple) and len(size) == 2:
            available_sizes[name] = size
    return available_sizes

AVAILABLE_PAPER_SIZES = get_available_paper_sizes()

def validate_hex_color(hex_color):
    """Validate if the provided string is a valid hex color code."""
    if not isinstance(hex_color, str):
        return False
    if not hex_color.startswith("#"):
            return False
    if len(hex_color) not in [4, 7]:
        return False
    hex_digits = "0123456789ABCDEFabcdef"
    for char in hex_color[1:]:
        if char not in hex_digits:
            return False
    return True

def create_grid_pdf(paper_width_mm, paper_height_mm, grid_size_mm=5, grid_color="#B7C9EE",
                    background_color="#FFFFFF", line_thickness=0.3):
    """
    Create a vector-based grid PDF using ReportLab with specified paper size and background color.
    
    Parameters:
    - paper_width_mm (float): Width of the paper in millimeters.
    - paper_height_mm (float): Height of the paper in millimeters.
    - grid_size_mm (float): Size of each grid square in millimeters.
    - grid_color (str): Hex color code for the grid lines.
    - background_color (str): Hex color code for the background.
    - line_thickness (float): Thickness of the grid lines in points.
    
    Returns:
        BytesIO: In-memory PDF file.
    """
    buffer = BytesIO()
    try:
        # Convert paper size from mm to points
        paper_width_pt = paper_width_mm * mm
        paper_height_pt = paper_height_mm * mm

        # Create a canvas with custom paper size
        c = canvas.Canvas(buffer, pagesize=(paper_width_pt, paper_height_pt))

        # Set background color
        background_color_rgb = tuple(int(background_color.lstrip("#")[i:i+2], 16)/255 for i in (0, 2, 4))
        c.setFillColorRGB(*background_color_rgb)
        c.rect(0, 0, paper_width_pt, paper_height_pt, fill=1, stroke=0)

        # Convert grid size to points
        grid_size_pt = grid_size_mm * mm

        # Convert hex color to RGB (0-1 range)
        grid_color_rgb = tuple(int(grid_color.lstrip("#")[i:i+2], 16)/255 for i in (0, 2, 4))

        # Set grid line color and line width
        c.setStrokeColorRGB(*grid_color_rgb)
        c.setLineWidth(line_thickness)  # Set line width based on user input

        # Draw vertical lines
        x = 0
        while x <= paper_width_pt:
            c.line(x, 0, x, paper_height_pt)
            x += grid_size_pt

        # Draw horizontal lines
        y = 0
        while y <= paper_height_pt:
            c.line(0, y, paper_width_pt, y)
            y += grid_size_pt

        # Finalize the PDF
        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        buffer.close()
        raise RuntimeError(f"Failed to create PDF: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    messages = []
    predefined_size_names = sorted(AVAILABLE_PAPER_SIZES.keys())
    pdf_count = get_pdf_count()

    if request.method == 'POST':
        # Retrieve form data
        paper_size_option = request.form.get('paper_size_option')
        predefined_size = request.form.get('predefined_size')
        custom_width_cm = request.form.get('custom_width_cm')
        custom_height_cm = request.form.get('custom_height_cm')
        grid_size_mm = request.form.get('grid_size_mm')
        grid_color = request.form.get('grid_color')
        background_color = request.form.get('background_color')
        line_thickness = request.form.get('line_thickness')
        output_filename = request.form.get('output_filename')

        # Validation
        # Paper size
        if paper_size_option == 'predefined':
            if predefined_size not in AVAILABLE_PAPER_SIZES:
                errors.append("Selected predefined paper size is not supported.")
            else:
                paper_width_pt, paper_height_pt = AVAILABLE_PAPER_SIZES[predefined_size]
                paper_width_mm = paper_width_pt / mm
                paper_height_mm = paper_height_pt / mm
        elif paper_size_option == 'custom':
            try:
                custom_width_cm = float(custom_width_cm)
                custom_height_cm = float(custom_height_cm)
                if custom_width_cm <= 0 or custom_height_cm <= 0:
                    errors.append("Custom paper dimensions must be positive numbers.")
                paper_width_mm = custom_width_cm * 10
                paper_height_mm = custom_height_cm * 10
            except ValueError:
                errors.append("Custom paper dimensions must be valid numbers.")
        else:
            errors.append("Invalid paper size option selected.")

        # Grid size
        try:
            grid_size_mm = float(grid_size_mm)
            if grid_size_mm <= 0:
                errors.append("Grid size must be a positive number.")
        except ValueError:
            errors.append("Grid size must be a valid number.")

        # Grid color
        if not validate_hex_color(grid_color):
            errors.append("Invalid hex color code for Grid Color.")

        # Background color
        if not validate_hex_color(background_color):
            errors.append("Invalid hex color code for Background Color.")

        # Line thickness
        try:
            line_thickness = float(line_thickness)
            if line_thickness <= 0:
                errors.append("Line thickness must be a positive number.")
        except ValueError:
            errors.append("Line thickness must be a valid number.")

        # Output filename
        if not output_filename.strip():
            output_filename = "grid_template.pdf"
        elif not output_filename.lower().endswith('.pdf'):
            output_filename += '.pdf'

        if errors:
            # Render the form with errors
            return render_template('index.html', predefined_sizes=predefined_size_names, errors=errors, messages=messages, count=pdf_count, output_filename=output_filename)
        
        # Generate PDF
        try:
            pdf_buffer = create_grid_pdf(
                paper_width_mm=paper_width_mm,
                paper_height_mm=paper_height_mm,
                grid_size_mm=grid_size_mm,
                grid_color=grid_color,
                background_color=background_color,
                line_thickness=line_thickness
            )
            # Increment the PDF count
            increment_pdf_count()
            pdf_count += 1  # Update the count for display
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/pdf'
            )
        except Exception as e:
            errors.append(str(e))
            return render_template('index.html', predefined_sizes=predefined_size_names, errors=errors, messages=messages, count=pdf_count, output_filename=output_filename)

    # GET request
    output_filename = "grid_template.pdf"
    return render_template('index.html', predefined_sizes=predefined_size_names, errors=errors, messages=messages, count=pdf_count, output_filename=output_filename)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5010))  # Default to 5000 if PORT isn't set
    app.run(host='0.0.0.0', port=port)

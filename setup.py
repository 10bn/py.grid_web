import os

# Define the project structure and file contents
project_structure = {
    "app.py": """import os
import inspect
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.units import mm, cm
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

def get_available_paper_sizes():
    \"""
    Retrieve all available paper sizes from reportlab.lib.pagesizes.
    
    Returns:
        dict: A dictionary mapping paper size names to their (width, height) in points.
    \"""
    available_sizes = {}
    for name, size in inspect.getmembers(pagesizes):
        if name.isupper() and isinstance(size, tuple) and len(size) == 2:
            available_sizes[name] = size
    return available_sizes

AVAILABLE_PAPER_SIZES = get_available_paper_sizes()

def validate_hex_color(hex_color):
    \"""Validate if the provided string is a valid hex color code.\"""
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
    \"""
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
    \"""
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
        errors = []

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
            errors.append("Output filename cannot be empty.")
        elif not output_filename.lower().endswith('.pdf'):
            output_filename += '.pdf'

        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('index'))

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

            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/pdf'
            )
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('index'))

    # GET request
    predefined_size_names = sorted(AVAILABLE_PAPER_SIZES.keys())
    return render_template('index.html', predefined_sizes=predefined_size_names)

if __name__ == '__main__':
    app.run(debug=True)
""",
    "requirements.txt": """Flask==2.2.5
reportlab==3.6.12
""",
    os.path.join("templates", "index.html"): """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Grid Template Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/styles.css') }}" rel="stylesheet">
</head>
<body>
    <div class="container my-5">
        <h1 class="text-center mb-4">Grid Template Generator</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        
        <form method="POST" action="{{ url_for('index') }}">
            <!-- Paper Size Selection -->
            <div class="mb-3">
                <label for="paper_size_option" class="form-label">Paper Size:</label>
                <select class="form-select" id="paper_size_option" name="paper_size_option" required>
                    <option value="predefined" selected>Predefined</option>
                    <option value="custom">Custom</option>
                </select>
            </div>

            <!-- Predefined Sizes -->
            <div class="mb-3" id="predefined_size_div">
                <label for="predefined_size" class="form-label">Select Size:</label>
                <select class="form-select" id="predefined_size" name="predefined_size" required>
                    {% for size in predefined_sizes %}
                        <option value="{{ size }}">{{ size }}</option>
                    {% endfor %}
                </select>
            </div>

            <!-- Custom Sizes -->
            <div id="custom_size_div" class="d-none">
                <div class="mb-3">
                    <label for="custom_width_cm" class="form-label">Width (cm):</label>
                    <input type="number" step="0.1" min="0.1" class="form-control" id="custom_width_cm" name="custom_width_cm" placeholder="e.g., 21.0">
                </div>
                <div class="mb-3">
                    <label for="custom_height_cm" class="form-label">Height (cm):</label>
                    <input type="number" step="0.1" min="0.1" class="form-control" id="custom_height_cm" name="custom_height_cm" placeholder="e.g., 29.7">
                </div>
            </div>

            <!-- Grid Size -->
            <div class="mb-3">
                <label for="grid_size_mm" class="form-label">Grid Size (mm):</label>
                <input type="number" step="0.1" min="0.1" class="form-control" id="grid_size_mm" name="grid_size_mm" value="5.0" required>
            </div>

            <!-- Grid Color -->
            <div class="mb-3">
                <label for="grid_color" class="form-label">Grid Color:</label>
                <input type="color" class="form-control form-control-color" id="grid_color" name="grid_color" value="#B7C9EE" title="Choose Grid Color">
            </div>

            <!-- Background Color -->
            <div class="mb-3">
                <label for="background_color" class="form-label">Background Color:</label>
                <input type="color" class="form-control form-control-color" id="background_color" name="background_color" value="#FFFFFF" title="Choose Background Color">
            </div>

            <!-- Line Thickness -->
            <div class="mb-3">
                <label for="line_thickness" class="form-label">Line Thickness (pt):</label>
                <input type="number" step="0.1" min="0.1" class="form-control" id="line_thickness" name="line_thickness" value="0.3" required>
            </div>

            <!-- Output Filename -->
            <div class="mb-3">
                <label for="output_filename" class="form-label">Output Filename:</label>
                <div class="input-group">
                    <input type="text" class="form-control" id="output_filename" name="output_filename" placeholder="e.g., A4_grid.pdf" required>
                    <button class="btn btn-outline-secondary" type="button" id="generate_filename">Generate Default</button>
                </div>
                <div class="form-text">Ensure the filename ends with .pdf</div>
            </div>

            <!-- Submit Button -->
            <div class="d-grid">
                <button type="submit" class="btn btn-primary btn-lg">Generate Grid PDF</button>
            </div>
        </form>
    </div>

    <!-- Bootstrap JS and Dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/scripts.js') }}"></script>
</body>
</html>
""",
    os.path.join("static", "css", "styles.css"): """body {
    background-color: #f8f9fa;
}

h1 {
    color: #343a40;
}
""",
    os.path.join("static", "js", "scripts.js"): """document.addEventListener('DOMContentLoaded', function () {
    const paperSizeOption = document.getElementById('paper_size_option');
    const predefinedSizeDiv = document.getElementById('predefined_size_div');
    const customSizeDiv = document.getElementById('custom_size_div');
    const generateFilenameBtn = document.getElementById('generate_filename');
    const outputFilenameInput = document.getElementById('output_filename');

    paperSizeOption.addEventListener('change', function () {
        if (this.value === 'custom') {
            predefinedSizeDiv.classList.add('d-none');
            customSizeDiv.classList.remove('d-none');
        } else {
            predefinedSizeDiv.classList.remove('d-none');
            customSizeDiv.classList.add('d-none');
        }
    });

    generateFilenameBtn.addEventListener('click', function () {
        const paperSizeOptionValue = paperSizeOption.value;
        let paperSizeStr = '';
        if (paperSizeOptionValue === 'predefined') {
            const predefinedSize = document.getElementById('predefined_size').value;
            paperSizeStr = predefinedSize;
        } else {
            const customWidth = document.getElementById('custom_width_cm').value;
            const customHeight = document.getElementById('custom_height_cm').value;
            paperSizeStr = `${customWidth}x${customHeight}cm`;
        }

        const gridSize = document.getElementById('grid_size_mm').value;
        const gridColor = document.getElementById('grid_color').value.slice(1).toUpperCase();
        const backgroundColor = document.getElementById('background_color').value.slice(1).toUpperCase();
        const lineThickness = document.getElementById('line_thickness').value;

        const filename = `${paperSizeStr}_grid_${Math.round(gridSize)}mm_${gridColor}_bg${backgroundColor}_${lineThickness}pt.pdf`;
        outputFilenameInput.value = filename;
    });
});
""",
}

def create_file(path, content):
    """Create a file with the given path and content."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {path}")
    except Exception as e:
        print(f"Failed to create {path}: {e}")

def main():
    # Create the main project directory
    project_dir = "grid_template_generator_web"
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
        print(f"Created project directory: {project_dir}")
    else:
        print(f"Project directory already exists: {project_dir}")

    # Change the working directory to the project directory
    os.chdir(project_dir)

    # Create subdirectories
    subdirs = ["templates", os.path.join("static", "css"), os.path.join("static", "js")]
    for subdir in subdirs:
        if not os.path.exists(subdir):
            os.makedirs(subdir)
            print(f"Created subdirectory: {subdir}")
        else:
            print(f"Subdirectory already exists: {subdir}")

    # Create and write files
    for filepath, content in project_structure.items():
        create_file(filepath, content)

    print("\nAll files have been created successfully!")
    print("Next Steps:")
    print("1. Navigate to the project directory:")
    print(f"   cd {project_dir}")
    print("2. (Optional) Create and activate a virtual environment:")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`")
    print("3. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("4. Run the Flask application:")
    print("   python app.py")
    print("5. Open your browser and go to http://127.0.0.1:5000/ to use the app.")

if __name__ == "__main__":
    main()

// static/js/scripts.js

// Toggle between Predefined and Custom Paper Sizes
document.getElementById('paper_size_option').addEventListener('change', function() {
    const predefinedDiv = document.getElementById('predefined_size_div');
    const customDiv = document.getElementById('custom_size_div');
    if (this.value === 'predefined') {
        predefinedDiv.classList.remove('d-none');
        customDiv.classList.add('d-none');
    } else {
        predefinedDiv.classList.add('d-none');
        customDiv.classList.remove('d-none');
    }
});

// Synchronize Grid Color Picker and Text Input
const gridColorPicker = document.getElementById('grid_color_picker');
const gridColorText = document.getElementById('grid_color_text');

gridColorPicker.addEventListener('input', function() {
    gridColorText.value = this.value.toUpperCase();
});

gridColorText.addEventListener('input', function() {
    if (/^#([0-9A-F]{3}){1,2}$/i.test(this.value)) {
        gridColorPicker.value = this.value;
        this.classList.remove('is-invalid');
    } else {
        this.classList.add('is-invalid');
    }
});

// Synchronize Background Color Picker and Text Input
const backgroundColorPicker = document.getElementById('background_color_picker');
const backgroundColorText = document.getElementById('background_color_text');

backgroundColorPicker.addEventListener('input', function() {
    backgroundColorText.value = this.value.toUpperCase();
});

backgroundColorText.addEventListener('input', function() {
    if (/^#([0-9A-F]{3}){1,2}$/i.test(this.value)) {
        backgroundColorPicker.value = this.value;
        this.classList.remove('is-invalid');
    } else {
        this.classList.add('is-invalid');
    }
});

// Generate Default Filename - Updated to include parameters
document.getElementById('generate_filename').addEventListener('click', function() {
    const paperSizeOption = document.getElementById('paper_size_option').value;
    let paperSize = '';

    if (paperSizeOption === 'predefined') {
        const predefinedSize = document.getElementById('predefined_size').value;
        paperSize = predefinedSize;
    } else if (paperSizeOption === 'custom') {
        const customWidth = document.getElementById('custom_width_cm').value;
        const customHeight = document.getElementById('custom_height_cm').value;
        paperSize = `Custom_${customWidth}x${customHeight}cm`;
    } else {
        paperSize = 'UnknownSize';
    }

    const gridSize = document.getElementById('grid_size_mm').value;
    const gridColor = document.getElementById('grid_color_text').value.replace('#', '');
    const lineThickness = document.getElementById('line_thickness').value;

    // Construct the filename
    const defaultFilename = `${paperSize}_grid_${gridSize}mm_${gridColor}_${lineThickness}pt.pdf`;

    // Replace any spaces or invalid characters with underscores
    const sanitizedFilename = defaultFilename.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_.-]/g, '');

    document.getElementById('output_filename').value = sanitizedFilename;
});
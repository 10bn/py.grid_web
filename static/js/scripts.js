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

// Generate Default Filename
document.getElementById('generate_filename').addEventListener('click', function() {
    const predefinedSize = document.getElementById('predefined_size');
    let size = predefinedSize.value;
    if (size === undefined) {
        size = 'Custom_Size';
    }
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const defaultFilename = `${size}_grid_${timestamp}.pdf`;
    document.getElementById('output_filename').value = defaultFilename;
});
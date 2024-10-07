document.addEventListener('DOMContentLoaded', function () {
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

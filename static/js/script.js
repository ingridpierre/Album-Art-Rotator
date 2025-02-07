document.addEventListener('DOMContentLoaded', function() {
    // Get the select element
    const select = document.getElementById('numberSelect');
    const selectedNumberDisplay = document.getElementById('selectedNumber');

    // Populate numbers 1-100
    for (let i = 1; i <= 100; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        select.appendChild(option);
    }

    // Handle selection changes
    select.addEventListener('change', function(e) {
        try {
            const selectedValue = e.target.value;
            selectedNumberDisplay.textContent = selectedValue || 'None';
        } catch (error) {
            console.error('Error handling selection:', error);
            selectedNumberDisplay.textContent = 'Error';
        }
    });
});

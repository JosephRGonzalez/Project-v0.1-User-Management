document.addEventListener('DOMContentLoaded', function () {
    const collegeSelect = document.getElementById('college-select');
    const majorSelect = document.getElementById('unit-select') || document.getElementById('major-select');

    if (!collegeSelect || !majorSelect) return;

    const allMajors = Array.from(majorSelect.options).slice(1);  // skip placeholder

    function updateMajors(selectedCollegeId) {
        majorSelect.innerHTML = '<option value="">Select Your Major</option>';
        allMajors.forEach(option => {
            if (option.getAttribute('data-parent') === selectedCollegeId) {
                majorSelect.appendChild(option);
            }
        });
        majorSelect.disabled = allMajors.filter(opt => opt.getAttribute('data-parent') === selectedCollegeId).length === 0;
    }

    if (collegeSelect.value) {
        updateMajors(collegeSelect.value);
    } else {
        majorSelect.disabled = true;
    }

    collegeSelect.addEventListener('change', function () {
        updateMajors(this.value);
    });
});

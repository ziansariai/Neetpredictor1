document.addEventListener('DOMContentLoaded', function () {
    const predictionForm = document.getElementById('prediction-form');
    const resultsSection = document.getElementById('results-section');
    const spinner = document.getElementById('spinner');
    const studentInfoDisplay = document.getElementById('student-info-display');
    const resultsTable = document.getElementById('results-table');
    const selectAllStatesBtn = document.getElementById('select-all-states');
    const stateCheckboxes = document.querySelectorAll('.state-checkbox');

    // Toggle MCC/State options
    const mccOptions = document.getElementById('mcc-options');
    const stateCounsellingRadio = document.getElementById('state');
    const mccCounsellingRadio = document.getElementById('mcc');

    function toggleCounsellingOptions() {
        if (stateCounsellingRadio.checked) {
            mccOptions.style.display = 'none';
        } else {
            mccOptions.style.display = 'block';
        }
    }
    if (stateCounsellingRadio){
        stateCounsellingRadio.addEventListener('change', toggleCounsellingOptions);
    }
    if (mccCounsellingRadio){
        mccCounsellingRadio.addEventListener('change', toggleCounsellingOptions);
    }

    // Select all states
    if (selectAllStatesBtn){
        selectAllStatesBtn.addEventListener('click', () => {
            const allSelected = Array.from(stateCheckboxes).every(checkbox => checkbox.checked);
            stateCheckboxes.forEach(checkbox => {
                checkbox.checked = !allSelected;
            });
            selectAllStatesBtn.textContent = allSelected ? 'Select All' : 'Deselect All';
        });
    }

    stateCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const allSelected = Array.from(stateCheckboxes).every(checkbox => checkbox.checked);
            if (selectAllStatesBtn){
                selectAllStatesBtn.textContent = allSelected ? 'Deselect All' : 'Select All';
            }
        });
    });


    // Form submission
    if (predictionForm) {
        predictionForm.addEventListener('submit', function (e) {
            e.preventDefault();
            resultsSection.style.display = 'block';
            spinner.style.display = 'block';
            studentInfoDisplay.style.display = 'none';
            resultsTable.innerHTML = '';

            const formData = new FormData(predictionForm);

            fetch('/predict', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                spinner.style.display = 'none';
                if (data.error) {
                    resultsTable.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                    return;
                }

                displayStudentInfo(data.student_info);
                displayResults(data.results);
            })
            .catch(error => {
                spinner.style.display = 'none';
                resultsTable.innerHTML = `<div class="alert alert-danger">An error occurred: ${error}</div>`;
            });
        });
    }

    function displayStudentInfo(info) {
        studentInfoDisplay.style.display = 'block';
        let infoHtml = `
            <div class="card-header">
                <h4>Your Details</h4>
            </div>
            <div class="card-body">
                <p><strong>AIR:</strong> ${info.air}</p>
                <p><strong>Domicile:</strong> ${info.domicile}</p>
                <p><strong>Category:</strong> ${info.category}</p>
                <p><strong>Sub Category:</strong> ${info.sub_category}</p>
                <p><strong>Quota:</strong> ${info.quota_name}</p>
                <p><strong>Course:</strong> ${info.course}</p>
            </div>`;
        studentInfoDisplay.innerHTML = infoHtml;
    }

    function displayResults(results) {
        if (results.length === 0) {
            resultsTable.innerHTML = '<div class="alert alert-warning">No matching colleges found based on your criteria.</div>';
            return;
        }

        let tableHtml = `
            <h3 class="mt-4">Predicted Colleges</h3>
            <table class="table table-striped table-bordered">
                <thead>
                    <tr>
                        <th>Year</th>
                        <th>Institute ID</th>
                        <th>Institute Name</th>
                        <th>Opening AIR</th>
                        <th>Closing AIR</th>
                    </tr>
                </thead>
                <tbody>
        `;

        results.forEach(item => {
            tableHtml += `
                <tr>
                    <td>${item.year}</td>
                    <td>${item.institute_id}</td>
                    <td>${item.institute_name}</td>
                    <td>${item.air_open}</td>
                    <td>${item.air_close}</td>
                </tr>
            `;
        });

        tableHtml += '</tbody></table>';
        resultsTable.innerHTML = tableHtml;

        // Basic pagination can be added here if needed
    }
});

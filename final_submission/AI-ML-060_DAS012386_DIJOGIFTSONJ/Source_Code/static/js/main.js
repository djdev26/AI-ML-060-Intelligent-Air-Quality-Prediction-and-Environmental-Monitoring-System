/**
 * AI-ML-060: Intelligent Air Quality Prediction System
 * Interactive Client-Side JavaScript
 */

document.addEventListener("DOMContentLoaded", function () {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });

    // Batch prediction form loading indicator
    const batchForm = document.getElementById("batch-upload-form");
    if (batchForm) {
        batchForm.addEventListener("submit", function () {
            const spinner = document.getElementById("batch-loading-spinner");
            const submitBtn = document.getElementById("batch-submit-btn");
            if (spinner && submitBtn) {
                spinner.classList.remove("d-none");
                submitBtn.setAttribute("disabled", "true");
                submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing Samples...`;
            }
        });
    }

    // Populate Sample Feature Values in Predict Form
    const sampleFillBtn = document.getElementById("fill-sample-btn");
    if (sampleFillBtn) {
        sampleFillBtn.addEventListener("click", function () {
            const sampleData = {
                "PT08_S1_CO": 1360.0,
                "NMHC_GT": 150.0,
                "C6H6_GT": 11.9,
                "PT08_S2_NMHC": 1046.0,
                "NOx_GT": 166.0,
                "PT08_S3_NOx": 1056.0,
                "NO2_GT": 113.0,
                "PT08_S4_NO2": 1692.0,
                "PT08_S5_O3": 1268.0,
                "T": 13.6,
                "RH": 48.9,
                "AH": 0.7578,
                "hour": 18,
                "month": 3,
                "day_of_week": 2
            };
            for (const [key, val] of Object.entries(sampleData)) {
                const input = document.getElementById(key);
                if (input) {
                    input.value = val;
                }
            }
        });
    }

    // Populate High CO Polluted Sample Values
    const highCoFillBtn = document.getElementById("fill-high-co-btn");
    if (highCoFillBtn) {
        highCoFillBtn.addEventListener("click", function () {
            const highCoData = {
                "PT08_S1_CO": 1850.0,
                "NMHC_GT": 450.0,
                "C6H6_GT": 28.5,
                "PT08_S2_NMHC": 1520.0,
                "NOx_GT": 680.0,
                "PT08_S3_NOx": 580.0,
                "NO2_GT": 210.0,
                "PT08_S4_NO2": 2150.0,
                "PT08_S5_O3": 1890.0,
                "T": 18.2,
                "RH": 65.0,
                "AH": 1.25,
                "hour": 19,
                "month": 11,
                "day_of_week": 4
            };
            for (const [key, val] of Object.entries(highCoData)) {
                const input = document.getElementById(key);
                if (input) {
                    input.value = val;
                }
            }
        });
    }
});

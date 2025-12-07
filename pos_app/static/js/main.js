// static/main.js

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [...document.querySelectorAll('[data-bs-toggle="tooltip"]')];
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));

    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Attach loading state to all forms' submit buttons
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', e => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.dataset.skipLoading) {
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                setLoading(submitBtn, true);
            }
        });
    });

    // Add currency formatting to price inputs
    document.querySelectorAll('input[type="number"][step="0.01"]').forEach(input => {
        input.addEventListener('input', () => formatCurrency(input));
    });

    // Search input with debounce
    document.querySelectorAll('input[data-search]').forEach(input => {
        input.addEventListener('input', debounce(() => {
            const searchTerm = input.value.toLowerCase();
            const table = input.closest('.table-responsive')?.querySelector('tbody');
            if (!table) return;

            table.querySelectorAll('tr').forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    });

    // Auto-focus quantity input when adding to cart
    document.querySelectorAll('button[data-product-id]').forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.dataset.productId;
            const quantityInput = document.querySelector(`input[name="quantity"][data-product="${productId}"]`);
            if (quantityInput) {
                setTimeout(() => {
                    quantityInput.focus();
                    quantityInput.select();
                }, 100);
            }
        });
    });

    // Real-time validation on blur
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('blur', () => validateField(input));
        });
    });
});

// Confirm delete dialog
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Set loading state for buttons
function setLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.innerHTML = '<span class="loading me-2"></span>Loading...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || 'Submit';
    }
}

// Format currency input value
function formatCurrency(input) {
    let value = input.value.replace(/[^\d.]/g, '');
    const parts = value.split('.');
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }
    if (parts[1] && parts[1].length > 2) {
        value = parts[0] + '.' + parts[1].substring(0, 2);
    }
    input.value = value;
}

// Debounce helper (preserves context & args)
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Print element by id
function printElement(elementId) {
    const printContent = document.getElementById(elementId);
    if (!printContent) return;

    const originalContent = document.body.innerHTML;
    document.body.innerHTML = printContent.innerHTML;
    window.print();
    document.body.innerHTML = originalContent;
    window.location.reload();
}

// Keyboard shortcuts
document.addEventListener('keydown', e => {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        const submitBtn = activeForm?.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.click();
    }

    // Escape to close Bootstrap modal
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const bsModal = bootstrap.Modal.getInstance(openModal);
            bsModal?.hide();
        }
    }
});

// Validate a single field
function validateField(field) {
    let isValid = true;
    let errorMessage = '';

    if (field.hasAttribute('required') && !field.value.trim()) {
        isValid = false;
        errorMessage = 'This field is required.';
    }

    if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address.';
        }
    }

    if (field.type === 'number' && field.value) {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');

        if (min && parseFloat(field.value) < parseFloat(min)) {
            isValid = false;
            errorMessage = `Value must be at least ${min}.`;
        }
        if (max && parseFloat(field.value) > parseFloat(max)) {
            isValid = false;
            errorMessage = `Value must be at most ${max}.`;
        }
    }

    field.classList.toggle('is-invalid', !isValid);
    field.classList.toggle('is-valid', isValid && field.value);

    let feedback = field.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentNode.appendChild(feedback);
    }
    feedback.textContent = errorMessage;
}

// AJAX helper with fetch API and CSRF token
async function ajaxRequest(url, method = 'GET', data = null, successCallback = null, errorCallback = null) {
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
    };

    try {
        const response = await fetch(url, {
            method,
            headers,
            body: data ? JSON.stringify(data) : null,
        });

        if (response.ok) {
            const jsonData = await response.json();
            if (successCallback) successCallback(jsonData);
        } else {
            const text = await response.text();
            if (errorCallback) errorCallback(response.status, text);
        }
    } catch (error) {
        if (errorCallback) errorCallback(0, error.message);
    }
}

// Get CSRF token from DOM
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Expose global functions
window.POS = {
    confirmDelete,
    setLoading,
    printElement,
    ajaxRequest
};

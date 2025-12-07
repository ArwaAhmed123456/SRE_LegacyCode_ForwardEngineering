// Custom JavaScript for POS System

// Initialize tooltips
document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Confirm delete actions
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Add loading state to buttons
function setLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.innerHTML = '<span class="loading me-2"></span>Loading...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || 'Submit';
    }
}

// Initialize loading states on form submit
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.dataset.skipLoading) {
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                setLoading(submitBtn, true);
            }
        });
    });
});

// Format currency inputs to 2 decimal places
function formatCurrency(input) {
    let value = input.value.replace(/[^\d.]/g, '');
    const parts = value.split('.');
    
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }
    if (parts[1]?.length > 2) {
        value = parts[0] + '.' + parts[1].substring(0, 2);
    }
    input.value = value;
}

// Attach currency formatting to price inputs
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[type="number"][step="0.01"]').forEach(input => {
        input.addEventListener('input', () => formatCurrency(input));
    });
});

// Debounce helper function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Table search filtering
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[data-search]').forEach(input => {
        input.addEventListener('input', debounce(() => {
            const searchTerm = input.value.toLowerCase();
            const tableBody = input.closest('.table-responsive').querySelector('tbody');
            const rows = tableBody.querySelectorAll('tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    });
});

// Print functionality
function printElement(elementId) {
    const printContent = document.getElementById(elementId);
    if (!printContent) return;

    const originalContent = document.body.innerHTML;
    document.body.innerHTML = printContent.innerHTML;
    window.print();
    document.body.innerHTML = originalContent;
    window.location.reload();
}

// Cart quantity focus on add to cart buttons
document.addEventListener('DOMContentLoaded', () => {
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
});

// Keyboard shortcuts
document.addEventListener('keydown', e => {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        if (activeForm) {
            const submitBtn = activeForm.querySelector('button[type="submit"]');
            submitBtn?.click();
        }
    }

    // Escape key to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const bsModal = bootstrap.Modal.getInstance(openModal);
            bsModal?.hide();
        }
    }
});

// Real-time form validation
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('blur', () => validateField(input));
        });
    });
});

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
        const val = parseFloat(field.value);

        if (min && val < parseFloat(min)) {
            isValid = false;
            errorMessage = `Value must be at least ${min}.`;
        }

        if (max && val > parseFloat(max)) {
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

// AJAX helpers
function ajaxRequest(url, method = 'GET', data = null, successCallback = null, errorCallback = null) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCsrfToken());

    xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            successCallback?.(JSON.parse(xhr.responseText));
        } else {
            errorCallback?.(xhr.status, xhr.responseText);
        }
    };

    xhr.onerror = () => {
        errorCallback?.(0, 'Network error');
    };

    xhr.send(data ? JSON.stringify(data) : null);
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Export functions for global use
window.POS = {
    confirmDelete,
    setLoading,
    printElement,
    ajaxRequest
};

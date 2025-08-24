// CallShield AI - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[name="screening_number"], input[name="forward_to"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0 && !value.startsWith('1')) {
                value = '1' + value;
            }
            if (value.length > 11) {
                value = value.substring(0, 11);
            }
            if (value.length >= 1) {
                e.target.value = '+' + value;
            }
        });
    });

    // PIN input validation
    const pinInputs = document.querySelectorAll('input[name="current_pin"]');
    pinInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 4);
        });
    });

    // Add confirmation to delete actions
    const deleteButtons = document.querySelectorAll('button[type="submit"]');
    deleteButtons.forEach(function(button) {
        if (button.textContent.includes('Remove') || button.textContent.includes('Delete')) {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to perform this action?')) {
                    e.preventDefault();
                }
            });
        }
    });

    // Copy webhook URLs to clipboard
    const webhookInfo = document.getElementById('webhook-info');
    if (webhookInfo) {
        const baseUrl = window.location.origin;
        const webhookUrl = baseUrl + '/voice/incoming';
        
        const webhookElement = document.createElement('div');
        webhookElement.className = 'alert alert-info';
        webhookElement.innerHTML = `
            <h6><i class="fas fa-webhook me-2"></i>Twilio Webhook URL:</h6>
            <div class="input-group">
                <input type="text" class="form-control" value="${webhookUrl}" readonly>
                <button class="btn btn-outline-secondary" type="button" onclick="copyWebhookUrl('${webhookUrl}')">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
            <small class="form-text">Configure this URL in your Twilio phone number settings.</small>
        `;
        webhookInfo.appendChild(webhookElement);
    }
});

// Copy webhook URL to clipboard
function copyWebhookUrl(url) {
    navigator.clipboard.writeText(url).then(function() {
        // Show temporary success message
        const button = event.target.closest('button');
        const originalHtml = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.classList.remove('btn-outline-secondary');
        button.classList.add('btn-success');
        
        setTimeout(function() {
            button.innerHTML = originalHtml;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-secondary');
        }, 2000);
    });
}

// Real-time status updates (optional enhancement)
function updateStatus() {
    // This could be expanded to check tenant verification status
    // and update the UI in real-time
    console.log('Status check - implement as needed');
}

// Initialize tooltips
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

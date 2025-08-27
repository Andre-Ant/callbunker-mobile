// CallBunker - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss only success/error alerts, NOT info/warning alerts (benefits messages)
    const alerts = document.querySelectorAll('.alert-success, .alert-danger:not(.benefits-alert)');
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

// Global variables for delete functionality
let deleteTarget = null;

// Copy forwarding number to clipboard
function copyForwardingNumber() {
    const number = '+16316417727';
    navigator.clipboard.writeText(number).then(function() {
        // Show success feedback
        const button = event.target.closest('button');
        if (button) {
            const originalIcon = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check text-success"></i>';
            button.classList.add('btn-success');
            button.classList.remove('btn-outline-primary');
            
            // Reset button after 2 seconds
            setTimeout(() => {
                button.innerHTML = originalIcon;
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-primary');
            }, 2000);
        }
        
        // Create toast notification
        showCopyToast('Forwarding number copied!');
    }).catch(function(err) {
        console.error('Failed to copy: ', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = number;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showCopyToast('Forwarding number copied!');
    });
}

// Confirm tenant deletion
function confirmDeleteTenant(screeningNumber, userName) {
    deleteTarget = screeningNumber;
    document.getElementById('deleteUserName').textContent = userName;
    document.getElementById('deleteUserNumber').textContent = screeningNumber;
    
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    deleteModal.show();
}

// Delete tenant
function deleteTenant() {
    if (!deleteTarget) return;
    
    // Create form and submit
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/admin/tenant/${encodeURIComponent(deleteTarget)}/delete`;
    
    // Add CSRF token if available
    const csrfToken = document.querySelector('meta[name=csrf-token]');
    if (csrfToken) {
        const tokenInput = document.createElement('input');
        tokenInput.type = 'hidden';
        tokenInput.name = 'csrf_token';
        tokenInput.value = csrfToken.getAttribute('content');
        form.appendChild(tokenInput);
    }
    
    document.body.appendChild(form);
    form.submit();
}

// Show copy notification toast
function showCopyToast(message) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 1050; min-width: 250px;">
            <i class="fas fa-check-circle me-2"></i>${message}
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

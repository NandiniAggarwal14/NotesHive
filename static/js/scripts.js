// Toast notification system
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const iconMap = {
        'success': '✓',
        'error': '✕',
        'warning': '⚠',
        'info': 'ℹ'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content" style="display: flex; align-items: center; gap: 0.75rem;">
            <strong style="font-size: 1.2rem;">${iconMap[type] || '•'}</strong>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Confirmation dialog
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--danger-color)';
            isValid = false;
        } else {
            input.style.borderColor = 'var(--gray-light)';
        }
    });
    
    return isValid;
}

// Search functionality (client-side filter)
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const noteCards = document.querySelectorAll('.note-card');
        let visibleCount = 0;
        
        noteCards.forEach(card => {
            const title = card.querySelector('.note-title')?.textContent.toLowerCase() || '';
            const description = card.querySelector('.note-description')?.textContent.toLowerCase() || '';
            
            if (title.includes(searchTerm) || description.includes(searchTerm)) {
                card.style.display = 'block';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Update result count
        const resultInfo = document.getElementById('search-result-info');
        if (resultInfo) {
            if (searchTerm) {
                resultInfo.textContent = `Found ${visibleCount} note${visibleCount !== 1 ? 's' : ''}`;
                resultInfo.style.display = 'block';
            } else {
                resultInfo.style.display = 'none';
            }
        }
    });
}

// Delete confirmation
function setupDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.btn-delete, a[href*="delete"]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirmDelete('Are you sure you want to delete this note? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
}

// Auto-resize textarea
function autoResizeTextarea() {
    const textareas = document.querySelectorAll('textarea.auto-resize, textarea.form-control');
    
    textareas.forEach(textarea => {
        function resize() {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }
        
        textarea.addEventListener('input', resize);
        resize(); // Initial resize
    });
}

// Character counter for textarea
function setupCharacterCounter() {
    const textareas = document.querySelectorAll('textarea[maxlength]');
    
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.style.cssText = 'color: var(--gray); font-size: 0.875rem; margin-top: 0.5rem; display: block;';
        textarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${textarea.value.length} / ${maxLength} characters`;
            counter.style.color = remaining < 50 ? 'var(--warning-color)' : 'var(--gray)';
        }
        
        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    setupDeleteConfirmations();
    autoResizeTextarea();
    setupCharacterCounter();
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Focus first input on auth pages
    const firstInput = document.querySelector('.auth-card input[type="text"]');
    if (firstInput) {
        firstInput.focus();
    }
});

// Flash message handling
window.addEventListener('load', function() {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'fadeOut 0.5s ease';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });
});

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-10px); }
    }
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(style);

// Main JavaScript file for Tourism Itinerary App

// Global variables
let currentSpeech = null;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Tourism Itinerary App loaded successfully!');
    
    // Make sure loading overlay is hidden on page load
    hideLoading();
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Check for speech synthesis support
    if (!('speechSynthesis' in window)) {
        console.warn('Speech synthesis not supported in this browser');
        hideSpeakBtn();
    }
});

function initializeEventListeners() {
    // Speech button functionality
    const speakBtn = document.getElementById('speakBtn');
    const stopSpeakBtn = document.getElementById('stopSpeakBtn');
    
    if (speakBtn) {
        speakBtn.addEventListener('click', handleSpeak);
    }
    
    if (stopSpeakBtn) {
        stopSpeakBtn.addEventListener('click', handleStopSpeak);
    }
    
    // Note: Loading overlay is managed by map.js for itinerary changes
}

// Speech functionality
function handleSpeak() {
    const descriptionText = document.getElementById('stopDescription').textContent;
    
    if (!descriptionText) {
        showAlert('No description available to read', 'warning');
        return;
    }
    
    // Stop any current speech
    if (currentSpeech) {
        speechSynthesis.cancel();
    }
    
    // Create new speech instance
    currentSpeech = new SpeechSynthesisUtterance(descriptionText);
    currentSpeech.rate = 0.9; // Slightly slower for clarity
    currentSpeech.pitch = 1;
    currentSpeech.volume = 1;
    
    // Event handlers
    currentSpeech.onstart = function() {
        document.getElementById('speakBtn').style.display = 'none';
        document.getElementById('stopSpeakBtn').style.display = 'inline-block';
        document.getElementById('speakBtn').classList.add('speaking');
    };
    
    currentSpeech.onend = function() {
        resetSpeechButtons();
    };
    
    currentSpeech.onerror = function(event) {
        console.error('Speech synthesis error:', event);
        showAlert('Error playing audio. Please try again.', 'danger');
        resetSpeechButtons();
    };
    
    // Start speaking
    speechSynthesis.speak(currentSpeech);
}

function handleStopSpeak() {
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
    }
    resetSpeechButtons();
}

function resetSpeechButtons() {
    document.getElementById('speakBtn').style.display = 'inline-block';
    document.getElementById('stopSpeakBtn').style.display = 'none';
    document.getElementById('speakBtn').classList.remove('speaking');
    currentSpeech = null;
}

function hideSpeakBtn() {
    const speakBtn = document.getElementById('speakBtn');
    const stopSpeakBtn = document.getElementById('stopSpeakBtn');
    if (speakBtn) speakBtn.style.display = 'none';
    if (stopSpeakBtn) stopSpeakBtn.style.display = 'none';
}

// Loading overlay functions
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        console.log('Showing loading overlay');
        overlay.style.setProperty('display', 'flex', 'important');
    } else {
        console.error('Loading overlay element not found');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        console.log('Hiding loading overlay');
        overlay.style.setProperty('display', 'none', 'important');
    } else {
        console.error('Loading overlay element not found');
    }
}

// Alert function
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 1050; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to body
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function sanitizeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    showAlert('An error occurred. Please refresh the page.', 'danger');
});

// Prevent form submission on Enter key in search fields
document.addEventListener('keypress', function(event) {
    if (event.key === 'Enter' && event.target.tagName === 'INPUT' && event.target.type === 'search') {
        event.preventDefault();
    }
});

// Export functions for use in other scripts
window.TourismApp = {
    showAlert,
    showLoading,
    hideLoading,
    formatDate,
    sanitizeHtml,
    resetSpeechButtons
};

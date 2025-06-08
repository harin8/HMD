// Set inactivity timeout to 1 hour (in milliseconds)
const INACTIVITY_TIMEOUT = 60 * 60 * 1000;
let inactivityTimer;

function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(performLogout, INACTIVITY_TIMEOUT);
}

function performLogout() {
    // Show warning message before logout
    if (confirm('Your session is about to expire due to inactivity. Click OK to log out.')) {
        window.location.href = '/accounts/logout/';
    } else {
        // If user clicks Cancel, reset the timer
        resetInactivityTimer();
    }
}

// Reset timer on user activity
document.addEventListener('mousemove', resetInactivityTimer);
document.addEventListener('keypress', resetInactivityTimer);
document.addEventListener('click', resetInactivityTimer);
document.addEventListener('scroll', resetInactivityTimer);

// Initialize timer when page loads
document.addEventListener('DOMContentLoaded', resetInactivityTimer);
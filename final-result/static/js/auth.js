/**
 * Authentication utilities and API helpers for Flask Auth frontend
 */

/**
 * Make API call with automatic authentication headers
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise<Response>} Fetch response
 */
async function apiCall(url, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };

    try {
        const response = await fetch(url, { ...options, headers });

        // Handle 401: token expired or invalid
        if (response.status === 401) {
            clearAuth();
            window.location.href = '/login?error=Session expired. Please login again.';
            return response;
        }

        return response;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

/**
 * Check if user is authenticated
 * @returns {boolean} True if access token exists
 */
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

/**
 * Clear authentication tokens from localStorage
 */
function clearAuth() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

/**
 * Update navigation links based on authentication state
 * Shows/hides links marked with data-auth-only and data-guest-only
 */
function updateNav() {
    const isAuth = isAuthenticated();

    // Show authenticated-only links
    document.querySelectorAll('[data-auth-only]').forEach(el => {
        el.style.display = isAuth ? '' : 'none';
    });

    // Show guest-only links
    document.querySelectorAll('[data-guest-only]').forEach(el => {
        el.style.display = isAuth ? 'none' : '';
    });
}

/**
 * Display a message to the user
 * @param {string} message - Message text
 * @param {string} type - Message type ('error' or 'success')
 */
function showMessage(message, type = 'error') {
    // Remove any existing messages first
    const existing = document.querySelector('.message');
    if (existing) {
        existing.remove();
    }

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.textContent = message;
    msgDiv.setAttribute('role', type === 'error' ? 'alert' : 'status');

    const main = document.querySelector('main');
    if (main) {
        main.prepend(msgDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            msgDiv.style.opacity = '0';
            setTimeout(() => msgDiv.remove(), 300);
        }, 5000);
    }
}

/**
 * Set button loading state
 * @param {HTMLButtonElement} button - Button element
 * @param {boolean} loading - True to show loading state
 * @param {string} originalText - Original button text to restore
 */
function setButtonLoading(button, loading, originalText = '') {
    if (loading) {
        button.dataset.originalText = button.textContent;
        button.textContent = 'Loading...';
        button.disabled = true;
    } else {
        button.textContent = originalText || button.dataset.originalText || button.textContent;
        button.disabled = false;
        delete button.dataset.originalText;
    }
}

/**
 * Decode JWT payload (without verification - for display purposes only)
 * @param {string} token - JWT token
 * @returns {Object|null} Decoded payload or null if invalid
 */
function decodeJWT(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Failed to decode JWT:', error);
        return null;
    }
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    // Update navigation based on auth state
    updateNav();

    // Parse URL parameters for messages
    const params = new URLSearchParams(window.location.search);

    const error = params.get('error');
    if (error) {
        showMessage(error, 'error');
    }

    const success = params.get('success');
    if (success) {
        showMessage(success, 'success');
    }
});

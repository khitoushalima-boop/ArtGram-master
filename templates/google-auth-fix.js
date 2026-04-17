// Google OAuth Fix for ArtGram
// Replace the problematic Google auth section in log.html with this improved version

window.handleGoogleSignIn = async (response) => {
  if (!response || !response.credential) {
    showAuthMessage('Google Sign-In was cancelled. Please try again.', 'error');
    return;
  }
  
  showAuthMessage('Connecting to Google...', 'success');
  
  try {
    const res = await fetch('http://localhost:8000/api/users/google/callback/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        token: response.credential
      })
    });

    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('token', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      localStorage.setItem('username', data.user.username);
      localStorage.setItem('email', data.user.email);
      localStorage.setItem('userId', data.user.id);
      showAuthMessage(`Success! Logged in as ${data.user.email}`, 'success');
      setTimeout(() => { window.location.href = '/index.html'; }, 1500);
    } else {
      const errorData = await res.json().catch(() => ({ error: 'Unknown error' }));
      showAuthMessage(errorData.error || 'Google login failed. Please try again.', 'error');
    }
  } catch (error) {
    console.error('Google Auth Error:', error);
    showAuthMessage('Connection error. Please check if the service is running.', 'error');
  }
};

// Initialize Google Sign-In
function initGoogleAuth() {
  if (typeof google !== 'undefined' && google.accounts && google.accounts.id) {
    google.accounts.id.initialize({
      client_id: "your-google-client-id.apps.googleusercontent.com", // Replace with your Google Client ID
      callback: window.handleGoogleSignIn,
      auto_select: false,
      cancel_on_tap_outside: false,
      ux_mode: 'popup',
      allowed_parent_origin: 'http://localhost:8001' // Allow your frontend domain
    });
    
    // Render the Google Sign-In button
    const buttonElement = document.getElementById('google-signin-button');
    if (buttonElement) {
      google.accounts.id.renderButton(buttonElement, {
        theme: 'outline',
        size: 'large',
        text: 'signin_with',
        shape: 'rectangular',
        logo_alignment: 'left'
      });
    }
    
    console.log('Google SDK initialized successfully');
  } else {
    // Retry mechanism
    setTimeout(initGoogleAuth, 100);
  }
}

// Error handling
window.handleGoogleError = (error) => {
  console.error('Google Sign-In error:', error);
  if (error.error === 'popup_closed_by_user') {
    showAuthMessage('Google Sign-In was cancelled. Please try again.', 'error');
  } else if (error.error === 'access_denied') {
    showAuthMessage('Access denied. Please try again.', 'error');
  } else if (error.error === 'immediate_failed') {
    showAuthMessage('Sign-in failed. Please try again.', 'error');
  } else {
    showAuthMessage('Google Sign-In failed. Please try again.', 'error');
  }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  initGoogleAuth();
});

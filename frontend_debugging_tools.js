/**
 * Frontend Debugging Tools for ArtGram Registration
 * Use these tools to debug silent button clicks and API communication issues
 */

// 1. Frontend Investigation - Button Click Logger
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 Frontend Debugging Tools Loaded');
    
    // Find all buttons on the page and add debugging
    const buttons = document.querySelectorAll('button');
    console.log(`📊 Found ${buttons.length} buttons on the page`);
    
    buttons.forEach((button, index) => {
        // Add click listener to all buttons for debugging
        button.addEventListener('click', function(e) {
            console.log(`🔘 Button ${index + 1} clicked:`, {
                id: this.id,
                className: this.className,
                textContent: this.textContent.trim(),
                type: this.type,
                form: this.form ? this.form.id : 'no form',
                event: 'click event triggered'
            });
        });
        
        console.log(`🔘 Button ${index + 1}:`, {
            id: button.id,
            className: button.className,
            textContent: button.textContent.trim(),
            type: button.type,
            form: button.form ? button.form.id : 'no form'
        });
    });
});

// 2. Form Data Logger - Add this to your form submission handler
function debugFormData(form) {
    console.log('📝 Form Data Debugging:');
    console.log('Form ID:', form.id);
    console.log('Form Action:', form.action);
    console.log('Form Method:', form.method);
    
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
        console.log(`🔑 ${key}:`, value);
    }
    
    // Also log as JSON for API testing
    const jsonData = JSON.stringify(data);
    console.log('📦 Form Data as JSON:', jsonData);
    
    return data;
}

// 3. Robust Fetch Implementation with Comprehensive Logging
async function robustFetch(url, options = {}) {
    console.log('🌐 Starting Robust Fetch...');
    console.log('📍 URL:', url);
    console.log('⚙️ Options:', options);
    
    // Default options
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
        },
        credentials: 'same-origin',
        mode: 'cors',
    };
    
    // Merge with provided options
    const fetchOptions = { ...defaultOptions, ...options };
    
    console.log('🔧 Final Fetch Options:', fetchOptions);
    
    try {
        console.log('⏳ Sending request...');
        const response = await fetch(url, fetchOptions);
        
        console.log('✅ Response received:');
        console.log('📊 Status:', response.status);
        console.log('📊 Status Text:', response.statusText);
        console.log('📊 Headers:', [...response.headers.entries()]);
        console.log('📊 URL:', response.url);
        
        // Try to parse response as JSON
        let responseData;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            try {
                responseData = await response.json();
                console.log('📦 Response Data:', responseData);
            } catch (jsonError) {
                console.warn('⚠️ Failed to parse JSON response:', jsonError);
                responseData = await response.text();
                console.log('📄 Response Text:', responseData);
            }
        } else {
            responseData = await response.text();
            console.log('📄 Response Text:', responseData);
        }
        
        // Return comprehensive response object
        return {
            ok: response.ok,
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
            data: responseData,
            url: response.url
        };
        
    } catch (error) {
        console.error('❌ Fetch Error:', error);
        console.error('🔍 Error Details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        
        // Check for common network errors
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            console.error('🌐 Network Error - Possible CORS or connectivity issue');
        } else if (error.name === 'TypeError' && error.message.includes('NetworkError')) {
            console.error('🌐 Network Error - Server unreachable');
        }
        
        throw error;
    }
}

// 4. Registration Form Handler with Complete Debugging
async function handleRegistrationSubmit(event) {
    console.log('🚀 Registration Form Submit Handler Called');
    
    // 1. Prevent default form behavior
    event.preventDefault();
    console.log('🛑 Form submission prevented');
    
    // 2. Get form element
    const form = event.target;
    console.log('📝 Form element:', form);
    
    // 3. Debug form data
    const formData = debugFormData(form);
    
    // 4. Validate required fields
    const requiredFields = ['username', 'email', 'password'];
    const missingFields = requiredFields.filter(field => !formData[field]);
    
    if (missingFields.length > 0) {
        console.error('❌ Missing required fields:', missingFields);
        alert(`Please fill in all required fields: ${missingFields.join(', ')}`);
        return;
    }
    
    // 5. Prepare API request
    const apiUrl = '/api/users/register/';
    console.log('🎯 API URL:', apiUrl);
    
    try {
        // 6. Make API call with robust fetch
        const response = await robustFetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Include CSRF token if needed
            },
            body: JSON.stringify(formData)
        });
        
        console.log('📊 API Response:', response);
        
        // 7. Handle response
        if (response.ok) {
            console.log('✅ Registration successful!');
            console.log('👤 User data:', response.data);
            
            // Store user data and tokens
            if (response.data.access) {
                localStorage.setItem('token', response.data.access);
                console.log('🔑 Token stored in localStorage');
            }
            
            if (response.data.user) {
                localStorage.setItem('user', JSON.stringify(response.data.user));
                console.log('👤 User data stored in localStorage');
            }
            
            // Show success message
            alert('Registration successful! Redirecting...');
            
            // Redirect to main page
            setTimeout(() => {
                window.location.href = '/index.html';
            }, 1000);
            
        } else {
            console.error('❌ Registration failed:', response);
            
            // Handle specific error cases
            let errorMessage = 'Registration failed. Please try again.';
            
            if (response.data) {
                if (response.data.error) {
                    errorMessage = `Registration failed: ${response.data.error}`;
                } else if (response.data.detail) {
                    errorMessage = `Registration failed: ${response.data.detail}`;
                } else if (response.data.non_field_errors) {
                    errorMessage = `Registration failed: ${response.data.non_field_errors.join(', ')}`;
                } else if (typeof response.data === 'object') {
                    const errors = Object.entries(response.data)
                        .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
                        .join(', ');
                    errorMessage = `Registration failed: ${errors}`;
                }
            }
            
            console.error('🚨 Error message:', errorMessage);
            alert(errorMessage);
        }
        
    } catch (error) {
        console.error('💥 Registration error:', error);
        alert('Network error. Please check your connection and try again.');
    }
}

// 5. CSRF Token Helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 6. Form Setup Function - Call this when page loads
function setupRegistrationForm() {
    console.log('🔧 Setting up registration form...');
    
    // Find the registration form
    const registrationForm = document.querySelector('form[action*="register"], form#registration-form, form.register-form');
    
    if (!registrationForm) {
        console.error('❌ Registration form not found!');
        console.log('🔍 Available forms:', document.querySelectorAll('form'));
        return;
    }
    
    console.log('✅ Registration form found:', registrationForm);
    
    // Find the submit button
    const submitButton = registrationForm.querySelector('button[type="submit"], button.create-account-btn, button.register-btn');
    
    if (!submitButton) {
        console.error('❌ Submit button not found!');
        console.log('🔍 Available buttons:', registrationForm.querySelectorAll('button'));
        return;
    }
    
    console.log('✅ Submit button found:', submitButton);
    
    // Add submit event listener to form
    registrationForm.addEventListener('submit', handleRegistrationSubmit);
    console.log('👂 Submit event listener added to form');
    
    // Also add click listener to button for debugging
    submitButton.addEventListener('click', function(e) {
        console.log('🔘 Submit button clicked directly:', {
            id: this.id,
            className: this.className,
            textContent: this.textContent.trim(),
            type: this.type,
            disabled: this.disabled
        });
    });
    
    console.log('✅ Registration form setup complete!');
}

// 7. Initialize debugging when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupRegistrationForm);
} else {
    setupRegistrationForm();
}

// 8. Export functions for global access
window.debugFormData = debugFormData;
window.robustFetch = robustFetch;
window.handleRegistrationSubmit = handleRegistrationSubmit;
window.setupRegistrationForm = setupRegistrationForm;

console.log('🎯 Frontend Debugging Tools Ready!');

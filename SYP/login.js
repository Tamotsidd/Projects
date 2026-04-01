const API = 'http://127.0.0.1:8000/api/auth';

function showError(boxId, message) {
    const box = document.getElementById(boxId);
    box.textContent = message;
    box.style.display = 'block';
}

function showSuccess(boxId, message) {
    const box = document.getElementById(boxId);
    box.textContent = message;
    box.style.display = 'block';
}

function clearMessages(errorId, successId) {
    document.getElementById(errorId).style.display = 'none';
    document.getElementById(successId).style.display = 'none';
}

// ── Show/hide doctor fields when role changes ─────────────────────────────────
document.getElementById('registerRole').addEventListener('change', function () {
    const doctorFields = document.getElementById('doctorFields');
    if (this.value === 'doctor') {
        doctorFields.style.display = 'block';
        document.getElementById('registerSpecialization').required = true;
        document.getElementById('registerLicense').required = true;
    } else {
        doctorFields.style.display = 'none';
        document.getElementById('registerSpecialization').required = false;
        document.getElementById('registerLicense').required = false;
    }
});

// ── REGISTER ──────────────────────────────────────────────────────────────────
document.getElementById('registerForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    clearMessages('registerError', 'registerSuccess');

    const role     = document.getElementById('registerRole').value;
    const password = document.getElementById('registerPassword').value;
    const confirm  = document.getElementById('registerConfirm').value;

    if (password !== confirm) {
        showError('registerError', 'Passwords do not match.');
        return;
    }

    const payload = {
        full_name:        document.getElementById('registerName').value.trim(),
        phone:            document.getElementById('registerPhone').value.trim(),
        email:            document.getElementById('registerEmail').value.trim(),
        role:             role,
        password:         password,
        confirm_password: confirm,
    };

    if (role === 'doctor') {
        payload.specialization   = document.getElementById('registerSpecialization').value.trim();
        payload.license_number   = document.getElementById('registerLicense').value.trim();
        payload.years_experience = parseInt(document.getElementById('registerExperience').value) || 0;
        payload.available_days   = document.getElementById('registerAvailableDays').value.trim();
    }

    const btn = document.getElementById('registerBtn');
    btn.textContent = 'Registering...';
    btn.disabled = true;

    try {
        const res  = await fetch(`${API}/register/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload),
        });
        const data = await res.json();

        if (res.ok) {
            localStorage.setItem('access_token',  data.tokens.access);
            localStorage.setItem('refresh_token', data.tokens.refresh);
            localStorage.setItem('user',           JSON.stringify(data.user));

            showSuccess('registerSuccess', `Welcome, ${data.user.full_name}! Redirecting...`);

            setTimeout(() => {
                if (data.user.role === 'doctor') {
                    window.location.href = 'doctor_dashboard.html';
                } else {
                    window.location.href = 'Front.html';
                }
            }, 1500);

        } else {
            showError('registerError', extractErrors(data));
            btn.textContent = 'Register';
            btn.disabled = false;
        }
    } catch (err) {
        showError('registerError', 'Server error. Make sure the backend is running.');
        btn.textContent = 'Register';
        btn.disabled = false;
    }
});

// ── LOGIN ─────────────────────────────────────────────────────────────────────
document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    clearMessages('loginError', 'loginSuccess');

    const payload = {
        phone:    document.getElementById('loginPhone').value.trim(),
        password: document.getElementById('loginPassword').value,
    };

    const btn = document.getElementById('loginBtn');
    btn.textContent = 'Logging in...';
    btn.disabled = true;

    try {
        const res  = await fetch(`${API}/login/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload),
        });
        const data = await res.json();

        if (res.ok) {
            localStorage.setItem('access_token',  data.tokens.access);
            localStorage.setItem('refresh_token', data.tokens.refresh);
            localStorage.setItem('user',           JSON.stringify(data.user));

            showSuccess('loginSuccess', `Welcome back, ${data.user.full_name}! Redirecting...`);

            setTimeout(() => {
                if (data.user.role === 'doctor') {
                    window.location.href = 'doctor_dashboard.html';
                } else if (data.user.role === 'admin') {
                    window.location.href = 'http://127.0.0.1:8000/admin/';
                } else {
                    window.location.href = 'Front.html';
                }
            }, 1500);

        } else {
            showError('loginError', extractErrors(data));
            btn.textContent = 'Login';
            btn.disabled = false;
        }
    } catch (err) {
        showError('loginError', 'Server error. Make sure the backend is running.');
        btn.textContent = 'Login';
        btn.disabled = false;
    }
});

// ── Extract error messages from Django response ───────────────────────────────
function extractErrors(data) {
    if (typeof data === 'string') return data;
    const messages = [];
    for (const key in data) {
        const val = data[key];
        if (Array.isArray(val)) messages.push(...val);
        else if (typeof val === 'string') messages.push(val);
    }
    return messages.join(' ') || 'Something went wrong. Please try again.';
}
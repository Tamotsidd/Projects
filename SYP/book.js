const API = 'http://127.0.0.1:8000/api';

// State
const booking = {
    doctorId:   null,
    doctorName: null,
    specialty:  null,
    date:       null,
    dateLabel:  null,
    time:       null,
    timeLabel:  null,
};

// Time map — label to backend value
const TIME_MAP = {
    '9:00 AM':  '09:00',
    '9:30 AM':  '09:30',
    '10:00 AM': '10:00',
    '10:30 AM': '10:30',
    '11:00 AM': '11:00',
    '11:30 AM': '11:30',
    '1:00 PM':  '13:00',
    '1:30 PM':  '13:30',
};

// ═══════════════════════════════════════════════════
// STEP 1 — Load doctors from API
// ═══════════════════════════════════════════════════

async function loadDoctors() {
    const grid = document.querySelector('.doctor-grid');
    grid.innerHTML = '<p style="color:#aaa;padding:20px;">Loading doctors...</p>';

    try {
        const res  = await fetch(`${API}/doctors/`);
        const data = await res.json();

        if (!data.length) {
            grid.innerHTML = '<p style="color:#f87171;">No doctors available.</p>';
            return;
        }

        grid.innerHTML = data.map(doc => `
            <label class="doc-card" onclick="selectDoctor(${doc.id}, '${doc.name}', '${doc.specialization}')">
                <input type="radio" name="doc" hidden value="${doc.id}">
                <div class="doc-body">
                    <h3>Dr. ${doc.name}</h3>
                    <p class="spec">${doc.specialization}</p>
                    <div class="doc-meta">
                        <span>${doc.years_experience} yrs experience</span>
                        <span>${doc.available_days}</span>
                    </div>
                </div>
            </label>
        `).join('');

    } catch (err) {
        grid.innerHTML = '<p style="color:#f87171;">Failed to load doctors. Is the server running?</p>';
        console.error(err);
    }
}

function selectDoctor(id, name, specialty) {
    booking.doctorId   = id;
    booking.doctorName = name;
    booking.specialty  = specialty;
    booking.date       = null;
    booking.dateLabel  = null;
    booking.time       = null;
    booking.timeLabel  = null;

    // Reset time grid
    document.querySelector('.time-grid').innerHTML =
        '<p style="color:#aaa;font-size:13px;">Select a date first</p>';

    updateSummary();
}

// ═══════════════════════════════════════════════════
// STEP 2 — Convert calendar date & load slots
// ═══════════════════════════════════════════════════

// "March 20, 2026" → "2026-03-20"
function convertDateToAPI(label) {
    const months = {
        'January':'01','February':'02','March':'03','April':'04',
        'May':'05','June':'06','July':'07','August':'08',
        'September':'09','October':'10','November':'11','December':'12'
    };
    const parts = label.replace(',', '').split(' ');
    return `${parts[2]}-${months[parts[0]]}-${parts[1].padStart(2,'0')}`;
}

async function loadSlots(dateLabel) {
    if (!booking.doctorId) {
        alert('Please select a doctor first!');
        return;
    }

    booking.date      = convertDateToAPI(dateLabel);
    booking.dateLabel = dateLabel;
    booking.time      = null;
    booking.timeLabel = null;

    updateSummary();

    const timeGrid = document.querySelector('.time-grid');
    timeGrid.innerHTML = '<p style="color:#aaa;font-size:13px;">Checking availability...</p>';

    try {
        const res  = await fetch(`${API}/slots/?doctor_id=${booking.doctorId}&date=${booking.date}`);
        const data = await res.json();

        if (!data.slots || data.slots.length === 0) {
            timeGrid.innerHTML =
                '<p style="color:#f87171;font-size:13px;">Doctor not available on this day.</p>';
            return;
        }

        timeGrid.innerHTML = data.slots.map(slot => `
            <label class="time-slot ${!slot.available ? 'booked-slot' : ''}"
                   onclick="${slot.available ? `selectTime('${slot.time}','${slot.label}')` : ''}">
                <input type="radio" name="time" hidden value="${slot.time}"
                       ${!slot.available ? 'disabled' : ''}>
                ${slot.label}
                ${!slot.available
                    ? '<br><small style="color:#f87171;font-size:10px;">Booked</small>'
                    : ''}
            </label>
        `).join('');

    } catch (err) {
        timeGrid.innerHTML = '<p style="color:#f87171;font-size:13px;">Failed to load slots.</p>';
        console.error(err);
    }
}

function selectTime(time, label) {
    booking.time      = time;
    booking.timeLabel = label;
    updateSummary();
}

// ═══════════════════════════════════════════════════
// STEP 3 — Update summary card
// ═══════════════════════════════════════════════════

function updateSummary() {
    document.querySelector('.summary-card').innerHTML = `
        <h3>Appointment Summary</h3>
        <div class="summary-item">
            <span class="summary-label">👨‍⚕️ Doctor</span>
            <span>${booking.doctorName ? 'Dr. ' + booking.doctorName : '—'}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">🏥 Specialty</span>
            <span>${booking.specialty || '—'}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">📅 Date</span>
            <span>${booking.dateLabel || '—'}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">🕒 Time</span>
            <span>${booking.timeLabel || '—'}</span>
        </div>
    `;
}

// ═══════════════════════════════════════════════════
// STEP 3 — Submit booking
// ═══════════════════════════════════════════════════

async function submitBooking(e) {
    e.preventDefault();

    const inputs       = document.querySelectorAll('.form-inputs .main-input');
    const patientName  = inputs[0].value.trim();
    const patientEmail = inputs[1].value.trim();
    const patientPhone = inputs[2].value.trim();

    if (!booking.doctorId)  { alert('Please select a doctor.');    return; }
    if (!booking.date)      { alert('Please select a date.');       return; }
    if (!booking.time)      { alert('Please select a time slot.');  return; }
    if (!patientName || !patientEmail || !patientPhone) {
        alert('Please fill in all your details.');
        return;
    }

    const btn = document.querySelector('button[type="submit"]');
    btn.textContent = 'Booking...';
    btn.disabled    = true;

    try {
        const res = await fetch(`${API}/book/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doctor_id:        booking.doctorId,
                appointment_date: booking.date,
                appointment_time: booking.time,
                patient_name:     patientName,
                patient_email:    patientEmail,
                patient_phone:    patientPhone,
            }),
        });

        const data = await res.json();

        if (res.ok) {
            showConfirmation(data.confirmation);
        } else {
            const errors = Object.values(data).flat().join('\n');
            alert('Booking failed:\n' + errors);
            btn.textContent = 'Confirm Appointment';
            btn.disabled    = false;
        }

    } catch (err) {
        alert('Something went wrong. Please try again.');
        btn.textContent = 'Confirm Appointment';
        btn.disabled    = false;
        console.error(err);
    }
}

// ═══════════════════════════════════════════════════
// CONFIRMATION PAGE
// ═══════════════════════════════════════════════════

function showConfirmation(data) {
    document.querySelector('.main-page').innerHTML = `
        <div class="confirmation-box">
            <div class="confirm-icon">✅</div>
            <h1>Appointment Confirmed!</h1>
            <p class="confirm-subtitle">Your appointment has been booked successfully.</p>

            <div class="confirm-reference">
                Booking Reference: <strong>${data.booking_reference}</strong>
            </div>

            <div class="confirm-details">
                <div class="confirm-row">
                    <span>👨‍⚕️ Doctor</span>
                    <strong>Dr. ${data.doctor_name}</strong>
                </div>
                <div class="confirm-row">
                    <span>🏥 Specialty</span>
                    <strong>${data.specialization}</strong>
                </div>
                <div class="confirm-row">
                    <span>📅 Date</span>
                    <strong>${data.appointment_date}</strong>
                </div>
                <div class="confirm-row">
                    <span>🕒 Time</span>
                    <strong>${data.time_label}</strong>
                </div>
                <div class="confirm-row">
                    <span>👤 Patient</span>
                    <strong>${data.patient_name}</strong>
                </div>
                <div class="confirm-row">
                    <span>📧 Email</span>
                    <strong>${data.patient_email}</strong>
                </div>
                <div class="confirm-row">
                    <span>📞 Phone</span>
                    <strong>${data.patient_phone}</strong>
                </div>
                <div class="confirm-row">
                    <span>📋 Status</span>
                    <strong class="status-pending">Pending ⏳</strong>
                </div>
            </div>

            <p class="confirm-note">
                Save your reference: <strong>${data.booking_reference}</strong>
            </p>

            <a href="book.html" class="continue-btn" style="display:inline-block;margin-top:20px;">
                Book Another Appointment
            </a>
        </div>
    `;
}

// ═══════════════════════════════════════════════════
// EVENT LISTENERS
// ═══════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

    // Load doctors on page load
    loadDoctors();

    // Listen for calendar date radio change
    document.addEventListener('change', (e) => {
        if (e.target.name === 'day') {
            loadSlots(e.target.value);
        }
    });

    // Listen for form submit
    document.querySelector('.booking-container').addEventListener('submit', submitBooking);
});
/**
 * validation.js — Symbiosis Admission Registration Form
 * Handles: real-time validation, password strength, toggle visibility,
 *          full form submit validation, success screen.
 */

'use strict';

/* ── Helpers ── */
const $ = id => document.getElementById(id);
const setError = (groupId, msgId, msg) => {
  const group = $(groupId);
  const span  = $(msgId);
  group.classList.add('has-error');
  group.classList.remove('has-success');
  span.textContent = msg;
};
const setSuccess = (groupId, msgId) => {
  const group = $(groupId);
  const span  = $(msgId);
  group.classList.remove('has-error');
  group.classList.add('has-success');
  span.textContent = '';
};
const clearState = (groupId, msgId) => {
  const group = $(groupId);
  const span  = $(msgId);
  group.classList.remove('has-error', 'has-success');
  span.textContent = '';
};

/* ── Validation Rules ── */
const RULES = {
  name(v) {
    const trimmed = v.trim();
    if (!trimmed)                        return 'Student name is required.';
    if (trimmed.length < 2)              return 'Name must be at least 2 characters.';
    if (trimmed.length > 80)             return 'Name must not exceed 80 characters.';
    if (!/^[A-Za-z\s'.'-]+$/.test(trimmed)) return 'Name may only contain letters and spaces.';
    return null;
  },
  email(v) {
    const trimmed = v.trim();
    if (!trimmed)          return 'Email ID is required.';
    // RFC-5322 simplified regex
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    if (!re.test(trimmed)) return 'Enter a valid email address (e.g. user@domain.com).';
    return null;
  },
  mobile(v) {
    const trimmed = v.trim();
    if (!trimmed)          return 'Mobile number is required.';
    if (!/^\d{10}$/.test(trimmed)) return 'Enter a valid 10-digit mobile number.';
    return null;
  },
  department(v) {
    return v ? null : 'Please select your department.';
  },
  gender() {
    const checked = document.querySelector('input[name="gender"]:checked');
    return checked ? null : 'Please select your gender.';
  },
  comments(v) {
    const trimmed = v.trim();
    if (!trimmed)          return 'Feedback comments are required.';
    if (trimmed.length < 10) return 'Please provide at least 10 characters of feedback.';
    if (trimmed.length > 1000) return 'Feedback must not exceed 1000 characters.';
    return null;
  }
};

/* ── Field Validators (called on blur / input) ── */
function validateName(live) {
  const val = $('name').value;
  const err = RULES.name(val);
  if (live && !val) { clearState('group-name', 'name-error'); return true; }
  if (err) { setError('group-name', 'name-error', err); return false; }
  setSuccess('group-name', 'name-error'); return true;
}
function validateEmail(live) {
  const val = $('email').value;
  const err = RULES.email(val);
  if (live && !val) { clearState('group-email', 'email-error'); return true; }
  if (err) { setError('group-email', 'email-error', err); return false; }
  setSuccess('group-email', 'email-error'); return true;
}
function validateMobile(live) {
  const val = $('mobile').value;
  const err = RULES.mobile(val);
  if (live && !val) { clearState('group-mobile', 'mobile-error'); return true; }
  if (err) { setError('group-mobile', 'mobile-error', err); return false; }
  setSuccess('group-mobile', 'mobile-error'); return true;
}
function validateDepartment() {
  const err = RULES.department($('department').value);
  if (err) { setError('group-department', 'department-error', err); return false; }
  setSuccess('group-department', 'department-error'); return true;
}
function validateGender() {
  const err = RULES.gender();
  if (err) { setError('group-gender', 'gender-error', err); return false; }
  setSuccess('group-gender', 'gender-error'); return true;
}
function validateComments(live) {
  const val = $('comments').value;
  const err = RULES.comments(val);
  if (live && !val) { clearState('group-comments', 'comments-error'); return true; }
  if (err) { setError('group-comments', 'comments-error', err); return false; }
  setSuccess('group-comments', 'comments-error'); return true;
}

/* ── Full Form Validation ── */
function validateAll() {
  const n  = validateName(false);
  const e  = validateEmail(false);
  const m  = validateMobile(false);
  const d  = validateDepartment(false);
  const g  = validateGender();
  const c  = validateComments(false);
  return n && e && m && d && g && c;
}

/* ── Reset ── */
function resetForm() {
  $('registrationForm').reset();
  ['group-name','group-email','group-mobile','group-department','group-gender','group-comments']
    .forEach(id => { const el = $(id); if(el) el.classList.remove('has-error','has-success'); });
  ['name-error','email-error','mobile-error','department-error','gender-error','comments-error']
    .forEach(id => { const el = $(id); if(el) el.textContent = ''; });
  $('successMsg').classList.add('hidden');
  $('registrationForm').classList.remove('hidden');
}
window.resetForm = resetForm;

/* ── DOMContentLoaded ── */
document.addEventListener('DOMContentLoaded', () => {

  /* Real-time listeners */
  $('name').addEventListener('input',  () => validateName(true));
  $('name').addEventListener('blur',   () => validateName(false));

  $('email').addEventListener('input', () => validateEmail(true));
  $('email').addEventListener('blur',  () => validateEmail(false));

  $('mobile').addEventListener('input', () => validateMobile(true));
  $('mobile').addEventListener('blur',  () => validateMobile(false));

  $('department').addEventListener('change', validateDepartment);

  document.querySelectorAll('input[name="gender"]')
    .forEach(r => r.addEventListener('change', validateGender));

  $('comments').addEventListener('input', () => validateComments(true));
  $('comments').addEventListener('blur',  () => validateComments(false));

  /* Form submit */
  $('registrationForm').addEventListener('submit', e => {
    e.preventDefault();
    if (!validateAll()) {
      /* Scroll to first error */
      const firstErr = document.querySelector('.has-error');
      if (firstErr) firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    /* Animate button */
    const btn = $('submitBtn');
    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = 'Submitting…';

    setTimeout(() => {
      $('registrationForm').classList.add('hidden');
      $('successMsg').classList.remove('hidden');
    }, 1200);
  });
});

const API_URL = import.meta.env.VITE_API_URL;

// FastAPI error bodies come in two shapes: a plain string `detail` for
// HTTPException (401/409), and an array of {msg, ...} objects for Pydantic's
// 422 validation errors. Normalize both into one readable string.
function formatApiError(detail) {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join("; ");
  }
  return "Something went wrong. Please try again.";
}

async function handleResponse(response) {
  if (response.ok) {
    return response.json();
  }
  let detail;
  try {
    detail = (await response.json()).detail;
  } catch {
    detail = undefined;
  }
  // Attach the HTTP status so callers can branch on it (e.g. 409 for a
  // double-booking) instead of string-matching the backend's message.
  const error = new Error(formatApiError(detail));
  error.status = response.status;
  throw error;
}

export function signup({ email, password, role }) {
  return fetch(`${API_URL}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, role }),
  }).then(handleResponse);
}

export function login({ email, password }) {
  // OAuth2PasswordRequestForm's field is called `username`, but the backend
  // treats it as the email — see backend/app/routers/auth.py.
  const body = new URLSearchParams({ username: email, password });
  return fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  }).then(handleResponse);
}

export function fetchMe(token) {
  return fetch(`${API_URL}/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then(handleResponse);
}

export function fetchMySlots(token) {
  return fetch(`${API_URL}/slots/mine`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then(handleResponse);
}

export function fetchOpenSlots(token) {
  return fetch(`${API_URL}/slots`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then(handleResponse);
}

export function createBooking(token, slotId) {
  return fetch(`${API_URL}/bookings`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ slot_id: slotId }),
  }).then(handleResponse);
}

export function createSlot(token, { start_time, end_time }) {
  return fetch(`${API_URL}/slots`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ start_time, end_time }),
  }).then(handleResponse);
}

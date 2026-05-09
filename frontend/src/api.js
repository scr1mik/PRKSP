const API_ROOT = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "/api";

async function request(path = "", options = {}) {
  const response = await fetch(`${API_ROOT}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export function fetchEvents() {
  return request("/events/");
}

export function createEvent(payload) {
  return request("/events/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateEvent(eventId, payload) {
  return request(`/events/${eventId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteEvent(eventId) {
  return request(`/events/${eventId}`, {
    method: "DELETE",
  });
}

export function registerUser(payload) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function loginUser(payload) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function logoutUser() {
  return request("/auth/logout", {
    method: "POST",
  });
}

export function fetchCurrentUser() {
  return request("/auth/me");
}

export function fetchRelease() {
  return request("/release");
}

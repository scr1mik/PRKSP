const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "/api/events";

async function request(path = "", options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
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
  return request("/");
}

export function createEvent(payload) {
  return request("/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateEvent(eventId, payload) {
  return request(`/${eventId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteEvent(eventId) {
  return request(`/${eventId}`, {
    method: "DELETE",
  });
}

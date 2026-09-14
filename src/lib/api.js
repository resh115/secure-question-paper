import { auth } from "./firebase";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:5000";


export async function getAuthToken() {
  const user = auth.currentUser;

  if (!user) {
    throw new Error("Firebase user is not authenticated.");
  }

  return await user.getIdToken();
}


export async function apiFetch(path, options = {}) {
  const user = auth.currentUser;

  if (!user) {
    throw new Error("Firebase user is not authenticated.");
  }

  const token = await user.getIdToken();

  const headers = new Headers(options.headers || {});

  headers.set(
    "Authorization",
    `Bearer ${token}`
  );

  if (!(options.body instanceof FormData)) {
    if (!headers.has("Content-Type")) {
      headers.set(
        "Content-Type",
        "application/json"
      );
    }
  }

  return fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
    }
  );
}


/*
 * Get the application user profile from Flask.
 *
 * This is different from auth.currentUser.
 * Firebase gives us authentication identity.
 * Flask + MongoDB gives us the application role.
 */
export async function getCurrentUser() {
  const response = await apiFetch("/api/auth/me", {
    method: "GET",
  });

  let data = {};

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data.error ||
      `Failed to load application profile (${response.status}).`
    );
  }

  return data;
}
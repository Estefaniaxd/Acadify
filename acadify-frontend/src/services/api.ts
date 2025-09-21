
const API_BASE_URL = 'http://localhost:5000/api';

function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
}

async function handleResponse(response: Response) {
  if (!response.ok) {
    let errorMsg = 'Error de conexión';
    try {
      const error = await response.json();
      errorMsg = error.message || errorMsg;
    } catch {}
    throw new Error(errorMsg);
  }
  return response.json();
}

export const api = {
  async get(url: string) {
    const response = await fetch(API_BASE_URL + url, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    return { data: await handleResponse(response) };
  },
  async post(url: string, body?: any) {
    const response = await fetch(API_BASE_URL + url, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: body ? JSON.stringify(body) : undefined,
    });
    return { data: await handleResponse(response) };
  },
  async put(url: string, body?: any) {
    const response = await fetch(API_BASE_URL + url, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: body ? JSON.stringify(body) : undefined,
    });
    return { data: await handleResponse(response) };
  },
  async delete(url: string) {
    const response = await fetch(API_BASE_URL + url, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      let errorMsg = 'Error de conexión';
      try {
        const error = await response.json();
        errorMsg = error.message || errorMsg;
      } catch {}
      throw new Error(errorMsg);
    }
    return { data: true };
  },
};
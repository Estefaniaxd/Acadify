import { API_BASE_URL, getAuthToken } from '../../config/api.config';

const INVITACIONES_BASE_URL = `${API_BASE_URL}/invitaciones`;

const buildHeaders = (): HeadersInit => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

async function handleResponse(res: Response) {
  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || 'Error en la solicitud de invitaciones');
  }
  return res.json();
}

// API para invitaciones de coordinador
export async function getInvitacionesPendientes() {
  const res = await fetch(`${INVITACIONES_BASE_URL}`, {
    credentials: 'include',
    headers: buildHeaders(),
  });
  return handleResponse(res);
}

export async function aceptarInvitacion(id: number) {
  const res = await fetch(`${INVITACIONES_BASE_URL}/${id}/aceptar`, {
    method: 'POST',
    credentials: 'include',
    headers: buildHeaders(),
  });
  return handleResponse(res);
}

// API para invitaciones de coordinador
export async function getInvitacionesPendientes() {
  const res = await fetch('/api/invitaciones', { credentials: 'include' });
  if (!res.ok) throw new Error('Error al obtener invitaciones');
  return await res.json();
}

export async function aceptarInvitacion(id: number) {
  const res = await fetch(`/api/invitaciones/${id}/aceptar`, {
    method: 'POST',
    credentials: 'include'
  });
  if (!res.ok) throw new Error('Error al aceptar invitación');
  return await res.json();
}

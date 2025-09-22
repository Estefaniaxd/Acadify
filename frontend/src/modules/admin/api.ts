// API para gestión de instituciones y coordinadores
export async function registrarInstitucion(nombre: string, email: string) {
  const res = await fetch('/api/instituciones', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nombre, email })
  });
  if (!res.ok) throw new Error('Error al registrar institución');
  return await res.json();
}

// Script de debug para verificar autenticación
console.log('🔍 Debug de Autenticación');
console.log('==========================');

// Verificar token en localStorage
const token = localStorage.getItem('access_token');
console.log('Token en localStorage:', token ? '✅ Presente' : '❌ No encontrado');
if (token) {
  console.log('Token preview:', token.substring(0, 50) + '...');
}

// Verificar datos de usuario
const userData = localStorage.getItem('user');
console.log('Datos de usuario:', userData ? '✅ Presente' : '❌ No encontrado');
if (userData) {
  try {
    const user = JSON.parse(userData);
    console.log('Usuario:', user);
  } catch (e) {
    console.log('❌ Error parseando datos de usuario');
  }
}

// Test de API call manual
if (token) {
  console.log('🚀 Probando llamada API...');
  fetch('http://localhost:8000/academic/cursos/mis-cursos', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log('Status:', response.status);
    console.log('Headers:', response.headers);
    return response.json();
  })
  .then(data => {
    console.log('✅ Respuesta API:', data);
  })
  .catch(error => {
    console.log('❌ Error API:', error);
  });
} else {
  console.log('⚠️ No se puede probar API sin token');
}
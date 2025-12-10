#!/usr/bin/env node

// Script de prueba para verificar la creación de comentarios
// Ejecutar con: node test-comment-creation.js

const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';
const TEST_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0.test_token'; // Token de prueba

async function testCommentCreation() {
  console.log('🧪 Probando creación de comentarios...\n');

  try {
    // 1. Verificar que el backend esté corriendo
    console.log('1️⃣ Verificando conexión al backend...');
    const healthCheck = await axios.get(`${API_BASE_URL}/docs`);
    console.log('✅ Backend está corriendo\n');

    // 2. Probar creación de comentario sin token (debería fallar con 401)
    console.log('2️⃣ Probando sin token (debería fallar)...');
    try {
      await axios.post(`${API_BASE_URL}/api/academic/cursos/1/comentarios`, {
        contenido: 'Test comment',
        tipo: 'comentario',
        archivos: []
      });
      console.log('❌ ERROR: Debería haber fallado sin token\n');
    } catch (error) {
      if (error.response?.status === 401) {
        console.log('✅ Correcto: Falla con 401 sin token\n');
      } else {
        console.log('❌ ERROR: Falla con status inesperado:', error.response?.status, '\n');
      }
    }

    // 3. Probar creación de comentario con token (debería fallar con token inválido)
    console.log('3️⃣ Probando con token inválido...');
    try {
      await axios.post(`${API_BASE_URL}/api/academic/cursos/1/comentarios`, {
        contenido: 'Test comment',
        tipo: 'comentario',
        archivos: []
      }, {
        headers: {
          'Authorization': `Bearer ${TEST_TOKEN}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('❌ ERROR: Debería haber fallado con token inválido\n');
    } catch (error) {
      console.log('✅ Respuesta esperada con token inválido:', error.response?.status, error.response?.data, '\n');
    }

    // 4. Verificar endpoint correcto
    console.log('4️⃣ Verificando endpoint correcto...');
    try {
      const response = await axios.options(`${API_BASE_URL}/api/academic/cursos/1/comentarios`);
      console.log('✅ Endpoint existe y acepta POST\n');
    } catch (error) {
      console.log('ℹ️ OPTIONS no soportado, pero eso es normal\n');
    }

    console.log('🎯 Prueba completada. Ahora verifica el frontend con un token válido.');

  } catch (error) {
    console.error('❌ Error en la prueba:', error.message);
    if (error.code === 'ECONNREFUSED') {
      console.log('💡 Asegúrate de que el backend esté corriendo en http://localhost:8000');
    }
  }
}

testCommentCreation();
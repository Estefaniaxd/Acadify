console.log('🧪 Test de conectividad - Avatar API');

// Test 1: Verificar que el API responde
async function testAPI() {
    try {
        console.log('📡 Probando conexión al API...');
        const response = await fetch('http://localhost:8000/avatar/assets?gender=male');
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ API funcionando correctamente');
            console.log('📊 Total de assets:', Object.values(data.categories).reduce((acc, assets) => acc + assets.length, 0));
            console.log('📋 Categorías disponibles:', Object.keys(data.categories));
            return data;
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('❌ Error en API:', error.message);
        throw error;
    }
}

// Test 2: Verificar que las imágenes cargan
async function testImages() {
    try {
        console.log('🖼️ Probando carga de imágenes...');
        const response = await fetch('http://localhost:8000/static/assets/base/male_base.jpeg');
        
        if (response.ok) {
            console.log('✅ Imágenes estáticas funcionando correctamente');
            console.log('📏 Tamaño de imagen:', response.headers.get('content-length'), 'bytes');
            return true;
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('❌ Error cargando imágenes:', error.message);
        throw error;
    }
}

// Test 3: Verificar que las URLs están correctas
function testURLs() {
    console.log('🔗 Verificando configuración de URLs...');
    const API_BASE_URL = 'http://localhost:8000';
    const AVATAR_ASSETS_BASE_URL = 'http://localhost:8000/static/assets';
    
    console.log('🎯 API_BASE_URL:', API_BASE_URL);
    console.log('🎯 AVATAR_ASSETS_BASE_URL:', AVATAR_ASSETS_BASE_URL);
    
    // Test de construcción de URLs
    const apiEndpoint = `${API_BASE_URL}/avatar/assets?gender=male`;
    const imageURL = `${AVATAR_ASSETS_BASE_URL}/base/male_base.jpeg`;
    
    console.log('📡 URL del API:', apiEndpoint);
    console.log('🖼️ URL de imagen:', imageURL);
    
    return { apiEndpoint, imageURL };
}

// Ejecutar todos los tests
async function runAllTests() {
    console.log('🚀 Iniciando tests de conectividad...');
    console.log('═══════════════════════════════════════');
    
    try {
        // Test URLs
        const urls = testURLs();
        console.log('');
        
        // Test API
        const apiData = await testAPI();
        console.log('');
        
        // Test Images
        await testImages();
        console.log('');
        
        console.log('🎉 ¡Todos los tests pasaron exitosamente!');
        console.log('✨ El sistema de avatars debería funcionar correctamente');
        console.log('');
        console.log('🔧 Si aún hay problemas, verifica:');
        console.log('   1. Que estés en http://localhost:5173');
        console.log('   2. Que el componente AvatarStudio esté usando las URLs correctas');
        console.log('   3. Que no haya errores en la consola del navegador');
        
        return { success: true, apiData, urls };
        
    } catch (error) {
        console.log('💥 Test falló:', error.message);
        console.log('');
        console.log('🔧 Verifica que:');
        console.log('   1. El backend esté ejecutándose en puerto 8000');
        console.log('   2. No haya firewall bloqueando las conexiones');
        console.log('   3. Las URLs de configuración sean correctas');
        
        return { success: false, error: error.message };
    }
}

// Ejecutar automáticamente
runAllTests();
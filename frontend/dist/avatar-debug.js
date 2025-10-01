// Script de debugging para Avatar Studio
console.log('🔧 Avatar Debugging Script activado');

// Test 1: Verificar configuración de URLs
const API_BASE_URL = 'http://localhost:8000';
const avatarAPI_URL = `${API_BASE_URL}/avatar/assets`;

console.log('📡 API URL:', avatarAPI_URL);

// Test 2: Simular la misma petición que hace AvatarStudio
async function testAvatarAPI() {
    console.log('🧪 Iniciando test de Avatar API...');
    
    try {
        const url = `${avatarAPI_URL}?gender=female`;
        console.log('🔗 URL de prueba:', url);
        
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Esto es importante para CORS
        });
        
        console.log('📊 Response status:', response.status);
        console.log('📊 Response ok:', response.ok);
        console.log('📊 Response headers:', [...response.headers.entries()]);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Error response:', errorText);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Data received successfully!');
        console.log('📋 Categories:', Object.keys(data.categories));
        console.log('📋 Total assets:', data.total_assets);
        console.log('📋 Resolution:', data.resolution);
        
        // Verificar específicamente la categoría base
        if (data.categories.base) {
            console.log('🎯 Base assets found:', data.categories.base.length);
            data.categories.base.forEach(asset => {
                console.log(`   - ${asset.display_name}: ${asset.filename} (${asset.target_gender})`);
            });
        } else {
            console.warn('⚠️ No base category found in response');
        }
        
        return data;
        
    } catch (error) {
        console.error('💥 Test failed:', error);
        console.error('🔧 Error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        return null;
    }
}

// Test 3: Probar imagen estática
async function testStaticImage() {
    console.log('🖼️ Testing static image access...');
    
    try {
        const imageUrl = 'http://localhost:8000/static/assets/base/female_base.jpeg';
        console.log('🔗 Image URL:', imageUrl);
        
        const response = await fetch(imageUrl);
        console.log('📊 Image response status:', response.status);
        console.log('📊 Image response ok:', response.ok);
        console.log('📊 Content-Type:', response.headers.get('content-type'));
        console.log('📊 Content-Length:', response.headers.get('content-length'));
        
        if (response.ok) {
            console.log('✅ Static image accessible!');
            
            // Crear un elemento img para probar la carga visual
            const img = new Image();
            img.onload = () => console.log('✅ Image loads visually!');
            img.onerror = () => console.error('❌ Image failed to load visually');
            img.src = imageUrl;
            
        } else {
            console.error('❌ Static image not accessible');
        }
        
    } catch (error) {
        console.error('💥 Static image test failed:', error);
    }
}

// Test 4: Simular la clase AvatarAPI completa
class TestAvatarAPI {
    constructor() {
        this.baseURL = `${API_BASE_URL}/avatar`;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            credentials: 'include',
        };

        console.log(`📡 Making request to: ${url}`);
        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ 
                error: 'Network error' 
            }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        return response.json();
    }

    async getAssetsManifest(gender) {
        const params = gender ? `?gender=${gender}` : '';
        return this.request(`/assets${params}`);
    }
}

// Ejecutar todos los tests
async function runAllTests() {
    console.log('🚀 Ejecutando todos los tests de avatar...');
    console.log('═══════════════════════════════════════════');
    
    // Test 1: API básico
    const apiResult = await testAvatarAPI();
    console.log('');
    
    // Test 2: Imagen estática
    await testStaticImage();
    console.log('');
    
    // Test 3: Clase API completa
    if (apiResult) {
        console.log('🧪 Testing AvatarAPI class...');
        try {
            const testAPI = new TestAvatarAPI();
            const result = await testAPI.getAssetsManifest('female');
            console.log('✅ AvatarAPI class working correctly!');
        } catch (error) {
            console.error('❌ AvatarAPI class failed:', error);
        }
    }
    
    console.log('');
    console.log('🎯 Tests completed!');
    console.log('Si todos los tests pasaron pero el componente no funciona,');
    console.log('revisa la consola del navegador para errores específicos.');
}

// Auto-ejecutar
runAllTests();
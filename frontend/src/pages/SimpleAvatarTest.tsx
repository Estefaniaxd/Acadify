import React, { useState, useEffect } from 'react';

// Copia simplificada de avatarAPI solo para testing
const API_BASE_URL = 'http://localhost:8000';

// Tipos para el test
interface AssetInfo {
  id: string;
  filename: string;
  display_name: string;
  target_gender: string;
}

interface ManifestResponse {
  resolution: [number, number];
  categories: Record<string, AssetInfo[]>;
  total_assets: number;
}

async function testAvatarAPI(): Promise<ManifestResponse> {
  const url = `${API_BASE_URL}/avatar/assets?gender=female`;
  console.log('🔗 Testing URL:', url);
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    // NO incluir credentials para endpoint público
    mode: 'cors', // Especificar explícitamente modo CORS
  });
  
  console.log('📊 Response status:', response.status);
  console.log('📊 Response ok:', response.ok);
  console.log('📊 Response headers available');
  
  if (!response.ok) {
    const errorText = await response.text().catch(() => 'No response text');
    console.error('❌ Error response text:', errorText);
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
}

export default function SimpleAvatarTest() {
  const [data, setData] = useState<ManifestResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        console.log('🚀 Starting simple avatar test...');
        const result = await testAvatarAPI();
        console.log('✅ Data received:', result);
        setData(result);
      } catch (err) {
        console.error('❌ Error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Probando conexión API...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
          <div className="text-red-500 text-4xl mb-4 text-center">❌</div>
          <h3 className="text-lg font-semibold mb-2">Error de Conexión</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Reintentar
          </button>
          <div className="mt-4 text-sm text-gray-500">
            <p>Verifica que el backend esté ejecutándose en:</p>
            <code className="bg-gray-100 px-2 py-1 rounded text-xs">http://localhost:8000</code>
          </div>
        </div>
      </div>
    );
  }

  if (data) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white p-8 rounded-lg shadow-lg mb-8">
            <h1 className="text-2xl font-bold mb-4 text-green-600">✅ Conexión Exitosa!</h1>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{data.total_assets}</div>
                <div className="text-sm text-gray-600">Total Assets</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{Object.keys(data.categories).length}</div>
                <div className="text-sm text-gray-600">Categorías</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{data.resolution[0]}×{data.resolution[1]}</div>
                <div className="text-sm text-gray-600">Resolución</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{data.categories.base?.length || 0}</div>
                <div className="text-sm text-gray-600">Bases</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-8 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Categorías Disponibles</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(data.categories).map(([category, assets]) => (
                <div key={category} className="border rounded-lg p-4">
                  <h3 className="font-medium text-gray-800 mb-2 capitalize">{category}</h3>
                  <p className="text-gray-600 text-sm">{assets.length} assets disponibles</p>
                  
                  {/* Mostrar algunas imágenes de muestra */}
                  <div className="mt-3 grid grid-cols-2 gap-2">
                    {assets.slice(0, 4).map((asset: AssetInfo, index: number) => (
                      <div key={index} className="text-center">
                        <img 
                          src={`http://localhost:8000/static/assets/${asset.filename}`}
                          alt={asset.display_name}
                          className="w-full h-16 object-cover rounded border"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none';
                          }}
                        />
                        <p className="text-xs text-gray-500 mt-1 truncate">{asset.display_name}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8 text-center">
            <a 
              href="/avatar" 
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 inline-block"
            >
              Ir al Editor de Avatar Completo
            </a>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
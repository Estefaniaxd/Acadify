import React from 'react';

// Componente de prueba simple para verificar que los clicks funcionan
export default function TestModal() {
    const [count, setCount] = React.useState(0);

    console.log('🧪 TestModal renderizado, count:', count);

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white p-8 rounded-lg">
                <h2 className="text-2xl mb-4">Test Modal</h2>
                <p className="mb-4">Clicks: {count}</p>
                <button
                    onClick={() => {
                        console.log('🧪 Botón clickeado!');
                        setCount(c => c + 1);
                    }}
                    className="px-4 py-2 bg-blue-500 text-white rounded"
                >
                    Click Me
                </button>
            </div>
        </div>
    );
}

/**
 * Script de Testing Avanzado para Avatar Studio
 * Mide performance, re-renders, y funcionalidad del hook
 */

console.log('%c🧪 Avatar Studio Performance Test', 'background: #667eea; color: white; padding: 10px; font-size: 16px; border-radius: 5px;');

// Test 1: Verificar que el hook está activo
function testHookIntegration() {
  console.log('\n📋 Test 1: Verificando integración del hook...');
  
  try {
    // Buscar elementos que indican que el hook está activo
    const categoryButtons = document.querySelectorAll('button[class*="category"]');
    const hasCategories = categoryButtons.length > 0;
    
    console.log(`✅ Categorías encontradas: ${categoryButtons.length}`);
    
    // Verificar localStorage (el hook persiste datos aquí)
    const maleLayers = localStorage.getItem('avatar_male_layers');
    const femaleLayers = localStorage.getItem('avatar_female_layers');
    
    console.log(`✅ localStorage configurado:`);
    console.log(`   Male layers: ${maleLayers ? JSON.parse(maleLayers).length : 0} capas`);
    console.log(`   Female layers: ${femaleLayers ? JSON.parse(femaleLayers).length : 0} capas`);
    
    return {
      success: true,
      categories: categoryButtons.length,
      hasLocalStorage: !!(maleLayers || femaleLayers)
    };
  } catch (error) {
    console.error('❌ Error en test de hook:', error);
    return { success: false, error: error.message };
  }
}

// Test 2: Medir re-renders en una operación
function testReRenders() {
  console.log('\n📋 Test 2: Midiendo re-renders...');
  console.log('💡 Instrucciones:');
  console.log('   1. Selecciona una categoría (Hair, Eyes, etc.)');
  console.log('   2. Click en 3 assets diferentes');
  console.log('   3. Espera 5 segundos');
  console.log('   4. Los resultados se mostrarán automáticamente');
  
  let renderCount = 0;
  const startTime = performance.now();
  
  // Observar cambios en el DOM
  const observer = new MutationObserver((mutations) => {
    renderCount++;
    
    // Log cada render para debugging
    if (renderCount <= 20) {
      console.log(`   Render #${renderCount} detectado`);
    }
  });
  
  const targetNode = document.querySelector('[class*="avatar"]');
  if (!targetNode) {
    console.error('❌ No se encontró el contenedor de Avatar Studio');
    return;
  }
  
  observer.observe(targetNode, { 
    attributes: true, 
    childList: true, 
    subtree: true,
    characterData: true
  });
  
  // Detener después de 5 segundos
  setTimeout(() => {
    observer.disconnect();
    const endTime = performance.now();
    const duration = (endTime - startTime).toFixed(0);
    
    console.log(`\n📊 Resultados de Re-renders:`);
    console.log(`   Total renders: ${renderCount}`);
    console.log(`   Duración: ${duration}ms`);
    console.log(`   Promedio: ${(duration / renderCount).toFixed(2)}ms por render`);
    
    // Evaluación
    if (renderCount < 25) {
      console.log(`   ✅ EXCELENTE: Menos de 25 renders (objetivo: 15-20)`);
      console.log(`   🎯 Mejora vs antes: ~${((50 - renderCount) / 50 * 100).toFixed(0)}% menos renders`);
    } else if (renderCount < 40) {
      console.log(`   ⚠️  ACEPTABLE: 25-40 renders`);
      console.log(`   💡 Aún hay margen de optimización`);
    } else {
      console.log(`   ❌ NECESITA OPTIMIZACIÓN: Más de 40 renders`);
      console.log(`   🔧 Revisar useEffect dependencies y memo`);
    }
    
    return { renderCount, duration };
  }, 5000);
  
  console.log('⏱️  Midiendo durante 5 segundos... (interactúa ahora)');
}

// Test 3: Verificar debouncing de localStorage
function testDebouncing() {
  console.log('\n📋 Test 3: Verificando debouncing de localStorage...');
  
  let saveCount = 0;
  const originalSetItem = localStorage.setItem;
  
  // Interceptar setItem para contar saves
  localStorage.setItem = function(key, value) {
    if (key.includes('avatar_')) {
      saveCount++;
      console.log(`   Save #${saveCount} a localStorage: ${key}`);
    }
    return originalSetItem.apply(this, arguments);
  };
  
  console.log('💡 Instrucciones:');
  console.log('   1. Agrega 5 capas rápidamente (< 2 segundos)');
  console.log('   2. Espera 1 segundo');
  console.log('   3. Deberías ver SOLO 1-2 saves (por el debounce de 500ms)');
  
  setTimeout(() => {
    localStorage.setItem = originalSetItem;
    
    console.log(`\n📊 Resultados de Debouncing:`);
    console.log(`   Total saves a localStorage: ${saveCount}`);
    
    if (saveCount <= 2) {
      console.log(`   ✅ EXCELENTE: Debouncing funcionando correctamente`);
      console.log(`   🎯 Sin debounce serían ~5 saves innecesarios`);
    } else if (saveCount <= 5) {
      console.log(`   ⚠️  REGULAR: Algunos saves extra`);
    } else {
      console.log(`   ❌ PROBLEMA: Demasiados saves`);
      console.log(`   🔧 Revisar debounce en useAvatarStudio`);
    }
  }, 3000);
  
  console.log('⏱️  Monitoreando durante 3 segundos...');
}

// Test 4: Memoria - Verificar cleanup
function testMemoryLeaks() {
  console.log('\n📋 Test 4: Verificando cleanup de memoria...');
  
  const initialHeap = performance.memory ? performance.memory.usedJSHeapSize : null;
  
  if (!initialHeap) {
    console.log('⚠️  performance.memory no disponible en este navegador');
    console.log('   Usa Chrome con --enable-precise-memory-info para este test');
    return;
  }
  
  console.log(`   Heap inicial: ${(initialHeap / 1024 / 1024).toFixed(2)} MB`);
  
  console.log('💡 Instrucciones:');
  console.log('   1. Agrega 10 capas');
  console.log('   2. Remueve todas las capas');
  console.log('   3. Repite 3 veces');
  console.log('   4. Espera 5 segundos para ver resultados');
  
  setTimeout(() => {
    const finalHeap = performance.memory.usedJSHeapSize;
    const heapDiff = finalHeap - initialHeap;
    const heapDiffMB = (heapDiff / 1024 / 1024).toFixed(2);
    
    console.log(`\n📊 Resultados de Memoria:`);
    console.log(`   Heap inicial: ${(initialHeap / 1024 / 1024).toFixed(2)} MB`);
    console.log(`   Heap final: ${(finalHeap / 1024 / 1024).toFixed(2)} MB`);
    console.log(`   Diferencia: ${heapDiffMB} MB`);
    
    if (Math.abs(heapDiff) < 5 * 1024 * 1024) { // < 5MB
      console.log(`   ✅ EXCELENTE: Sin memory leaks detectados`);
      console.log(`   🎯 Cleanup funcionando correctamente`);
    } else if (Math.abs(heapDiff) < 10 * 1024 * 1024) { // < 10MB
      console.log(`   ⚠️  ACEPTABLE: Ligero incremento de memoria`);
    } else {
      console.log(`   ❌ POSIBLE MEMORY LEAK`);
      console.log(`   🔧 Revisar cleanup en useEffect`);
    }
  }, 10000);
  
  console.log('⏱️  Monitoreando durante 10 segundos...');
}

// Test 5: Funcionalidad completa
function testFullFunctionality() {
  console.log('\n📋 Test 5: Test de funcionalidad completa...');
  
  const tests = {
    mount: false,
    categories: false,
    assets: false,
    gender: false,
    preview: false,
    localStorage: false
  };
  
  try {
    // 1. Montaje
    const container = document.querySelector('[class*="avatar"]');
    tests.mount = !!container;
    console.log(`   ${tests.mount ? '✅' : '❌'} Componente montado`);
    
    // 2. Categorías
    const categories = document.querySelectorAll('button[class*="category"]');
    tests.categories = categories.length > 0;
    console.log(`   ${tests.categories ? '✅' : '❌'} Categorías visibles: ${categories.length}`);
    
    // 3. Assets
    const assets = document.querySelectorAll('[class*="asset"], img[alt*="asset"]');
    tests.assets = assets.length > 0;
    console.log(`   ${tests.assets ? '✅' : '❌'} Assets disponibles: ${assets.length}`);
    
    // 4. Controles de género
    const genderButtons = Array.from(document.querySelectorAll('button')).filter(
      btn => btn.textContent.toLowerCase().includes('male') || 
             btn.textContent.toLowerCase().includes('female')
    );
    tests.gender = genderButtons.length >= 2;
    console.log(`   ${tests.gender ? '✅' : '❌'} Controles de género: ${genderButtons.length}`);
    
    // 5. Preview
    const previewImage = document.querySelector('img[src*="dicebear"]');
    tests.preview = !!previewImage;
    console.log(`   ${tests.preview ? '✅' : '⚠️ '} Preview ${tests.preview ? 'visible' : 'no generado aún'}`);
    
    // 6. localStorage
    const hasStorage = localStorage.getItem('avatar_male_layers') || localStorage.getItem('avatar_female_layers');
    tests.localStorage = !!hasStorage;
    console.log(`   ${tests.localStorage ? '✅' : '⚠️ '} localStorage ${tests.localStorage ? 'configurado' : 'vacío (normal si es primera vez)'}`);
    
    // Resumen
    const passed = Object.values(tests).filter(t => t).length;
    const total = Object.keys(tests).length;
    const percentage = ((passed / total) * 100).toFixed(0);
    
    console.log(`\n📊 Resultado Final: ${passed}/${total} tests pasados (${percentage}%)`);
    
    if (percentage >= 80) {
      console.log('   🎉 ¡EXCELENTE! Avatar Studio funcionando correctamente');
    } else if (percentage >= 60) {
      console.log('   ⚠️  Funcional pero con algunas limitaciones');
    } else {
      console.log('   ❌ Requiere atención - varios componentes fallan');
    }
    
    return { tests, passed, total, percentage };
  } catch (error) {
    console.error('❌ Error en test de funcionalidad:', error);
    return { error: error.message };
  }
}

// Menú interactivo
console.log('\n💡 Tests disponibles:');
console.log('   window.testHook() - Verifica integración del hook');
console.log('   window.testReRenders() - Mide re-renders (5s)');
console.log('   window.testDebouncing() - Verifica debounce de localStorage (3s)');
console.log('   window.testMemory() - Detecta memory leaks (10s)');
console.log('   window.testFull() - Test completo de funcionalidad');
console.log('   window.runAllTests() - Ejecuta TODOS los tests en secuencia');

// Exponer funciones globalmente
window.testHook = testHookIntegration;
window.testReRenders = testReRenders;
window.testDebouncing = testDebouncing;
window.testMemory = testMemoryLeaks;
window.testFull = testFullFunctionality;

// Función para ejecutar todos los tests
window.runAllTests = function() {
  console.clear();
  console.log('%c🚀 Ejecutando TODOS los tests...', 'background: #10b981; color: white; padding: 10px; font-size: 16px; border-radius: 5px;');
  
  testHookIntegration();
  
  setTimeout(() => {
    testFullFunctionality();
  }, 1000);
  
  setTimeout(() => {
    console.log('\n⏭️  Iniciando test de re-renders en 3 segundos...');
    console.log('💡 Prepárate para interactuar con Avatar Studio');
  }, 2000);
  
  setTimeout(() => {
    testReRenders();
  }, 5000);
  
  setTimeout(() => {
    console.log('\n⏭️  Iniciando test de debouncing en 3 segundos...');
  }, 11000);
  
  setTimeout(() => {
    testDebouncing();
  }, 14000);
  
  console.log('\n📅 Timeline de tests:');
  console.log('   0s: Hook + Funcionalidad');
  console.log('   5s: Re-renders (interactúa 5s)');
  console.log('   14s: Debouncing (interactúa 3s)');
  console.log('   Total: ~17 segundos');
};

// Auto-ejecutar test básico
console.log('\n🎬 Ejecutando test básico automáticamente...\n');
testHookIntegration();
testFullFunctionality();

console.log('\n✨ Para ejecutar todos los tests: window.runAllTests()');

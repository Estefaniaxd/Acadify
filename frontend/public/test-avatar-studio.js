/**
 * Script de testing para Avatar Studio V2
 * 
 * Para usar:
 * 1. Abre http://localhost:5173/avatar
 * 2. Abre la consola del navegador (F12)
 * 3. Copia y pega este script
 * 4. Ejecuta: testAvatarStudio()
 */

window.testAvatarStudio = function() {
  console.log('🧪 Iniciando tests de Avatar Studio...\n');
  
  // Test 1: Verificar que el componente está montado
  console.log('📋 Test 1: Verificar montaje del componente');
  const avatarContainer = document.querySelector('[class*="avatar"]');
  if (avatarContainer) {
    console.log('✅ Componente Avatar Studio montado correctamente');
  } else {
    console.log('❌ No se encontró el componente Avatar Studio');
    return;
  }
  
  // Test 2: Verificar categorías
  console.log('\n📋 Test 2: Verificar categorías de assets');
  const categories = document.querySelectorAll('[role="tab"], button[class*="tab"]');
  console.log(`✅ Encontradas ${categories.length} categorías`);
  if (categories.length > 0) {
    console.log('   Categorías:', Array.from(categories).map(c => c.textContent).join(', '));
  }
  
  // Test 3: Verificar assets disponibles
  console.log('\n📋 Test 3: Verificar assets disponibles');
  const assets = document.querySelectorAll('[class*="asset"], img[alt*="asset"]');
  console.log(`✅ Encontrados ${assets.length} assets visibles`);
  
  // Test 4: Verificar controles de género
  console.log('\n📋 Test 4: Verificar controles de género');
  const genderButtons = Array.from(document.querySelectorAll('button')).filter(
    btn => btn.textContent.toLowerCase().includes('male') || 
           btn.textContent.toLowerCase().includes('female') ||
           btn.textContent.toLowerCase().includes('masculino') ||
           btn.textContent.toLowerCase().includes('femenino')
  );
  console.log(`✅ Encontrados ${genderButtons.length} botones de género`);
  
  // Test 5: Verificar localStorage
  console.log('\n📋 Test 5: Verificar persistencia en localStorage');
  const maleLayers = localStorage.getItem('avatar_male_layers');
  const femaleLayers = localStorage.getItem('avatar_female_layers');
  console.log('✅ localStorage configurado:');
  console.log('   - Male layers:', maleLayers ? JSON.parse(maleLayers).length + ' capas' : 'vacío');
  console.log('   - Female layers:', femaleLayers ? JSON.parse(femaleLayers).length + ' capas' : 'vacío');
  
  // Test 6: Verificar preview
  console.log('\n📋 Test 6: Verificar área de preview');
  const previewImage = document.querySelector('img[src*="dicebear"], img[class*="preview"]');
  if (previewImage) {
    console.log('✅ Preview encontrado:', previewImage.src);
  } else {
    console.log('⚠️  Preview no visible (normal si no hay capas seleccionadas)');
  }
  
  console.log('\n✨ Tests completados!');
  console.log('\n📝 Próximos pasos manuales:');
  console.log('   1. Selecciona una categoría (Hair, Eyes, etc.)');
  console.log('   2. Click en un asset para agregarlo');
  console.log('   3. Verifica que aparece en "Capas seleccionadas"');
  console.log('   4. Click en el botón X para removerlo');
  console.log('   5. Cambia entre Male/Female');
  console.log('   6. Click en "Visualizar" para ver el preview');
  
  return {
    categories: categories.length,
    assets: assets.length,
    genderButtons: genderButtons.length,
    hasLocalStorage: !!(maleLayers || femaleLayers),
    hasPreview: !!previewImage
  };
};

// Test de performance
window.testAvatarPerformance = function() {
  console.log('⚡ Iniciando tests de performance...\n');
  
  let renderCount = 0;
  const startTime = performance.now();
  
  // Observar cambios en el DOM
  const observer = new MutationObserver((mutations) => {
    renderCount++;
  });
  
  const targetNode = document.querySelector('[class*="avatar"]');
  if (targetNode) {
    observer.observe(targetNode, { 
      attributes: true, 
      childList: true, 
      subtree: true 
    });
    
    console.log('✅ Observer configurado. Interactúa con Avatar Studio...');
    console.log('   (Agrega 5 capas y luego ejecuta: testAvatarPerformance.stop())');
    
    return {
      stop: () => {
        observer.disconnect();
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        console.log('\n📊 Resultados de Performance:');
        console.log(`   - Renders detectados: ${renderCount}`);
        console.log(`   - Duración: ${duration.toFixed(2)}ms`);
        console.log(`   - Promedio: ${(duration / renderCount).toFixed(2)}ms por render`);
        
        if (renderCount < 25) {
          console.log('   ✅ EXCELENTE: Menos de 25 renders (objetivo: 15-20)');
        } else if (renderCount < 40) {
          console.log('   ⚠️  ACEPTABLE: 25-40 renders');
        } else {
          console.log('   ❌ NECESITA OPTIMIZACIÓN: Más de 40 renders');
        }
        
        return { renderCount, duration };
      }
    };
  } else {
    console.log('❌ No se encontró el componente Avatar Studio');
  }
};

console.log('✅ Scripts de testing cargados!');
console.log('   - testAvatarStudio() para tests funcionales');
console.log('   - testAvatarPerformance() para tests de performance');

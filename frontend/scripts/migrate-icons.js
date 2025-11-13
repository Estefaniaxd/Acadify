#!/usr/bin/env node

/**
 * Script de Migración Automática de Íconos
 * Migra de react-icons y @heroicons/react a lucide-react
 * 
 * Uso: node scripts/migrate-icons.js [--dry-run] [--path src/components]
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Mapeo completo de íconos
const iconMap = {
  // React Icons - Feather (Fi)
  FiMenu: 'Menu',
  FiX: 'X',
  FiHome: 'Home',
  FiUser: 'User',
  FiUsers: 'Users',
  FiMail: 'Mail',
  FiLock: 'Lock',
  FiUnlock: 'Unlock',
  FiEye: 'Eye',
  FiEyeOff: 'EyeOff',
  FiCheck: 'Check',
  FiCheckCircle: 'CheckCircle',
  FiCheckCircle2: 'CheckCircle2',
  FiX: 'X',
  FiXCircle: 'XCircle',
  FiAlertCircle: 'AlertCircle',
  FiAlertTriangle: 'AlertTriangle',
  FiInfo: 'Info',
  FiChevronDown: 'ChevronDown',
  FiChevronUp: 'ChevronUp',
  FiChevronLeft: 'ChevronLeft',
  FiChevronRight: 'ChevronRight',
  FiChevronsLeft: 'ChevronsLeft',
  FiChevronsRight: 'ChevronsRight',
  FiArrowRight: 'ArrowRight',
  FiArrowLeft: 'ArrowLeft',
  FiArrowUp: 'ArrowUp',
  FiArrowDown: 'ArrowDown',
  FiSend: 'Send',
  FiTrash: 'Trash',
  FiTrash2: 'Trash2',
  FiEdit: 'Edit',
  FiEdit2: 'Edit2',
  FiEdit3: 'Edit3',
  FiSave: 'Save',
  FiDownload: 'Download',
  FiUpload: 'Upload',
  FiSearch: 'Search',
  FiFilter: 'Filter',
  FiPlus: 'Plus',
  FiMinus: 'Minus',
  FiSettings: 'Settings',
  FiLogOut: 'LogOut',
  FiLogIn: 'LogIn',
  FiBell: 'Bell',
  FiCalendar: 'Calendar',
  FiClock: 'Clock',
  FiStar: 'Star',
  FiHeart: 'Heart',
  FiThumbsUp: 'ThumbsUp',
  FiThumbsDown: 'ThumbsDown',
  FiMessageCircle: 'MessageCircle',
  FiMessageSquare: 'MessageSquare',
  FiPhone: 'Phone',
  FiVideo: 'Video',
  FiCamera: 'Camera',
  FiImage: 'Image',
  FiFile: 'File',
  FiFileText: 'FileText',
  FiFolder: 'Folder',
  FiFolderPlus: 'FolderPlus',
  FiBook: 'Book',
  FiBookOpen: 'BookOpen',
  FiClipboard: 'Clipboard',
  FiCopy: 'Copy',
  FiExternalLink: 'ExternalLink',
  FiLink: 'Link',
  FiLink2: 'Link2',
  FiShare: 'Share',
  FiShare2: 'Share2',
  FiGrid: 'Grid',
  FiList: 'List',
  FiMoreVertical: 'MoreVertical',
  FiMoreHorizontal: 'MoreHorizontal',
  FiRefreshCw: 'RefreshCw',
  FiRotateCw: 'RotateCw',
  FiZap: 'Zap',
  FiPlay: 'Play',
  FiPause: 'Pause',
  FiSkipForward: 'SkipForward',
  FiSkipBack: 'SkipBack',
  FiVolume: 'Volume',
  FiVolume2: 'Volume2',
  FiVolumeX: 'VolumeX',
  FiSun: 'Sun',
  FiMoon: 'Moon',
  FiCloud: 'Cloud',
  FiGlobe: 'Globe',
  FiMapPin: 'MapPin',
  FiShield: 'Shield',
  FiAward: 'Award',
  FiTrophy: 'Trophy',
  FiTarget: 'Target',
  FiTrendingUp: 'TrendingUp',
  FiTrendingDown: 'TrendingDown',
  FiBarChart: 'BarChart',
  FiBarChart2: 'BarChart2',
  FiPieChart: 'PieChart',
  FiActivity: 'Activity',
  FiPackage: 'Package',
  FiShoppingCart: 'ShoppingCart',
  FiTag: 'Tag',
  FiDollarSign: 'DollarSign',
  FiCreditCard: 'CreditCard',
  
  // React Icons - Hero Icons (Hi)
  HiSparkles: 'Sparkles',
  HiAcademicCap: 'GraduationCap',
  HiBookOpen: 'BookOpen',
  HiChartBar: 'BarChart',
  HiChatAlt2: 'MessageSquare',
  HiCog: 'Settings',
  HiUserGroup: 'Users',
  HiBeaker: 'FlaskConical',
  HiLightningBolt: 'Zap',
  HiTrendingUp: 'TrendingUp',
  HiCalendar: 'Calendar',
  HiClipboardCheck: 'ClipboardCheck',
  HiClipboardList: 'ClipboardList',
  HiDocumentText: 'FileText',
  HiFolder: 'Folder',
  HiHome: 'Home',
  HiMail: 'Mail',
  HiMenu: 'Menu',
  HiUserCircle: 'UserCircle',
  HiX: 'X',
  
  // React Icons - Font Awesome (Fa)
  FaBuilding: 'Building',
  FaUniversity: 'School',
  FaSchool: 'School',
  FaGraduationCap: 'GraduationCap',
  FaBook: 'Book',
  FaChalkboardTeacher: 'Presentation',
  FaUserGraduate: 'GraduationCap',
  FaUserTie: 'UserCircle',
  FaUsers: 'Users',
  FaUser: 'User',
  FaCog: 'Settings',
  FaCalendar: 'Calendar',
  FaChartLine: 'LineChart',
  FaChartBar: 'BarChart',
  FaTrophy: 'Trophy',
  FaMedal: 'Medal',
  FaStar: 'Star',
  FaAward: 'Award',
  FaFileAlt: 'FileText',
  FaClipboard: 'Clipboard',
  FaEdit: 'Edit',
  FaTrash: 'Trash',
  FaPlus: 'Plus',
  FaMinus: 'Minus',
  FaCheck: 'Check',
  FaTimes: 'X',
  FaArrowRight: 'ArrowRight',
  FaArrowLeft: 'ArrowLeft',
  
  // React Icons - Bootstrap (Bi)
  BiBook: 'Book',
  BiCalendar: 'Calendar',
  BiUser: 'User',
  BiHome: 'Home',
  BiMenu: 'Menu',
  BiX: 'X',
  
  // React Icons - Remix (Ri)
  RiBook2Line: 'BookOpen',
  RiCalendarLine: 'Calendar',
  RiUserLine: 'User',
  
  // React Icons - Simple Icons (Si) - Casos especiales
  SiReact: 'Component', // No hay equivalente directo, usamos Component
  SiTailwindcss: 'Palette',
  SiGithub: 'Github',
  SiTypescript: 'Code',
  
  // @heroicons/react
  AcademicCapIcon: 'GraduationCap',
  ArrowRightIcon: 'ArrowRight',
  ArrowLeftIcon: 'ArrowLeft',
  BellIcon: 'Bell',
  BookOpenIcon: 'BookOpen',
  CalendarIcon: 'Calendar',
  ChartBarIcon: 'BarChart',
  ChatBubbleLeftRightIcon: 'MessageSquare',
  CheckCircleIcon: 'CheckCircle',
  CheckIcon: 'Check',
  ChevronDownIcon: 'ChevronDown',
  ChevronRightIcon: 'ChevronRight',
  ClipboardDocumentListIcon: 'ClipboardList',
  CogIcon: 'Settings',
  DocumentTextIcon: 'FileText',
  EnvelopeIcon: 'Mail',
  ExclamationCircleIcon: 'AlertCircle',
  EyeIcon: 'Eye',
  EyeSlashIcon: 'EyeOff',
  HomeIcon: 'Home',
  InformationCircleIcon: 'Info',
  LockClosedIcon: 'Lock',
  MagnifyingGlassIcon: 'Search',
  PaperAirplaneIcon: 'Send',
  PencilIcon: 'Edit',
  PlusIcon: 'Plus',
  TrashIcon: 'Trash',
  UserCircleIcon: 'UserCircle',
  UserGroupIcon: 'Users',
  UserIcon: 'User',
  XMarkIcon: 'X',
};

// Patrones de importación a buscar
const importPatterns = [
  /import\s+{([^}]+)}\s+from\s+['"]react-icons\/fi['"]/g,
  /import\s+{([^}]+)}\s+from\s+['"]react-icons\/fa['"]/g,
  /import\s+{([^}]+)}\s+from\s+['"]react-icons\/hi['"]/g,
  /import\s+{([^}]+)}\s+from\s+['"]react-icons\/bi['"]/g,
  /import\s+{([^}]+)}\s+from\s+['"]react-icons\/ri['"]/g,
  /import\s+{([^}]+)}\s+from\s+['"]react-icons\/si['"]/g,
  /import\s+{([^}]+)}\s+from\s+['"]@heroicons\/react\/24\/outline['"]/g,
  /import\s+{([^}]+)}\s+from\s+['"]@heroicons\/react\/24\/solid['"]/g,
  /import\s+{([^}]+)}\s+from\s+['"]@heroicons\/react\/20\/solid['"]/g,
];

// Configuración
const args = process.argv.slice(2);
const isDryRun = args.includes('--dry-run');
const targetPath = args.find(arg => arg.startsWith('--path='))?.split('=')[1] || 'src';

let stats = {
  filesProcessed: 0,
  filesModified: 0,
  iconsReplaced: 0,
  errors: 0,
  warnings: [],
};

/**
 * Procesa un archivo
 */
function processFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;
    let newImports = new Set();
    let iconsToReplace = [];

    // Buscar y procesar importaciones
    importPatterns.forEach(pattern => {
      const matches = [...content.matchAll(pattern)];
      matches.forEach(match => {
        const importedIcons = match[1].split(',').map(i => i.trim());
        
        importedIcons.forEach(iconImport => {
          // Manejar alias (ej: FiMenu as MenuIcon)
          const [iconName, alias] = iconImport.split(/\s+as\s+/).map(s => s.trim());
          const newIconName = iconMap[iconName];
          
          if (newIconName) {
            newImports.add(alias || newIconName);
            iconsToReplace.push({
              old: iconName,
              new: newIconName,
              alias: alias,
            });
          } else {
            stats.warnings.push(`⚠️  ${filePath}: No se encontró mapeo para ${iconName}`);
          }
        });
        
        // Remover importación antigua
        content = content.replace(match[0], '');
        modified = true;
      });
    });

    if (modified) {
      // Agregar nueva importación de lucide-react
      if (newImports.size > 0) {
        const sortedImports = Array.from(newImports).sort();
        const newImport = `import { ${sortedImports.join(', ')} } from 'lucide-react';\n`;
        
        // Insertar después de la última importación o al inicio
        const lastImportIndex = content.lastIndexOf('import ');
        if (lastImportIndex !== -1) {
          const endOfLine = content.indexOf('\n', lastImportIndex);
          content = content.slice(0, endOfLine + 1) + newImport + content.slice(endOfLine + 1);
        } else {
          content = newImport + content;
        }
      }

      // Reemplazar uso de íconos en JSX
      iconsToReplace.forEach(({ old, new: newName, alias }) => {
        const displayName = alias || newName;
        // Reemplazar <FiMenu /> por <Menu />
        const jsxPattern = new RegExp(`<${old}([\\s/>])`, 'g');
        content = content.replace(jsxPattern, `<${displayName}$1`);
        // Reemplazar {FiMenu} por {Menu}
        const varPattern = new RegExp(`([^\\w])${old}([^\\w])`, 'g');
        content = content.replace(varPattern, `$1${displayName}$2`);
        
        stats.iconsReplaced++;
      });

      // Limpiar importaciones vacías
      content = content.replace(/import\s+{\s*}\s+from\s+['"][^'"]+['"];?\n?/g, '');
      
      // Guardar archivo (o mostrar preview en dry-run)
      if (isDryRun) {
        console.log(`\n📄 ${filePath}:`);
        console.log(`   ✓ ${iconsToReplace.length} íconos migrados`);
        console.log(`   → ${Array.from(newImports).join(', ')}`);
      } else {
        fs.writeFileSync(filePath, content, 'utf8');
        console.log(`✅ ${filePath} (${iconsToReplace.length} íconos)`);
      }
      
      stats.filesModified++;
    }

    stats.filesProcessed++;
  } catch (error) {
    stats.errors++;
    console.error(`❌ Error en ${filePath}:`, error.message);
  }
}

/**
 * Procesa directorio recursivamente
 */
function processDirectory(dirPath) {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    
    if (entry.isDirectory()) {
      // Skip node_modules, dist, build, etc.
      if (!['node_modules', 'dist', 'build', 'coverage', '.git'].includes(entry.name)) {
        processDirectory(fullPath);
      }
    } else if (entry.isFile()) {
      // Solo procesar archivos .tsx, .ts, .jsx, .js
      if (/\.(tsx?|jsx?)$/.test(entry.name)) {
        processFile(fullPath);
      }
    }
  }
}

/**
 * Main
 */
function main() {
  console.log('🚀 Iniciando migración de íconos...\n');
  console.log(`📁 Path: ${targetPath}`);
  console.log(`🔍 Modo: ${isDryRun ? 'DRY RUN (solo preview)' : 'ESCRITURA'}\n`);
  
  const startTime = Date.now();
  const fullPath = path.resolve(process.cwd(), targetPath);
  
  if (!fs.existsSync(fullPath)) {
    console.error(`❌ Error: El path ${fullPath} no existe`);
    process.exit(1);
  }
  
  // Verificar si es archivo o directorio
  const stat = fs.statSync(fullPath);
  if (stat.isFile()) {
    processFile(fullPath);
  } else {
    processDirectory(fullPath);
  }
  
  const duration = ((Date.now() - startTime) / 1000).toFixed(2);
  
  // Resumen
  console.log('\n' + '='.repeat(60));
  console.log('📊 RESUMEN DE MIGRACIÓN');
  console.log('='.repeat(60));
  console.log(`✓ Archivos procesados:    ${stats.filesProcessed}`);
  console.log(`✓ Archivos modificados:   ${stats.filesModified}`);
  console.log(`✓ Íconos reemplazados:    ${stats.iconsReplaced}`);
  console.log(`✗ Errores:                ${stats.errors}`);
  console.log(`⚠  Advertencias:          ${stats.warnings.length}`);
  console.log(`⏱  Tiempo:                ${duration}s`);
  
  if (stats.warnings.length > 0 && stats.warnings.length <= 10) {
    console.log('\n⚠️  ADVERTENCIAS:');
    stats.warnings.forEach(w => console.log(w));
  } else if (stats.warnings.length > 10) {
    console.log(`\n⚠️  ${stats.warnings.length} advertencias (demasiadas para mostrar)`);
  }
  
  if (isDryRun) {
    console.log('\n💡 Esto fue un DRY RUN. Ejecuta sin --dry-run para aplicar cambios.');
  } else {
    console.log('\n✅ Migración completada!');
    console.log('\n📋 PRÓXIMOS PASOS:');
    console.log('   1. Verificar que todo compila: npm run build');
    console.log('   2. Ejecutar tests: npm run test');
    console.log('   3. Revisar cambios: git diff');
    console.log('   4. Si todo OK, remover dependencias antiguas:');
    console.log('      pnpm remove react-icons @heroicons/react');
  }
}

main();

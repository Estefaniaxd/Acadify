/**
 * Sistema centralizado de íconos usando lucide-react
 * 
 * Beneficios:
 * - Tree-shaking óptimo (solo iconos usados en bundle)
 * - Tipado fuerte con TypeScript
 * - Consistencia visual en toda la app
 * - Fácil migración de react-icons/heroicons
 * - Bundle más pequeño (~30KB menos)
 * 
 * Uso:
 * import { CheckIcon, XIcon, ... } from '@/components/ui/icons';
 */

import { type LucideIcon } from 'lucide-react';

// Re-exportar todos los íconos que usamos en la app
export {
  // Navegación y UI básica
  Menu,
  X,
  ChevronRight,
  ChevronLeft,
  ChevronDown,
  ChevronUp,
  ChevronsLeft,
  ChevronsRight,
  Home,
  ArrowRight,
  ArrowLeft,
  MoreHorizontal,
  
  // Estados y feedback
  Check,
  CheckCircle,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Info,
  XCircle,
  Minus,
  
  // Autenticación y usuario
  User,
  Users,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Shield,
  ShieldCheck,
  Key,
  
  // Contenido y comunicación
  MessageSquare,
  MessageCircle,
  Send,
  Paperclip,
  Image as ImageIcon,
  File,
  FileText,
  Heart,
  Smile,
  Reply,
  Pin,
  
  // Académico
  BookOpen,
  GraduationCap,
  Calendar,
  Clock,
  TrendingUp,
  Award,
  Target,
  Star,
  Zap,
  
  // Acciones
  Edit,
  Edit2,
  Save,
  Trash,
  Trash2,
  Plus,
  Search,
  Filter,
  RefreshCw,
  Download,
  Upload,
  Copy,
  ExternalLink,
  
  // Configuración y admin
  Settings,
  Sliders,
  Bell,
  BellOff,
  HelpCircle,
  LogOut,
  LogIn,
  UserPlus,
  
  // Navegación compleja
  Loader,
  Loader2,
  Sun,
  Moon,
  Code,
  GitBranch,
  Github,
  
  // Empresarial
  Building,
  Building2,
  Briefcase,
  
  // Media y contenido
  Play,
  Pause,
  Volume2,
  VolumeX,
  
  // Otros
  MoreVertical,
  Sparkles,
  Lightbulb,
  Trophy,
} from 'lucide-react';

// Type para componentes que aceptan íconos
export type IconComponent = LucideIcon;

/**
 * Props estándar para componentes de ícono
 */
export interface IconProps {
  className?: string;
  size?: number | string;
  strokeWidth?: number;
}

/**
 * Mapeo de íconos de react-icons a lucide-react
 * Para facilitar la migración
 */
export const IconMap = {
  // Feather Icons (react-icons/fi) → lucide-react
  FiMenu: 'Menu',
  FiX: 'X',
  FiHome: 'Home',
  FiUser: 'User',
  FiUsers: 'Users',
  FiMail: 'Mail',
  FiLock: 'Lock',
  FiEye: 'Eye',
  FiEyeOff: 'EyeOff',
  FiShield: 'Shield',
  FiKey: 'Key',
  FiSend: 'Send',
  FiCheckCircle: 'CheckCircle2',
  FiAlertCircle: 'AlertCircle',
  FiAlertTriangle: 'AlertTriangle',
  FiInfo: 'Info',
  FiCheck: 'Check',
  FiMinus: 'Minus',
  FiChevronDown: 'ChevronDown',
  FiChevronRight: 'ChevronRight',
  FiChevronLeft: 'ChevronLeft',
  FiChevronsLeft: 'ChevronsLeft',
  FiChevronsRight: 'ChevronsRight',
  FiMoreHorizontal: 'MoreHorizontal',
  FiSun: 'Sun',
  FiMoon: 'Moon',
  FiPlay: 'Play',
  FiArrowRight: 'ArrowRight',
  FiArrowLeft: 'ArrowLeft',
  FiStar: 'Star',
  FiTrendingUp: 'TrendingUp',
  FiZap: 'Zap',
  FiCode: 'Code',
  FiGitBranch: 'GitBranch',
  FiHeart: 'Heart',
  FiSettings: 'Settings',
  FiBell: 'Bell',
  FiLogOut: 'LogOut',
  FiEdit: 'Edit2',
  FiTrash: 'Trash2',
  FiPlus: 'Plus',
  FiSearch: 'Search',
  FiFilter: 'Filter',
  FiRefreshCw: 'RefreshCw',
  FiDownload: 'Download',
  FiUpload: 'Upload',
  FiCopy: 'Copy',
  FiExternalLink: 'ExternalLink',
  FiCalendar: 'Calendar',
  FiClock: 'Clock',
  FiBook: 'BookOpen',
  FiAward: 'Award',
  FiTarget: 'Target',
  
  // Hero Icons (react-icons/hi) → lucide-react
  HiSparkles: 'Sparkles',
  HiOutlineOfficeBuilding: 'Building2',
  HiOutlineKey: 'Key',
  HiAcademicCap: 'GraduationCap',
  HiShieldCheck: 'ShieldCheck',
  HiLightningBolt: 'Zap',
  HiOutlineEmojiHappy: 'Smile',
  
  // Font Awesome (react-icons/fa) → lucide-react
  FaBuilding: 'Building',
  FaSave: 'Save',
  FaTimes: 'X',
  FaUpload: 'Upload',
  FaSpinner: 'Loader2',
  FaEdit: 'Edit',
  FaTrash: 'Trash',
  FaPlus: 'Plus',
  FaSearch: 'Search',
  FaEye: 'Eye',
  FaGraduationCap: 'GraduationCap',
  FaCheck: 'Check',
  FaFilter: 'Filter',
  FaSort: 'ArrowUpDown',
  FaCalendar: 'Calendar',
  FaClock: 'Clock',
  FaUsers: 'Users',
  
  // Remix Icons (react-icons/ri) → lucide-react
  RiStarLine: 'Star',
  
  // Bi Icons (react-icons/bi) → lucide-react
  BiReply: 'Reply',
  BiPin: 'Pin',
  
  // @heroicons/react → lucide-react
  PaperClipIcon: 'Paperclip',
  PhotoIcon: 'ImageIcon',
  ChatBubbleLeftEllipsisIcon: 'MessageCircle',
  HeartIcon: 'Heart',
  FaceSmileIcon: 'Smile',
  EllipsisHorizontalIcon: 'MoreHorizontal',
  ArrowUturnLeftIcon: 'Reply',
} as const;

/**
 * Configuración por defecto para los íconos
 */
export const defaultIconProps = {
  size: 20,
  strokeWidth: 2,
} as const;

/**
 * Helper para aplicar props consistentes a los íconos
 */
export const iconProps = (overrides?: Partial<IconProps>): IconProps => ({
  ...defaultIconProps,
  ...overrides,
});

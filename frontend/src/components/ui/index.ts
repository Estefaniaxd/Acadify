/**
 * UI Components Library
 * 
 * Biblioteca completa de componentes siguiendo principios SOLID y Clean Code:
 * - Single Responsibility: Cada componente hace una cosa
 * - Open/Closed: Extensibles vía props
 * - Liskov Substitution: API consistente
 * - Interface Segregation: Props específicas
 * - Dependency Inversion: Usan hooks compartidos
 * 
 * Características:
 * - Modo oscuro/claro
 * - Accesibilidad (WCAG 2.1 AA/AAA)
 * - TypeScript completo
 * - Animaciones Framer Motion
 * - Sistema de diseño unificado
 */

// ========== COMPONENTES BASE ==========

// Button
export { 
  Button, 
  ButtonGroup,
  type ButtonProps,
  type ButtonVariant,
  type ButtonSize,
} from './Button';

// Input
export {
  Input,
  Textarea,
  type InputProps,
  type TextareaProps,
  type InputSize,
} from './Input';

// Select
export {
  Select,
  type SelectProps,
  type SelectOption,
  type SelectSize,
} from './Select';

// Checkbox
export {
  Checkbox,
  type CheckboxProps,
  type CheckboxSize,
} from './Checkbox';

// Radio
export {
  Radio,
  RadioGroup,
  type RadioProps,
  type RadioGroupProps,
  type RadioSize,
} from './Radio';

// Switch
export {
  Switch,
  type SwitchProps,
  type SwitchSize,
} from './Switch';

// ========== COMPONENTES DE LAYOUT ==========

// Card
export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  type CardProps,
  type CardVariant,
  type CardPadding,
} from './Card';

// ========== COMPONENTES DE FEEDBACK ==========

// Badge
export {
  Badge,
  BadgeCounter,
  BadgeDot,
  type BadgeProps,
  type BadgeCounterProps,
  type BadgeDotProps,
  type BadgeVariant,
  type BadgeSize,
} from './Badge';

// Alert
export {
  Alert,
  type AlertProps,
  type AlertVariant,
} from './Alert';

// Skeleton
export {
  Skeleton,
  SkeletonCard,
  SkeletonAvatar,
  SkeletonList,
  type SkeletonProps,
} from './Skeleton';

// Progress
export {
  Progress,
  CircularProgress,
  type ProgressProps,
  type CircularProgressProps,
  type ProgressSize,
  type ProgressVariant,
} from './Progress';

// Spinner
export {
  Spinner,
  SpinnerDots,
  SpinnerPulse,
  type SpinnerProps,
  type SpinnerDotsProps,
  type SpinnerPulseProps,
  type SpinnerSize,
  type SpinnerVariant,
} from './Spinner';

// Modal
export {
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  type ModalProps,
  type ModalHeaderProps,
  type ModalBodyProps,
  type ModalFooterProps,
  type ModalSize,
} from './Modal';

// Toast
export { default as Toast, type ToastProps } from './Toast';

// ========== COMPONENTES ESPECIALIZADOS ==========

// EmojiPicker
export { default as EmojiPicker } from './EmojiPicker';

// ========== COMPONENTES DE NAVEGACIÓN ==========

// Tabs
export {
  Tabs,
  type TabsProps,
  type Tab,
  type TabVariant,
  type TabSize,
  type TabOrientation,
} from './Tabs';

// Breadcrumb
export {
  Breadcrumb,
  type BreadcrumbProps,
  type BreadcrumbItem,
} from './Breadcrumb';

// Pagination
export {
  Pagination,
  type PaginationProps,
  type PaginationSize,
} from './Pagination';

// Dropdown
export {
  Dropdown,
  type DropdownProps,
  type MenuItem,
  type MenuItemType,
  type MenuPlacement,
} from './Dropdown';

// Stepper
export {
  Stepper,
  type StepperProps,
  type Step,
  type StepStatus,
  type StepperOrientation,
} from './Stepper';

// ========== SISTEMA DE ÍCONOS ==========

// Sistema centralizado de íconos con lucide-react
export * from './icons';
export type { IconComponent, IconProps } from './icons';

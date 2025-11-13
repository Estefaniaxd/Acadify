import { StyleProp, ViewStyle, TextStyle, ImageStyle } from 'react-native';

type Style = StyleProp<ViewStyle | TextStyle | ImageStyle>;

/**
 * Utilidad para combinar estilos de React Native
 * Reemplaza la funcionalidad de clsx/twMerge para StyleSheet
 * 
 * @example
 * ```tsx
 * cn(styles.base, isActive && styles.active, customStyle)
 * ```
 */
export function cn(...styles: (Style | false | null | undefined)[]): Style {
  return styles.filter(Boolean) as Style;
}

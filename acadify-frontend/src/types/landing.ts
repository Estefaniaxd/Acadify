// Tipos para los componentes de la landing page

export interface FeatureItem {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  delay?: number;
}

export interface TestimonialItem {
  id: string;
  name: string;
  role: string;
  institution: string;
  content: string;
  avatar: string;
  rating: number;
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlocked: boolean;
  points: number;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

export interface StatItem {
  id: string;
  value: string;
  label: string;
  icon: string;
  color: string;
}

export interface GamificationElement {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
  features: string[];
}

export interface PricingPlan {
  id: string;
  name: string;
  price: string;
  description: string;
  features: string[];
  popular?: boolean;
  buttonText: string;
  color: string;
}

export interface SocialLink {
  name: string;
  url: string;
  icon: string;
}

export interface NavigationItem {
  name: string;
  href: string;
  external?: boolean;
}

// Tipos adicionales para animaciones
export interface AnimationProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
  className?: string;
}

// Tipos para la mascota Rutilio
export interface RutilioState {
  emotion: 'happy' | 'excited' | 'thinking' | 'celebrating' | 'sleeping';
  level: number;
  experience: number;
  accessories: string[];
}

export default interface LandingPageProps {
  isLoading?: boolean;
  user?: any;
}
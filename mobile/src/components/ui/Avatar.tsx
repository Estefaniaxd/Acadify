import React from 'react';
import { View, Text, Image, ImageSourcePropType, StyleSheet, ViewStyle } from 'react-native';

export interface AvatarProps {
  source?: ImageSourcePropType;
  alt: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  status?: 'online' | 'away' | 'busy' | 'offline';
  style?: ViewStyle;
}

export const Avatar: React.FC<AvatarProps> = ({ source, alt, size = 'md', status, style }) => {
  const initials = alt.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  return (
    <View style={[styles.cont, style]}>
      <View style={[styles.av, styles[`s_${size}`]]}>
        {source ? <Image source={source} style={styles.img} /> : <Text style={[styles.txt, styles[`ts_${size}`]]}>{initials}</Text>}
      </View>
      {status && <View style={[styles.dot, styles[`dot_${size}`], styles[`st_${status}`]]} />}
    </View>
  );
};

const styles = StyleSheet.create({
  cont: { position: 'relative' },
  av: { borderRadius: 999, backgroundColor: '#7c3aed', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' },
  s_xs: { width: 24, height: 24 },
  s_sm: { width: 32, height: 32 },
  s_md: { width: 40, height: 40 },
  s_lg: { width: 48, height: 48 },
  s_xl: { width: 56, height: 56 },
  s_2xl: { width: 64, height: 64 },
  img: { width: '100%', height: '100%' },
  txt: { color: '#fff', fontWeight: '600' },
  ts_xs: { fontSize: 10 },
  ts_sm: { fontSize: 12 },
  ts_md: { fontSize: 14 },
  ts_lg: { fontSize: 16 },
  ts_xl: { fontSize: 20 },
  ts_2xl: { fontSize: 24 },
  dot: { position: 'absolute', borderRadius: 999, borderWidth: 2, borderColor: '#fff' },
  dot_xs: { width: 8, height: 8, right: -1, bottom: -1 },
  dot_sm: { width: 10, height: 10, right: 0, bottom: 0 },
  dot_md: { width: 12, height: 12, right: 0, bottom: 0 },
  dot_lg: { width: 14, height: 14, right: 1, bottom: 1 },
  dot_xl: { width: 16, height: 16, right: 2, bottom: 2 },
  dot_2xl: { width: 18, height: 18, right: 2, bottom: 2 },
  st_online: { backgroundColor: '#10b981' },
  st_away: { backgroundColor: '#f59e0b' },
  st_busy: { backgroundColor: '#dc2626' },
  st_offline: { backgroundColor: '#6b7280' },
});

export default Avatar;

import AjustesPageAdvanced from './AjustesPageAdvanced';

export default function AjustesPage({ theme, setTheme }: { theme: 'light' | 'dark', setTheme: (t: 'light' | 'dark') => void }) {
  return <AjustesPageAdvanced />;
}

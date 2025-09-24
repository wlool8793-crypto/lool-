import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import all translation files
import en from '../assets/locales/en.json';
import hi from '../assets/locales/hi.json';
import es from '../assets/locales/es.json';
import fr from '../assets/locales/fr.json';
import de from '../assets/locales/de.json';
import ar from '../assets/locales/ar.json';
import zh from '../assets/locales/zh.json';
import ja from '../assets/locales/ja.json';
import pt from '../assets/locales/pt.json';
import ur from '../assets/locales/ur.json';
import bn from '../assets/locales/bn.json';
import gu from '../assets/locales/gu.json';

export const resources = {
  en: {
    translation: en,
  },
  hi: {
    translation: hi,
  },
  es: {
    translation: es,
  },
  fr: {
    translation: fr,
  },
  de: {
    translation: de,
  },
  ar: {
    translation: ar,
  },
  zh: {
    translation: zh,
  },
  ja: {
    translation: ja,
  },
  pt: {
    translation: pt,
  },
  ur: {
    translation: ur,
  },
  bn: {
    translation: bn,
  },
  gu: {
    translation: gu,
  },
};

export const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸', direction: 'ltr' },
  { code: 'hi', name: 'हिन्दी', flag: '🇮🇳', direction: 'ltr' },
  { code: 'es', name: 'Español', flag: '🇪🇸', direction: 'ltr' },
  { code: 'fr', name: 'Français', flag: '🇫🇷', direction: 'ltr' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪', direction: 'ltr' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦', direction: 'rtl' },
  { code: 'zh', name: '中文', flag: '🇨🇳', direction: 'ltr' },
  { code: 'ja', name: '日本語', flag: '🇯🇵', direction: 'ltr' },
  { code: 'pt', name: 'Português', flag: '🇵🇹', direction: 'ltr' },
  { code: 'ur', name: 'اردو', flag: '🇵🇰', direction: 'rtl' },
  { code: 'bn', name: 'বাংলা', flag: '🇧🇩', direction: 'ltr' },
  { code: 'gu', name: 'ગુજરાતી', flag: '🇮🇳', direction: 'ltr' },
];

// RTL language detection
export const isRTL = (language: string): boolean => {
  const rtlLanguages = ['ar', 'ur'];
  return rtlLanguages.includes(language);
};

// Initialize i18n
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: import.meta.env.NODE_ENV === 'development',

    interpolation: {
      escapeValue: false, // React already escapes by default
    },

    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },

    react: {
      useSuspense: false,
    },
  });

// Apply RTL/LTR direction to document
i18n.on('languageChanged', (lng) => {
  document.documentElement.dir = isRTL(lng) ? 'rtl' : 'ltr';
  document.documentElement.lang = lng;
});

export default i18n;
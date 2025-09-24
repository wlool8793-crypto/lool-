import i18n from './i18n';

// Date and time formatting utilities
export const formatDate = (date: string | Date, format?: 'short' | 'medium' | 'long'): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const locale = i18n.language;

  const options: Intl.DateTimeFormatOptions = {
    short: { dateStyle: 'short' },
    medium: { dateStyle: 'medium' },
    long: { dateStyle: 'long' }
  }[format || 'medium'] as Intl.DateTimeFormatOptions;

  return new Intl.DateTimeFormat(locale, options).format(dateObj);
};

export const formatDateTime = (date: string | Date, format?: 'short' | 'medium' | 'long'): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const locale = i18n.language;

  const options: Intl.DateTimeFormatOptions = {
    short: { dateStyle: 'short', timeStyle: 'short' },
    medium: { dateStyle: 'medium', timeStyle: 'short' },
    long: { dateStyle: 'long', timeStyle: 'short' }
  }[format || 'medium'] as Intl.DateTimeFormatOptions;

  return new Intl.DateTimeFormat(locale, options).format(dateObj);
};

export const formatTime = (time: string, format?: 'short' | 'medium'): string => {
  const [hours, minutes] = time.split(':');
  const date = new Date();
  date.setHours(parseInt(hours), parseInt(minutes));
  const locale = i18n.language;

  const options: Intl.DateTimeFormatOptions = {
    short: { hour: 'numeric', minute: 'numeric' },
    medium: { hour: 'numeric', minute: 'numeric', hour12: true }
  }[format || 'short'] as Intl.DateTimeFormatOptions;

  return new Intl.DateTimeFormat(locale, options).format(date);
};

// Number and currency formatting
export const formatNumber = (number: number, options?: Intl.NumberFormatOptions): string => {
  const locale = i18n.language;
  return new Intl.NumberFormat(locale, options).format(number);
};

export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  const locale = i18n.language;
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

export const formatPercentage = (value: number, decimals: number = 1): string => {
  const locale = i18n.language;
  return new Intl.NumberFormat(locale, {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value / 100);
};

export const formatPhoneNumber = (phoneNumber: string, countryCode?: string): string => {
  // Remove all non-digit characters
  const cleaned = phoneNumber.replace(/\D/g, '');

  // Simple formatting based on length and country
  if (countryCode === 'IN' && cleaned.length === 10) {
    return cleaned.replace(/(\d{5})(\d{5})/, '$1 $2');
  }

  if (countryCode === 'US' && cleaned.length === 10) {
    return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
  }

  // Default formatting
  return phoneNumber;
};

// Address formatting by region
export const formatAddress = (address: {
  street?: string;
  city?: string;
  state?: string;
  pinCode?: string;
  country?: string;
}, format?: 'full' | 'compact'): string => {
  const locale = i18n.language;

  if (format === 'compact') {
    return [address.city, address.state].filter(Boolean).join(', ');
  }

  // Region-specific formatting
  if (locale === 'hi' || locale === 'bn' || locale === 'gu') {
    // Indian address format
    return [
      address.street,
      address.city,
      address.state,
      address.pinCode,
      address.country
    ].filter(Boolean).join(', ');
  }

  if (locale === 'ar') {
    // Arabic RTL format
    return [
      address.country,
      address.pinCode,
      address.state,
      address.city,
      address.street
    ].filter(Boolean).join('، ');
  }

  // Western format
  return [
    address.street,
    address.city,
    address.state + ' ' + (address.pinCode || ''),
    address.country
  ].filter(Boolean).join(', ');
};

// Name formatting and salutations
export const formatName = (firstName: string, lastName?: string, middleName?: string, format?: 'full' | 'first' | 'formal'): string => {
  const locale = i18n.language;

  if (format === 'first') {
    return firstName;
  }

  if (format === 'formal') {
    const salutations: Record<string, string> = {
      en: 'Mr./Ms.',
      hi: 'श्री/श्रीमती',
      ar: 'السيد/السيدة',
      fr: 'M./Mme',
      es: 'Sr./Sra.',
      de: 'Herr/Frau',
      zh: '先生/女士',
      ja: '様/さん',
      pt: 'Sr./Sra.',
      ur: 'محترم/محترمه',
      bn: 'শ্রী/শ্রীমতী',
      gu: 'શ્રી/શ્રીમતી'
    };

    const salutation = salutations[locale] || salutations.en;
    return `${salutation} ${firstName} ${lastName || ''}`.trim();
  }

  // Full name with locale-specific ordering
  if (locale === 'zh' || locale === 'ja' || locale === 'ko') {
    // Asian format: Last Name First Name
    return `${lastName || ''} ${firstName}`.trim();
  }

  if (locale === 'ar' || locale === 'ur') {
    // Arabic/Urdu format: First Name Father's Name Last Name
    return `${firstName} ${middleName || ''} ${lastName || ''}`.trim();
  }

  // Western format: First Name Middle Name Last Name
  return `${firstName} ${middleName || ''} ${lastName || ''}`.trim();
};

export const getSalutation = (gender: 'male' | 'female', maritalStatus?: string): string => {
  const locale = i18n.language;

  const salutations: Record<string, Record<string, string>> = {
    en: { male: 'Mr.', female: maritalStatus === 'married' ? 'Mrs.' : 'Ms.' },
    hi: { male: 'श्री', female: maritalStatus === 'married' ? 'श्रीमती' : 'कुमारी' },
    ar: { male: 'السيد', female: maritalStatus === 'married' ? 'السيدة' : 'آنسة' },
    fr: { male: 'M.', female: maritalStatus === 'married' ? 'Mme' : 'Mlle' },
    es: { male: 'Sr.', female: maritalStatus === 'married' ? 'Sra.' : 'Srta.' },
    de: { male: 'Herr', female: maritalStatus === 'married' ? 'Frau' : 'Fräulein' },
    zh: { male: '先生', female: maritalStatus === 'married' ? '夫人' : '小姐' },
    ja: { male: '様', female: maritalStatus === 'married' ? '様' : 'さん' },
    pt: { male: 'Sr.', female: maritalStatus === 'married' ? 'Sra.' : 'Srta.' },
    ur: { male: 'محترم', female: maritalStatus === 'married' ? 'محترمه' : 'محترمه' },
    bn: { male: 'শ্রী', female: maritalStatus === 'married' ? 'শ্রীমতী' : 'কুমারী' },
    gu: { male: 'શ્રી', female: maritalStatus === 'married' ? 'શ્રીમતી' : 'કુમારી' }
  };

  return salutations[locale]?.[gender] || salutations.en[gender];
};

// Cultural and regional helpers
export const getCountryName = (countryCode: string): string => {
  const locale = i18n.language;
  try {
    const regionNames = new Intl.DisplayNames([locale], { type: 'region' });
    return regionNames.of(countryCode) || countryCode;
  } catch {
    return countryCode;
  }
};

export const getLanguageName = (languageCode: string): string => {
  const locale = i18n.language;
  try {
    const languageNames = new Intl.DisplayNames([locale], { type: 'language' });
    return languageNames.of(languageCode) || languageCode;
  } catch {
    return languageCode;
  }
};

export const getCurrencySymbol = (currencyCode: string): string => {
  const locale = i18n.language;
  try {
    return (0).toLocaleString(locale, {
      style: 'currency',
      currency: currencyCode,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
      currencyDisplay: 'symbol'
    }).replace(/\d/g, '').trim();
  } catch {
    return currencyCode;
  }
};

// Text direction utilities
export const isRTL = (text?: string): boolean => {
  const rtlLanguages = ['ar', 'ur', 'he', 'fa', 'yi'];
  return rtlLanguages.includes(i18n.language) ||
         (text && /[\u0591-\u07FF\uFB1D-\uFDFD\uFE70-\uFEFC]/.test(text));
};

export const getDirection = (): 'ltr' | 'rtl' => {
  return isRTL() ? 'rtl' : 'ltr';
};

// Unit conversions with localization
export const formatHeight = (height: string, unit?: 'cm' | 'ft' | 'in'): string => {
  const locale = i18n.language;

  // Parse height (assume cm if not specified)
  const heightValue = parseInt(height.replace(/\D/g, ''));
  if (isNaN(heightValue)) return height;

  if (locale === 'en' && (unit === 'ft' || !unit)) {
    const feet = Math.floor(heightValue / 30.48);
    const inches = Math.round((heightValue % 30.48) / 2.54);
    return `${feet}'${inches}"`;
  }

  return `${heightValue} cm`;
};

export const formatWeight = (weight: string, unit?: 'kg' | 'lbs'): string => {
  const locale = i18n.language;

  // Parse weight (assume kg if not specified)
  const weightValue = parseInt(weight.replace(/\D/g, ''));
  if (isNaN(weightValue)) return weight;

  if (locale === 'en' && (unit === 'lbs' || !unit)) {
    const pounds = Math.round(weightValue * 2.20462);
    return `${pounds} lbs`;
  }

  return `${weightValue} kg`;
};

// Age calculation and formatting
export const calculateAge = (birthDate: string): number => {
  const birth = new Date(birthDate);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }

  return age;
};

export const formatAge = (birthDate: string, format?: 'years' | 'years_months'): string => {
  const birth = new Date(birthDate);
  const today = new Date();

  const years = today.getFullYear() - birth.getFullYear();
  const months = today.getMonth() - birth.getMonth();

  if (format === 'years_months') {
    const adjustedMonths = months < 0 ? 12 + months : months;
    const adjustedYears = months < 0 ? years - 1 : years;
    return `${adjustedYears}y ${adjustedMonths}m`;
  }

  return `${years} years`;
};

// Validation helpers
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPhone = (phone: string, countryCode?: string): boolean => {
  const cleaned = phone.replace(/\D/g, '');

  if (countryCode === 'IN') {
    return cleaned.length === 10 && /^[6-9]/.test(cleaned);
  }

  if (countryCode === 'US') {
    return cleaned.length === 10;
  }

  // Generic validation
  return cleaned.length >= 10 && cleaned.length <= 15;
};

export const isValidPinCode = (pinCode: string, countryCode?: string): boolean => {
  const cleaned = pinCode.replace(/\D/g, '');

  if (countryCode === 'IN') {
    return /^[1-9][0-9]{5}$/.test(cleaned);
  }

  if (countryCode === 'US') {
    return /^[0-9]{5}(?:-[0-9]{4})?$/.test(cleaned);
  }

  // Generic validation
  return cleaned.length >= 5 && cleaned.length <= 10;
};

// Text utilities
export const truncateText = (text: string, maxLength: number, suffix: string = '...'): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - suffix.length) + suffix;
};

export const capitalizeFirst = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

export const toTitleCase = (text: string): string => {
  return text.replace(/\w\S*/g, (txt) =>
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  );
};

// Date helpers
export const getDaysBetween = (startDate: string, endDate: string): number => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const diffTime = Math.abs(end.getTime() - start.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

export const addYears = (date: string, years: number): string => {
  const result = new Date(date);
  result.setFullYear(result.getFullYear() + years);
  return result.toISOString().split('T')[0];
};

export const isDateValid = (dateString: string): boolean => {
  const date = new Date(dateString);
  return !isNaN(date.getTime());
};

// Export all utilities
export const LocalizationUtils = {
  formatDate,
  formatDateTime,
  formatTime,
  formatNumber,
  formatCurrency,
  formatPercentage,
  formatPhoneNumber,
  formatAddress,
  formatName,
  getSalutation,
  getCountryName,
  getLanguageName,
  getCurrencySymbol,
  isRTL,
  getDirection,
  formatHeight,
  formatWeight,
  calculateAge,
  formatAge,
  isValidEmail,
  isValidPhone,
  isValidPinCode,
  truncateText,
  capitalizeFirst,
  toTitleCase,
  getDaysBetween,
  addYears,
  isDateValid
};
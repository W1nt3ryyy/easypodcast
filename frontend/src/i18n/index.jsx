/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState } from 'react';
import ru from './ru';
import en from './en';

const locales = { ru, en };

const I18nContext = createContext();

export function I18nProvider({ children, initialLocale = 'ru' }) {
  const [locale, setLocale] = useState(initialLocale);

  const t = (key) => {
    const keys = key.split('.');
    let value = locales[locale];
    for (const k of keys) {
      if (value && typeof value === 'object') {
        value = value[k];
      } else {
        return key;
      }
    }
    return value || key;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return null;
    const months = t('date.months');
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    return `${date.getDate()} ${months[date.getMonth()]}, ${date.getFullYear()}`;
  };

  const formatDuration = (duration) => {
    if (!duration) return null;
    const num = typeof duration === 'number' ? duration : parseInt(duration, 10);
    if (isNaN(num)) return String(duration);

    const hours = Math.floor(num / 3600);
    const mins = Math.floor((num % 3600) / 60);

    if (hours > 0) {
      return `${hours}${t('duration.hours')} ${mins}${t('duration.min')}`;
    }
    return `${mins} ${t('duration.min')}`;
  };

  return (
    <I18nContext.Provider value={{ locale, setLocale, t, formatDate, formatDuration }}>
      {children}
    </I18nContext.Provider>
  );
}

export const useI18n = () => useContext(I18nContext);

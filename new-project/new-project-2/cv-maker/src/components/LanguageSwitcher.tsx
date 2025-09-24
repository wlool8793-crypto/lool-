import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ChevronDown, Globe } from 'lucide-react';
import { languages, isRTL } from '../lib/i18n';
import { Button } from './ui/button';
import { cn } from '../lib/utils';

interface LanguageSwitcherProps {
  className?: string;
  variant?: 'default' | 'ghost' | 'outline';
  size?: 'default' | 'sm' | 'lg';
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  className,
  variant = 'ghost',
  size = 'sm',
}) => {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);

  const currentLanguage = languages.find((lang) => lang.code === i18n.language) || languages[0];

  const handleLanguageChange = (languageCode: string) => {
    i18n.changeLanguage(languageCode);
    localStorage.setItem('i18nextLng', languageCode);
    setIsOpen(false);
  };

  return (
    <div className={cn('relative', className)}>
      <Button
        variant={variant}
        size={size}
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-2',
          isRTL(i18n.language) && 'flex-row-reverse'
        )}
      >
        <Globe className="h-4 w-4" />
        <span>{currentLanguage.flag}</span>
        <span className="hidden sm:inline">{currentLanguage.name}</span>
        <ChevronDown className={cn('h-4 w-4', isOpen && 'rotate-180')} />
      </Button>

      {isOpen && (
        <div
          className={cn(
            'absolute right-0 z-50 mt-2 w-48 rounded-md border bg-popover shadow-md',
            isRTL(i18n.language) && 'right-auto left-0'
          )}
        >
          <div className="max-h-80 overflow-y-auto">
            {languages.map((language) => (
              <button
                key={language.code}
                onClick={() => handleLanguageChange(language.code)}
                className={cn(
                  'w-full px-4 py-2 text-left hover:bg-accent hover:text-accent-foreground',
                  'flex items-center gap-3 transition-colors',
                  language.code === i18n.language && 'bg-accent text-accent-foreground'
                )}
              >
                <span className="text-lg">{language.flag}</span>
                <span className="flex-1">{language.name}</span>
                {language.code === i18n.language && (
                  <span className="text-sm text-muted-foreground">✓</span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
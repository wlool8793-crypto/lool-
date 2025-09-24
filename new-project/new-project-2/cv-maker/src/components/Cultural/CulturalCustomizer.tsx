import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Palette, Star, Globe, Sparkles, Settings, Languages } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/Input';
import { cn } from '../lib/utils';

interface CulturalTheme {
  id: string;
  name: string;
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    text: string;
  };
  symbols: string[];
  patterns: string[];
  region: string;
}

interface CulturalCustomizerProps {
  onThemeChange: (theme: CulturalTheme) => void;
  className?: string;
}

const culturalThemes: CulturalTheme[] = [
  {
    id: 'north_indian',
    name: 'North Indian',
    colors: {
      primary: '#dc2626',
      secondary: '#f59e0b',
      accent: '#fbbf24',
      background: '#fef2f2',
      text: '#7f1d1d'
    },
    symbols: ['🕉️', '🪷', '🔥', '🌅'],
    patterns: ['mandala', 'paisley', 'floral', 'geometric'],
    region: 'North India'
  },
  {
    id: 'south_indian',
    name: 'South Indian',
    colors: {
      primary: '#ea580c',
      secondary: '#d97706',
      accent: '#facc15',
      background: '#fff7ed',
      text: '#7c2d12'
    },
    symbols: ['🪔', '🌸', '🐘', '🏛️'],
    patterns: ['kolam', 'temple', 'mango', 'traditional'],
    region: 'South India'
  },
  {
    id: 'bengali',
    name: 'Bengali',
    colors: {
      primary: '#be123c',
      secondary: '#e11d48',
      accent: '#f43f5e',
      background: '#fdf2f8',
      text: '#831843'
    },
    symbols: ['🎨', '📚', '🌺', '🎭'],
    patterns: ['alpona', 'floral', 'artistic', 'cultural'],
    region: 'Bengal'
  },
  {
    id: 'gujarati',
    name: 'Gujarati',
    colors: {
      primary: '#059669',
      secondary: '#10b981',
      accent: '#34d399',
      background: '#f0fdf4',
      text: '#064e3b'
    },
    symbols: ['🎪', '🥘', '🪕', '🎪'],
    patterns: ['bandhani', 'mirror', 'geometric', 'colorful'],
    region: 'Gujarat'
  },
  {
    id: 'punjabi',
    name: 'Punjabi',
    colors: {
      primary: '#7c3aed',
      secondary: '#8b5cf6',
      accent: '#a78bfa',
      background: '#faf5ff',
      text: '#4c1d95'
    },
    symbols: ['🎵', '🌾', '💃', '👳'],
    patterns: ['phulkari', 'embroidery', 'vibrant', 'traditional'],
    region: 'Punjab'
  },
  {
    id: 'muslim',
    name: 'Muslim',
    colors: {
      primary: '#0284c7',
      secondary: '#0ea5e9',
      accent: '#38bdf8',
      background: '#f0f9ff',
      text: '#0c4a6e'
    },
    symbols: ['☪️', '🕌', '🌙', '✨'],
    patterns: ['islamic', 'geometric', 'calligraphy', 'arabesque'],
    region: 'Muslim Community'
  },
  {
    id: 'western',
    name: 'Western',
    colors: {
      primary: '#374151',
      secondary: '#6b7280',
      accent: '#9ca3af',
      background: '#f9fafb',
      text: '#111827'
    },
    symbols: ['💼', '🎓', '🏆', '⭐'],
    patterns: ['minimal', 'modern', 'clean', 'professional'],
    region: 'Western'
  }
];

export const CulturalCustomizer: React.FC<CulturalCustomizerProps> = ({
  onThemeChange,
  className = ''
}) => {
  const { t } = useTranslation();
  const [selectedTheme, setSelectedTheme] = useState<CulturalTheme>(culturalThemes[0]);
  const [customColors, setCustomColors] = useState(false);
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
  const [selectedPattern, setSelectedPattern] = useState('');

  const handleThemeSelect = (theme: CulturalTheme) => {
    setSelectedTheme(theme);
    onThemeChange(theme);
  };

  const toggleSymbol = (symbol: string) => {
    setSelectedSymbols(prev =>
      prev.includes(symbol)
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    );
  };

  return (
    <div className={cn('space-y-6', className)}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            {t('cultural.cultural_symbols')} & {t('cultural.traditional_designs')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Theme Selection */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Select Cultural Theme</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {culturalThemes.map((theme) => (
                <div
                  key={theme.id}
                  className={cn(
                    'p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md',
                    selectedTheme.id === theme.id
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 hover:border-gray-300'
                  )}
                  onClick={() => handleThemeSelect(theme)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{theme.name}</h4>
                    <div className="flex gap-1">
                      {theme.colors.primary && (
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: theme.colors.primary }}
                        />
                      )}
                      {theme.colors.secondary && (
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: theme.colors.secondary }}
                        />
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">{theme.region}</p>
                  <div className="flex gap-1 mt-2">
                    {theme.symbols.slice(0, 3).map((symbol, index) => (
                      <span key={index} className="text-sm">{symbol}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Color Customization */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold">Color Scheme</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCustomColors(!customColors)}
              >
                <Settings className="h-4 w-4 mr-2" />
                {customColors ? 'Use Theme Colors' : 'Customize Colors'}
              </Button>
            </div>

            {customColors ? (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {Object.entries(selectedTheme.colors).map(([key, value]) => (
                  <div key={key}>
                    <label className="block text-sm font-medium mb-1 capitalize">
                      {key}
                    </label>
                    <Input
                      type="color"
                      value={value}
                      onChange={(e) => {
                        const newTheme = {
                          ...selectedTheme,
                          colors: {
                            ...selectedTheme.colors,
                            [key]: e.target.value
                          }
                        };
                        setSelectedTheme(newTheme);
                        onThemeChange(newTheme);
                      }}
                      className="h-10 w-full"
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex gap-2">
                {Object.entries(selectedTheme.colors).map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div
                      className="w-12 h-12 rounded-lg shadow-sm"
                      style={{ backgroundColor: value }}
                    />
                    <div className="text-xs mt-1 capitalize">{key}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Cultural Symbols */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Cultural Symbols</h3>
            <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
              {selectedTheme.symbols.map((symbol) => (
                <button
                  key={symbol}
                  className={cn(
                    'text-3xl p-3 rounded-lg border-2 transition-all hover:scale-110',
                    selectedSymbols.includes(symbol)
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-200 hover:border-gray-300'
                  )}
                  onClick={() => toggleSymbol(symbol)}
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>

          {/* Patterns */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Pattern Style</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {selectedTheme.patterns.map((pattern) => (
                <button
                  key={pattern}
                  className={cn(
                    'p-4 rounded-lg border-2 text-center transition-all',
                    selectedPattern === pattern
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-200 hover:border-gray-300'
                  )}
                  onClick={() => setSelectedPattern(pattern)}
                >
                  <div className="font-medium capitalize">{pattern}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Live Preview */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Preview</h3>
            <div
              className="p-6 rounded-lg"
              style={{
                backgroundColor: selectedTheme.colors.background,
                color: selectedTheme.colors.text
              }}
            >
              <div className="space-y-4">
                <div
                  className="p-4 rounded"
                  style={{ backgroundColor: selectedTheme.colors.primary + '20' }}
                >
                  <h4 className="font-bold" style={{ color: selectedTheme.colors.primary }}>
                    Cultural Biodata Header
                  </h4>
                </div>
                <div className="flex gap-2">
                  {selectedSymbols.slice(0, 3).map((symbol) => (
                    <span key={symbol} className="text-2xl">{symbol}</span>
                  ))}
                </div>
                <div
                  className="p-3 rounded text-center text-sm"
                  style={{ backgroundColor: selectedTheme.colors.accent + '30' }}
                >
                  Pattern: {selectedPattern || 'None selected'}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
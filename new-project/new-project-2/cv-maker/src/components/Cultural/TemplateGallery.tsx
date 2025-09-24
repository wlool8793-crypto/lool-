import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  marriageTemplates,
  professionalTemplates,
  getPopularTemplates,
  getPremiumTemplates,
  TemplateLibrary
} from '../../lib/culturalTemplateLibrary';

interface TemplateGalleryProps {
  category?: 'marriage' | 'professional';
  culture?: string;
  onTemplateSelect?: (template: TemplateLibrary) => void;
  showFilters?: boolean;
}

export const TemplateGallery: React.FC<TemplateGalleryProps> = ({
  category,
  culture,
  onTemplateSelect,
  showFilters = true
}) => {
  const { t } = useTranslation();
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'marriage' | 'professional'>(category || 'all');
  const [selectedCulture, setSelectedCulture] = useState<string>('all');
  const [priceFilter, setPriceFilter] = useState<'all' | 'free' | 'premium'>('all');
  const [sortBy, setSortBy] = useState<'popularity' | 'name' | 'recent'>('popularity');
  const [searchQuery, setSearchQuery] = useState('');

  // Get all templates based on filters
  const getFilteredTemplates = () => {
    let templates: TemplateLibrary[] = [];

    if (selectedCategory === 'all') {
      templates = [...marriageTemplates, ...professionalTemplates];
    } else if (selectedCategory === 'marriage') {
      templates = marriageTemplates;
    } else {
      templates = professionalTemplates;
    }

    // Apply culture filter
    if (selectedCulture !== 'all') {
      templates = templates.filter(t => t.culture === selectedCulture);
    }

    // Apply price filter
    if (priceFilter === 'free') {
      templates = templates.filter(t => !t.isPremium);
    } else if (priceFilter === 'premium') {
      templates = templates.filter(t => t.isPremium);
    }

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      templates = templates.filter(t =>
        t.name.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.culture.toLowerCase().includes(query) ||
        t.features.some(f => f.toLowerCase().includes(query))
      );
    }

    // Sort templates
    templates.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'recent':
          return b.id.localeCompare(a.id);
        case 'popularity':
        default:
          return b.popularity - a.popularity;
      }
    });

    return templates;
  };

  const filteredTemplates = getFilteredTemplates();
  const popularTemplates = getPopularTemplates(4);
  const premiumTemplates = getPremiumTemplates();

  // Get all available cultures
  const allTemplates = [...marriageTemplates, ...professionalTemplates];
  const cultures = [...new Set(allTemplates.map(t => t.culture))];

  const TemplateCard: React.FC<{ template: TemplateLibrary; size?: 'small' | 'medium' | 'large' }> = ({
    template,
    size = 'medium'
  }) => {
    const sizeClasses = {
      small: 'text-xs',
      medium: 'text-sm',
      large: 'text-base'
    };

    const cardClasses = {
      small: 'p-3',
      medium: 'p-4',
      large: 'p-6'
    };

    return (
      <div
        className={`bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer overflow-hidden ${cardClasses[size]}`}
        onClick={() => onTemplateSelect?.(template)}
      >
        <div className="relative mb-3">
          <div className={`h-${size === 'small' ? '16' : size === 'medium' ? '24' : '32'} bg-gradient-to-r ${
            template.category === 'marriage'
              ? size === 'small' ? 'from-red-400 to-pink-400' : 'from-red-500 to-pink-500'
              : size === 'small' ? 'from-blue-400 to-purple-400' : 'from-blue-500 to-purple-500'
          } flex items-center justify-center rounded`}>
            <div className="text-white text-center">
              <div className={`${size === 'small' ? 'text-xl' : size === 'medium' ? 'text-3xl' : 'text-4xl'} mb-1`}>
                {template.culture === 'Indian' ? '🕉️' :
                 template.culture === 'Muslim' ? '☪️' :
                 template.culture === 'Christian' ? '✝️' :
                 template.culture === 'Western' ? '🌍' : '🏛️'}
              </div>
              {size !== 'small' && (
                <div className={`${size === 'medium' ? 'text-xs' : 'text-sm'} font-medium opacity-90`}>
                  {template.name}
                </div>
              )}
            </div>
          </div>

          {template.isPremium && (
            <div className={`absolute top-1 right-1 bg-yellow-400 text-yellow-900 px-${size === 'small' ? '1' : '2'} py-${size === 'small' ? '0.5' : '1'} rounded text-xs font-bold`}>
              {size === 'small' ? 'PRO' : 'PREMIUM'}
            </div>
          )}
        </div>

        <div className="space-y-2">
          <h3 className={`font-semibold text-gray-900 line-clamp-2 ${sizeClasses[size]}`}>
            {template.name}
          </h3>

          {size !== 'small' && (
            <p className={`text-gray-600 line-clamp-2 ${sizeClasses[size]}`}>
              {template.description}
            </p>
          )}

          <div className="flex items-center justify-between">
            <span className={`text-gray-500 ${sizeClasses[size]}`}>
              {template.culture}
            </span>
            <div className="flex items-center">
              <span className="text-yellow-500">⭐</span>
              <span className={`ml-1 text-gray-600 ${sizeClasses[size]}`}>
                {template.popularity}%
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              template.category === 'marriage'
                ? 'bg-pink-100 text-pink-800'
                : 'bg-blue-100 text-blue-800'
            }`}>
              {template.category === 'marriage' ? t('marriage') : t('professional')}
            </span>

            <button
              onClick={(e) => {
                e.stopPropagation();
                onTemplateSelect?.(template);
              }}
              className={`px-2 py-1 rounded text-xs font-medium ${
                template.isPremium
                  ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
                  : 'bg-blue-500 hover:bg-blue-600 text-white'
              }`}
            >
              {template.isPremium ? t('unlock') : t('use')}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t('templateGallery')}
        </h1>
        <p className="text-gray-600">
          {t('templateGalleryDescription')}
        </p>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <input
              type="text"
              placeholder={t('searchTemplates')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            />

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            >
              <option value="all">{t('allCategories')}</option>
              <option value="marriage">{t('marriageTemplates')}</option>
              <option value="professional">{t('professionalTemplates')}</option>
            </select>

            <select
              value={selectedCulture}
              onChange={(e) => setSelectedCulture(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            >
              <option value="all">{t('allCultures')}</option>
              {cultures.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>

            <select
              value={priceFilter}
              onChange={(e) => setPriceFilter(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            >
              <option value="all">{t('allPrices')}</option>
              <option value="free">{t('freeOnly')}</option>
              <option value="premium">{t('premiumOnly')}</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            >
              <option value="popularity">{t('mostPopular')}</option>
              <option value="name">{t('alphabetical')}</option>
              <option value="recent">{t('mostRecent')}</option>
            </select>
          </div>

          <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
            <span>{filteredTemplates.length} {t('templatesFound')}</span>
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory(category || 'all');
                setSelectedCulture('all');
                setPriceFilter('all');
                setSortBy('popularity');
              }}
              className="text-blue-600 hover:text-blue-800"
            >
              {t('clearFilters')}
            </button>
          </div>
        </div>
      )}

      {/* Featured Sections */}
      <div className="space-y-8">
        {/* Popular Templates */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">{t('popularTemplates')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {popularTemplates.map(template => (
              <TemplateCard key={template.id} template={template} size="medium" />
            ))}
          </div>
        </div>

        {/* Premium Templates */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold text-gray-900">{t('premiumTemplates')}</h2>
            <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
              {t('exclusiveDesigns')}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {premiumTemplates.slice(0, 3).map(template => (
              <TemplateCard key={template.id} template={template} size="large" />
            ))}
          </div>
        </div>

        {/* Marriage Templates */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">{t('marriageBiodataTemplates')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {marriageTemplates.slice(0, 4).map(template => (
              <TemplateCard key={template.id} template={template} size="medium" />
            ))}
          </div>
        </div>

        {/* Professional Templates */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">{t('professionalCvTemplates')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {professionalTemplates.slice(0, 2).map(template => (
              <TemplateCard key={template.id} template={template} size="large" />
            ))}
          </div>
        </div>

        {/* All Templates */}
        {filteredTemplates.length > 0 ? (
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              {selectedCategory === 'all' ? t('allTemplates') :
               selectedCategory === 'marriage' ? t('marriageTemplates') : t('professionalTemplates')}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {filteredTemplates.map(template => (
                <TemplateCard key={template.id} template={template} size="medium" />
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📄</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">{t('noTemplatesFound')}</h3>
            <p className="text-gray-600">{t('tryDifferentSearch')}</p>
          </div>
        )}
      </div>

      {/* Culture Categories */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">{t('browseByCulture')}</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {cultures.map(culture => (
            <button
              key={culture}
              onClick={() => setSelectedCulture(culture)}
              className={`p-4 rounded-lg border-2 text-center transition-colors ${
                selectedCulture === culture
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-2">
                {culture === 'Indian' ? '🕉️' :
                 culture === 'Muslim' ? '☪️' :
                 culture === 'Christian' ? '✝️' :
                 culture === 'Western' ? '🌍' : '🏛️'}
              </div>
              <div className="text-sm font-medium text-gray-900">{culture}</div>
              <div className="text-xs text-gray-600">
                {allTemplates.filter(t => t.culture === culture).length} {t('templates')}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TemplateGallery;
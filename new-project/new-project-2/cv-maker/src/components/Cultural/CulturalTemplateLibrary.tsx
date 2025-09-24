import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  marriageTemplates,
  professionalTemplates,
  getTemplateById,
  getTemplatesByCategory,
  getPremiumTemplates,
  getPopularTemplates,
  getRecommendedTemplates,
  searchTemplates,
  getTemplateStatistics,
  TemplateLibrary
} from '../../lib/culturalTemplateLibrary';

interface CulturalTemplateLibraryProps {
  category: 'marriage' | 'professional';
  userData?: {
    culture?: string;
    religion?: string;
    region?: string;
  };
  onTemplateSelect?: (template: TemplateLibrary) => void;
}

export const CulturalTemplateLibrary: React.FC<CulturalTemplateLibraryProps> = ({
  category,
  userData,
  onTemplateSelect
}) => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'marriage' | 'professional'>(category);
  const [selectedCulture, setSelectedCulture] = useState<string>('all');
  const [showPremiumOnly, setShowPremiumOnly] = useState(false);
  const [sortBy, setSortBy] = useState<'popularity' | 'name' | 'recent'>('popularity');
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateLibrary | null>(null);

  // Get all available cultures
  const allTemplates = [...marriageTemplates, ...professionalTemplates];
  const cultures = [...new Set(allTemplates.map(t => t.culture))];

  // Filter and sort templates
  const getFilteredTemplates = () => {
    let templates: TemplateLibrary[] = [];

    if (selectedCategory === 'all') {
      templates = allTemplates;
    } else {
      templates = getTemplatesByCategory(selectedCategory);
    }

    if (selectedCulture !== 'all') {
      templates = templates.filter(t => t.culture === selectedCulture);
    }

    if (showPremiumOnly) {
      templates = templates.filter(t => t.isPremium);
    }

    if (searchQuery.trim()) {
      templates = searchTemplates(searchQuery, {
        category: selectedCategory === 'all' ? undefined : selectedCategory,
        culture: selectedCulture === 'all' ? undefined : selectedCulture,
        isPremium: showPremiumOnly ? true : undefined
      });
    }

    // Sort templates
    templates.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'recent':
          return b.id.localeCompare(a.id); // Simple ID-based sorting
        case 'popularity':
        default:
          return b.popularity - a.popularity;
      }
    });

    return templates;
  };

  const filteredTemplates = getFilteredTemplates();
  const recommendedTemplates = userData ? getRecommendedTemplates({ ...userData, category }) : [];
  const popularTemplates = getPopularTemplates(6);

  const statistics = getTemplateStatistics();

  const handleTemplateClick = (template: TemplateLibrary) => {
    setSelectedTemplate(template);
  };

  const handleUseTemplate = (template: TemplateLibrary) => {
    if (onTemplateSelect) {
      onTemplateSelect(template);
    }
  };

  const TemplateCard: React.FC<{ template: TemplateLibrary }> = ({ template }) => (
    <div
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 overflow-hidden"
      onClick={() => handleTemplateClick(template)}
    >
      <div className="relative">
        <div className={`h-32 bg-gradient-to-r ${template.category === 'marriage' ? 'from-red-500 to-pink-500' : 'from-blue-500 to-purple-500'} flex items-center justify-center`}>
          <div className="text-white text-center">
            <div className="text-2xl mb-1">{template.culture === 'Indian' ? '🕉️' : template.culture === 'Muslim' ? '☪️' : template.culture === 'Christian' ? '✝️' : '🌍'}</div>
            <div className="text-sm font-medium">{template.name}</div>
          </div>
        </div>
        {template.isPremium && (
          <div className="absolute top-2 right-2 bg-yellow-400 text-yellow-900 px-2 py-1 rounded text-xs font-bold">
            PREMIUM
          </div>
        )}
      </div>

      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-500">{template.culture}</span>
          <div className="flex items-center">
            <span className="text-yellow-500">⭐</span>
            <span className="text-sm text-gray-600 ml-1">{template.popularity}%</span>
          </div>
        </div>

        <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2">{template.name}</h3>
        <p className="text-sm text-gray-600 mb-3 line-clamp-3">{template.description}</p>

        <div className="flex flex-wrap gap-1 mb-3">
          {template.features.slice(0, 3).map((feature, index) => (
            <span key={index} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
              {feature}
            </span>
          ))}
          {template.features.length > 3 && (
            <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
              +{template.features.length - 3} more
            </span>
          )}
        </div>

        <div className="flex items-center justify-between">
          <span className={`text-xs font-medium px-2 py-1 rounded ${
            template.category === 'marriage' ? 'bg-pink-100 text-pink-800' : 'bg-blue-100 text-blue-800'
          }`}>
            {template.category === 'marriage' ? t('marriageBiodata') : t('professionalCv')}
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleUseTemplate(template);
            }}
            className={`px-3 py-1 rounded text-sm font-medium ${
              template.isPremium
                ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {template.isPremium ? t('unlock') : t('useTemplate')}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t('culturalTemplateLibrary')}
        </h1>
        <p className="text-gray-600 mb-4">
          {t('culturalTemplateLibraryDescription')}
        </p>

        {/* Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="text-2xl font-bold text-blue-600">{statistics.total}</div>
            <div className="text-sm text-gray-600">{t('totalTemplates')}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="text-2xl font-bold text-green-600">{statistics.cultures}</div>
            <div className="text-sm text-gray-600">{t('culturesSupported')}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="text-2xl font-bold text-purple-600">{statistics.premium}</div>
            <div className="text-sm text-gray-600">{t('premiumTemplates')}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="text-2xl font-bold text-orange-600">{Math.round(statistics.averagePopularity)}%</div>
            <div className="text-sm text-gray-600">{t('averageRating')}</div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div className="md:col-span-2">
            <input
              type="text"
              placeholder={t('searchTemplates')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value as any)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">{t('allCategories')}</option>
            <option value="marriage">{t('marriageBiodata')}</option>
            <option value="professional">{t('professionalCv')}</option>
          </select>
          <select
            value={selectedCulture}
            onChange={(e) => setSelectedCulture(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">{t('allCultures')}</option>
            {cultures.map(culture => (
              <option key={culture} value={culture}>{culture}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={showPremiumOnly}
              onChange={(e) => setShowPremiumOnly(e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm">{t('premiumOnly')}</span>
          </label>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-1 border border-gray-300 rounded text-sm"
          >
            <option value="popularity">{t('sortByPopularity')}</option>
            <option value="name">{t('sortByName')}</option>
            <option value="recent">{t('sortByRecent')}</option>
          </select>

          <div className="text-sm text-gray-600">
            {filteredTemplates.length} {t('templatesFound')}
          </div>
        </div>
      </div>

      {/* Recommended Templates */}
      {recommendedTemplates.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">{t('recommendedForYou')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recommendedTemplates.slice(0, 3).map(template => (
              <TemplateCard key={template.id} template={template} />
            ))}
          </div>
        </div>
      )}

      {/* Popular Templates */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">{t('popularTemplates')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {popularTemplates.map(template => (
            <TemplateCard key={template.id} template={template} />
          ))}
        </div>
      </div>

      {/* All Templates */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          {selectedCategory === 'all' ? t('allTemplates') :
           selectedCategory === 'marriage' ? t('marriageTemplates') : t('professionalTemplates')}
        </h2>

        {filteredTemplates.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📄</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">{t('noTemplatesFound')}</h3>
            <p className="text-gray-600">{t('tryDifferentFilters')}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {filteredTemplates.map(template => (
              <TemplateCard key={template.id} template={template} />
            ))}
          </div>
        )}
      </div>

      {/* Template Detail Modal */}
      {selectedTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedTemplate.name}</h2>
                  <p className="text-gray-600">{selectedTemplate.culture} • {selectedTemplate.category}</p>
                </div>
                <button
                  onClick={() => setSelectedTemplate(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className={`h-48 mb-4 rounded-lg bg-gradient-to-r ${
                selectedTemplate.category === 'marriage' ? 'from-red-500 to-pink-500' : 'from-blue-500 to-purple-500'
              } flex items-center justify-center`}>
                <div className="text-white text-center">
                  <div className="text-6xl mb-2">
                    {selectedTemplate.culture === 'Indian' ? '🕉️' :
                     selectedTemplate.culture === 'Muslim' ? '☪️' :
                     selectedTemplate.culture === 'Christian' ? '✝️' : '🌍'}
                  </div>
                  <div className="text-lg font-medium">{selectedTemplate.name}</div>
                </div>
              </div>

              <div className="mb-4">
                <h3 className="font-semibold text-gray-900 mb-2">{t('description')}</h3>
                <p className="text-gray-700">{selectedTemplate.description}</p>
              </div>

              <div className="mb-4">
                <h3 className="font-semibold text-gray-900 mb-2">{t('features')}</h3>
                <div className="grid grid-cols-2 gap-2">
                  {selectedTemplate.features.map((feature, index) => (
                    <div key={index} className="flex items-center text-sm text-gray-700">
                      <span className="text-green-500 mr-2">✓</span>
                      {feature}
                    </div>
                  ))}
                </div>
              </div>

              <div className="mb-4">
                <h3 className="font-semibold text-gray-900 mb-2">{t('customizations')}</h3>
                <div className="space-y-2">
                  {selectedTemplate.customizations.map((customization, index) => (
                    <div key={index} className="text-sm text-gray-700">
                      <span className="font-medium">{customization.name}:</span> {customization.description}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    <span className="text-yellow-500">⭐</span>
                    <span className="ml-1 font-medium">{selectedTemplate.popularity}%</span>
                  </div>
                  {selectedTemplate.isPremium && (
                    <span className="bg-yellow-400 text-yellow-900 px-2 py-1 rounded text-xs font-bold">
                      PREMIUM
                    </span>
                  )}
                </div>
                <button
                  onClick={() => handleUseTemplate(selectedTemplate)}
                  className={`px-6 py-2 rounded-lg font-medium ${
                    selectedTemplate.isPremium
                      ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
                >
                  {selectedTemplate.isPremium ? t('unlockPremium') : t('useThisTemplate')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CulturalTemplateLibrary;
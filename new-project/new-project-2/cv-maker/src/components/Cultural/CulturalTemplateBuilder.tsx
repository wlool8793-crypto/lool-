import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { MarriageBiodata } from '../../types/marriage';
import {
  culturalTemplateRegistry,
  getCulturalTemplate,
  TemplateCustomization
} from '../../lib/culturalTemplateLibrary';

interface CulturalTemplateBuilderProps {
  data: MarriageBiodata;
  templateId: string;
  onCustomizationChange?: (customizations: Record<string, any>) => void;
  onTemplateExport?: (format: 'pdf' | 'image') => void;
}

export const CulturalTemplateBuilder: React.FC<CulturalTemplateBuilderProps> = ({
  data,
  templateId,
  onCustomizationChange,
  onTemplateExport
}) => {
  const { t } = useTranslation();
  const [customizations, setCustomizations] = useState<Record<string, any>>({});
  const [activeSection, setActiveSection] = useState('customize');
  const [isExporting, setIsExporting] = useState(false);

  const template = getCulturalTemplate(templateId);

  if (!template) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 text-6xl mb-4">❌</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">{t('templateNotFound')}</h3>
        <p className="text-gray-600">{t('templateNotFoundDescription')}</p>
      </div>
    );
  }

  const handleCustomizationChange = (name: string, value: string) => {
    const newCustomizations = { ...customizations, [name]: value };
    setCustomizations(newCustomizations);
    if (onCustomizationChange) {
      onCustomizationChange(newCustomizations);
    }
  };

  const handleExport = async (format: 'pdf' | 'image') => {
    setIsExporting(true);
    try {
      if (onTemplateExport) {
        await onTemplateExport(format);
      }
      // Here you would implement actual export functionality
      console.log(`Exporting template as ${format}`, { data, customizations });
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const applyCustomizationStyles = () => {
    const styles: React.CSSProperties = {};

    template.customizations.forEach(customization => {
      if (customization.type === 'color' && customizations[customization.name]) {
        if (customization.name.toLowerCase().includes('primary')) {
          styles['--primary-color'] = customizations[customization.name];
        } else if (customization.name.toLowerCase().includes('secondary')) {
          styles['--secondary-color'] = customizations[customization.name];
        } else if (customization.name.toLowerCase().includes('background')) {
          styles['--background-color'] = customizations[customization.name];
        }
      }
    });

    return styles;
  };

  const HeaderSection = template.components.header;
  const PersonalSection = template.components.personal;
  const FamilySection = template.components.family;
  const HoroscopeSection = template.components.horoscope;
  const FooterSection = template.components.footer;

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t('templateBuilder')}
        </h1>
        <p className="text-gray-600">
          {t('templateBuilderDescription')} - {template.name}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Customization Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border p-6 sticky top-6">
            <div className="flex space-x-1 mb-4">
              <button
                onClick={() => setActiveSection('customize')}
                className={`flex-1 py-2 px-3 rounded text-sm font-medium ${
                  activeSection === 'customize'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {t('customize')}
              </button>
              <button
                onClick={() => setActiveSection('export')}
                className={`flex-1 py-2 px-3 rounded text-sm font-medium ${
                  activeSection === 'export'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {t('export')}
              </button>
            </div>

            {activeSection === 'customize' && (
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">{t('customizationOptions')}</h3>

                {template.customizations.map((customization, index) => (
                  <div key={index} className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700">
                      {customization.name}
                    </label>
                    <p className="text-xs text-gray-500">{customization.description}</p>

                    {customization.type === 'color' && (
                      <div className="grid grid-cols-3 gap-2">
                        {customization.options.map((color, colorIndex) => (
                          <button
                            key={colorIndex}
                            onClick={() => handleCustomizationChange(customization.name, color)}
                            className={`w-full h-8 rounded border-2 ${
                              customizations[customization.name] === color
                                ? 'border-gray-900'
                                : 'border-gray-300'
                            }`}
                            style={{ backgroundColor: color }}
                            title={color}
                          />
                        ))}
                      </div>
                    )}

                    {customization.type === 'font' && (
                      <select
                        value={customizations[customization.name] || customization.defaultValue}
                        onChange={(e) => handleCustomizationChange(customization.name, e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                      >
                        {customization.options.map((option, optionIndex) => (
                          <option key={optionIndex} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    )}

                    {customization.type === 'layout' && (
                      <select
                        value={customizations[customization.name] || customization.defaultValue}
                        onChange={(e) => handleCustomizationChange(customization.name, e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                      >
                        {customization.options.map((option, optionIndex) => (
                          <option key={optionIndex} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    )}
                  </div>
                ))}

                <div className="pt-4 border-t">
                  <button
                    onClick={() => setCustomizations({})}
                    className="w-full py-2 px-4 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm font-medium"
                  >
                    {t('resetCustomizations')}
                  </button>
                </div>
              </div>
            )}

            {activeSection === 'export' && (
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">{t('exportOptions')}</h3>

                <div className="space-y-3">
                  <button
                    onClick={() => handleExport('pdf')}
                    disabled={isExporting}
                    className="w-full py-3 px-4 bg-red-600 text-white rounded hover:bg-red-700 font-medium disabled:opacity-50"
                  >
                    {isExporting ? t('exporting') : t('exportAsPDF')}
                  </button>

                  <button
                    onClick={() => handleExport('image')}
                    disabled={isExporting}
                    className="w-full py-3 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium disabled:opacity-50"
                  >
                    {isExporting ? t('exporting') : t('exportAsImage')}
                  </button>

                  <button
                    onClick={() => {
                      const html = document.getElementById('template-preview')?.innerHTML;
                      if (html) {
                        navigator.clipboard.writeText(html);
                        alert(t('htmlCopied'));
                      }
                    }}
                    className="w-full py-3 px-4 bg-green-600 text-white rounded hover:bg-green-700 font-medium"
                  >
                    {t('copyHTML')}
                  </button>
                </div>

                <div className="pt-4 border-t">
                  <h4 className="font-medium text-gray-900 mb-2">{t('exportSettings')}</h4>
                  <div className="space-y-2 text-sm">
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      {t('includeWatermark')}
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      {t('highQuality')}
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      {t('compressForWeb')}
                    </label>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Template Preview */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{t('templatePreview')}</h3>
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    // Zoom functionality
                    const preview = document.getElementById('template-preview');
                    if (preview) {
                      const currentScale = parseFloat(preview.style.transform?.replace('scale(', '')?.replace(')', '') || '1');
                      const newScale = Math.min(currentScale + 0.1, 2);
                      preview.style.transform = `scale(${newScale})`;
                    }
                  }}
                  className="p-2 bg-gray-100 rounded hover:bg-gray-200"
                >
                  🔍+
                </button>
                <button
                  onClick={() => {
                    const preview = document.getElementById('template-preview');
                    if (preview) {
                      const currentScale = parseFloat(preview.style.transform?.replace('scale(', '')?.replace(')', '') || '1');
                      const newScale = Math.max(currentScale - 0.1, 0.5);
                      preview.style.transform = `scale(${newScale})`;
                    }
                  }}
                  className="p-2 bg-gray-100 rounded hover:bg-gray-200"
                >
                  🔍-
                </button>
              </div>
            </div>

            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 overflow-auto">
              <div
                id="template-preview"
                className="transition-transform duration-200"
                style={applyCustomizationStyles()}
              >
                {/* Header */}
                <div className="mb-6">
                  <HeaderSection data={data} customizations={customizations} />
                </div>

                {/* Personal Information */}
                <div className="mb-6">
                  <PersonalSection data={data} customizations={customizations} />
                </div>

                {/* Family Information */}
                <div className="mb-6">
                  <FamilySection data={data} customizations={customizations} />
                </div>

                {/* Horoscope Information */}
                <div className="mb-6">
                  <HoroscopeSection data={data} customizations={customizations} />
                </div>

                {/* Footer */}
                <div>
                  <FooterSection data={data} customizations={customizations} />
                </div>
              </div>
            </div>

            {/* Template Info */}
            <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
              <div className="bg-gray-50 p-3 rounded">
                <span className="font-medium text-gray-700">{t('templateName')}:</span>
                <span className="ml-2 text-gray-600">{template.name}</span>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <span className="font-medium text-gray-700">{t('culture')}:</span>
                <span className="ml-2 text-gray-600">{template.culture}</span>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <span className="font-medium text-gray-700">{t('customizationsApplied')}:</span>
                <span className="ml-2 text-gray-600">{Object.keys(customizations).length}</span>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <span className="font-medium text-gray-700">{t('lastModified')}:</span>
                <span className="ml-2 text-gray-600">{new Date().toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CulturalTemplateBuilder;
import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Button } from '../../common/Button';
import { Share2 } from 'lucide-react';
import { TraditionalTemplate, ModernTraditionalTemplate, MinimalContemporaryTemplate } from '../../CVTemplates/Marriage';
import { MarriagePDFGenerator } from '../../../utils/marriagePDFGenerator';
import { SharingPanel } from '../../common/SharingPanel';

export const MarriagePreviewStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [selectedTemplate, setSelectedTemplate] = React.useState('traditional');
  const [isExporting, setIsExporting] = React.useState(false);
  const [showSharing, setShowSharing] = React.useState(false);
  const previewRef = React.useRef<HTMLDivElement>(null);

  const handleTemplateChange = (template: string) => {
    setSelectedTemplate(template);
    dispatch({ type: 'SET_TEMPLATE', payload: template });
  };

  const handleBack = () => {
    dispatch({ type: 'PREVIOUS_STEP' });
  };

  const handleExport = async () => {
    if (!previewRef.current || !state.marriageData) {
      alert('Unable to generate PDF. Please ensure all data is filled correctly.');
      return;
    }

    setIsExporting(true);
    try {
      console.log('🚀 [Export] Starting PDF generation...');

      await MarriagePDFGenerator.downloadPDF(
        previewRef.current,
        state.marriageData,
        undefined,
        {
          template: selectedTemplate as any,
          quality: 'high',
          includeWatermark: true,
          language: 'en'
        }
      );

      console.log('✅ [Export] PDF generated and downloaded successfully');

    } catch (error) {
      console.error('❌ [Export] PDF generation failed:', error);
      alert(`Failed to generate PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handlePreview = async () => {
    if (!previewRef.current || !state.marriageData) {
      alert('Unable to preview PDF. Please ensure all data is filled correctly.');
      return;
    }

    setIsExporting(true);
    try {
      console.log('👁️ [Preview] Starting PDF preview...');

      await MarriagePDFGenerator.previewPDF(
        previewRef.current,
        state.marriageData,
        {
          template: selectedTemplate as any,
          quality: 'high',
          includeWatermark: true,
          language: 'en'
        }
      );

      console.log('✅ [Preview] PDF preview opened successfully');

    } catch (error) {
      console.error('❌ [Preview] PDF preview failed:', error);
      alert(`Failed to preview PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handleSaveAndComplete = () => {
    dispatch({ type: 'MARK_AS_SAVED' });
    alert('Marriage biodata saved successfully!');
  };

  const getTemplateComponent = () => {
    switch (selectedTemplate) {
      case 'traditional':
        return <TraditionalTemplate data={state.marriageData} />;
      case 'modern':
        return <ModernTraditionalTemplate data={state.marriageData} />;
      case 'minimal':
        return <MinimalContemporaryTemplate data={state.marriageData} />;
      default:
        return <TraditionalTemplate data={state.marriageData} />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Marriage Biodata Preview</h2>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Template Selection & Sharing */}
        <div className="xl:col-span-1 space-y-6">
          {/* Template Selection */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Choose Template</h3>
            <div className="space-y-3">
              {[
                { id: 'traditional', name: 'Traditional', description: 'Classic marriage biodata format' },
                { id: 'modern', name: 'Modern Traditional', description: 'Contemporary design with traditional elements' },
                { id: 'minimal', name: 'Minimal Contemporary', description: 'Clean and minimalist design' },
              ].map(template => (
                <button
                  key={template.id}
                  type="button"
                  onClick={() => handleTemplateChange(template.id)}
                  className={`w-full p-3 text-left rounded-md border transition-colors ${
                    selectedTemplate === template.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="font-medium">{template.name}</div>
                  <div className="text-sm text-gray-600 mt-1">{template.description}</div>
                </button>
              ))}
            </div>

            <div className="mt-6 space-y-3">
              <Button
                type="button"
                variant="outline"
                onClick={handleBack}
                className="w-full"
              >
                Back to Edit
              </Button>
              <Button
                type="button"
                onClick={handleExport}
                className="w-full"
              >
                Export as PDF
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={handlePreview}
                className="w-full"
                disabled={isExporting}
              >
                {isExporting ? 'Generating Preview...' : 'Preview PDF'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowSharing(!showSharing)}
                className="w-full"
              >
                <Share2 className="w-4 h-4 mr-2" />
                {showSharing ? 'Hide Sharing' : 'Share Biodata'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={handleSaveAndComplete}
                className="w-full"
              >
                Save and Complete
              </Button>
            </div>

            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
              <h4 className="font-semibold text-green-900 mb-2">Preview Tips</h4>
              <ul className="text-sm text-green-800 space-y-1">
                <li>• Review all information for accuracy</li>
                <li>• Check spelling and grammar</li>
                <li>• Ensure photos are clear and appropriate</li>
                <li>• Verify contact information</li>
                <li>• Make sure you're happy with the template</li>
              </ul>
            </div>
          </div>

          {/* Sharing Panel */}
          {showSharing && state.marriageData && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <SharingPanel
                element={previewRef.current}
                data={state.marriageData}
                template={selectedTemplate}
                onShare={(method) => console.log(`Shared via: ${method}`)}
              />
            </div>
          )}
        </div>

        {/* Preview Area */}
        <div className="xl:col-span-2">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="mb-4 flex justify-between items-center">
              <h3 className="text-lg font-semibold">Live Preview</h3>
              <div className="text-sm text-gray-500">
                Template: {selectedTemplate.charAt(0).toUpperCase() + selectedTemplate.slice(1)}
              </div>
            </div>

            <div
              ref={previewRef}
              className="border border-gray-200 rounded-lg p-4 bg-white min-h-[600px] overflow-auto"
            >
              {getTemplateComponent()}
            </div>

            <div className="mt-4 text-sm text-gray-600">
              <p>This is a preview of your marriage biodata. Click "Export as PDF" to download or "Save and Complete" to finish.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
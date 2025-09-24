import React, { useState, lazy, Suspense } from 'react';
import { useCV } from '@/contexts/CVContext';
import { useToast } from '@/contexts/ToastContext';
import type { FormStep } from '@/types/cv';
import { validateStep } from '@/utils/validation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Eye, Download, ArrowLeft, FileText } from 'lucide-react';
import { exportToPDF } from '@/utils/pdfExport';

// Lazy load templates for better performance
const ModernTemplate = lazy(() => import('@/components/CVTemplates/ModernTemplate').then(module => ({ default: module.ModernTemplate })));
const TraditionalTemplate = lazy(() => import('@/components/CVTemplates/TraditionalTemplate').then(module => ({ default: module.TraditionalTemplate })));
const MinimalTemplate = lazy(() => import('@/components/CVTemplates/MinimalTemplate').then(module => ({ default: module.MinimalTemplate })));

// Template loading fallback component
const TemplateLoader = () => (
  <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
    <div className="text-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
      <p className="text-gray-600">Loading template...</p>
    </div>
  </div>
);

type TemplateType = 'modern' | 'traditional' | 'minimal';

const templateOptions = [
  {
    id: 'modern' as TemplateType,
    name: 'Modern',
    description: 'Clean, professional design with gradient headers',
    component: ModernTemplate,
  },
  {
    id: 'traditional' as TemplateType,
    name: 'Traditional',
    description: 'Classic, formal design with borders and structured layout',
    component: TraditionalTemplate,
  },
  {
    id: 'minimal' as TemplateType,
    name: 'Minimal',
    description: 'Simple, clean design with minimal styling',
    component: MinimalTemplate,
  },
];

export const PreviewStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const { showToast } = useToast();
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateType>(state.selectedTemplate || 'modern');
  const [isExporting, setIsExporting] = useState(false);

  const handleTemplateChange = (template: TemplateType) => {
    setSelectedTemplate(template);
    dispatch({ type: 'UPDATE_SETTINGS', payload: { template } });
  };

  const handleExportPDF = async () => {
    // Validate that all required sections are completed
    const validation = validateStep('preview', state.cvData);
    if (!validation.isValid) {
      showToast('Please complete all required sections before exporting', 'error');
      return;
    }

    setIsExporting(true);
    try {
      await exportToPDF(`${state.cvData.personalInfo.fullName || 'CV'}_${selectedTemplate}`);
      showToast('PDF exported successfully!', 'success');
    } catch (error) {
      console.error('Failed to export PDF:', error);
      showToast('Failed to export PDF. Please try again.', 'error');
    } finally {
      setIsExporting(false);
    }
  };

  const handlePrevious = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'languages' });
  };

  const handleEdit = (step: FormStep) => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: step });
  };

  const selectedTemplateData = templateOptions.find(t => t.id === selectedTemplate);
  const TemplateComponent = selectedTemplateData?.component || ModernTemplate;

  const getSectionStatus = (section: string) => {
    switch (section) {
      case 'personal':
        return state.cvData.personalInfo.fullName ? 'completed' : 'missing';
      case 'summary':
        return state.cvData.professionalSummary ? 'completed' : 'missing';
      case 'experience':
        return state.cvData.workExperience.length > 0 ? 'completed' : 'missing';
      case 'education':
        return state.cvData.education.length > 0 ? 'completed' : 'missing';
      case 'skills':
        return state.cvData.skills.length > 0 ? 'completed' : 'missing';
      case 'projects':
        return state.cvData.projects.length > 0 ? 'completed' : 'missing';
      case 'certifications':
        return state.cvData.certifications.length > 0 ? 'completed' : 'missing';
      case 'languages':
        return state.cvData.languages.length > 0 ? 'completed' : 'missing';
      default:
        return 'missing';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'missing':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            CV Preview & Export
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Template Selection */}
            <div className="lg:w-1/3 space-y-4">
              <h3 className="text-lg font-semibold">Choose Template</h3>
              <div className="space-y-3">
                {templateOptions.map((template) => (
                  <Card
                    key={template.id}
                    className={`cursor-pointer transition-all ${
                      selectedTemplate === template.id
                        ? 'ring-2 ring-blue-500 bg-blue-50'
                        : 'hover:shadow-md'
                    }`}
                    onClick={() => handleTemplateChange(template.id)}
                  >
                    <CardContent className="p-4">
                      <h4 className="font-medium mb-1">{template.name}</h4>
                      <p className="text-sm text-gray-600">{template.description}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Export Controls */}
              <div className="space-y-3 pt-4">
                <Button
                  onClick={handleExportPDF}
                  disabled={isExporting}
                  className="w-full"
                >
                  <Download className="h-4 w-4 mr-2" />
                  {isExporting ? 'Exporting...' : 'Export to PDF'}
                </Button>
                <Button
                  onClick={handlePrevious}
                  variant="outline"
                  className="w-full"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Languages
                </Button>
              </div>

              {/* Section Status */}
              <div className="space-y-3 pt-4">
                <h3 className="text-lg font-semibold">CV Sections</h3>
                <div className="space-y-2">
                  {[
                    { id: 'personal', name: 'Personal Info', step: 'personal' as FormStep },
                    { id: 'summary', name: 'Summary', step: 'summary' as FormStep },
                    { id: 'experience', name: 'Experience', step: 'experience' as FormStep },
                    { id: 'education', name: 'Education', step: 'education' as FormStep },
                    { id: 'skills', name: 'Skills', step: 'skills' as FormStep },
                    { id: 'projects', name: 'Projects', step: 'projects' as FormStep },
                    { id: 'certifications', name: 'Certifications', step: 'certifications' as FormStep },
                    { id: 'languages', name: 'Languages', step: 'languages' as FormStep },
                  ].map((section) => (
                    <div
                      key={section.id}
                      className="flex items-center justify-between p-2 rounded hover:bg-gray-50 cursor-pointer"
                      onClick={() => handleEdit(section.step)}
                    >
                      <span className="text-sm font-medium">{section.name}</span>
                      <span className={`text-xs ${getStatusColor(getSectionStatus(section.id))}`}>
                        {getSectionStatus(section.id) === 'completed' ? '✓ Complete' : '✗ Missing'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Preview */}
            <div className="lg:w-2/3">
              <div className="sticky top-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      {selectedTemplateData?.name} Template Preview
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="border rounded-lg overflow-hidden bg-white">
                      <div className="transform scale-50 origin-top-left w-[200%]">
                        <Suspense fallback={<TemplateLoader />}>
                          <TemplateComponent data={state.cvData} />
                        </Suspense>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
import { PDFUtils, PDFMetadata, PDFSecurityOptions, WatermarkOptions } from './pdfUtils';
import { CVData } from '../types/cv';
import { MarriageBiodata } from '../types/marriage';

export interface TemplateStyleConfig {
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    text: string;
  };
  fonts: {
    heading: string;
    body: string;
    accent: string;
  };
  spacing: {
    section: number;
    subsection: number;
    item: number;
  };
  layout: {
    headerHeight: number;
    sectionMargin: number;
    columnLayout: boolean;
  };
}

export interface TemplatePDFConfig {
  quality: number;
  margins: string;
  dpi: number;
  format: 'A4' | 'A3' | 'Letter';
  orientation: 'portrait' | 'landscape';
  templateStyle: TemplateStyleConfig;
  customStyles?: string;
  includePageNumbers?: boolean;
  includeHeaderFooter?: boolean;
}

export class TemplatePDFGenerator {
  private static getTemplateStyles(templateId: string): TemplateStyleConfig {
    const styles: Record<string, TemplateStyleConfig> = {
      minimal: {
        colors: {
          primary: '#2563eb',
          secondary: '#64748b',
          accent: '#0f172a',
          background: '#ffffff',
          text: '#1e293b'
        },
        fonts: {
          heading: 'Inter, sans-serif',
          body: 'Inter, sans-serif',
          accent: 'Georgia, serif'
        },
        spacing: {
          section: 24,
          subsection: 16,
          item: 8
        },
        layout: {
          headerHeight: 120,
          sectionMargin: 20,
          columnLayout: false
        }
      },
      modern: {
        colors: {
          primary: '#7c3aed',
          secondary: '#6b7280',
          accent: '#4c1d95',
          background: '#ffffff',
          text: '#111827'
        },
        fonts: {
          heading: 'Poppins, sans-serif',
          body: 'Poppins, sans-serif',
          accent: 'Playfair Display, serif'
        },
        spacing: {
          section: 32,
          subsection: 20,
          item: 12
        },
        layout: {
          headerHeight: 140,
          sectionMargin: 24,
          columnLayout: true
        }
      },
      traditional: {
        colors: {
          primary: '#1e293b',
          secondary: '#64748b',
          accent: '#0f172a',
          background: '#ffffff',
          text: '#334155'
        },
        fonts: {
          heading: 'Times New Roman, serif',
          body: 'Times New Roman, serif',
          accent: 'Times New Roman, serif'
        },
        spacing: {
          section: 28,
          subsection: 18,
          item: 10
        },
        layout: {
          headerHeight: 100,
          sectionMargin: 22,
          columnLayout: false
        }
      },
      marriage_elegant: {
        colors: {
          primary: '#be185d',
          secondary: '#64748b',
          accent: '#831843',
          background: '#fef7ff',
          text: '#1e293b'
        },
        fonts: {
          heading: 'Playfair Display, serif',
          body: 'Lato, sans-serif',
          accent: 'Dancing Script, cursive'
        },
        spacing: {
          section: 30,
          subsection: 20,
          item: 12
        },
        layout: {
          headerHeight: 160,
          sectionMargin: 25,
          columnLayout: false
        }
      },
      marriage_modern: {
        colors: {
          primary: '#f59e0b',
          secondary: '#6b7280',
          accent: '#d97706',
          background: '#fffbeb',
          text: '#111827'
        },
        fonts: {
          heading: 'Montserrat, sans-serif',
          body: 'Montserrat, sans-serif',
          accent: 'Pacifico, cursive'
        },
        spacing: {
          section: 32,
          subsection: 18,
          item: 10
        },
        layout: {
          headerHeight: 150,
          sectionMargin: 20,
          columnLayout: true
        }
      },
      marriage_traditional: {
        colors: {
          primary: '#dc2626',
          secondary: '#64748b',
          accent: '#991b1b',
          background: '#fef2f2',
          text: '#1e293b'
        },
        fonts: {
          heading: 'Times New Roman, serif',
          body: 'Times New Roman, serif',
          accent: 'Brush Script MT, cursive'
        },
        spacing: {
          section: 28,
          subsection: 16,
          item: 8
        },
        layout: {
          headerHeight: 140,
          sectionMargin: 18,
          columnLayout: false
        }
      }
    };

    return styles[templateId] || styles.minimal;
  }

  static async generateCVPDF(
    elementId: string,
    cvData: CVData,
    templateId: string,
    config: Partial<TemplatePDFConfig> = {},
    filename: string = 'cv.pdf',
    metadata?: PDFMetadata,
    security?: PDFSecurityOptions,
    watermark?: WatermarkOptions
  ): Promise<void> {
    const templateStyle = this.getTemplateStyles(templateId);
    const finalConfig: TemplatePDFConfig = {
      quality: 0.95,
      margins: '20mm',
      dpi: 300,
      format: 'A4',
      orientation: 'portrait',
      templateStyle,
      includePageNumbers: true,
      includeHeaderFooter: true,
      ...config
    };

    // Apply template-specific styles to the element
    await this.applyTemplateStyles(elementId, templateStyle, templateId);

    // Generate PDF with enhanced features
    await PDFUtils.generatePDFFromElement(
      elementId,
      finalConfig,
      filename,
      {
        ...metadata,
        title: `${cvData.personalInfo.fullName} - CV`,
        subject: 'Curriculum Vitae',
        keywords: `CV, ${cvData.personalInfo.fullName}`
      },
      security,
      watermark
    );
  }

  static async generateMarriagePDF(
    elementId: string,
    marriageData: MarriageBiodata,
    templateId: string,
    config: Partial<TemplatePDFConfig> = {},
    filename: string = 'biodata.pdf',
    metadata?: PDFMetadata,
    security?: PDFSecurityOptions,
    watermark?: WatermarkOptions
  ): Promise<void> {
    const templateStyle = this.getTemplateStyles(templateId);
    const finalConfig: TemplatePDFConfig = {
      quality: 0.95,
      margins: '20mm',
      dpi: 300,
      format: 'A4',
      orientation: 'portrait',
      templateStyle,
      includePageNumbers: true,
      includeHeaderFooter: true,
      ...config
    };

    // Apply template-specific styles for marriage biodata
    await this.applyMarriageTemplateStyles(elementId, templateStyle, templateId);

    // Generate PDF with enhanced features
    await PDFUtils.generatePDFFromElement(
      elementId,
      finalConfig,
      filename,
      {
        ...metadata,
        title: `${marriageData.personalInfo.fullName} - Marriage Biodata`,
        subject: 'Marriage Biodata',
        keywords: `Marriage, Biodata, ${marriageData.personalInfo.fullName}, ${marriageData.personalInfo.religion}`
      },
      security,
      watermark
    );
  }

  private static async applyTemplateStyles(elementId: string, style: TemplateStyleConfig, templateId: string): Promise<void> {
    const element = document.getElementById(elementId);
    if (!element) return;

    const customStyles = `
      <style>
        #${elementId} {
          font-family: ${style.fonts.body};
          color: ${style.colors.text};
          background-color: ${style.colors.background};
          line-height: 1.6;
        }

        #${elementId} h1, #${elementId} h2, #${elementId} h3, #${elementId} h4, #${elementId} h5, #${elementId} h6 {
          font-family: ${style.fonts.heading};
          color: ${style.colors.primary};
          margin-bottom: ${style.spacing.subsection}px;
        }

        #${elementId} h1 {
          font-size: 2.5em;
          font-weight: 700;
          margin-bottom: ${style.spacing.section}px;
        }

        #${elementId} h2 {
          font-size: 1.8em;
          font-weight: 600;
          border-bottom: 2px solid ${style.colors.primary};
          padding-bottom: 8px;
          margin-top: ${style.spacing.section}px;
        }

        #${elementId} h3 {
          font-size: 1.3em;
          font-weight: 600;
          color: ${style.colors.accent};
        }

        #${elementId} .section {
          margin-bottom: ${style.spacing.section}px;
        }

        #${elementId} .subsection {
          margin-bottom: ${style.spacing.subsection}px;
        }

        #${elementId} .item {
          margin-bottom: ${style.spacing.item}px;
        }

        #${elementId} .accent-text {
          font-family: ${style.fonts.accent};
          color: ${style.colors.accent};
        }

        #${elementId} .primary-color {
          color: ${style.colors.primary};
        }

        #${elementId} .secondary-color {
          color: ${style.colors.secondary};
        }

        #${elementId} .header {
          background-color: ${style.colors.primary};
          color: white;
          padding: 20px;
          margin-bottom: ${style.spacing.section}px;
          border-radius: 8px;
        }

        #${elementId} .card {
          background-color: white;
          border: 1px solid ${style.colors.secondary};
          border-radius: 8px;
          padding: 20px;
          margin-bottom: ${style.spacing.subsection}px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        #${elementId} .highlight {
          background-color: ${style.colors.primary}20;
          padding: 2px 4px;
          border-radius: 4px;
        }

        #${elementId} ul, #${elementId} ol {
          padding-left: 20px;
        }

        #${elementId} li {
          margin-bottom: ${style.spacing.item}px;
        }

        @media print {
          #${elementId} {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
        }
      </style>
    `;

    // Add styles to document head
    const styleElement = document.createElement('style');
    styleElement.textContent = customStyles;
    document.head.appendChild(styleElement);

    // Add template-specific classes
    element.classList.add(`template-${templateId}`);

    if (style.layout.columnLayout) {
      element.classList.add('column-layout');
    }
  }

  private static async applyMarriageTemplateStyles(elementId: string, style: TemplateStyleConfig, templateId: string): Promise<void> {
    const element = document.getElementById(elementId);
    if (!element) return;

    const marriageStyles = `
      <style>
        #${elementId} {
          font-family: ${style.fonts.body};
          color: ${style.colors.text};
          background-color: ${style.colors.background};
          line-height: 1.7;
        }

        #${elementId} .biodata-header {
          text-align: center;
          background: linear-gradient(135deg, ${style.colors.primary}, ${style.colors.accent});
          color: white;
          padding: 30px;
          margin-bottom: ${style.spacing.section}px;
          border-radius: 12px;
          position: relative;
          overflow: hidden;
        }

        #${elementId} .biodata-header::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="hearts" patternUnits="userSpaceOnUse" width="20" height="20"><text x="2" y="15" font-size="12" fill="%23ffffff20">♥</text></pattern></defs><rect width="100" height="100" fill="url(%23hearts)"/></svg>');
          opacity: 0.1;
        }

        #${elementId} .biodata-title {
          font-family: ${style.fonts.accent};
          font-size: 2.8em;
          margin-bottom: 10px;
          position: relative;
          z-index: 1;
        }

        #${elementId} .personal-details {
          background-color: white;
          border: 2px solid ${style.colors.primary};
          border-radius: 12px;
          padding: 25px;
          margin-bottom: ${style.spacing.section}px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        #${elementId} .family-details {
          background-color: white;
          border: 2px solid ${style.colors.secondary};
          border-radius: 12px;
          padding: 25px;
          margin-bottom: ${style.spacing.section}px;
        }

        #${elementId} .preferences-section {
          background-color: white;
          border: 2px solid ${style.colors.accent};
          border-radius: 12px;
          padding: 25px;
          margin-bottom: ${style.spacing.section}px;
        }

        #${elementId} .detail-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid ${style.colors.secondary}20;
        }

        #${elementId} .detail-label {
          font-weight: 600;
          color: ${style.colors.primary};
          min-width: 150px;
        }

        #${elementId} .detail-value {
          text-align: right;
          flex: 1;
        }

        #${elementId} .section-title {
          font-family: ${style.fonts.heading};
          color: ${style.colors.primary};
          font-size: 1.6em;
          margin-bottom: ${style.spacing.subsection}px;
          text-align: center;
          position: relative;
        }

        #${elementId} .section-title::after {
          content: '';
          position: absolute;
          bottom: -8px;
          left: 50%;
          transform: translateX(-50%);
          width: 60px;
          height: 2px;
          background-color: ${style.colors.accent};
        }

        #${elementId} .photo-frame {
          width: 150px;
          height: 150px;
          border: 4px solid ${style.colors.primary};
          border-radius: 50%;
          overflow: hidden;
          margin: 0 auto 20px;
          box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        #${elementId} .photo-frame img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        @media print {
          #${elementId} {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }

          #${elementId} .biodata-header {
            background: ${style.colors.primary} !important;
          }
        }
      </style>
    `;

    // Add marriage-specific styles to document head
    const styleElement = document.createElement('style');
    styleElement.textContent = marriageStyles;
    document.head.appendChild(styleElement);

    // Add marriage-specific classes
    element.classList.add(`marriage-template-${templateId}`);
    element.classList.add('biodata-document');
  }

  static async generateTemplatePreview(
    elementId: string,
    templateId: string,
    config: Partial<TemplatePDFConfig> = {}
  ): Promise<string> {
    const templateStyle = this.getTemplateStyles(templateId);
    const finalConfig: TemplatePDFConfig = {
      quality: 0.8,
      margins: '20mm',
      dpi: 150,
      format: 'A4',
      orientation: 'portrait',
      templateStyle,
      includePageNumbers: false,
      includeHeaderFooter: false,
      ...config
    };

    return await PDFUtils.previewPDF(elementId, finalConfig);
  }

  static async optimizeTemplateForPrint(
    elementId: string,
    _templateId: string
  ): Promise<void> {
    const element = document.getElementById(elementId);
    if (!element) return;

    const printStyles = `
      <style>
        @media print {
          #${elementId} {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
            color-adjust: exact;
          }

          #${elementId} * {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
            color-adjust: exact;
          }

          #${elementId} .no-print {
            display: none !important;
          }

          #${elementId} .print-break {
            page-break-before: always;
          }

          #${elementId} .avoid-break {
            page-break-inside: avoid;
          }

          #${elementId} .print-only {
            display: block !important;
          }
        }
      </style>
    `;

    const printStyleElement = document.createElement('style');
    printStyleElement.textContent = printStyles;
    document.head.appendChild(printStyleElement);
  }
}
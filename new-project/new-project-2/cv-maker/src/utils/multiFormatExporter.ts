import { PDFUtils, PDFConfig, PDFMetadata, PDFSecurityOptions, WatermarkOptions } from './pdfUtils';
import { TemplatePDFGenerator } from './templatePDFGenerator';
import { CVData } from '../types/cv';
import { MarriageData } from '../types/marriage';

export interface ExportOptions {
  format: 'pdf' | 'docx' | 'html' | 'json' | 'txt';
  quality?: 'low' | 'medium' | 'high';
  includePhoto?: boolean;
  watermark?: WatermarkOptions;
  password?: string;
  encryption?: boolean;
  filename?: string;
  templateId?: string;
}

export interface ExportResult {
  success: boolean;
  filename: string;
  format: string;
  size: number;
  url?: string;
  error?: string;
}

export interface DOCXExportOptions {
  template?: 'modern' | 'professional' | 'simple';
  includeStyles?: boolean;
  embedImages?: boolean;
  compressImages?: boolean;
}

export interface HTMLExportOptions {
  includeStyles?: boolean;
  responsive?: boolean;
  interactive?: boolean;
  printOptimized?: boolean;
}

export interface JSONExportOptions {
  prettyPrint?: boolean;
  includeMetadata?: boolean;
  compress?: boolean;
}

export class MultiFormatExporter {
  static async exportCV(
    elementId: string,
    cvData: CVData,
    options: ExportOptions
  ): Promise<ExportResult> {
    const timestamp = new Date().toISOString().split('T')[0];
    const baseFilename = options.filename || `${cvData.personalInfo.firstName}_${cvData.personalInfo.lastName}_CV_${timestamp}`;

    try {
      switch (options.format) {
        case 'pdf':
          return await this.exportToPDF(elementId, cvData, options, baseFilename);
        case 'docx':
          return await this.exportToDOCX(elementId, cvData, options, baseFilename);
        case 'html':
          return await this.exportToHTML(elementId, cvData, options, baseFilename);
        case 'json':
          return await this.exportToJSON(cvData, options, baseFilename);
        case 'txt':
          return await this.exportToText(cvData, options, baseFilename);
        default:
          throw new Error(`Unsupported export format: ${options.format}`);
      }
    } catch (error) {
      console.error('Export failed:', error);
      return {
        success: false,
        filename: baseFilename,
        format: options.format,
        size: 0,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  static async exportMarriageBiodata(
    elementId: string,
    marriageData: MarriageData,
    options: ExportOptions
  ): Promise<ExportResult> {
    const timestamp = new Date().toISOString().split('T')[0];
    const baseFilename = options.filename || `${marriageData.personalInfo.firstName}_${marriageData.personalInfo.lastName}_Biodata_${timestamp}`;

    try {
      switch (options.format) {
        case 'pdf':
          return await this.exportMarriageToPDF(elementId, marriageData, options, baseFilename);
        case 'docx':
          return await this.exportMarriageToDOCX(elementId, marriageData, options, baseFilename);
        case 'html':
          return await this.exportMarriageToHTML(elementId, marriageData, options, baseFilename);
        case 'json':
          return await this.exportMarriageToJSON(marriageData, options, baseFilename);
        case 'txt':
          return await this.exportMarriageToText(marriageData, options, baseFilename);
        default:
          throw new Error(`Unsupported export format: ${options.format}`);
      }
    } catch (error) {
      console.error('Export failed:', error);
      return {
        success: false,
        filename: baseFilename,
        format: options.format,
        size: 0,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  private static async exportToPDF(
    elementId: string,
    cvData: CVData,
    options: ExportOptions,
    filename: string
  ): Promise<ExportResult> {
    const qualityMap = {
      low: { quality: 0.7, dpi: 150 },
      medium: { quality: 0.85, dpi: 200 },
      high: { quality: 0.95, dpi: 300 }
    };

    const config = qualityMap[options.quality || 'medium'];
    const pdfConfig: PDFConfig = {
      ...config,
      margins: '20mm',
      format: 'A4',
      orientation: 'portrait'
    };

    const metadata: PDFMetadata = {
      title: `${cvData.personalInfo.firstName} ${cvData.personalInfo.lastName} - CV`,
      author: `${cvData.personalInfo.firstName} ${cvData.personalInfo.lastName}`,
      subject: 'Curriculum Vitae',
      keywords: `CV, ${cvData.personalInfo.profession}, ${cvData.personalInfo.firstName} ${cvData.personalInfo.lastName}`,
      creationDate: new Date()
    };

    const security: PDFSecurityOptions = {
      password: options.password,
      permissions: {
        printing: true,
        modifying: false,
        copying: true,
        annotating: false,
        fillingForms: false,
        extracting: false,
        assembling: false
      }
    };

    await TemplatePDFGenerator.generateCVPDF(
      elementId,
      cvData,
      options.templateId || 'minimal',
      pdfConfig,
      `${filename}.pdf`,
      metadata,
      security,
      options.watermark
    );

    return {
      success: true,
      filename: `${filename}.pdf`,
      format: 'pdf',
      size: 0 // Will be calculated when file is saved
    };
  }

  private static async exportToDOCX(
    elementId: string,
    cvData: CVData,
    options: ExportOptions,
    filename: string
  ): Promise<ExportResult> {
    // Note: DOCX export requires a library like docx ormammoth.js
    // This is a placeholder implementation using HTML conversion
    const htmlContent = await this.generateCVHTML(elementId, cvData, options);
    const docxContent = this.convertHTMLToDOCX(htmlContent);

    const blob = new Blob([docxContent], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    this.downloadBlob(blob, `${filename}.docx`);

    return {
      success: true,
      filename: `${filename}.docx`,
      format: 'docx',
      size: blob.size
    };
  }

  private static async exportToHTML(
    elementId: string,
    cvData: CVData,
    options: ExportOptions,
    filename: string
  ): Promise<ExportResult> {
    const htmlContent = await this.generateCVHTML(elementId, cvData, options);
    const blob = new Blob([htmlContent], { type: 'text/html' });
    this.downloadBlob(blob, `${filename}.html`);

    return {
      success: true,
      filename: `${filename}.html`,
      format: 'html',
      size: blob.size
    };
  }

  private static async exportToJSON(
    cvData: CVData,
    options: ExportOptions,
    filename: string
  ): Promise<ExportResult> {
    const exportData = {
      ...cvData,
      metadata: {
        exportedAt: new Date().toISOString(),
        version: '1.0',
        format: 'cv'
      }
    };

    const jsonString = JSON.stringify(exportData, null, options.quality === 'high' ? 2 : 0);
    const blob = new Blob([jsonString], { type: 'application/json' });
    this.downloadBlob(blob, `${filename}.json`);

    return {
      success: true,
      filename: `${filename}.json`,
      format: 'json',
      size: blob.size
    };
  }

  private static async exportToText(
    cvData: CVData,
    options: ExportOptions,
    filename: string
  ): Promise<ExportResult> {
    const textContent = this.generateCVText(cvData);
    const blob = new Blob([textContent], { type: 'text/plain' });
    this.downloadBlob(blob, `${filename}.txt`);

    return {
      success: true,
      filename: `${filename}.txt`,
      format: 'txt',
      size: blob.size
    };
  }

  // Marriage biodata export methods
  private static async exportMarriageToPDF(
    elementId: string,
    marriageData: MarriageData,
    options: ExportOptions,
    filename: string
  ): Promise<ExportResult> {
    const qualityMap = {
      low: { quality: 0.7, dpi: 150 },
      medium: { quality: 0.85, dpi: 200 },
      high: { quality: 0.95, dpi: 300 }
    };

    const config = qualityMap[options.quality || 'medium'];
    const pdfConfig: PDFConfig = {
      ...config,
      margins: '20mm',
      format: 'A4',
      orientation: 'portrait'
    };

    const metadata: PDFMetadata = {
      title: `${marriageData.personalInfo.firstName} ${marriageData.personalInfo.lastName} - Marriage Biodata`,
      author: `${marriageData.personalInfo.firstName} ${marriageData.personalInfo.lastName}`,
      subject: 'Marriage Biodata',
      keywords: `Marriage, Biodata, ${marriageData.personalInfo.firstName} ${marriageData.personalInfo.lastName}, ${marriageData.religion}`,
      creationDate: new Date()
    };

    const security: PDFSecurityOptions = {
      password: options.password,
      permissions: {
        printing: true,
        modifying: false,
        copying: true,
        annotating: false,
        fillingForms: false,
        extracting: false,
        assembling: false
      }
    };

    await TemplatePDFGenerator.generateMarriagePDF(
      elementId,
      marriageData,
      options.templateId || 'marriage_elegant',
      pdfConfig,
      `${filename}.pdf`,
      metadata,
      security,
      options.watermark
    );

    return {
      success: true,
      filename: `${filename}.pdf`,
      format: 'pdf',
      size: 0
    };
  }

  private static async exportMarriageToDOCX(
    elementId: string,
    marriageData: MarriageData,
    options: ExportOptions,
    filename: string
  ): Promise<ExportResult> {
    const htmlContent = await this.generateMarriageHTML(elementId, marriageData, options);
    const docxContent = this.convertHTMLToDOCX(htmlContent);

    const blob = new Blob([docxContent], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    this.downloadBlob(blob, `${filename}.docx`);

    return {
      success: true,
      filename: `${filename}.docx`,
      format: 'docx',
      size: blob.size
    };
  }

  private static async exportMarriageToHTML(
    elementId: string,
    marriageData: MarriageData,
    options: ExportOptions,
    filename: string
  ): Promise<ExportResult> {
    const htmlContent = await this.generateMarriageHTML(elementId, marriageData, options);
    const blob = new Blob([htmlContent], { type: 'text/html' });
    this.downloadBlob(blob, `${filename}.html`);

    return {
      success: true,
      filename: `${filename}.html`,
      format: 'html',
      size: blob.size
    };
  }

  private static async exportMarriageToJSON(
    marriageData: MarriageData,
    options: ExportOptions,
    filename: string
  ): Promise<ExportResult> {
    const exportData = {
      ...marriageData,
      metadata: {
        exportedAt: new Date().toISOString(),
        version: '1.0',
        format: 'marriage_biodata'
      }
    };

    const jsonString = JSON.stringify(exportData, null, options.quality === 'high' ? 2 : 0);
    const blob = new Blob([jsonString], { type: 'application/json' });
    this.downloadBlob(blob, `${filename}.json`);

    return {
      success: true,
      filename: `${filename}.json`,
      format: 'json',
      size: blob.size
    };
  }

  private static async exportMarriageToText(
    marriageData: MarriageData,
    options: ExportOptions,
    filename: string
  ): Promise<ExportResult> {
    const textContent = this.generateMarriageText(marriageData);
    const blob = new Blob([textContent], { type: 'text/plain' });
    this.downloadBlob(blob, `${filename}.txt`);

    return {
      success: true,
      filename: `${filename}.txt`,
      format: 'txt',
      size: blob.size
    };
  }

  // Helper methods
  private static async generateCVHTML(elementId: string, cvData: CVData, options: ExportOptions): Promise<string> {
    const element = document.getElementById(elementId);
    if (!element) throw new Error('Element not found');

    // Clone element to avoid modifying original
    const clone = element.cloneNode(true) as HTMLElement;

    // Remove interactive elements
    const interactiveElements = clone.querySelectorAll('button, input, select, textarea, .no-export');
    interactiveElements.forEach(el => el.remove());

    // Add export metadata
    const metadata = document.createElement('div');
    metadata.innerHTML = `
      <div class="export-metadata" style="display: none;">
        Exported on: ${new Date().toLocaleString()}<br>
        Format: CV<br>
        Quality: ${options.quality || 'medium'}
      </div>
    `;
    clone.insertBefore(metadata, clone.firstChild);

    return clone.outerHTML;
  }

  private static async generateMarriageHTML(elementId: string, marriageData: MarriageData, options: ExportOptions): Promise<string> {
    const element = document.getElementById(elementId);
    if (!element) throw new Error('Element not found');

    const clone = element.cloneNode(true) as HTMLElement;

    // Remove interactive elements
    const interactiveElements = clone.querySelectorAll('button, input, select, textarea, .no-export');
    interactiveElements.forEach(el => el.remove());

    // Add export metadata
    const metadata = document.createElement('div');
    metadata.innerHTML = `
      <div class="export-metadata" style="display: none;">
        Exported on: ${new Date().toLocaleString()}<br>
        Format: Marriage Biodata<br>
        Quality: ${options.quality || 'medium'}
      </div>
    `;
    clone.insertBefore(metadata, clone.firstChild);

    return clone.outerHTML;
  }

  private static convertHTMLToDOCX(htmlContent: string): string {
    // Placeholder for DOCX conversion
    // In a real implementation, you would use a library like docx
    return htmlContent; // This would be proper DOCX content
  }

  private static generateCVText(cvData: CVData): string {
    const { personalInfo, experience, education, skills, summary, languages, certifications, projects } = cvData;

    let text = `CURRICULUM VITAE\n`;
    text += `${personalInfo.firstName} ${personalInfo.lastName}\n`;
    text += `${personalInfo.email} | ${personalInfo.phone}\n`;
    text += `${personalInfo.address}, ${personalInfo.city}, ${personalInfo.country} ${personalInfo.zipCode}\n\n`;

    if (summary) {
      text += `PROFESSIONAL SUMMARY\n`;
      text += `${summary}\n\n`;
    }

    if (experience && experience.length > 0) {
      text += `EXPERIENCE\n`;
      experience.forEach(exp => {
        text += `${exp.position} at ${exp.company}\n`;
        text += `${exp.startDate} - ${exp.endDate || 'Present'}\n`;
        if (exp.description) text += `${exp.description}\n`;
        text += '\n';
      });
    }

    if (education && education.length > 0) {
      text += `EDUCATION\n`;
      education.forEach(edu => {
        text += `${edu.degree} in ${edu.field}\n`;
        text += `${edu.institution}, ${edu.location}\n`;
        text += `${edu.startDate} - ${edu.endDate}\n`;
        if (edu.gpa) text += `GPA: ${edu.gpa}\n`;
        text += '\n';
      });
    }

    if (skills && skills.length > 0) {
      text += `SKILLS\n`;
      skills.forEach(skill => {
        text += `${skill.name}: ${skill.level}\n`;
      });
      text += '\n';
    }

    return text;
  }

  private static generateMarriageText(marriageData: MarriageData): string {
    const { personalInfo, familyInfo, education, profession, preferences, expectations } = marriageData;

    let text = `MARRIAGE BIODATA\n`;
    text += `${personalInfo.firstName} ${personalInfo.lastName}\n`;
    text += `${personalInfo.email} | ${personalInfo.phone}\n\n`;

    text += `PERSONAL INFORMATION\n`;
    text += `Age: ${personalInfo.age}\n`;
    text += `Height: ${personalInfo.height}\n`;
    text += `Religion: ${personalInfo.religion}\n`;
    text += `Caste: ${personalInfo.caste}\n`;
    text += `Mother Tongue: ${personalInfo.motherTongue}\n\n`;

    if (familyInfo) {
      text += `FAMILY INFORMATION\n`;
      text += `Father's Occupation: ${familyInfo.fatherOccupation}\n`;
      text += `Mother's Occupation: ${familyInfo.motherOccupation}\n`;
      text += `Siblings: ${familyInfo.siblings}\n`;
      text += `Family Status: ${familyInfo.familyStatus}\n\n`;
    }

    if (education && education.length > 0) {
      text += `EDUCATION\n`;
      education.forEach(edu => {
        text += `${edu.degree} in ${edu.field}\n`;
        text += `${edu.institution}\n`;
        text += `${edu.startDate} - ${edu.endDate}\n\n`;
      });
    }

    if (profession) {
      text += `PROFESSION\n`;
      text += `${profession.occupation}\n`;
      text += `${profession.company}\n`;
      text += `Income: ${profession.income}\n\n`;
    }

    return text;
  }

  private static downloadBlob(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  static async exportMultipleFormats(
    elementId: string,
    data: CVData | MarriageData,
    formats: ExportOptions[],
    isMarriage: boolean = false
  ): Promise<ExportResult[]> {
    const results: ExportResult[] = [];

    for (const format of formats) {
      try {
        const result = isMarriage
          ? await this.exportMarriageBiodata(elementId, data as MarriageData, format)
          : await this.exportCV(elementId, data as CVData, format);

        results.push(result);
      } catch (error) {
        results.push({
          success: false,
          filename: format.filename || 'unknown',
          format: format.format,
          size: 0,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }

    return results;
  }

  static async createExportPackage(
    elementId: string,
    data: CVData | MarriageData,
    options: {
      formats?: ExportOptions[];
      includeOriginal?: boolean;
      compress?: boolean;
    },
    isMarriage: boolean = false
  ): Promise<Blob> {
    const formats = options.formats || [
      { format: 'pdf' as const, quality: 'high' },
      { format: 'html' as const, quality: 'medium' },
      { format: 'json' as const, quality: 'medium' }
    ];

    const results = await this.exportMultipleFormats(elementId, data, formats, isMarriage);

    // Note: Package creation would require a ZIP library
    // This is a placeholder implementation
    const packageContent = JSON.stringify({
      exportedAt: new Date().toISOString(),
      files: results,
      data: isMarriage ? data : data
    }, null, 2);

    return new Blob([packageContent], { type: 'application/json' });
  }
}
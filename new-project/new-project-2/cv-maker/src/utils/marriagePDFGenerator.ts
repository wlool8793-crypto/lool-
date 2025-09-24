import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { MarriageBiodata } from '../types/marriage';

export interface MarriagePDFExportOptions {
  template: 'traditional' | 'modern' | 'minimal' | 'premium';
  quality: 'low' | 'medium' | 'high';
  includeWatermark: boolean;
  password?: string;
  language: 'en' | 'hi';
}

export class MarriagePDFGenerator {
  private static readonly DEFAULT_OPTIONS: MarriagePDFExportOptions = {
    template: 'traditional',
    quality: 'high',
    includeWatermark: true,
    language: 'en'
  };

  /**
   * Generate PDF from HTML element
   */
  static async generatePDF(
    element: HTMLElement,
    data: MarriageBiodata,
    options: Partial<MarriagePDFExportOptions> = {}
  ): Promise<Blob> {
    const config = { ...this.DEFAULT_OPTIONS, ...options };

    try {
      console.log('📄 [PDF] Starting PDF generation...', { template: config.template, quality: config.quality });

      // Configure canvas capture
      const canvas = await html2canvas(element, {
        scale: config.quality === 'high' ? 3 : config.quality === 'medium' ? 2 : 1.5,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        width: element.scrollWidth,
        height: element.scrollHeight
      });

      console.log('📄 [PDF] Canvas captured, dimensions:', { width: canvas.width, height: canvas.height });

      // Calculate PDF dimensions
      const imgWidth = 210; // A4 width in mm
      const pageHeight = 295; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;

      // Create PDF
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      let position = 0;

      // Add first page
      pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      // Add additional pages if content is longer than one page
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      // Add metadata
      this.addMetadata(pdf, data, config);

      // Add watermark if enabled
      if (config.includeWatermark) {
        this.addWatermark(pdf, data);
      }

      // Add password protection if provided
      if (config.password) {
        this.addPasswordProtection(pdf, config.password);
      }

      console.log('📄 [PDF] PDF generation completed successfully');
      return pdf.output('blob');

    } catch (error) {
      console.error('❌ [PDF] Error generating PDF:', error);
      throw new Error(`PDF generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Add PDF metadata
   */
  private static addMetadata(pdf: jsPDF, data: MarriageBiodata, config: MarriagePDFExportOptions) {
    const metadata = {
      title: `${data.personalInfo.fullName} - Marriage Biodata`,
      subject: 'Marriage Biodata Document',
      author: data.personalInfo.fullName,
      creator: 'CV Maker - Marriage Biodata Generator',
      producer: 'CV Maker',
      keywords: [
        'marriage',
        'biodata',
        data.personalInfo.religion,
        data.personalInfo.motherTongue,
        config.template
      ].join(', ')
    };

    pdf.setProperties(metadata);
  }

  /**
   * Add watermark to PDF
   */
  private static addWatermark(pdf: jsPDF, data: MarriageBiodata) {
    const pageCount = pdf.getNumberOfPages();
    const watermarkText = `${data.personalInfo.fullName} - Marriage Biodata`;

    pdf.setGState({ opacity: 0.1 });
    pdf.setTextColor(128, 128, 128);
    pdf.setFontSize(40);

    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();

      // Add diagonal watermark
      pdf.text(watermarkText, pageWidth / 2, pageHeight / 2, {
        angle: 45,
        align: 'center'
      });
    }

    pdf.setGState({ opacity: 1 });
  }

  /**
   * Add password protection
   */
  private static addPasswordProtection(pdf: jsPDF, password: string) {
    // Note: jsPDF doesn't support password protection in the basic version
    // This would require jspdf-autotable or similar plugin
    console.log('🔒 [PDF] Password protection requested:', password);
    // For now, we'll just log it. In production, you'd use a PDF library that supports encryption
  }

  /**
   * Generate and download PDF
   */
  static async downloadPDF(
    element: HTMLElement,
    data: MarriageBiodata,
    filename?: string,
    options: Partial<MarriagePDFExportOptions> = {}
  ): Promise<void> {
    try {
      const pdfBlob = await this.generatePDF(element, data, options);
      const defaultFilename = `${data.personalInfo.fullName.replace(/\s+/g, '_')}_Marriage_Biodata.pdf`;
      const finalFilename = filename || defaultFilename;

      // Create download link
      const url = URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = finalFilename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      console.log('📥 [PDF] PDF downloaded successfully:', finalFilename);

    } catch (error) {
      console.error('❌ [PDF] Error downloading PDF:', error);
      throw error;
    }
  }

  /**
   * Generate PDF for sharing (returns base64)
   */
  static async generatePDFForSharing(
    element: HTMLElement,
    data: MarriageBiodata,
    options: Partial<MarriagePDFExportOptions> = {}
  ): Promise<string> {
    try {
      const pdfBlob = await this.generatePDF(element, data, options);
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(pdfBlob);
      });
    } catch (error) {
      console.error('❌ [PDF] Error generating PDF for sharing:', error);
      throw error;
    }
  }

  /**
   * Preview PDF in new tab
   */
  static async previewPDF(
    element: HTMLElement,
    data: MarriageBiodata,
    options: Partial<MarriagePDFExportOptions> = {}
  ): Promise<void> {
    try {
      const pdfBlob = await this.generatePDF(element, data, options);
      const pdfUrl = URL.createObjectURL(pdfBlob);

      // Open in new tab
      window.open(pdfUrl, '_blank');

      // Clean up after 5 minutes
      setTimeout(() => URL.revokeObjectURL(pdfUrl), 300000);

      console.log('👁️ [PDF] PDF preview opened in new tab');

    } catch (error) {
      console.error('❌ [PDF] Error previewing PDF:', error);
      throw error;
    }
  }

  /**
   * Get estimated file size
   */
  static async estimateFileSize(
    element: HTMLElement,
    quality: 'low' | 'medium' | 'high' = 'high'
  ): Promise<string> {
    try {
      const canvas = await html2canvas(element, {
        scale: quality === 'high' ? 3 : quality === 'medium' ? 2 : 1.5,
        useCORS: true,
        logging: false
      });

      const dataSize = canvas.toDataURL('image/png').length;
      const estimatedPDFSize = Math.round(dataSize * 0.3); // Rough estimate

      if (estimatedPDFSize < 1024) {
        return `${estimatedPDFSize} B`;
      } else if (estimatedPDFSize < 1024 * 1024) {
        return `${Math.round(estimatedPDFSize / 1024)} KB`;
      } else {
        return `${Math.round(estimatedPDFSize / (1024 * 1024))} MB`;
      }

    } catch (error) {
      console.error('❌ [PDF] Error estimating file size:', error);
      return 'Unknown size';
    }
  }
}
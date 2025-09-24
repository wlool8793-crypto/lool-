import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { PDFConfig, ExportOptions } from '../types/common';

export interface PDFMetadata {
  title?: string;
  author?: string;
  subject?: string;
  keywords?: string;
  creator?: string;
  producer?: string;
  creationDate?: Date;
}

export interface PDFSecurityOptions {
  password?: string;
  ownerPassword?: string;
  permissions?: {
    printing?: boolean;
    modifying?: boolean;
    copying?: boolean;
    annotating?: boolean;
    fillingForms?: boolean;
    extracting?: boolean;
    assembling?: boolean;
  };
}

export interface WatermarkOptions {
  text?: string;
  image?: string;
  opacity?: number;
  fontSize?: number;
  color?: string;
  angle?: number;
  position?: 'center' | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
}

export interface PDFFontOptions {
  family?: string;
  size?: number;
  color?: string;
  weight?: 'normal' | 'bold' | 'bolder' | 'lighter';
  style?: 'normal' | 'italic' | 'oblique';
}

export class PDFUtils {
  static async generatePDFFromElement(
    elementId: string,
    config: PDFConfig = {
      quality: 0.95,
      margins: '20mm',
      dpi: 300,
      format: 'A4',
      orientation: 'portrait'
    },
    filename: string = 'document.pdf',
    metadata?: PDFMetadata,
    security?: PDFSecurityOptions,
    watermark?: WatermarkOptions
  ): Promise<void> {
    try {
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error(`Element with id "${elementId}" not found`);
      }

      // Create canvas from element
      const canvas = await html2canvas(element, {
        scale: config.dpi / 96,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        quality: config.quality,
      });

      // Calculate dimensions
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const pdf = new jsPDF({
        orientation: config.orientation,
        unit: 'mm',
        format: config.format.toLowerCase(),
      });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();

      // Convert margins from string to number
      const margins = this.parseMargins(config.margins);
      const contentWidth = pageWidth - margins.left - margins.right;
      const contentHeight = pageHeight - margins.top - margins.bottom;

      // Calculate scale to fit content
      const scale = Math.min(contentWidth / (imgWidth * 0.264583), contentHeight / (imgHeight * 0.264583));
      const scaledWidth = imgWidth * 0.264583 * scale;
      const scaledHeight = imgHeight * 0.264583 * scale;

      // Add watermark if provided
      if (watermark) {
        this.addWatermark(pdf, watermark, pageWidth, pageHeight);
      }

      // Set metadata if provided
      if (metadata) {
        this.setPDFMetadata(pdf, metadata);
      }

      // Apply security if provided
      if (security) {
        this.applyPDFSecurity(pdf, security);
      }

      // Save the PDF
      pdf.save(filename);
    } catch (error) {
      console.error('Error generating PDF:', error);
      throw new Error('Failed to generate PDF');
    }
  }

  static async generateMultiPagePDF(
    elementIds: string[],
    config: PDFConfig = {
      quality: 0.95,
      margins: '20mm',
      dpi: 300,
      format: 'A4',
      orientation: 'portrait'
    },
    filename: string = 'document.pdf'
  ): Promise<void> {
    try {
      const pdf = new jsPDF({
        orientation: config.orientation,
        unit: 'mm',
        format: config.format.toLowerCase(),
      });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margins = this.parseMargins(config.margins);
      const contentWidth = pageWidth - margins.left - margins.right;
      const contentHeight = pageHeight - margins.top - margins.bottom;

      for (let i = 0; i < elementIds.length; i++) {
        if (i > 0) {
          pdf.addPage();
        }

        const element = document.getElementById(elementIds[i]);
        if (!element) {
          console.warn(`Element with id "${elementIds[i]}" not found`);
          continue;
        }

        const canvas = await html2canvas(element, {
          scale: config.dpi / 96,
          useCORS: true,
          allowTaint: true,
          backgroundColor: '#ffffff',
          logging: false,
          quality: config.quality,
        });

        const imgWidth = canvas.width;
        const imgHeight = canvas.height;
        const scale = Math.min(contentWidth / (imgWidth * 0.264583), contentHeight / (imgHeight * 0.264583));
        const scaledWidth = imgWidth * 0.264583 * scale;
        const scaledHeight = imgHeight * 0.264583 * scale;

        pdf.addImage(
          canvas.toDataURL('image/jpeg', config.quality),
          'JPEG',
          margins.left,
          margins.top,
          scaledWidth,
          scaledHeight
        );
      }

      pdf.save(filename);
    } catch (error) {
      console.error('Error generating multi-page PDF:', error);
      throw new Error('Failed to generate multi-page PDF');
    }
  }

  static async generateProtectedPDF(
    elementId: string,
    config: PDFConfig & { password?: string },
    filename: string = 'document.pdf'
  ): Promise<void> {
    try {
      const pdfBlob = await this.generatePDFBlob(elementId, config);

      if (config.password) {
        // Note: jsPDF doesn't support password protection natively
        // This is a placeholder for future implementation
        console.warn('Password protection not implemented yet');
      }

      // Create download link
      const url = URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error generating protected PDF:', error);
      throw new Error('Failed to generate protected PDF');
    }
  }

  static async generatePDFBlob(
    elementId: string,
    config: PDFConfig = {
      quality: 0.95,
      margins: '20mm',
      dpi: 300,
      format: 'A4',
      orientation: 'portrait'
    }
  ): Promise<Blob> {
    try {
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error(`Element with id "${elementId}" not found`);
      }

      const canvas = await html2canvas(element, {
        scale: config.dpi / 96,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        quality: config.quality,
      });

      const pdf = new jsPDF({
        orientation: config.orientation,
        unit: 'mm',
        format: config.format.toLowerCase(),
      });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margins = this.parseMargins(config.margins);
      const contentWidth = pageWidth - margins.left - margins.right;
      const contentHeight = pageHeight - margins.top - margins.bottom;

      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const scale = Math.min(contentWidth / (imgWidth * 0.264583), contentHeight / (imgHeight * 0.264583));
      const scaledWidth = imgWidth * 0.264583 * scale;
      const scaledHeight = imgHeight * 0.264583 * scale;

      pdf.addImage(
        canvas.toDataURL('image/jpeg', config.quality),
        'JPEG',
        margins.left,
        margins.top,
        scaledWidth,
        scaledHeight
      );

      return pdf.output('blob');
    } catch (error) {
      console.error('Error generating PDF blob:', error);
      throw new Error('Failed to generate PDF blob');
    }
  }

  private static parseMargins(margins: string): { top: number; right: number; bottom: number; left: number } {
    const marginValues = margins.split(' ');

    switch (marginValues.length) {
      case 1:
        return {
          top: parseFloat(marginValues[0]),
          right: parseFloat(marginValues[0]),
          bottom: parseFloat(marginValues[0]),
          left: parseFloat(marginValues[0])
        };
      case 2:
        return {
          top: parseFloat(marginValues[0]),
          right: parseFloat(marginValues[1]),
          bottom: parseFloat(marginValues[0]),
          left: parseFloat(marginValues[1])
        };
      case 3:
        return {
          top: parseFloat(marginValues[0]),
          right: parseFloat(marginValues[1]),
          bottom: parseFloat(marginValues[2]),
          left: parseFloat(marginValues[1])
        };
      case 4:
        return {
          top: parseFloat(marginValues[0]),
          right: parseFloat(marginValues[1]),
          bottom: parseFloat(marginValues[2]),
          left: parseFloat(marginValues[3])
        };
      default:
        return { top: 20, right: 20, bottom: 20, left: 20 };
    }
  }

  static async previewPDF(
    elementId: string,
    config: PDFConfig = {
      quality: 0.95,
      margins: '20mm',
      dpi: 300,
      format: 'A4',
      orientation: 'portrait'
    }
  ): Promise<string> {
    try {
      const blob = await this.generatePDFBlob(elementId, config);
      return URL.createObjectURL(blob);
    } catch (error) {
      console.error('Error generating PDF preview:', error);
      throw new Error('Failed to generate PDF preview');
    }
  }

  static addWatermark(
    pdf: jsPDF,
    watermark: WatermarkOptions,
    pageWidth: number,
    pageHeight: number
  ): void {
    const opacity = watermark.opacity || 0.1;
    const fontSize = watermark.fontSize || 50;
    const color = watermark.color || '#cccccc';
    const angle = watermark.angle || 45;
    const position = watermark.position || 'center';

    pdf.setGState({ opacity });
    pdf.setFontSize(fontSize);
    pdf.setTextColor(color);
    pdf.setFont('helvetica', 'normal');

    let x = pageWidth / 2;
    let y = pageHeight / 2;

    switch (position) {
      case 'top-left':
        x = 20;
        y = 30;
        break;
      case 'top-right':
        x = pageWidth - 20;
        y = 30;
        break;
      case 'bottom-left':
        x = 20;
        y = pageHeight - 20;
        break;
      case 'bottom-right':
        x = pageWidth - 20;
        y = pageHeight - 20;
        break;
    }

    if (watermark.text) {
      pdf.text(watermark.text, x, y, { angle, align: position === 'center' ? 'center' : 'left' });
    }

    if (watermark.image) {
      // Note: For image watermarking, you'd need to load the image first
      // This is a placeholder for future implementation
      console.warn('Image watermarking not implemented yet');
    }

    pdf.setGState({ opacity: 1 });
  }

  static setPDFMetadata(pdf: jsPDF, metadata: PDFMetadata): void {
    if (metadata.title) pdf.setProperties({ title: metadata.title });
    if (metadata.author) pdf.setProperties({ author: metadata.author });
    if (metadata.subject) pdf.setProperties({ subject: metadata.subject });
    if (metadata.keywords) pdf.setProperties({ keywords: metadata.keywords });
    if (metadata.creator) pdf.setProperties({ creator: metadata.creator });
    if (metadata.producer) pdf.setProperties({ producer: metadata.producer });
  }

  static applyPDFSecurity(pdf: jsPDF, security: PDFSecurityOptions): void {
    // Note: jsPDF has limited security support
    // This is a placeholder for future implementation with PDFKit or similar
    if (security.password) {
      console.warn('PDF password protection requires additional libraries');
    }
  }

  static async generateOptimizedPDF(
    elementId: string,
    config: PDFConfig & { compression?: 'fast' | 'best' } = {
      quality: 0.95,
      margins: '20mm',
      dpi: 300,
      format: 'A4',
      orientation: 'portrait',
      compression: 'fast'
    },
    filename: string = 'document.pdf'
  ): Promise<void> {
    try {
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error(`Element with id "${elementId}" not found`);
      }

      // Apply optimization styles temporarily
      const originalStyles = element.style.cssText;
      element.style.cssText += `
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
      `;

      const canvas = await html2canvas(element, {
        scale: config.dpi / 96,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        quality: config.compression === 'best' ? 1 : config.quality,
      });

      // Restore original styles
      element.style.cssText = originalStyles;

      const pdf = new jsPDF({
        orientation: config.orientation,
        unit: 'mm',
        format: config.format.toLowerCase(),
      });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margins = this.parseMargins(config.margins);
      const contentWidth = pageWidth - margins.left - margins.right;
      const contentHeight = pageHeight - margins.top - margins.bottom;

      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const scale = Math.min(contentWidth / (imgWidth * 0.264583), contentHeight / (imgHeight * 0.264583));
      const scaledWidth = imgWidth * 0.264583 * scale;
      const scaledHeight = imgHeight * 0.264583 * scale;

      pdf.addImage(
        canvas.toDataURL('image/jpeg', config.quality),
        'JPEG',
        margins.left,
        margins.top,
        scaledWidth,
        scaledHeight
      );

      pdf.save(filename);
    } catch (error) {
      console.error('Error generating optimized PDF:', error);
      throw new Error('Failed to generate optimized PDF');
    }
  }

  static async generatePDFFromHTML(
    html: string,
    config: PDFConfig = {
      quality: 0.95,
      margins: '20mm',
      dpi: 300,
      format: 'A4',
      orientation: 'portrait'
    },
    filename: string = 'document.pdf'
  ): Promise<void> {
    try {
      // Create temporary element
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = html;
      tempDiv.style.position = 'absolute';
      tempDiv.style.left = '-9999px';
      tempDiv.style.width = '210mm';
      tempDiv.style.backgroundColor = '#ffffff';
      document.body.appendChild(tempDiv);

      await this.generatePDFFromElement(tempDiv.id, config, filename);

      // Clean up
      document.body.removeChild(tempDiv);
    } catch (error) {
      console.error('Error generating PDF from HTML:', error);
      throw new Error('Failed to generate PDF from HTML');
    }
  }

  static async splitPDFPages(
    elementId: string,
    config: PDFConfig = {
      quality: 0.95,
      margins: '20mm',
      dpi: 300,
      format: 'A4',
      orientation: 'portrait'
    }
  ): Promise<Blob[]> {
    try {
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error(`Element with id "${elementId}" not found`);
      }

      const canvas = await html2canvas(element, {
        scale: config.dpi / 96,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        quality: config.quality,
      });

      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const pdf = new jsPDF({
        orientation: config.orientation,
        unit: 'mm',
        format: config.format.toLowerCase(),
      });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margins = this.parseMargins(config.margins);
      const contentWidth = pageWidth - margins.left - margins.right;
      const contentHeight = pageHeight - margins.top - margins.bottom;

      const scale = Math.min(contentWidth / (imgWidth * 0.264583), contentHeight / (imgHeight * 0.264583));
      const scaledWidth = imgWidth * 0.264583 * scale;
      const scaledHeight = imgHeight * 0.264583 * scale;

      const pages: Blob[] = [];
      let currentY = 0;

      while (currentY < scaledHeight) {
        const pagePdf = new jsPDF({
          orientation: config.orientation,
          unit: 'mm',
          format: config.format.toLowerCase(),
        });

        const pageHeightPixels = Math.min(contentHeight / scale, scaledHeight - currentY);
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = imgWidth;
        tempCanvas.height = Math.min(pageHeightPixels * scale / 0.264583, imgHeight - currentY * scale / 0.264583);

        const tempCtx = tempCanvas.getContext('2d');
        if (tempCtx) {
          tempCtx.drawImage(canvas, 0, currentY * scale / 0.264583, imgWidth, tempCanvas.height, 0, 0, imgWidth, tempCanvas.height);
        }

        pagePdf.addImage(
          tempCanvas.toDataURL('image/jpeg', config.quality),
          'JPEG',
          margins.left,
          margins.top,
          scaledWidth,
          pageHeightPixels
        );

        pages.push(pagePdf.output('blob'));
        currentY += contentHeight;
      }

      return pages;
    } catch (error) {
      console.error('Error splitting PDF pages:', error);
      throw new Error('Failed to split PDF pages');
    }
  }

  static async mergePDFs(pdfBlobs: Blob[], filename: string = 'merged.pdf'): Promise<void> {
    try {
      if (pdfBlobs.length === 0) {
        throw new Error('No PDFs to merge');
      }

      // Note: PDF merging requires a library like PDF-lib
      // This is a placeholder for future implementation
      console.warn('PDF merging requires additional libraries like PDF-lib');

      // For now, just download the first PDF
      const url = URL.createObjectURL(pdfBlobs[0]);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error merging PDFs:', error);
      throw new Error('Failed to merge PDFs');
    }
  }
}
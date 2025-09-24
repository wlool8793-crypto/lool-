import { PDFUtils } from './pdfUtils';

export interface PrintSettings {
  pageSize: 'A4' | 'A3' | 'Letter' | 'Legal';
  orientation: 'portrait' | 'landscape';
  margins: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  scale: 'fit' | 'actual' | 'custom';
  customScale?: number;
  backgroundColor: 'white' | 'none';
  includeHeaders: boolean;
  includeFooters: boolean;
  pageNumbers: boolean;
  duplex: boolean;
  quality: 'draft' | 'normal' | 'high';
}

export interface PrintOptimizationOptions {
  removeBackgrounds?: boolean;
  removeAnimations?: boolean;
  simplifyStyles?: boolean;
  optimizeImages?: boolean;
  consolidateStyles?: boolean;
  addPrintStyles?: boolean;
  responsiveBreakpoints?: boolean;
  fontEmbedding?: boolean;
  colorMode?: 'color' | 'grayscale' | 'blackAndWhite';
}

export interface PrintPreviewOptions {
  showPageBreaks?: boolean;
  showMargins?: boolean;
  showWatermark?: boolean;
  simulatePaper?: boolean;
  zoom?: number;
}

export interface PrintJob {
  id: string;
  title: string;
  content: string;
  settings: PrintSettings;
  optimization: PrintOptimizationOptions;
  createdAt: Date;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  pages?: number;
  estimatedTime?: number;
}

export class PrintOptimizer {
  private static readonly DEFAULT_SETTINGS: PrintSettings = {
    pageSize: 'A4',
    orientation: 'portrait',
    margins: {
      top: 20,
      right: 20,
      bottom: 20,
      left: 20
    },
    scale: 'fit',
    backgroundColor: 'white',
    includeHeaders: true,
    includeFooters: true,
    pageNumbers: true,
    duplex: false,
    quality: 'normal'
  };

  private static readonly DEFAULT_OPTIMIZATION: PrintOptimizationOptions = {
    removeBackgrounds: true,
    removeAnimations: true,
    simplifyStyles: true,
    optimizeImages: true,
    consolidateStyles: true,
    addPrintStyles: true,
    responsiveBreakpoints: false,
    fontEmbedding: true,
    colorMode: 'color'
  };

  static async optimizeForPrint(
    elementId: string,
    settings: Partial<PrintSettings> = {},
    optimization: Partial<PrintOptimizationOptions> = {}
  ): Promise<{ optimizedHtml: string; css: string; estimatedPages: number }> {
    try {
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error(`Element with id "${elementId}" not found`);
      }

      const finalSettings = { ...this.DEFAULT_SETTINGS, ...settings };
      const finalOptimization = { ...this.DEFAULT_OPTIMIZATION, ...optimization };

      // Clone the element to avoid modifying the original
      const clone = element.cloneNode(true) as HTMLElement;

      // Apply optimizations
      await this.applyOptimizations(clone, finalOptimization);

      // Generate print-specific CSS
      const printCSS = this.generatePrintCSS(finalSettings, finalOptimization);

      // Estimate pages
      const estimatedPages = await this.estimatePages(clone, finalSettings);

      return {
        optimizedHtml: clone.outerHTML,
        css: printCSS,
        estimatedPages
      };
    } catch (error) {
      console.error('Error optimizing for print:', error);
      throw new Error('Failed to optimize document for printing');
    }
  }

  static async createPrintPreview(
    elementId: string,
    previewOptions: PrintPreviewOptions = {}
  ): Promise<string> {
    try {
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error(`Element with id "${elementId}" not found`);
      }

      // Apply preview-specific optimizations
      const optimization: PrintOptimizationOptions = {
        removeBackgrounds: true,
        simplifyStyles: true,
        optimizeImages: true,
        colorMode: previewOptions.showWatermark ? 'grayscale' : 'color'
      };

      const { optimizedHtml, css } = await this.optimizeForPrint(elementId, {}, optimization);

      // Create preview container
      const previewHTML = this.generatePreviewHTML(optimizedHtml, css, previewOptions);

      return previewHTML;
    } catch (error) {
      console.error('Error creating print preview:', error);
      throw new Error('Failed to create print preview');
    }
  }

  static async printWithDialog(
    elementId: string,
    settings: Partial<PrintSettings> = {},
    optimization: Partial<PrintOptimizationOptions> = {}
  ): Promise<void> {
    try {
      const { optimizedHtml, css } = await this.optimizeForPrint(elementId, settings, optimization);

      // Create a temporary print window
      const printWindow = window.open('', '_blank');
      if (!printWindow) {
        throw new Error('Failed to open print window');
      }

      // Write content to print window
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Print Document</title>
          <style>${css}</style>
        </head>
        <body>
          ${optimizedHtml}
        </body>
        </html>
      `);

      printWindow.document.close();

      // Wait for content to load, then print
      printWindow.onload = () => {
        printWindow.print();
        printWindow.close();
      };
    } catch (error) {
      console.error('Error printing with dialog:', error);
      throw new Error('Failed to print document');
    }
  }

  static async generatePrintPDF(
    elementId: string,
    settings: Partial<PrintSettings> = {},
    optimization: Partial<PrintOptimizationOptions> = {},
    filename: string = 'document.pdf'
  ): Promise<void> {
    try {
      const pdfConfig = {
        quality: settings.quality === 'high' ? 0.95 : settings.quality === 'draft' ? 0.7 : 0.85,
        margins: `${settings.margins?.top || 20}mm ${settings.margins?.right || 20}mm ${settings.margins?.bottom || 20}mm ${settings.margins?.left || 20}mm`,
        dpi: settings.quality === 'high' ? 300 : settings.quality === 'draft' ? 150 : 200,
        format: settings.pageSize || 'A4',
        orientation: settings.orientation || 'portrait'
      };

      await PDFUtils.generatePDFFromElement(elementId, pdfConfig, filename);
    } catch (error) {
      console.error('Error generating print PDF:', error);
      throw new Error('Failed to generate print PDF');
    }
  }

  static async batchPrint(
    elementIds: string[],
    settings: Partial<PrintSettings> = {},
    optimization: Partial<PrintOptimizationOptions> = {}
  ): Promise<PrintJob[]> {
    const jobs: PrintJob[] = [];

    for (let i = 0; i < elementIds.length; i++) {
      const elementId = elementIds[i];
      const job: PrintJob = {
        id: this.generateJobId(),
        title: `Print Job ${i + 1}`,
        content: '',
        settings: { ...this.DEFAULT_SETTINGS, ...settings },
        optimization: { ...this.DEFAULT_OPTIMIZATION, ...optimization },
        createdAt: new Date(),
        status: 'pending'
      };

      try {
        job.status = 'processing';

        const { optimizedHtml, estimatedPages } = await this.optimizeForPrint(elementId, settings, optimization);
        job.content = optimizedHtml;
        job.pages = estimatedPages;
        job.estimatedTime = estimatedPages * 2; // Estimate 2 seconds per page

        job.status = 'completed';
      } catch (error) {
        job.status = 'failed';
        console.error(`Failed to process print job for ${elementId}:`, error);
      }

      jobs.push(job);
    }

    return jobs;
  }

  static async detectPrintIssues(
    elementId: string
  ): Promise<{
    issues: PrintIssue[];
    recommendations: string[];
    score: number;
  }> {
    try {
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error(`Element with id "${elementId}" not found`);
      }

      const issues: PrintIssue[] = [];
      const recommendations: string[] = [];
      let score = 100;

      // Check for common print issues
      await this.checkContentOverflow(element, issues, score);
      await this.checkImageOptimization(element, issues, score);
      await this.checkColorContrast(element, issues, score);
      await this.checkFontEmbedding(element, issues, score);
      await this.checkLayoutIssues(element, issues, score);

      // Generate recommendations based on issues
      recommendations.push(...this.generateRecommendations(issues));

      // Calculate score
      score = Math.max(0, 100 - (issues.length * 10));

      return {
        issues,
        recommendations,
        score
      };
    } catch (error) {
      console.error('Error detecting print issues:', error);
      return {
        issues: [],
        recommendations: ['Unable to analyze document for print issues'],
        score: 0
      };
    }
  }

  private static async applyOptimizations(
    element: HTMLElement,
    optimization: PrintOptimizationOptions
  ): Promise<void> {
    // Remove backgrounds if specified
    if (optimization.removeBackgrounds) {
      this.removeBackgrounds(element);
    }

    // Remove animations
    if (optimization.removeAnimations) {
      this.removeAnimations(element);
    }

    // Simplify styles
    if (optimization.simplifyStyles) {
      this.simplifyStyles(element);
    }

    // Optimize images
    if (optimization.optimizeImages) {
      await this.optimizeImages(element);
    }

    // Handle color mode
    if (optimization.colorMode) {
      this.applyColorMode(element, optimization.colorMode);
    }
  }

  private static generatePrintCSS(
    settings: PrintSettings,
    optimization: PrintOptimizationOptions
  ): string {
    const margins = settings.margins;

    return `
      @page {
        size: ${settings.pageSize} ${settings.orientation};
        margin: ${margins.top}mm ${margins.right}mm ${margins.bottom}mm ${margins.left}mm;
        ${settings.duplex ? 'marks: crop cross;' : ''}
      }

      @media print {
        * {
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
          color-adjust: exact !important;
        }

        body {
          margin: 0;
          padding: 0;
          background: ${settings.backgroundColor === 'white' ? 'white' : 'none'};
          font-family: 'Times New Roman', serif;
          line-height: 1.5;
        }

        .no-print {
          display: none !important;
        }

        .page-break {
          page-break-before: always;
        }

        .avoid-break {
          page-break-inside: avoid;
        }

        .print-break-after {
          page-break-after: always;
        }

        /* Header and Footer styles */
        .print-header {
          position: running(header);
          border-bottom: 1px solid #ccc;
          padding-bottom: 10px;
          margin-bottom: 20px;
        }

        .print-footer {
          position: running(footer);
          border-top: 1px solid #ccc;
          padding-top: 10px;
          margin-top: 20px;
        }

        @page {
          @top-center {
            content: element(header);
          }
          @bottom-center {
            content: element(footer);
          }
        }

        /* Page numbers */
        .page-number::after {
          content: counter(page);
        }

        .total-pages::after {
          content: counter(pages);
        }

        /* Image optimization */
        img {
          max-width: 100%;
          height: auto;
          display: block;
          ${optimization.optimizeImages ? 'image-rendering: crisp-edges;' : ''}
        }

        /* Table optimization */
        table {
          border-collapse: collapse;
          width: 100%;
        }

        table, th, td {
          border: 1px solid #ddd;
        }

        th, td {
          padding: 8px;
          text-align: left;
        }

        /* Color mode adjustments */
        ${optimization.colorMode === 'grayscale' ? `
          * {
            filter: grayscale(100%) !important;
          }
        ` : ''}

        ${optimization.colorMode === 'blackAndWhite' ? `
          * {
            filter: grayscale(100%) contrast(200%) !important;
          }
        ` : ''}

        /* Font embedding */
        ${optimization.fontEmbedding ? `
          @font-face {
            font-family: 'CustomFont';
            src: local('CustomFont');
          }
        ` : ''}

        /* Quality adjustments */
        ${settings.quality === 'draft' ? `
          * {
            font-weight: normal !important;
            text-decoration: none !important;
          }
        ` : ''}
      }
    `;
  }

  private static generatePreviewHTML(
    content: string,
    css: string,
    options: PrintPreviewOptions
  ): string {
    const zoom = options.zoom || 100;
    const showPageBreaks = options.showPageBreaks ?? true;
    const showMargins = options.showMargins ?? false;

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Print Preview</title>
        <style>
          body {
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
            font-family: Arial, sans-serif;
          }

          .preview-container {
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            transform: scale(${zoom / 100});
            transform-origin: top left;
            max-width: ${zoom}%;
            overflow: hidden;
          }

          .preview-content {
            ${showPageBreaks ? 'box-shadow: 0 0 0 1px rgba(0,0,0,0.1);' : ''}
            ${showMargins ? 'padding: 20mm;' : ''}
          }

          ${css}

          ${options.showWatermark ? `
            .watermark {
              position: fixed;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%) rotate(-45deg);
              font-size: 48px;
              color: rgba(0,0,0,0.1);
              pointer-events: none;
              z-index: 1000;
              white-space: nowrap;
            }
          ` : ''}
        </style>
      </head>
      <body>
        ${options.showWatermark ? '<div class="watermark">PREVIEW</div>' : ''}
        <div class="preview-container">
          <div class="preview-content">
            ${content}
          </div>
        </div>
      </body>
      </html>
    `;
  }

  private static async estimatePages(element: HTMLElement, settings: PrintSettings): Promise<number> {
    // This is a simplified estimation
    // In a real implementation, you would use more sophisticated algorithms
    const lineHeight = 16; // Approximate line height in pixels
    const pageHeight = this.getPageHeightInPixels(settings.pageSize);
    const effectiveHeight = pageHeight - (settings.margins.top + settings.margins.bottom) * 3.78; // Convert mm to pixels

    const elementHeight = element.scrollHeight;
    const estimatedPages = Math.ceil(elementHeight / effectiveHeight);

    return Math.max(1, estimatedPages);
  }

  private static getPageHeightInPixels(pageSize: string): number {
    const sizes: Record<string, number> = {
      'A4': 1123, // 297mm in pixels at 96dpi
      'A3': 1587, // 420mm in pixels at 96dpi
      'Letter': 1056, // 11 inches in pixels at 96dpi
      'Legal': 1344 // 14 inches in pixels at 96dpi
    };

    return sizes[pageSize] || 1123;
  }

  private static removeBackgrounds(element: HTMLElement): void {
    const allElements = element.querySelectorAll('*');
    allElements.forEach(el => {
      const htmlElement = el as HTMLElement;
      htmlElement.style.background = 'transparent';
      htmlElement.style.backgroundColor = 'transparent';
    });
  }

  private static removeAnimations(element: HTMLElement): void {
    const animatedElements = element.querySelectorAll('*');
    animatedElements.forEach(el => {
      const htmlElement = el as HTMLElement;
      htmlElement.style.animation = 'none';
      htmlElement.style.transition = 'none';
      htmlElement.style.transform = 'none';
    });
  }

  private static simplifyStyles(element: HTMLElement): void {
    const styledElements = element.querySelectorAll('*');
    styledElements.forEach(el => {
      const htmlElement = el as HTMLElement;
      // Remove complex styles that might cause printing issues
      htmlElement.style.boxShadow = 'none';
      htmlElement.style.textShadow = 'none';
      htmlElement.style.borderRadius = '0';
      htmlElement.style.filter = 'none';
    });
  }

  private static async optimizeImages(element: HTMLElement): Promise<void> {
    const images = element.querySelectorAll('img');
    for (const img of images) {
      const imageElement = img as HTMLImageElement;
      // Wait for image to load
      if (!imageElement.complete) {
        await new Promise((resolve) => {
          imageElement.onload = resolve;
          imageElement.onerror = resolve;
        });
      }

      // Optimize for print
      imageElement.style.imageRendering = 'crisp-edges';
      imageElement.style.maxWidth = '100%';
      imageElement.style.height = 'auto';
    }
  }

  private static applyColorMode(element: HTMLElement, colorMode: string): void {
    if (colorMode === 'grayscale' || colorMode === 'blackAndWhite') {
      element.style.filter = colorMode === 'grayscale' ? 'grayscale(100%)' : 'grayscale(100%) contrast(200%)';
    }
  }

  private static async checkContentOverflow(
    element: HTMLElement,
    issues: PrintIssue[],
    score: number
  ): Promise<void> {
    // Check for elements that might overflow pages
    const elements = element.querySelectorAll('table, img, pre, code');
    elements.forEach(el => {
      const htmlElement = el as HTMLElement;
      if (htmlElement.scrollWidth > htmlElement.offsetWidth) {
        issues.push({
          type: 'overflow',
          element: el.tagName.toLowerCase(),
          severity: 'high',
          message: 'Element may overflow page boundaries',
          suggestion: 'Consider resizing or reformatting this element'
        });
        score -= 15;
      }
    });
  }

  private static async checkImageOptimization(
    element: HTMLElement,
    issues: PrintIssue[],
    score: number
  ): Promise<void> {
    const images = element.querySelectorAll('img');
    images.forEach(img => {
      const imageElement = img as HTMLImageElement;
      if (imageElement.naturalWidth > 1200) {
        issues.push({
          type: 'image_size',
          element: 'img',
          severity: 'medium',
          message: 'Image is larger than necessary for print',
          suggestion: 'Resize image to reduce file size and improve print quality'
        });
        score -= 10;
      }
    });
  }

  private static async checkColorContrast(
    element: HTMLElement,
    issues: PrintIssue[],
    score: number
  ): Promise<void> {
    // Simplified color contrast check
    const textElements = element.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6');
    textElements.forEach(el => {
      const htmlElement = el as HTMLElement;
      const style = window.getComputedStyle(htmlElement);
      const backgroundColor = style.backgroundColor;
      const color = style.color;

      if (this.isLowContrast(color, backgroundColor)) {
        issues.push({
          type: 'contrast',
          element: el.tagName.toLowerCase(),
          severity: 'medium',
          message: 'Low color contrast may affect readability',
          suggestion: 'Use darker text on lighter backgrounds or vice versa'
        });
        score -= 10;
      }
    });
  }

  private static async checkFontEmbedding(
    element: HTMLElement,
    issues: PrintIssue[],
    score: number
  ): Promise<void> {
    // Check for custom fonts that might not be available when printing
    const elements = element.querySelectorAll('*');
    const customFonts = new Set<string>();

    elements.forEach(el => {
      const style = window.getComputedStyle(el as HTMLElement);
      const fontFamily = style.fontFamily;
      if (!this.isSystemFont(fontFamily)) {
        customFonts.add(fontFamily);
      }
    });

    if (customFonts.size > 0) {
      issues.push({
        type: 'fonts',
        element: 'document',
        severity: 'low',
        message: `Custom fonts detected: ${Array.from(customFonts).join(', ')}`,
        suggestion: 'Ensure fonts are embedded or use system fonts for better compatibility'
      });
      score -= 5;
    }
  }

  private static async checkLayoutIssues(
    element: HTMLElement,
    issues: PrintIssue[],
    score: number
  ): Promise<void> {
    // Check for common layout issues
    const tables = element.querySelectorAll('table');
    tables.forEach(table => {
      const rows = table.querySelectorAll('tr');
      if (rows.length > 50) {
        issues.push({
          type: 'layout',
          element: 'table',
          severity: 'high',
          message: 'Large table may span multiple pages',
          suggestion: 'Consider splitting the table or using landscape orientation'
        });
        score -= 20;
      }
    });
  }

  private static isLowContrast(color1: string, color2: string): boolean {
    // Simplified contrast check
    return Math.random() > 0.8; // Placeholder
  }

  private static isSystemFont(fontFamily: string): boolean {
    const systemFonts = [
      'Arial', 'Helvetica', 'Times New Roman', 'Times',
      'Courier New', 'Courier', 'Georgia', 'Verdana',
      'Palatino', 'Garamond', 'Bookman', 'Comic Sans MS',
      'Trebuchet MS', 'Arial Black', 'Impact'
    ];

    return systemFonts.some(font => fontFamily.includes(font));
  }

  private static generateRecommendations(issues: PrintIssue[]): string[] {
    const recommendations: string[] = [];

    const issueTypes = issues.map(issue => issue.type);
    const uniqueTypes = [...new Set(issueTypes)];

    if (uniqueTypes.includes('overflow')) {
      recommendations.push('Check content that may overflow page boundaries');
    }

    if (uniqueTypes.includes('image_size')) {
      recommendations.push('Optimize images for print to reduce file size');
    }

    if (uniqueTypes.includes('contrast')) {
      recommendations.push('Improve color contrast for better readability');
    }

    if (uniqueTypes.includes('fonts')) {
      recommendations.push('Use system fonts or ensure proper font embedding');
    }

    if (uniqueTypes.includes('layout')) {
      recommendations.push('Consider adjusting layout for multi-page documents');
    }

    return recommendations;
  }

  private static generateJobId(): string {
    return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

interface PrintIssue {
  type: string;
  element: string;
  severity: 'low' | 'medium' | 'high';
  message: string;
  suggestion: string;
}
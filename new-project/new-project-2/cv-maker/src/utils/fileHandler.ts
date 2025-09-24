import { FileUploadConfig, ImageCropConfig } from '../types/common';

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
  speed: number; // bytes per second
  timeRemaining: number; // seconds
}

export interface FileMetadata {
  name: string;
  size: number;
  type: string;
  lastModified: number;
  extension: string;
  hash?: string;
  dimensions?: { width: number; height: number };
  duration?: number; // for video/audio files
  bitrate?: number; // for video/audio files
}

export interface SecureUploadOptions {
  maxFiles?: number;
  allowedTypes?: string[];
  maxSize?: number;
  requireHash?: boolean;
  virusScan?: boolean;
  sanitizeContent?: boolean;
  checkDimensions?: boolean;
  maxRetries?: number;
  chunkSize?: number;
  enableResumable?: boolean;
}

export interface UploadResult {
  success: boolean;
  file: File;
  metadata: FileMetadata;
  url?: string;
  error?: string;
  warnings?: string[];
}

export class FileHandler {
  static validateFile(file: File, config: FileUploadConfig): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Check file size
    if (file.size > config.maxSize) {
      errors.push(`File size must be less than ${config.maxSize / 1024 / 1024}MB`);
    }

    // Check file type
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    const isAllowedType = config.allowedTypes.some(type => {
      const typeExtension = type.split('/')[1];
      return typeExtension === fileExtension;
    });

    if (!isAllowedType) {
      errors.push(`File type not allowed. Allowed types: ${config.allowedTypes.join(', ')}`);
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  static readFileAsDataURL(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          resolve(e.target.result as string);
        } else {
          reject(new Error('Failed to read file'));
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(file);
    });
  }

  static readFileAsArrayBuffer(file: File): Promise<ArrayBuffer> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          resolve(e.target.result as ArrayBuffer);
        } else {
          reject(new Error('Failed to read file'));
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsArrayBuffer(file);
    });
  }

  static downloadFile(content: string | Blob, filename: string, mimeType?: string): void {
    const blob = typeof content === 'string'
      ? new Blob([content], { type: mimeType || 'text/plain' })
      : content;

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  static getFileExtension(filename: string): string {
    return filename.split('.').pop()?.toLowerCase() || '';
  }

  static sanitizeFilename(filename: string): string {
    return filename
      .replace(/[^a-z0-9.]/gi, '_')
      .replace(/_+/g, '_')
      .toLowerCase();
  }

  static async advancedFileUpload(
    files: FileList | File[],
    options: SecureUploadOptions = {},
    onProgress?: (progress: UploadProgress, fileIndex: number) => void
  ): Promise<UploadResult[]> {
    const results: UploadResult[] = [];
    const maxFiles = options.maxFiles || 10;
    const maxSize = options.maxSize || 10 * 1024 * 1024; // 10MB
    const allowedTypes = options.allowedTypes || [
      'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
      'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain', 'text/html'
    ];

    // Validate number of files
    if (files.length > maxFiles) {
      return [{
        success: false,
        file: files[0],
        metadata: await this.getFileMetadata(files[0]),
        error: `Maximum ${maxFiles} files allowed`
      }];
    }

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      try {
        const result = await this.processSingleFile(file, {
          ...options,
          maxSize,
          allowedTypes
        }, (progress) => {
          if (onProgress) {
            onProgress(progress, i);
          }
        });

        results.push(result);
      } catch (error) {
        results.push({
          success: false,
          file,
          metadata: await this.getFileMetadata(file),
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }

    return results;
  }

  private static async processSingleFile(
    file: File,
    options: SecureUploadOptions,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResult> {
    const warnings: string[] = [];
    const metadata = await this.getFileMetadata(file);

    // Enhanced validation
    if (options.allowedTypes && !options.allowedTypes.includes(file.type)) {
      throw new Error(`File type ${file.type} not allowed`);
    }

    if (options.maxSize && file.size > options.maxSize) {
      throw new Error(`File size exceeds limit of ${this.formatFileSize(options.maxSize)}`);
    }

    // Generate file hash for security
    let hash: string | undefined;
    if (options.requireHash) {
      hash = await this.generateFileHash(file);
      metadata.hash = hash;
    }

    // Check image dimensions if required
    if (options.checkDimensions && file.type.startsWith('image/')) {
      const dimensions = await this.getImageDimensions(file);
      metadata.dimensions = dimensions;

      if (dimensions.width > 4096 || dimensions.height > 4096) {
        warnings.push('Image dimensions exceed 4096px, may affect performance');
      }
    }

    // Simulate upload progress
    if (onProgress) {
      await this.simulateUploadProgress(file.size, onProgress);
    }

    // Create object URL for preview
    const url = URL.createObjectURL(file);

    return {
      success: true,
      file,
      metadata,
      url,
      warnings: warnings.length > 0 ? warnings : undefined
    };
  }

  static async getFileMetadata(file: File): Promise<FileMetadata> {
    const metadata: FileMetadata = {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified,
      extension: this.getFileExtension(file.name)
    };

    // Extract additional metadata for specific file types
    if (file.type.startsWith('image/')) {
      try {
        const dimensions = await this.getImageDimensions(file);
        metadata.dimensions = dimensions;
      } catch (error) {
        console.warn('Failed to get image dimensions:', error);
      }
    }

    if (file.type.startsWith('video/') || file.type.startsWith('audio/')) {
      try {
        const mediaMetadata = await this.getMediaMetadata(file);
        metadata.duration = mediaMetadata.duration;
        metadata.bitrate = mediaMetadata.bitrate;
      } catch (error) {
        console.warn('Failed to get media metadata:', error);
      }
    }

    return metadata;
  }

  private static async getImageDimensions(file: File): Promise<{ width: number; height: number }> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const url = URL.createObjectURL(file);

      img.onload = () => {
        resolve({
          width: img.naturalWidth,
          height: img.naturalHeight
        });
        URL.revokeObjectURL(url);
      };

      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('Failed to load image'));
      };

      img.src = url;
    });
  }

  private static async getMediaMetadata(file: File): Promise<{ duration: number; bitrate: number }> {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      const url = URL.createObjectURL(file);

      video.onloadedmetadata = () => {
        resolve({
          duration: video.duration,
          bitrate: 0 // Would need more complex calculation
        });
        URL.revokeObjectURL(url);
      };

      video.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('Failed to load media'));
      };

      video.src = url;
    });
  }

  private static async generateFileHash(file: File): Promise<string> {
    const buffer = await this.readFileAsArrayBuffer(file);
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  private static async simulateUploadProgress(
    totalSize: number,
    onProgress: (progress: UploadProgress) => void
  ): Promise<void> {
    return new Promise((resolve) => {
      let loaded = 0;
      const chunkSize = totalSize / 20; // 20 progress updates
      const startTime = Date.now();

      const updateProgress = () => {
        loaded += chunkSize;
        if (loaded > totalSize) loaded = totalSize;

        const elapsed = (Date.now() - startTime) / 1000;
        const speed = loaded / elapsed;
        const remaining = (totalSize - loaded) / speed;

        onProgress({
          loaded,
          total: totalSize,
          percentage: Math.round((loaded / totalSize) * 100),
          speed,
          timeRemaining: remaining
        });

        if (loaded < totalSize) {
          setTimeout(updateProgress, 100);
        } else {
          resolve();
        }
      };

      updateProgress();
    });
  }

  static async createFilePreview(
    file: File,
    maxWidth: number = 200,
    maxHeight: number = 200
  ): Promise<string> {
    if (!file.type.startsWith('image/')) {
      throw new Error('File is not an image');
    }

    return new Promise((resolve, reject) => {
      const img = new Image();
      const url = URL.createObjectURL(file);

      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        if (!ctx) {
          URL.revokeObjectURL(url);
          reject(new Error('Failed to create canvas context'));
          return;
        }

        // Calculate new dimensions
        let { width, height } = img;
        const ratio = Math.min(maxWidth / width, maxHeight / height);

        if (ratio < 1) {
          width *= ratio;
          height *= ratio;
        }

        canvas.width = width;
        canvas.height = height;

        // Draw image
        ctx.drawImage(img, 0, 0, width, height);

        // Get data URL
        const previewUrl = canvas.toDataURL('image/jpeg', 0.8);
        URL.revokeObjectURL(url);
        resolve(previewUrl);
      };

      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('Failed to load image'));
      };

      img.src = url;
    });
  }

  static async secureFileProcessing(
    file: File,
    options: {
      sanitize?: boolean;
      compress?: boolean;
      maxSize?: number;
      quality?: number;
    } = {}
  ): Promise<File> {
    let processedFile = file;

    // Sanitize filename
    const safeName = this.sanitizeFilename(file.name);
    if (safeName !== file.name) {
      processedFile = new File([processedFile], safeName, {
        type: processedFile.type,
        lastModified: processedFile.lastModified
      });
    }

    // Compress if it's an image
    if (options.compress && file.type.startsWith('image/')) {
      processedFile = await this.compressImage(processedFile, {
        quality: options.quality || 0.8,
        maxWidth: options.maxSize || 1920,
        maxHeight: options.maxSize || 1080
      });
    }

    return processedFile;
  }

  private static async compressImage(
    file: File,
    options: { quality: number; maxWidth: number; maxHeight: number }
  ): Promise<File> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const url = URL.createObjectURL(file);

      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        if (!ctx) {
          URL.revokeObjectURL(url);
          reject(new Error('Failed to create canvas context'));
          return;
        }

        // Calculate new dimensions
        let { width, height } = img;
        const ratio = Math.min(options.maxWidth / width, options.maxHeight / height);

        if (ratio < 1) {
          width *= ratio;
          height *= ratio;
        }

        canvas.width = width;
        canvas.height = height;

        // Draw image
        ctx.drawImage(img, 0, 0, width, height);

        // Convert to blob
        canvas.toBlob((blob) => {
          if (!blob) {
            URL.revokeObjectURL(url);
            reject(new Error('Failed to compress image'));
            return;
          }

          const compressedFile = new File([blob], file.name, {
            type: file.type,
            lastModified: Date.now()
          });

          URL.revokeObjectURL(url);
          resolve(compressedFile);
        }, file.type, options.quality);
      };

      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('Failed to load image'));
      };

      img.src = url;
    });
  }

  static async batchFileProcessing(
    files: File[],
    processor: (file: File) => Promise<File>,
    onProgress?: (processed: number, total: number) => void
  ): Promise<File[]> {
    const results: File[] = [];

    for (let i = 0; i < files.length; i++) {
      try {
        const processedFile = await processor(files[i]);
        results.push(processedFile);

        if (onProgress) {
          onProgress(i + 1, files.length);
        }
      } catch (error) {
        console.error(`Failed to process file ${files[i].name}:`, error);
        results.push(files[i]); // Keep original if processing fails
      }
    }

    return results;
  }

  static validateFileType(file: File, allowedTypes: string[]): boolean {
    return allowedTypes.some(type => {
      if (type.includes('*')) {
        const [mainType] = type.split('/');
        return file.type.startsWith(mainType + '/');
      }
      return file.type === type;
    });
  }

  static async checkFileSecurity(file: File): Promise<{ safe: boolean; threats: string[] }> {
    const threats: string[] = [];

    // Check file extension vs actual content type
    const extension = this.getFileExtension(file.name);
    const expectedTypes = this.getExpectedTypesForExtension(extension);

    if (!expectedTypes.includes(file.type)) {
      threats.push('File extension does not match content type');
    }

    // Check for suspicious file signatures
    if (await this.hasSuspiciousSignature(file)) {
      threats.push('File has suspicious signature');
    }

    // Check file size合理性
    if (file.size === 0) {
      threats.push('File is empty');
    }

    if (file.size > 100 * 1024 * 1024) { // 100MB
      threats.push('File is unusually large');
    }

    return {
      safe: threats.length === 0,
      threats
    };
  }

  private static getExpectedTypesForExtension(extension: string): string[] {
    const typeMap: Record<string, string[]> = {
      'jpg': ['image/jpeg'],
      'jpeg': ['image/jpeg'],
      'png': ['image/png'],
      'gif': ['image/gif'],
      'pdf': ['application/pdf'],
      'doc': ['application/msword'],
      'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
      'txt': ['text/plain'],
      'html': ['text/html']
    };

    return typeMap[extension] || [];
  }

  private static async hasSuspiciousSignature(file: File): Promise<boolean> {
    // This is a simplified check
    // In a real implementation, you would check file headers
    const buffer = await this.readFileAsArrayBuffer(file);
    const bytes = new Uint8Array(buffer.slice(0, 4)); // Check first 4 bytes

    // Common safe signatures
    const safeSignatures = [
      [0x89, 0x50, 0x4E, 0x47], // PNG
      [0xFF, 0xD8, 0xFF], // JPEG
      [0x25, 0x50, 0x44, 0x46], // PDF
      [0x3C, 0x3F, 0x78, 0x6D] // XML/HTML
    ];

    // Check if signature matches any known safe patterns
    for (const signature of safeSignatures) {
      let matches = true;
      for (let i = 0; i < signature.length && i < bytes.length; i++) {
        if (bytes[i] !== signature[i]) {
          matches = false;
          break;
        }
      }
      if (matches) return false;
    }

    return true; // Unknown signature, considered suspicious
  }
}
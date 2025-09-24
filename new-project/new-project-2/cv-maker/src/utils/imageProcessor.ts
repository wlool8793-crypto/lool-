import { ImageCropConfig } from '../types/common';

export interface PhotoMetadata {
  width: number;
  height: number;
  fileSize: number;
  format: string;
  quality: number;
  aspectRatio: number;
  hasTransparency?: boolean;
  dominantColor?: string;
  exif?: any;
}

export interface PhotoProcessingOptions {
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
  format?: 'jpeg' | 'png' | 'webp';
  preserveExif?: boolean;
  autoOrient?: boolean;
  removeBackground?: boolean;
  enhanceColors?: boolean;
  reduceNoise?: boolean;
  sharpen?: boolean;
}

export interface WatermarkOptions {
  text?: string;
  image?: string;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center';
  opacity?: number;
  fontSize?: number;
  color?: string;
  padding?: number;
  angle?: number;
}

export interface FaceDetectionOptions {
  detectFaces?: boolean;
  cropToFace?: boolean;
  facePadding?: number;
  blurOtherFaces?: boolean;
}

export class ImageProcessor {
  static async loadImage(src: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = src;
    });
  }

  static async resizeImage(
    image: HTMLImageElement,
    maxWidth: number,
    maxHeight: number,
    quality: number = 0.8
  ): Promise<string> {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    // Calculate new dimensions
    let { width, height } = image;

    if (width > maxWidth || height > maxHeight) {
      const ratio = Math.min(maxWidth / width, maxHeight / height);
      width *= ratio;
      height *= ratio;
    }

    // Set canvas dimensions
    canvas.width = width;
    canvas.height = height;

    // Draw resized image
    ctx.drawImage(image, 0, 0, width, height);

    // Convert to blob
    return new Promise((resolve, reject) => {
      canvas.toBlob(
        (blob) => {
          if (blob) {
            const reader = new FileReader();
            reader.onload = (e) => {
              if (e.target?.result) {
                resolve(e.target.result as string);
              } else {
                reject(new Error('Failed to convert image to data URL'));
              }
            };
            reader.onerror = () => reject(new Error('Failed to read blob'));
            reader.readAsDataURL(blob);
          } else {
            reject(new Error('Failed to create blob'));
          }
        },
        'image/jpeg',
        quality
      );
    });
  }

  static async cropImage(
    image: HTMLImageElement,
    cropConfig: ImageCropConfig,
    quality: number = 0.8
  ): Promise<string> {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    // Set canvas dimensions
    canvas.width = cropConfig.width;
    canvas.height = cropConfig.height;

    // Draw cropped image
    ctx.drawImage(
      image,
      cropConfig.x,
      cropConfig.y,
      cropConfig.width,
      cropConfig.height,
      0,
      0,
      cropConfig.width,
      cropConfig.height
    );

    // Convert to blob
    return new Promise((resolve, reject) => {
      canvas.toBlob(
        (blob) => {
          if (blob) {
            const reader = new FileReader();
            reader.onload = (e) => {
              if (e.target?.result) {
                resolve(e.target.result as string);
              } else {
                reject(new Error('Failed to convert image to data URL'));
              }
            };
            reader.onerror = () => reject(new Error('Failed to read blob'));
            reader.readAsDataURL(blob);
          } else {
            reject(new Error('Failed to create blob'));
          }
        },
        'image/jpeg',
        quality
      );
    });
  }

  static async optimizeImage(
    src: string,
    maxWidth: number,
    maxHeight: number,
    quality: number = 0.8
  ): Promise<string> {
    const image = await this.loadImage(src);
    return this.resizeImage(image, maxWidth, maxHeight, quality);
  }

  static async compressImage(
    src: string,
    quality: number = 0.8
  ): Promise<string> {
    const image = await this.loadImage(src);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    canvas.width = image.width;
    canvas.height = image.height;
    ctx.drawImage(image, 0, 0);

    return new Promise((resolve, reject) => {
      canvas.toBlob(
        (blob) => {
          if (blob) {
            const reader = new FileReader();
            reader.onload = (e) => {
              if (e.target?.result) {
                resolve(e.target.result as string);
              } else {
                reject(new Error('Failed to convert image to data URL'));
              }
            };
            reader.onerror = () => reject(new Error('Failed to read blob'));
            reader.readAsDataURL(blob);
          } else {
            reject(new Error('Failed to create blob'));
          }
        },
        'image/jpeg',
        quality
      );
    });
  }

  static async getImageDimensions(src: string): Promise<{ width: number; height: number }> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        resolve({
          width: img.width,
          height: img.height
        });
      };
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = src;
    });
  }

  static createThumbnail(
    src: string,
    size: number = 100,
    quality: number = 0.8
  ): Promise<string> {
    return this.optimizeImage(src, size, size, quality);
  }

  static async extractPhotoMetadata(file: File): Promise<PhotoMetadata> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const url = URL.createObjectURL(file);

      img.onload = () => {
        const metadata: PhotoMetadata = {
          width: img.naturalWidth,
          height: img.naturalHeight,
          fileSize: file.size,
          format: file.type.split('/')[1],
          quality: 1,
          aspectRatio: img.naturalWidth / img.naturalHeight
        };

        // Check for transparency
        if (file.type === 'image/png') {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          if (ctx) {
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            ctx.drawImage(img, 0, 0);
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const hasAlpha = imageData.data.some((_, index) => index % 4 === 3 && imageData.data[index] < 255);
            metadata.hasTransparency = hasAlpha;
          }
        }

        // Extract dominant color
        metadata.dominantColor = this.extractDominantColor(img);

        URL.revokeObjectURL(url);
        resolve(metadata);
      };

      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('Failed to load image'));
      };

      img.src = url;
    });
  }

  static async processPhoto(
    file: File,
    options: PhotoProcessingOptions = {}
  ): Promise<{ processedFile: File; metadata: PhotoMetadata }> {
    const metadata = await this.extractPhotoMetadata(file);
    let processedFile = file;

    // Auto-orientation
    if (options.autoOrient) {
      processedFile = await this.autoOrientImage(processedFile);
    }

    // Resize if needed
    if (options.maxWidth || options.maxHeight) {
      processedFile = await this.resizeFile(
        processedFile,
        options.maxWidth || metadata.width,
        options.maxHeight || metadata.height,
        options.quality || 0.8
      );
    }

    // Apply enhancements
    if (options.enhanceColors) {
      processedFile = await this.enhanceColors(processedFile);
    }

    if (options.reduceNoise) {
      processedFile = await this.reduceNoise(processedFile);
    }

    if (options.sharpen) {
      processedFile = await this.sharpenImage(processedFile);
    }

    // Convert format if needed
    if (options.format && !file.type.includes(options.format)) {
      processedFile = await this.convertFormat(processedFile, options.format, options.quality || 0.8);
    }

    return { processedFile, metadata };
  }

  static async addWatermark(
    file: File,
    watermark: WatermarkOptions
  ): Promise<File> {
    const img = await this.loadImage(URL.createObjectURL(file));
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    canvas.width = img.width;
    canvas.height = img.height;

    // Draw original image
    ctx.drawImage(img, 0, 0);

    // Apply watermark
    ctx.globalAlpha = watermark.opacity || 0.5;

    if (watermark.text) {
      this.addTextWatermark(ctx, watermark, canvas.width, canvas.height);
    }

    if (watermark.image) {
      await this.addImageWatermark(ctx, watermark, canvas.width, canvas.height);
    }

    ctx.globalAlpha = 1;

    return this.canvasToFile(canvas, file.name, file.type);
  }

  static async optimizeForPDF(
    file: File,
    options: {
      maxWidth?: number;
      maxHeight?: number;
      quality?: number;
      targetSize?: number; // in KB
    } = {}
  ): Promise<File> {
    const metadata = await this.extractPhotoMetadata(file);
    let processedFile = file;

    // Set default dimensions for PDF optimization
    const maxWidth = options.maxWidth || 800;
    const maxHeight = options.maxHeight || 1000;
    const quality = options.quality || 0.8;

    // First resize
    processedFile = await this.resizeFile(processedFile, maxWidth, maxHeight, quality);

    // If target size is specified, iteratively compress
    if (options.targetSize) {
      const targetBytes = options.targetSize * 1024;
      let currentQuality = quality;

      while (processedFile.size > targetBytes && currentQuality > 0.3) {
        currentQuality -= 0.1;
        processedFile = await this.compressFile(processedFile, currentQuality);
      }
    }

    return processedFile;
  }

  static async createMultipleThumbnails(
    file: File,
    sizes: number[] = [50, 100, 200, 400]
  ): Promise<{ size: number; url: string; file: File }[]> {
    const results = [];

    for (const size of sizes) {
      const thumbnail = await this.createThumbnail(
        URL.createObjectURL(file),
        size,
        0.8
      );

      const thumbnailFile = await this.dataURLtoFile(thumbnail, `thumb_${size}_${file.name}`, 'image/jpeg');

      results.push({
        size,
        url: thumbnail,
        file: thumbnailFile
      });
    }

    return results;
  }

  static async detectFaces(file: File): Promise<{ faces: any[]; processedImage?: File }> {
    // Note: This is a placeholder for face detection
    // In a real implementation, you would use a library like face-api.js or integrate with a service
    return {
      faces: [],
      processedImage: file
    };
  }

  static async removeBackground(file: File): Promise<File> {
    // Note: This is a placeholder for background removal
    // In a real implementation, you would use a library like remove.bg or similar
    return file;
  }

  private static extractDominantColor(img: HTMLImageElement): string {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) return '#000000';

    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    let r = 0, g = 0, b = 0;
    let count = 0;

    // Sample every 10th pixel for performance
    for (let i = 0; i < data.length; i += 40) {
      r += data[i];
      g += data[i + 1];
      b += data[i + 2];
      count++;
    }

    r = Math.floor(r / count);
    g = Math.floor(g / count);
    b = Math.floor(b / count);

    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  }

  private static async autoOrientImage(file: File): Promise<File> {
    // Placeholder for auto-orientation based on EXIF data
    return file;
  }

  private static async resizeFile(
    file: File,
    maxWidth: number,
    maxHeight: number,
    quality: number
  ): Promise<File> {
    const img = await this.loadImage(URL.createObjectURL(file));
    const resized = await this.resizeImage(img, maxWidth, maxHeight, quality);
    return this.dataURLtoFile(resized, file.name, 'image/jpeg');
  }

  private static async compressFile(file: File, quality: number): Promise<File> {
    const img = await this.loadImage(URL.createObjectURL(file));
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);

    return this.canvasToFile(canvas, file.name, 'image/jpeg', quality);
  }

  private static async enhanceColors(file: File): Promise<File> {
    const img = await this.loadImage(URL.createObjectURL(file));
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    // Simple color enhancement
    for (let i = 0; i < data.length; i += 4) {
      // Increase contrast slightly
      data[i] = Math.min(255, data[i] * 1.1);     // Red
      data[i + 1] = Math.min(255, data[i + 1] * 1.1); // Green
      data[i + 2] = Math.min(255, data[i + 2] * 1.1); // Blue
    }

    ctx.putImageData(imageData, 0, 0);

    return this.canvasToFile(canvas, file.name, file.type);
  }

  private static async reduceNoise(file: File): Promise<File> {
    const img = await this.loadImage(URL.createObjectURL(file));
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    // Simple noise reduction using 3x3 kernel
    for (let y = 1; y < canvas.height - 1; y++) {
      for (let x = 1; x < canvas.width - 1; x++) {
        for (let c = 0; c < 3; c++) {
          let sum = 0;
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              const idx = ((y + dy) * canvas.width + (x + dx)) * 4 + c;
              sum += data[idx];
            }
          }
          const idx = (y * canvas.width + x) * 4 + c;
          data[idx] = sum / 9; // Average of 3x3 neighborhood
        }
      }
    }

    ctx.putImageData(imageData, 0, 0);

    return this.canvasToFile(canvas, file.name, file.type);
  }

  private static async sharpenImage(file: File): Promise<File> {
    const img = await this.loadImage(URL.createObjectURL(file));
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    const width = canvas.width;
    const height = canvas.height;

    // Sharpen kernel
    const kernel = [
      0, -1, 0,
      -1, 5, -1,
      0, -1, 0
    ];

    const newData = new Uint8ClampedArray(data);

    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        for (let c = 0; c < 3; c++) {
          let sum = 0;
          for (let ky = -1; ky <= 1; ky++) {
            for (let kx = -1; kx <= 1; kx++) {
              const idx = ((y + ky) * width + (x + kx)) * 4 + c;
              const kernelIdx = (ky + 1) * 3 + (kx + 1);
              sum += data[idx] * kernel[kernelIdx];
            }
          }
          const idx = (y * width + x) * 4 + c;
          newData[idx] = Math.max(0, Math.min(255, sum));
        }
      }
    }

    const newImageData = new ImageData(newData, width, height);
    ctx.putImageData(newImageData, 0, 0);

    return this.canvasToFile(canvas, file.name, file.type);
  }

  private static async convertFormat(file: File, format: 'jpeg' | 'png' | 'webp', quality: number): Promise<File> {
    const img = await this.loadImage(URL.createObjectURL(file));
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);

    const mimeType = `image/${format}`;
    return this.canvasToFile(canvas, file.name.replace(/\.[^/.]+$/, `.${format}`), mimeType, quality);
  }

  private static addTextWatermark(
    ctx: CanvasRenderingContext2D,
    watermark: WatermarkOptions,
    width: number,
    height: number
  ): void {
    if (!watermark.text) return;

    ctx.font = `${watermark.fontSize || 24}px Arial`;
    ctx.fillStyle = watermark.color || '#ffffff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    let x = width / 2;
    let y = height / 2;
    const padding = watermark.padding || 20;

    switch (watermark.position) {
      case 'top-left':
        x = padding;
        y = padding;
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        break;
      case 'top-right':
        x = width - padding;
        y = padding;
        ctx.textAlign = 'right';
        ctx.textBaseline = 'top';
        break;
      case 'bottom-left':
        x = padding;
        y = height - padding;
        ctx.textAlign = 'left';
        ctx.textBaseline = 'bottom';
        break;
      case 'bottom-right':
        x = width - padding;
        y = height - padding;
        ctx.textAlign = 'right';
        ctx.textBaseline = 'bottom';
        break;
    }

    if (watermark.angle) {
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate((watermark.angle * Math.PI) / 180);
      ctx.fillText(watermark.text, 0, 0);
      ctx.restore();
    } else {
      ctx.fillText(watermark.text, x, y);
    }
  }

  private static async addImageWatermark(
    ctx: CanvasRenderingContext2D,
    watermark: WatermarkOptions,
    width: number,
    height: number
  ): Promise<void> {
    if (!watermark.image) return;

    const watermarkImg = await this.loadImage(watermark.image);
    const padding = watermark.padding || 20;
    const maxSize = Math.min(width, height) * 0.2; // Max 20% of image size

    let wmWidth = watermarkImg.width;
    let wmHeight = watermarkImg.height;

    // Scale watermark to fit
    if (wmWidth > maxSize || wmHeight > maxSize) {
      const ratio = Math.min(maxSize / wmWidth, maxSize / wmHeight);
      wmWidth *= ratio;
      wmHeight *= ratio;
    }

    let x = width / 2 - wmWidth / 2;
    let y = height / 2 - wmHeight / 2;

    switch (watermark.position) {
      case 'top-left':
        x = padding;
        y = padding;
        break;
      case 'top-right':
        x = width - wmWidth - padding;
        y = padding;
        break;
      case 'bottom-left':
        x = padding;
        y = height - wmHeight - padding;
        break;
      case 'bottom-right':
        x = width - wmWidth - padding;
        y = height - wmHeight - padding;
        break;
    }

    ctx.drawImage(watermarkImg, x, y, wmWidth, wmHeight);
  }

  private static canvasToFile(
    canvas: HTMLCanvasElement,
    filename: string,
    mimeType: string,
    quality: number = 0.8
  ): Promise<File> {
    return new Promise((resolve, reject) => {
      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(new File([blob], filename, { type: mimeType }));
          } else {
            reject(new Error('Failed to create blob'));
          }
        },
        mimeType,
        quality
      );
    });
  }

  private static dataURLtoFile(dataURL: string, filename: string, mimeType: string): Promise<File> {
    return new Promise((resolve, reject) => {
      fetch(dataURL)
        .then(res => res.blob())
        .then(blob => {
          resolve(new File([blob], filename, { type: mimeType }));
        })
        .catch(reject);
    });
  }
}
import {
  SecurePhoto,
  PhotoAccessPermissions,
  TemporaryAccess,
  EncryptedData
} from '../types/encryption';
import { EncryptionUtils } from './encryptionUtils';
import DOMPurify from 'dompurify';

export interface PhotoWatermarkConfig {
  text: string;
  fontSize: number;
  fontFamily: string;
  color: string;
  opacity: number;
  position: 'center' | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  rotation: number;
}

export interface PhotoBlurConfig {
  enabled: boolean;
  level: number; // 0-100
  blurType: 'gaussian' | 'pixelate' | 'mosaic';
  excludeAreas?: Array<{
    x: number;
    y: number;
    width: number;
    height: number;
  }>;
}

export interface PhotoProtectionSettings {
  watermark: PhotoWatermarkConfig;
  blur: PhotoBlurConfig;
  accessControl: PhotoAccessPermissions;
  encryption: {
    enabled: boolean;
    keyId: string;
  };
  metadata: {
    stripExif: boolean;
    stripGps: boolean;
    stripPersonal: boolean;
  };
}

export class PhotoProtectionUtils {
  private static readonly DEFAULT_WATERMARK: PhotoWatermarkConfig = {
    text: 'Confidential',
    fontSize: 16,
    fontFamily: 'Arial',
    color: '#000000',
    opacity: 0.3,
    position: 'center',
    rotation: -45
  };

  private static readonly DEFAULT_BLUR: PhotoBlurConfig = {
    enabled: false,
    level: 0,
    blurType: 'gaussian'
  };

  private static readonly DEFAULT_ACCESS_CONTROL: PhotoAccessPermissions = {
    owner: 'full',
    family: 'view',
    contacts: 'view',
    public: 'none',
    temporaryAccess: []
  };

  static async createSecurePhoto(
    file: File,
    settings: PhotoProtectionSettings,
    userId: string
  ): Promise<SecurePhoto> {
    const encryptedContent = await this.encryptPhoto(file, settings.encryption);
    const thumbnail = await this.createThumbnail(file, settings);
    const encryptedThumbnail = thumbnail ? await this.encryptPhoto(thumbnail, settings.encryption) : undefined;

    const metadata = await this.extractPhotoMetadata(file, settings);
    const accessPermissions = this.createAccessPermissions(settings.accessControl, userId);

    return {
      id: EncryptionUtils.generateSecureId('photo'),
      originalName: file.name,
      encryptedContent,
      thumbnail: encryptedThumbnail,
      metadata,
      accessPermissions,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
  }

  static async applyWatermark(
    imageElement: HTMLImageElement,
    config: PhotoWatermarkConfig
  ): Promise<string> {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Canvas context not available');
    }

    canvas.width = imageElement.width;
    canvas.height = imageElement.height;

    // Draw original image
    ctx.drawImage(imageElement, 0, 0);

    // Apply watermark
    ctx.save();
    ctx.globalAlpha = config.opacity;
    ctx.fillStyle = config.color;
    ctx.font = `${config.fontSize}px ${config.fontFamily}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Calculate position
    const position = this.calculateWatermarkPosition(canvas.width, canvas.height, config);

    // Apply rotation if needed
    if (config.rotation !== 0) {
      ctx.translate(position.x, position.y);
      ctx.rotate((config.rotation * Math.PI) / 180);
      ctx.fillText(config.text, 0, 0);
      ctx.restore();
    } else {
      ctx.fillText(config.text, position.x, position.y);
      ctx.restore();
    }

    return canvas.toDataURL();
  }

  static async applyBlur(
    imageElement: HTMLImageElement,
    config: PhotoBlurConfig
  ): Promise<string> {
    if (!config.enabled || config.level === 0) {
      return imageElement.src;
    }

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Canvas context not available');
    }

    canvas.width = imageElement.width;
    canvas.height = imageElement.height;

    // Draw original image
    ctx.drawImage(imageElement, 0, 0);

    // Apply blur based on type
    switch (config.blurType) {
      case 'gaussian':
        ctx.filter = `blur(${config.level / 10}px)`;
        break;
      case 'pixelate':
        ctx.imageSmoothingEnabled = false;
        // Pixelate effect by scaling down and up
        const pixelSize = Math.max(1, Math.floor(config.level / 10));
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        if (tempCtx) {
          tempCanvas.width = Math.ceil(canvas.width / pixelSize);
          tempCanvas.height = Math.ceil(canvas.height / pixelSize);
          tempCtx.drawImage(canvas, 0, 0, tempCanvas.width, tempCanvas.height);
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(tempCanvas, 0, 0, canvas.width, canvas.height);
        }
        return canvas.toDataURL();
      case 'mosaic':
        return this.applyMosaicBlur(canvas, ctx, config.level);
    }

    return canvas.toDataURL();
  }

  static async stripMetadata(
    file: File,
    settings: PhotoProtectionSettings['metadata']
  ): Promise<File> {
    if (!settings.stripExif && !settings.stripGps && !settings.stripPersonal) {
      return file;
    }

    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');

          if (!ctx) {
            resolve(file);
            return;
          }

          canvas.width = img.width;
          canvas.height = img.height;
          ctx.drawImage(img, 0, 0);

          canvas.toBlob((blob) => {
            if (blob) {
              const cleanFile = new File([blob], file.name, {
                type: file.type,
                lastModified: Date.now()
              });
              resolve(cleanFile);
            } else {
              resolve(file);
            }
          }, file.type);
        };
        img.src = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    });
  }

  static validatePhotoAccess(
    photo: SecurePhoto,
    userId: string,
    userRole: string,
    relationship: string = 'public'
  ): { canView: boolean; canDownload: boolean } {
    let canView = false;
    let canDownload = false;

    // Check owner access
    if (photo.metadata.encryptedBy === userId) {
      canView = true;
      canDownload = true;
    }

    // Check relationship-based access
    if (!canView) {
      switch (relationship) {
        case 'family':
          canView = photo.accessPermissions.family === 'view' || photo.accessPermissions.family === 'download';
          canDownload = photo.accessPermissions.family === 'download';
          break;
        case 'contacts':
          canView = photo.accessPermissions.contacts === 'view' || photo.accessPermissions.contacts === 'download';
          canDownload = photo.accessPermissions.contacts === 'download';
          break;
        case 'public':
          canView = photo.accessPermissions.public === 'view' || photo.accessPermissions.public === 'download';
          canDownload = photo.accessPermissions.public === 'download';
          break;
      }
    }

    // Check temporary access
    if (!canView) {
      const tempAccess = photo.accessPermissions.temporaryAccess.find(
        access => access.grantedTo === userId && access.isActive && new Date(access.expiresAt) > new Date()
      );

      if (tempAccess) {
        canView = tempAccess.permissions === 'view' || tempAccess.permissions === 'download';
        canDownload = tempAccess.permissions === 'download';
      }
    }

    return { canView, canDownload };
  }

  static grantTemporaryAccess(
    photo: SecurePhoto,
    grantedTo: string,
    grantedBy: string,
    permissions: 'view' | 'download',
    expiresAt: string,
    maxAccessCount?: number
  ): SecurePhoto {
    const newAccess: TemporaryAccess = {
      id: EncryptionUtils.generateSecureId('access'),
      grantedTo,
      grantedBy,
      permissions,
      expiresAt,
      isActive: true,
      accessCount: 0,
      maxAccessCount
    };

    photo.accessPermissions.temporaryAccess.push(newAccess);
    photo.updatedAt = new Date().toISOString();

    return photo;
  }

  static revokeTemporaryAccess(photo: SecurePhoto, accessId: string): SecurePhoto {
    const accessIndex = photo.accessPermissions.temporaryAccess.findIndex(
      access => access.id === accessId
    );

    if (accessIndex !== -1) {
      photo.accessPermissions.temporaryAccess[accessIndex].isActive = false;
      photo.updatedAt = new Date().toISOString();
    }

    return photo;
  }

  static async createPhotoPreview(
    photo: SecurePhoto,
    key: string,
    settings: PhotoProtectionSettings
  ): Promise<string> {
    const decryptedContent = await EncryptionUtils.decryptData(photo.encryptedContent, key);
    const imageElement = await this.loadImageFromBase64(decryptedContent);

    // Apply watermark if enabled
    if (settings.watermark.text) {
      return this.applyWatermark(imageElement, settings.watermark);
    }

    // Apply blur if enabled
    if (settings.blur.enabled && settings.blur.level > 0) {
      return this.applyBlur(imageElement, settings.blur);
    }

    return decryptedContent;
  }

  private static async encryptPhoto(
    file: File,
    encryptionSettings: PhotoProtectionSettings['encryption']
  ): Promise<EncryptedData> {
    if (!encryptionSettings.enabled) {
      throw new Error('Encryption is not enabled');
    }

    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const base64Data = e.target?.result as string;
          const key = EncryptionUtils.generateSecureToken(32);
          const encrypted = await EncryptionUtils.encryptData(base64Data, key);
          resolve(encrypted);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(file);
    });
  }

  private static async createThumbnail(
    file: File,
    settings: PhotoProtectionSettings
  ): Promise<File | null> {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');

          if (!ctx) {
            resolve(null);
            return;
          }

          // Create thumbnail (max 200x200)
          const maxSize = 200;
          let width = img.width;
          let height = img.height;

          if (width > height) {
            if (width > maxSize) {
              height *= maxSize / width;
              width = maxSize;
            }
          } else {
            if (height > maxSize) {
              width *= maxSize / height;
              height = maxSize;
            }
          }

          canvas.width = width;
          canvas.height = height;
          ctx.drawImage(img, 0, 0, width, height);

          canvas.toBlob((blob) => {
            if (blob) {
              const thumbnailFile = new File([blob], `thumb_${file.name}`, {
                type: file.type,
                lastModified: Date.now()
              });
              resolve(thumbnailFile);
            } else {
              resolve(null);
            }
          }, file.type, 0.8);
        };
        img.src = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    });
  }

  private static async extractPhotoMetadata(
    file: File,
    settings: PhotoProtectionSettings
  ): Promise<SecurePhoto['metadata']> {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          resolve({
            mimeType: file.type,
            width: img.width,
            height: img.height,
            size: file.size,
            checksum: EncryptionUtils.generateSecureToken(16),
            encryptedBy: 'system',
            encryptedAt: new Date().toISOString(),
            watermark: settings.watermark.text.length > 0,
            blurLevel: settings.blur.enabled ? settings.blur.level : 0
          });
        };
        img.src = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    });
  }

  private static createAccessPermissions(
    accessControl: PhotoAccessPermissions,
    userId: string
  ): PhotoAccessPermissions {
    return {
      ...accessControl,
      temporaryAccess: accessControl.temporaryAccess.filter(access =>
        new Date(access.expiresAt) > new Date()
      )
    };
  }

  private static calculateWatermarkPosition(
    width: number,
    height: number,
    config: PhotoWatermarkConfig
  ): { x: number; y: number } {
    switch (config.position) {
      case 'center':
        return { x: width / 2, y: height / 2 };
      case 'top-left':
        return { x: 50, y: 50 };
      case 'top-right':
        return { x: width - 50, y: 50 };
      case 'bottom-left':
        return { x: 50, y: height - 50 };
      case 'bottom-right':
        return { x: width - 50, y: height - 50 };
      default:
        return { x: width / 2, y: height / 2 };
    }
  }

  private static applyMosaicBlur(
    canvas: HTMLCanvasElement,
    ctx: CanvasRenderingContext2D,
    level: number
  ): string {
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    const blockSize = Math.max(2, Math.floor(level / 5));

    for (let y = 0; y < canvas.height; y += blockSize) {
      for (let x = 0; x < canvas.width; x += blockSize) {
        // Get average color for this block
        let r = 0, g = 0, b = 0, a = 0;
        let count = 0;

        for (let dy = 0; dy < blockSize && y + dy < canvas.height; dy++) {
          for (let dx = 0; dx < blockSize && x + dx < canvas.width; dx++) {
            const idx = ((y + dy) * canvas.width + (x + dx)) * 4;
            r += data[idx];
            g += data[idx + 1];
            b += data[idx + 2];
            a += data[idx + 3];
            count++;
          }
        }

        r = Math.floor(r / count);
        g = Math.floor(g / count);
        b = Math.floor(b / count);
        a = Math.floor(a / count);

        // Fill the block with average color
        for (let dy = 0; dy < blockSize && y + dy < canvas.height; dy++) {
          for (let dx = 0; dx < blockSize && x + dx < canvas.width; dx++) {
            const idx = ((y + dy) * canvas.width + (x + dx)) * 4;
            data[idx] = r;
            data[idx + 1] = g;
            data[idx + 2] = b;
            data[idx + 3] = a;
          }
        }
      }
    }

    ctx.putImageData(imageData, 0, 0);
    return canvas.toDataURL();
  }

  private static loadImageFromBase64(base64: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = base64;
    });
  }

  static sanitizePhotoName(filename: string): string {
    return DOMPurify.sanitize(filename, {
      ALLOWED_TAGS: [],
      ALLOWED_ATTR: []
    }).replace(/[^a-zA-Z0-9._-]/g, '_');
  }

  static generatePhotoId(): string {
    return EncryptionUtils.generateSecureId('photo');
  }
}
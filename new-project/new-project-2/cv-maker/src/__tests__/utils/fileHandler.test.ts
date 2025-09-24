import { vi } from 'vitest';
import { FileHandler, UploadProgress, FileMetadata, SecureUploadOptions, UploadResult } from '@/utils/fileHandler';

// Mock global functions that might not be available in test environment
global.URL.createObjectURL = vi.fn(() => 'mock-url');
global.URL.revokeObjectURL = vi.fn();

describe('FileHandler', () => {
  const mockFileConfig = {
    maxSize: 5 * 1024 * 1024, // 5MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'],
    maxFiles: 5,
    maxWidth: 1920,
    maxHeight: 1080,
    quality: 0.8,
  };

  const createMockFile = (name: string, type: string, size?: number): File => {
    const content = size ? 'x'.repeat(size) : 'mock content';
    const blob = new Blob([content], { type });
    return new File([blob], name, { type });
  };

  describe('validateFile', () => {
    it('should validate a valid file successfully', () => {
      const validFile = createMockFile('test.jpg', 'image/jpeg');
      const result = FileHandler.validateFile(validFile, mockFileConfig);

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject file that exceeds max size', () => {
      const oversizedFile = createMockFile('large.jpg', 'image/jpeg'); // 10MB
      const result = FileHandler.validateFile(oversizedFile, mockFileConfig);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('File size exceeds maximum allowed size');
    });

    it('should reject file with unsupported type', () => {
      const invalidTypeFile = createMockFile('test.exe', 'application/x-executable');
      const result = FileHandler.validateFile(invalidTypeFile, mockFileConfig);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('File type not supported');
    });

    it('should validate multiple file types correctly', () => {
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
      const invalidTypes = ['text/plain', 'application/x-executable', 'video/mp4'];

      validTypes.forEach(type => {
        const file = createMockFile(`test.${type.split('/')[1]}`, type);
        const result = FileHandler.validateFile(file, mockFileConfig);
        expect(result.isValid).toBe(true);
      });

      invalidTypes.forEach(type => {
        const file = createMockFile(`test.${type.split('/')[1]}`, type);
        const result = FileHandler.validateFile(file, mockFileConfig);
        expect(result.isValid).toBe(false);
      });
    });

    it('should handle edge case: file size exactly at max size', () => {
      const exactSizeFile = createMockFile('exact.jpg', 'image/jpeg', mockFileConfig.maxSize);
      const result = FileHandler.validateFile(exactSizeFile, mockFileConfig);

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should handle edge case: file size just over max size', () => {
      const slightlyOversizedFile = createMockFile('oversized.jpg', 'image/jpeg', mockFileConfig.maxSize + 1);
      const result = FileHandler.validateFile(slightlyOversizedFile, mockFileConfig);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('File size exceeds maximum allowed size');
    });
  });

  describe('extractMetadata', () => {
    it('should extract basic metadata correctly', async () => {
      const file = createMockFile('test.jpg', 'image/jpeg');
      const metadata = await FileHandler.extractMetadata(file);

      expect(metadata.name).toBe('test.jpg');
      expect(metadata.size).toBe(1024);
      expect(metadata.type).toBe('image/jpeg');
      expect(metadata.extension).toBe('jpg');
      expect(metadata.lastModified).toBeInstanceOf(Number);
    });

    it('should extract file extension correctly', async () => {
      const testCases = [
        { name: 'test.jpg', expected: 'jpg' },
        { name: 'document.pdf', expected: 'pdf' },
        { name: 'archive.tar.gz', expected: 'gz' },
        { name: 'noextension', expected: '' },
        { name: 'multiple.dots.file.name.txt', expected: 'txt' },
      ];

      for (const testCase of testCases) {
        const file = createMockFile(testCase.name, 'text/plain');
        const metadata = await FileHandler.extractMetadata(file);
        expect(metadata.extension).toBe(testCase.expected);
      }
    });

    it('should handle files with no extension', async () => {
      const file = createMockFile('filename', 'text/plain');
      const metadata = await FileHandler.extractMetadata(file);

      expect(metadata.extension).toBe('');
      expect(metadata.name).toBe('filename');
    });

    it('should handle special characters in filenames', async () => {
      const file = createMockFile('测试文件.jpg', 'image/jpeg');
      const metadata = await FileHandler.extractMetadata(file);

      expect(metadata.name).toBe('测试文件.jpg');
      expect(metadata.extension).toBe('jpg');
    });
  });

  describe('sanitizeFileName', () => {
    it('should sanitize file names by removing dangerous characters', () => {
      const dangerousNames = [
        '../../../malicious.js',
        'test..exe',
        'file/name.txt',
        'test\\file.pdf',
        'test:file.jpg',
        'test*file.png',
        'test?file.gif',
        'test"file.doc',
        'test<file.html',
        'test>file.css',
        'test|file.js',
      ];

      dangerousNames.forEach(name => {
        const sanitized = FileHandler.sanitizeFileName(name);
        expect(sanitized).not.toContain('../');
        expect(sanitized).not.toContain('..');
        expect(sanitized).not.toContain('/');
        expect(sanitized).not.toContain('\\');
        expect(sanitized).not.toContain(':');
        expect(sanitized).not.toContain('*');
        expect(sanitized).not.toContain('?');
        expect(sanitized).not.toContain('"');
        expect(sanitized).not.toContain('<');
        expect(sanitized).not.toContain('>');
        expect(sanitized).not.toContain('|');
      });
    });

    it('should preserve safe characters', () => {
      const safeName = 'my-file_123.txt';
      const sanitized = FileHandler.sanitizeFileName(safeName);

      expect(sanitized).toBe(safeName);
    });

    it('should handle empty file names', () => {
      const sanitized = FileHandler.sanitizeFileName('');
      expect(sanitized).toBe('unnamed_file');
    });

    it('should handle very long file names', () => {
      const longName = 'a'.repeat(300) + '.txt';
      const sanitized = FileHandler.sanitizeFileName(longName);

      expect(sanitized.length).toBeLessThanOrEqual(255);
      expect(sanitized.endsWith('.txt')).toBe(true);
    });
  });

  describe('calculateUploadProgress', () => {
    it('should calculate progress correctly for partial uploads', () => {
      const progress: UploadProgress = FileHandler.calculateUploadProgress(50, 100);

      expect(progress.loaded).toBe(50);
      expect(progress.total).toBe(100);
      expect(progress.percentage).toBe(50);
      expect(progress.speed).toBeGreaterThan(0);
      expect(progress.timeRemaining).toBeGreaterThan(0);
    });

    it('should handle completed uploads', () => {
      const progress: UploadProgress = FileHandler.calculateUploadProgress(100, 100);

      expect(progress.loaded).toBe(100);
      expect(progress.total).toBe(100);
      expect(progress.percentage).toBe(100);
      expect(progress.timeRemaining).toBe(0);
    });

    it('should handle zero-byte files', () => {
      const progress: UploadProgress = FileHandler.calculateUploadProgress(0, 0);

      expect(progress.loaded).toBe(0);
      expect(progress.total).toBe(0);
      expect(progress.percentage).toBe(0);
    });

    it('should handle upload start', () => {
      const progress: UploadProgress = FileHandler.calculateUploadProgress(0, 1000);

      expect(progress.loaded).toBe(0);
      expect(progress.total).toBe(1000);
      expect(progress.percentage).toBe(0);
      expect(progress.timeRemaining).toBeGreaterThan(0);
    });
  });

  describe('generateSecureUploadOptions', () => {
    it('should generate secure upload options with defaults', () => {
      const options = FileHandler.generateSecureUploadOptions();

      expect(options.maxFiles).toBe(5);
      expect(options.allowedTypes).toContain('image/jpeg');
      expect(options.maxSize).toBeGreaterThan(0);
      expect(options.requireHash).toBe(true);
      expect(options.virusScan).toBe(true);
      expect(options.sanitizeContent).toBe(true);
    });

    it('should override defaults with provided options', () => {
      const customOptions: SecureUploadOptions = {
        maxFiles: 10,
        allowedTypes: ['image/png'],
        maxSize: 1024,
      };

      const options = FileHandler.generateSecureUploadOptions(customOptions);

      expect(options.maxFiles).toBe(10);
      expect(options.allowedTypes).toEqual(['image/png']);
      expect(options.maxSize).toBe(1024);
    });

    it('should validate upload options', () => {
      const invalidOptions: SecureUploadOptions = {
        maxFiles: -1,
        maxSize: -1,
      };

      const options = FileHandler.generateSecureUploadOptions(invalidOptions);

      // Should fallback to reasonable defaults
      expect(options.maxFiles).toBeGreaterThan(0);
      expect(options.maxSize).toBeGreaterThan(0);
    });
  });

  describe('processUploadResult', () => {
    it('should process successful upload result', async () => {
      const file = createMockFile('test.jpg', 'image/jpeg');
      const metadata: FileMetadata = {
        name: 'test.jpg',
        size: 1024,
        type: 'image/jpeg',
        lastModified: Date.now(),
        extension: 'jpg',
      };

      const result: UploadResult = await FileHandler.processUploadResult(file, metadata, true);

      expect(result.success).toBe(true);
      expect(result.file).toBe(file);
      expect(result.metadata).toBe(metadata);
      expect(result.url).toBeDefined();
      expect(result.error).toBeUndefined();
    });

    it('should process failed upload result', async () => {
      const file = createMockFile('test.jpg', 'image/jpeg');
      const metadata: FileMetadata = {
        name: 'test.jpg',
        size: 1024,
        type: 'image/jpeg',
        lastModified: Date.now(),
        extension: 'jpg',
      };

      const result: UploadResult = await FileHandler.processUploadResult(file, metadata, false, 'Upload failed');

      expect(result.success).toBe(false);
      expect(result.file).toBe(file);
      expect(result.metadata).toBe(metadata);
      expect(result.error).toBe('Upload failed');
      expect(result.url).toBeUndefined();
    });

    it('should handle upload with warnings', async () => {
      const file = createMockFile('test.jpg', 'image/jpeg');
      const metadata: FileMetadata = {
        name: 'test.jpg',
        size: 1024,
        type: 'image/jpeg',
        lastModified: Date.now(),
        extension: 'jpg',
      };

      const warnings = ['File was compressed during upload'];
      const result: UploadResult = await FileHandler.processUploadResult(file, metadata, true, undefined, warnings);

      expect(result.success).toBe(true);
      expect(result.warnings).toEqual(warnings);
    });
  });

  describe('performance testing', () => {
    it('should handle bulk file validation efficiently', () => {
      const files = Array.from({ length: 100 }, (_, i) =>
        createMockFile(`file${i}.jpg`, 'image/jpeg')
      );

      const start = performance.now();
      const results = files.map(file => FileHandler.validateFile(file, mockFileConfig));
      const end = performance.now();

      expect(results.every(result => result.isValid)).toBe(true);
      expect(end - start).toBeLessThan(100); // Should complete in under 100ms
    });

    it('should handle metadata extraction efficiently', async () => {
      const files = Array.from({ length: 50 }, (_, i) =>
        createMockFile(`file${i}.jpg`, 'image/jpeg')
      );

      const start = performance.now();
      const metadataList = await Promise.all(files.map(file => FileHandler.extractMetadata(file)));
      const end = performance.now();

      expect(metadataList.length).toBe(50);
      expect(metadataList.every(metadata => metadata.name)).toBe(true);
      expect(end - start).toBeLessThan(200); // Should complete in under 200ms
    });

    it('should handle rapid file name sanitization', () => {
      const dangerousNames = Array.from({ length: 1000 }, (_, i) => `../../../malicious${i}.js`);

      const start = performance.now();
      const sanitizedNames = dangerousNames.map(name => FileHandler.sanitizeFileName(name));
      const end = performance.now();

      expect(sanitizedNames.every(name => !name.includes('../'))).toBe(true);
      expect(end - start).toBeLessThan(50); // Should complete in under 50ms
    });
  });

  describe('error handling', () => {
    it('should handle invalid file objects gracefully', () => {
      const invalidFile = null as unknown as File;

      expect(() => {
        FileHandler.validateFile(invalidFile, mockFileConfig);
      }).toThrow();
    });

    it('should handle missing configuration', () => {
      const file = createMockFile('test.jpg', 'image/jpeg');
      const invalidConfig = null as unknown as FileConfig;

      expect(() => {
        FileHandler.validateFile(file, invalidConfig);
      }).toThrow();
    });

    it('should handle metadata extraction errors', async () => {
      const invalidFile = { name: 'test.jpg' } as File;

      await expect(FileHandler.extractMetadata(invalidFile)).rejects.toThrow();
    });
  });

  describe('integration with browser APIs', () => {
    beforeEach(() => {
      vi.spyOn(global.URL, 'createObjectURL').mockReturnValue('mock-url');
      vi.spyOn(global.URL, 'revokeObjectURL').mockImplementation(() => {});
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it('should use URL.createObjectURL for generating file URLs', async () => {
      const file = createMockFile('test.jpg', 'image/jpeg');
      const metadata: FileMetadata = {
        name: 'test.jpg',
        size: 1024,
        type: 'image/jpeg',
        lastModified: Date.now(),
        extension: 'jpg',
      };

      const result: UploadResult = await FileHandler.processUploadResult(file, metadata, true);

      expect(URL.createObjectURL).toHaveBeenCalledWith(file);
      expect(result.url).toBe('mock-url');
    });

    it('should revoke object URLs when appropriate', () => {
      // This would typically be tested with actual cleanup logic
      expect(URL.revokeObjectURL).toBeDefined();
    });
  });
});
import DOMPurify from 'dompurify';
import {
  EncryptionConfig,
  EncryptedData,
  KeyPair,
  SymmetricKey,
  EncryptionMetadata,
  PasswordHash,
  KeyDerivationParams
} from '../types/encryption';

export class EncryptionUtils {
  private static readonly DEFAULT_CONFIG: EncryptionConfig = {
    algorithm: 'AES-GCM',
    keySize: 256,
    ivSize: 12,
    tagSize: 16,
    iterations: 100000
  };

  private static readonly ALGORITHM = 'AES-GCM';
  private static readonly KEY_SIZE = 256;
  private static readonly IV_SIZE = 12;
  private static readonly ITERATIONS = 100000;

  static async generateKeyPair(): Promise<KeyPair> {
    const keyPair = await window.crypto.subtle.generateKey(
      {
        name: 'RSA-OAEP',
        modulusLength: 2048,
        publicExponent: new Uint8Array([1, 0, 1]),
        hash: 'SHA-256',
      },
      true,
      ['encrypt', 'decrypt']
    );

    const publicKey = await window.crypto.subtle.exportKey('spki', keyPair.publicKey);
    const privateKey = await window.crypto.subtle.exportKey('pkcs8', keyPair.privateKey);

    return {
      publicKey: this.arrayBufferToBase64(publicKey),
      privateKey: this.arrayBufferToBase64(privateKey),
      keyId: this.generateKeyId(),
      algorithm: 'RSA-OAEP',
      keySize: 2048,
      createdAt: new Date().toISOString()
    };
  }

  static async generateSymmetricKey(): Promise<SymmetricKey> {
    const key = await window.crypto.subtle.generateKey(
      {
        name: this.ALGORITHM,
        length: this.KEY_SIZE,
      },
      true,
      ['encrypt', 'decrypt']
    );

    const exportedKey = await window.crypto.subtle.exportKey('raw', key);

    return {
      key: this.arrayBufferToBase64(exportedKey),
      keyId: this.generateKeyId(),
      algorithm: this.ALGORITHM,
      keySize: this.KEY_SIZE,
      createdAt: new Date().toISOString(),
      usage: 'both'
    };
  }

  static async deriveKeyFromPassword(
    password: string,
    salt: string,
    params?: Partial<KeyDerivationParams>
  ): Promise<string> {
    const encoder = new TextEncoder();
    const passwordData = encoder.encode(password);
    const saltData = encoder.encode(salt);

    const keyMaterial = await window.crypto.subtle.importKey(
      'raw',
      passwordData,
      { name: 'PBKDF2' },
      false,
      ['deriveBits', 'deriveKey']
    );

    const key = await window.crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: saltData,
        iterations: params?.iterations || this.ITERATIONS,
        hash: 'SHA-256',
      },
      keyMaterial,
      { name: this.ALGORITHM, length: this.KEY_SIZE },
      true,
      ['encrypt', 'decrypt']
    );

    const exportedKey = await window.crypto.subtle.exportKey('raw', key);
    return this.arrayBufferToBase64(exportedKey);
  }

  static async encryptData(
    data: string,
    key: string,
    config?: Partial<EncryptionConfig>
  ): Promise<EncryptedData> {
    const finalConfig = { ...this.DEFAULT_CONFIG, ...config };
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);

    const keyBuffer = this.base64ToArrayBuffer(key);
    const cryptoKey = await window.crypto.subtle.importKey(
      'raw',
      keyBuffer,
      { name: finalConfig.algorithm },
      false,
      ['encrypt']
    );

    const iv = window.crypto.getRandomValues(new Uint8Array(finalConfig.ivSize));

    const encryptedData = await window.crypto.subtle.encrypt(
      {
        name: finalConfig.algorithm,
        iv: iv,
        tagLength: finalConfig.tagSize,
      },
      cryptoKey,
      dataBuffer
    );

    const ciphertext = new Uint8Array(encryptedData);
    const tag = ciphertext.slice(-finalConfig.tagSize!);
    const actualCiphertext = ciphertext.slice(0, -finalConfig.tagSize!);

    return {
      iv: this.arrayBufferToBase64(iv),
      ciphertext: this.arrayBufferToBase64(actualCiphertext),
      tag: this.arrayBufferToBase64(tag),
      algorithm: finalConfig.algorithm,
      timestamp: new Date().toISOString()
    };
  }

  static async decryptData(
    encryptedData: EncryptedData,
    key: string
  ): Promise<string> {
    const encoder = new TextEncoder();
    const keyBuffer = this.base64ToArrayBuffer(key);

    const cryptoKey = await window.crypto.subtle.importKey(
      'raw',
      keyBuffer,
      { name: encryptedData.algorithm },
      false,
      ['decrypt']
    );

    const iv = this.base64ToArrayBuffer(encryptedData.iv);
    const ciphertext = this.base64ToArrayBuffer(encryptedData.ciphertext);
    const tag = this.base64ToArrayBuffer(encryptedData.tag!);

    const encryptedWithTag = new Uint8Array(ciphertext.byteLength + tag.byteLength);
    encryptedWithTag.set(new Uint8Array(ciphertext), 0);
    encryptedWithTag.set(new Uint8Array(tag), ciphertext.byteLength);

    const decryptedData = await window.crypto.subtle.decrypt(
      {
        name: encryptedData.algorithm,
        iv: iv,
        tagLength: 16,
      },
      cryptoKey,
      encryptedWithTag
    );

    return new TextDecoder().decode(decryptedData);
  }

  static async hashPassword(
    password: string,
    salt?: string
  ): Promise<PasswordHash> {
    const encoder = new TextEncoder();
    const passwordData = encoder.encode(password);
    const saltData = salt ? encoder.encode(salt) : window.crypto.getRandomValues(new Uint8Array(16));

    const keyMaterial = await window.crypto.subtle.importKey(
      'raw',
      passwordData,
      { name: 'PBKDF2' },
      false,
      ['deriveBits']
    );

    const derivedBits = await window.crypto.subtle.deriveBits(
      {
        name: 'PBKDF2',
        salt: saltData,
        iterations: this.ITERATIONS,
        hash: 'SHA-256',
      },
      keyMaterial,
      256
    );

    return {
      hash: this.arrayBufferToBase64(derivedBits),
      salt: this.arrayBufferToBase64(saltData),
      algorithm: 'pbkdf2',
      iterations: this.ITERATIONS,
      version: '1'
    };
  }

  static async verifyPassword(
    password: string,
    hash: PasswordHash
  ): Promise<boolean> {
    const computedHash = await this.hashPassword(password, hash.salt);
    return computedHash.hash === hash.hash;
  }

  static generateSecureToken(length: number = 32): string {
    const array = new Uint8Array(length);
    window.crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  static generateKeyId(): string {
    return `key_${Date.now()}_${this.generateSecureToken(8)}`;
  }

  static sanitizeInput(input: string): string {
    return DOMPurify.sanitize(input, {
      ALLOWED_TAGS: [],
      ALLOWED_ATTR: []
    });
  }

  static validateEncryptedData(encryptedData: EncryptedData): boolean {
    return !!(
      encryptedData.iv &&
      encryptedData.ciphertext &&
      encryptedData.tag &&
      encryptedData.algorithm &&
      encryptedData.timestamp
    );
  }

  static createEncryptionMetadata(
    encryptedBy: string,
    keyId: string,
    algorithm: string
  ): EncryptionMetadata {
    return {
      encryptedBy,
      encryptedAt: new Date().toISOString(),
      algorithm,
      keyId,
      version: '1.0',
      checksum: this.generateSecureToken(16)
    };
  }

  private static arrayBufferToBase64(buffer: ArrayBuffer): string {
    return btoa(String.fromCharCode(...new Uint8Array(buffer)));
  }

  private static base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }

  static async encryptJSON(
    data: any,
    key: string,
    config?: Partial<EncryptionConfig>
  ): Promise<EncryptedData> {
    const jsonData = JSON.stringify(data);
    return this.encryptData(jsonData, key, config);
  }

  static async decryptJSON<T>(
    encryptedData: EncryptedData,
    key: string
  ): Promise<T> {
    const jsonString = await this.decryptData(encryptedData, key);
    return JSON.parse(jsonString);
  }

  static async generateHMAC(
    data: string,
    key: string
  ): Promise<string> {
    const encoder = new TextEncoder();
    const keyData = encoder.encode(key);
    const dataData = encoder.encode(data);

    const cryptoKey = await window.crypto.subtle.importKey(
      'raw',
      keyData,
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    );

    const signature = await window.crypto.subtle.sign(
      'HMAC',
      cryptoKey,
      dataData
    );

    return this.arrayBufferToBase64(signature);
  }

  static async verifyHMAC(
    data: string,
    key: string,
    signature: string
  ): Promise<boolean> {
    const computedSignature = await this.generateHMAC(data, key);
    return computedSignature === signature;
  }

  static generateSecureId(prefix: string = 'sec'): string {
    const timestamp = Date.now().toString(36);
    const random = this.generateSecureToken(8);
    return `${prefix}_${timestamp}_${random}`;
  }

  static isSecureEnvironment(): boolean {
    return (
      typeof window !== 'undefined' &&
      typeof window.crypto !== 'undefined' &&
      typeof window.crypto.subtle !== 'undefined'
    );
  }
}
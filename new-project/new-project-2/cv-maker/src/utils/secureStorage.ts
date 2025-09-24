import {
  SecureStorageItem,
  EncryptedData
} from '../types/encryption';
import { EncryptionUtils } from './encryptionUtils';

export class SecureStorage {
  private static readonly STORAGE_PREFIX = 'cv_maker_secure_';
  private static readonly ENCRYPTION_KEY_KEY = 'encryption_key';
  private static readonly MASTER_KEY_KEY = 'master_key';
  private static readonly SALT_KEY = 'storage_salt';

  private static masterKey: string | null = null;
  private static isInitialized = false;

  static async initialize(password?: string): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Check if we already have a master key
      const existingMasterKey = localStorage.getItem(this.STORAGE_PREFIX + this.MASTER_KEY_KEY);

      if (existingMasterKey) {
        // Decrypt the master key if password is provided
        if (password) {
          this.masterKey = await this.decryptMasterKey(existingMasterKey, password);
        } else {
          // For now, use the key as-is (in production, this would require proper authentication)
          this.masterKey = existingMasterKey;
        }
      } else {
        // Generate a new master key
        this.masterKey = EncryptionUtils.generateSecureToken(32);

        // If password is provided, encrypt the master key
        if (password) {
          const encryptedMasterKey = await this.encryptMasterKey(this.masterKey, password);
          localStorage.setItem(this.STORAGE_PREFIX + this.MASTER_KEY_KEY, encryptedMasterKey);
        } else {
          localStorage.setItem(this.STORAGE_PREFIX + this.MASTER_KEY_KEY, this.masterKey);
        }
      }

      // Generate or retrieve salt
      const existingSalt = localStorage.getItem(this.STORAGE_PREFIX + this.SALT_KEY);
      if (!existingSalt) {
        const salt = EncryptionUtils.generateSecureToken(16);
        localStorage.setItem(this.STORAGE_PREFIX + this.SALT_KEY, salt);
      }

      this.isInitialized = true;
    } catch (error) {
      console.error('Failed to initialize secure storage:', error);
      throw new Error('Failed to initialize secure storage');
    }
  }

  static async store(key: string, value: unknown, expiresAt?: Date): Promise<void> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    if (!this.masterKey) {
      throw new Error('Secure storage not initialized');
    }

    try {
      // Serialize the value
      const serializedValue = JSON.stringify(value);

      // Encrypt the value
      const encryptedData = await EncryptionUtils.encryptData(serializedValue, this.masterKey);

      // Create storage item
      const storageItem: SecureStorageItem = {
        id: EncryptionUtils.generateSecureId('storage'),
        key: this.STORAGE_PREFIX + key,
        value: encryptedData,
        metadata: EncryptionUtils.createEncryptionMetadata(
          'system',
          'storage',
          encryptedData.algorithm
        ),
        expiresAt: expiresAt?.toISOString(),
        accessCount: 0,
        lastAccessed: new Date().toISOString()
      };

      // Store in localStorage
      localStorage.setItem(this.STORAGE_PREFIX + key, JSON.stringify(storageItem));
    } catch (error) {
      console.error('Failed to store secure data:', error);
      throw new Error('Failed to store secure data');
    }
  }

  static async retrieve<T>(key: string): Promise<T | null> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    if (!this.masterKey) {
      throw new Error('Secure storage not initialized');
    }

    try {
      const storedItem = localStorage.getItem(this.STORAGE_PREFIX + key);
      if (!storedItem) {
        return null;
      }

      const storageItem: SecureStorageItem = JSON.parse(storedItem);

      // Check if expired
      if (storageItem.expiresAt && new Date(storageItem.expiresAt) < new Date()) {
        this.remove(key);
        return null;
      }

      // Decrypt the value
      const decryptedValue = await EncryptionUtils.decryptData(storageItem.value, this.masterKey);

      // Update access count and last accessed time
      storageItem.accessCount++;
      storageItem.lastAccessed = new Date().toISOString();
      localStorage.setItem(this.STORAGE_PREFIX + key, JSON.stringify(storageItem));

      return JSON.parse(decryptedValue);
    } catch (error) {
      console.error('Failed to retrieve secure data:', error);
      return null;
    }
  }

  static async remove(key: string): Promise<void> {
    localStorage.removeItem(this.STORAGE_PREFIX + key);
  }

  static async clear(): Promise<void> {
    const keysToRemove: string[] = [];

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.STORAGE_PREFIX)) {
        keysToRemove.push(key);
      }
    }

    keysToRemove.forEach(key => localStorage.removeItem(key));

    this.masterKey = null;
    this.isInitialized = false;
  }

  static async export(): Promise<string> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    const exportData: Record<string, unknown> = {};

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.STORAGE_PREFIX)) {
        const cleanKey = key.replace(this.STORAGE_PREFIX, '');
        const value = await this.retrieve(cleanKey);
        if (value !== null) {
          exportData[cleanKey] = value;
        }
      }
    }

    return JSON.stringify(exportData, null, 2);
  }

  static async import(exportData: string, password?: string): Promise<void> {
    try {
      const data = JSON.parse(exportData);

      // Clear existing data
      await this.clear();

      // Reinitialize with password if provided
      await this.initialize(password);

      // Import each key-value pair
      for (const [key, value] of Object.entries(data)) {
        await this.store(key, value);
      }
    } catch (error) {
      console.error('Failed to import secure data:', error);
      throw new Error('Failed to import secure data');
    }
  }

  static async listKeys(): Promise<string[]> {
    const keys: string[] = [];

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.STORAGE_PREFIX)) {
        keys.push(key.replace(this.STORAGE_PREFIX, ''));
      }
    }

    return keys;
  }

  static async getStorageInfo(): Promise<{
    totalItems: number;
    totalSize: number;
    expiredItems: number;
    items: Array<{
      key: string;
      accessCount: number;
      lastAccessed: string;
      expiresAt?: string;
    }>;
  }> {
    const items: Array<{
      key: string;
      accessCount: number;
      lastAccessed: string;
      expiresAt?: string;
    }> = [];
    let totalSize = 0;
    let expiredItems = 0;

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.STORAGE_PREFIX)) {
        try {
          const storageItem: SecureStorageItem = JSON.parse(localStorage.getItem(key) || '{}');

          items.push({
            key: key.replace(this.STORAGE_PREFIX, ''),
            accessCount: storageItem.accessCount || 0,
            lastAccessed: storageItem.lastAccessed || '',
            expiresAt: storageItem.expiresAt
          });

          totalSize += key.length + localStorage.getItem(key)!.length;

          if (storageItem.expiresAt && new Date(storageItem.expiresAt) < new Date()) {
            expiredItems++;
          }
        } catch {
          // Skip invalid items
        }
      }
    }

    return {
      totalItems: items.length,
      totalSize,
      expiredItems,
      items
    };
  }

  static async cleanupExpired(): Promise<number> {
    let removedCount = 0;

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.STORAGE_PREFIX)) {
        try {
          const storageItem: SecureStorageItem = JSON.parse(localStorage.getItem(key) || '{}');

          if (storageItem.expiresAt && new Date(storageItem.expiresAt) < new Date()) {
            localStorage.removeItem(key);
            removedCount++;
          }
        } catch {
          // Remove invalid items
          localStorage.removeItem(key);
          removedCount++;
        }
      }
    }

    return removedCount;
  }

  static async generateBackup(): Promise<string> {
    const backup = {
      timestamp: new Date().toISOString(),
      version: '1.0',
      data: await this.export(),
      checksum: await EncryptionUtils.generateHMAC(await this.export(), 'backup')
    };

    return JSON.stringify(backup, null, 2);
  }

  static async restoreFromBackup(backupData: string, password?: string): Promise<boolean> {
    try {
      const backup = JSON.parse(backupData);

      // Verify backup integrity
      const checksum = await EncryptionUtils.generateHMAC(backup.data, 'backup');
      if (checksum !== backup.checksum) {
        throw new Error('Backup integrity check failed');
      }

      // Restore data
      await this.import(backup.data, password);

      return true;
    } catch (error) {
      console.error('Failed to restore from backup:', error);
      return false;
    }
  }

  static async changePassword(oldPassword: string, newPassword: string): Promise<boolean> {
    if (!this.isInitialized) {
      await this.initialize(oldPassword);
    }

    if (!this.masterKey) {
      return false;
    }

    try {
      // Export current data
      const currentData = await this.export();

      // Clear storage
      await this.clear();

      // Reinitialize with new password
      await this.initialize(newPassword);

      // Import data
      await this.import(currentData);

      return true;
    } catch (error) {
      console.error('Failed to change password:', error);
      return false;
    }
  }

  static isSecureEnvironment(): boolean {
    return EncryptionUtils.isSecureEnvironment();
  }

  static getStorageStats(): {
    isInitialized: boolean;
    hasMasterKey: boolean;
    totalKeys: number;
    estimatedSize: number;
  } {
    let totalSize = 0;
    let totalKeys = 0;

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.STORAGE_PREFIX)) {
        totalKeys++;
        totalSize += key.length + localStorage.getItem(key)!.length;
      }
    }

    return {
      isInitialized: this.isInitialized,
      hasMasterKey: !!this.masterKey,
      totalKeys,
      estimatedSize: totalSize
    };
  }

  private static async encryptMasterKey(masterKey: string, password: string): Promise<string> {
    const salt = EncryptionUtils.generateSecureToken(16);
    const derivedKey = await EncryptionUtils.deriveKeyFromPassword(password, salt);
    return await EncryptionUtils.encryptData(masterKey, derivedKey);
  }

  private static async decryptMasterKey(encryptedMasterKey: string, password: string): Promise<string> {
    const salt = localStorage.getItem(this.STORAGE_PREFIX + this.SALT_KEY) || EncryptionUtils.generateSecureToken(16);
    const derivedKey = await EncryptionUtils.deriveKeyFromPassword(password, salt);

    try {
      const encryptedData: EncryptedData = JSON.parse(encryptedMasterKey);
      return await EncryptionUtils.decryptData(encryptedData, derivedKey);
    } catch {
      throw new Error('Invalid password');
    }
  }
}
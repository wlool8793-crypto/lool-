export interface EncryptionConfig {
  algorithm: 'AES-GCM' | 'AES-CBC' | 'RSA-OAEP';
  keySize: 128 | 192 | 256;
  ivSize: number;
  tagSize?: number;
  iterations: number;
}

export interface EncryptedData {
  iv: string;
  ciphertext: string;
  tag?: string;
  algorithm: string;
  keyId?: string;
  timestamp: string;
}

export interface KeyPair {
  publicKey: string;
  privateKey: string;
  keyId: string;
  algorithm: string;
  keySize: number;
  createdAt: string;
  expiresAt?: string;
}

export interface SymmetricKey {
  key: string;
  keyId: string;
  algorithm: string;
  keySize: number;
  createdAt: string;
  expiresAt?: string;
  usage: 'encryption' | 'decryption' | 'both';
}

export interface EncryptionMetadata {
  encryptedBy: string;
  encryptedAt: string;
  algorithm: string;
  keyId: string;
  version: string;
  checksum: string;
}

export interface SecureStorageItem {
  id: string;
  key: string;
  value: EncryptedData;
  metadata: EncryptionMetadata;
  expiresAt?: string;
  accessCount: number;
  lastAccessed: string;
}

export interface PasswordHash {
  hash: string;
  salt: string;
  algorithm: 'bcrypt' | 'scrypt' | 'argon2' | 'pbkdf2';
  iterations: number;
  memory?: number;
  parallelism?: number;
  version: string;
}

export interface SecureDocument {
  id: string;
  name: string;
  type: string;
  size: number;
  encryptedContent: EncryptedData;
  metadata: {
    mimeType: string;
    checksum: string;
    encryptedBy: string;
    encryptedAt: string;
    accessPermissions: string[];
  };
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface SecurePhoto {
  id: string;
  originalName: string;
  encryptedContent: EncryptedData;
  thumbnail?: EncryptedData;
  metadata: {
    mimeType: string;
    width: number;
    height: number;
    size: number;
    checksum: string;
    encryptedBy: string;
    encryptedAt: string;
    watermark?: boolean;
    blurLevel?: number;
  };
  accessPermissions: PhotoAccessPermissions;
  createdAt: string;
  updatedAt: string;
}

export interface PhotoAccessPermissions {
  owner: 'full';
  family: 'view' | 'download' | 'none';
  contacts: 'view' | 'none';
  public: 'view' | 'none';
  temporaryAccess: TemporaryAccess[];
}

export interface TemporaryAccess {
  id: string;
  grantedTo: string;
  grantedBy: string;
  permissions: 'view' | 'download';
  expiresAt: string;
  isActive: boolean;
  accessCount: number;
  maxAccessCount?: number;
}

export interface SecureShare {
  id: string;
  documentId: string;
  shareToken: string;
  password?: string;
  permissions: 'view' | 'download' | 'edit';
  expiresAt?: string;
  maxAccessCount?: number;
  accessCount: number;
  createdBy: string;
  createdAt: string;
  isActive: boolean;
  accessLogs: ShareAccessLog[];
}

export interface ShareAccessLog {
  id: string;
  accessedBy: string;
  ipAddress: string;
  userAgent: string;
  timestamp: string;
  action: 'view' | 'download' | 'edit';
  success: boolean;
}

export interface EncryptionKeyRotation {
  keyId: string;
  newKeyId: string;
  rotatedAt: string;
  rotatedBy: string;
  status: 'pending' | 'completed' | 'failed';
  affectedItems: string[];
}

export interface SecureBackup {
  id: string;
  name: string;
  encryptedData: EncryptedData;
  metadata: {
    size: number;
    checksum: string;
    encryptedAt: string;
    algorithm: string;
  };
  schedule: BackupSchedule;
  retention: number; // days
  lastBackup: string;
  nextBackup: string;
  status: 'active' | 'paused' | 'failed';
}

export interface BackupSchedule {
  frequency: 'daily' | 'weekly' | 'monthly';
  time: string; // HH:MM format
  day?: number; // for weekly/monthly
  timezone: string;
}

export interface KeyDerivationParams {
  algorithm: 'pbkdf2' | 'scrypt' | 'argon2';
  salt: string;
  iterations: number;
  memory?: number;
  parallelism?: number;
  hashLength: number;
}
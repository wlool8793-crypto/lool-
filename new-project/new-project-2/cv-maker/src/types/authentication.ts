export interface User {
  id: string;
  email: string;
  phone?: string;
  fullName: string;
  avatar?: string;
  role: UserRole;
  status: UserStatus;
  emailVerified: boolean;
  phoneVerified: boolean;
  twoFactorEnabled: boolean;
  lastLoginAt?: string;
  createdAt: string;
  updatedAt: string;
  settings: UserSettings;
  security: UserSecurity;
}

export type UserRole = 'admin' | 'user' | 'family_member' | 'guest' | 'moderator';
export type UserStatus = 'active' | 'inactive' | 'suspended' | 'banned' | 'pending_verification';

export interface UserSettings {
  language: string;
  theme: 'light' | 'dark' | 'auto';
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  security: SecuritySettings;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  sms: boolean;
  securityAlerts: boolean;
  loginAlerts: boolean;
  dataSharingAlerts: boolean;
  privacyUpdates: boolean;
}

export interface PrivacySettings {
  profileVisibility: 'public' | 'private' | 'unlisted';
  dataSharing: boolean;
  analytics: boolean;
  marketing: boolean;
}

export interface SecuritySettings {
  sessionTimeout: number;
  requirePasswordChange: boolean;
  loginAttempts: number;
  suspiciousActivityAlerts: boolean;
  dataEncryption: boolean;
  twoFactor: boolean;
}

export interface UserSecurity {
  passwordHash: string;
  salt: string;
  twoFactorSecret?: string;
  backupCodes?: string[];
  securityQuestions: SecurityQuestion[];
  devices: Device[];
  sessions: Session[];
  loginAttempts: LoginAttempt[];
}

export interface SecurityQuestion {
  id: string;
  question: string;
  answerHash: string;
  salt: string;
  createdAt: string;
}

export interface Device {
  id: string;
  name: string;
  type: 'desktop' | 'mobile' | 'tablet';
  platform: string;
  browser: string;
  ipAddress: string;
  lastUsed: string;
  isTrusted: boolean;
  createdAt: string;
}

export interface Session {
  id: string;
  token: string;
  refreshToken: string;
  device: Device;
  ipAddress: string;
  userAgent: string;
  expiresAt: string;
  createdAt: string;
  isActive: boolean;
}

export interface LoginAttempt {
  id: string;
  email: string;
  ipAddress: string;
  userAgent: string;
  success: boolean;
  timestamp: string;
  failureReason?: string;
  location?: {
    country: string;
    city: string;
    latitude: number;
    longitude: number;
  };
}

export interface TwoFactorAuth {
  enabled: boolean;
  method: 'app' | 'sms' | 'email';
  secret: string;
  backupCodes: string[];
  recoveryEmail?: string;
  recoveryPhone?: string;
}

export interface AuthToken {
  accessToken: string;
  refreshToken: string;
  tokenType: 'Bearer';
  expiresIn: number;
  scope: string[];
}

export interface LoginRequest {
  email: string;
  password: string;
  twoFactorCode?: string;
  rememberMe: boolean;
  deviceInfo?: {
    name: string;
    type: 'desktop' | 'mobile' | 'tablet';
  };
}

export interface RegisterRequest {
  email: string;
  password: string;
  fullName: string;
  phone?: string;
  agreeToTerms: boolean;
  consentToDataProcessing: boolean;
  captchaToken?: string;
}

export interface PasswordResetRequest {
  email: string;
  captchaToken?: string;
}

export interface PasswordResetConfirm {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface SecurityQuestionSetup {
  questions: Array<{
    question: string;
    answer: string;
  }>;
}

export interface TwoFactorSetup {
  method: 'app' | 'sms' | 'email';
  secret?: string;
  code?: string;
  recoveryEmail?: string;
  recoveryPhone?: string;
}

export interface AuthResponse {
  success: boolean;
  user?: User;
  token?: AuthToken;
  requiresTwoFactor?: boolean;
  requiresEmailVerification?: boolean;
  requiresPasswordChange?: boolean;
  error?: string;
  message?: string;
}

export interface SessionInfo {
  id: string;
  userId: string;
  device: Device;
  ipAddress: string;
  userAgent: string;
  createdAt: string;
  lastActivity: string;
  expiresAt: string;
  isActive: boolean;
}

export interface SecurityAlert {
  id: string;
  userId: string;
  type: 'login_attempt' | 'password_change' | 'data_access' | 'suspicious_activity' | 'device_change';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  details: Record<string, any>;
  timestamp: string;
  read: boolean;
  actionTaken?: boolean;
}
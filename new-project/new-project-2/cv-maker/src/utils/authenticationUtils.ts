import {
  User,
  AuthToken,
  LoginRequest,
  RegisterRequest,
  PasswordResetRequest,
  PasswordResetConfirm,
  ChangePasswordRequest,
  SecurityQuestionSetup,
  TwoFactorSetup,
  AuthResponse,
  SessionInfo,
  SecurityAlert,
  LoginAttempt,
  Device,
  Session,
  TwoFactorAuth,
  SecurityQuestion
} from '../types/authentication';
import { EncryptionUtils } from './encryptionUtils';
import { SecureStorage } from './secureStorage';

export interface AuthConfig {
  sessionTimeout: number;
  maxLoginAttempts: number;
  lockoutDuration: number;
  requireEmailVerification: boolean;
  requireTwoFactor: boolean;
  passwordPolicy: {
    minLength: number;
    requireUppercase: boolean;
    requireLowercase: boolean;
    requireNumbers: boolean;
    requireSpecialChars: boolean;
    preventReusedPasswords: number;
    expireAfterDays: number;
  };
}

export class AuthenticationUtils {
  private static readonly DEFAULT_CONFIG: AuthConfig = {
    sessionTimeout: 30 * 60 * 1000, // 30 minutes
    maxLoginAttempts: 5,
    lockoutDuration: 15 * 60 * 1000, // 15 minutes
    requireEmailVerification: true,
    requireTwoFactor: false,
    passwordPolicy: {
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
      preventReusedPasswords: 5,
      expireAfterDays: 90
    }
  };

  private static readonly USERS_STORAGE_KEY = 'auth_users';
  private static readonly SESSIONS_STORAGE_KEY = 'auth_sessions';
  private static readonly LOGIN_ATTEMPTS_KEY = 'auth_login_attempts';
  private static readonly SECURITY_ALERTS_KEY = 'auth_security_alerts';

  static async initialize(): Promise<void> {
    await SecureStorage.initialize();
  }

  static async register(request: RegisterRequest): Promise<AuthResponse> {
    try {
      // Validate request
      const validationError = this.validateRegisterRequest(request);
      if (validationError) {
        return { success: false, error: validationError };
      }

      // Check if user already exists
      const existingUser = await this.getUserByEmail(request.email);
      if (existingUser) {
        return { success: false, error: 'User already exists with this email' };
      }

      // Hash password
      const passwordHash = await EncryptionUtils.hashPassword(request.password);

      // Create user
      const user: User = {
        id: EncryptionUtils.generateSecureId('user'),
        email: request.email,
        phone: request.phone,
        fullName: request.fullName,
        role: 'user',
        status: 'active',
        emailVerified: false,
        phoneVerified: false,
        twoFactorEnabled: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        settings: {
          language: 'en',
          theme: 'auto',
          notifications: {
            email: true,
            push: true,
            sms: false,
            securityAlerts: true,
            loginAlerts: true,
            dataSharingAlerts: true,
            privacyUpdates: true
          },
          privacy: {
            profileVisibility: 'private',
            dataSharing: false,
            analytics: false,
            marketing: false
          },
          security: {
            sessionTimeout: this.DEFAULT_CONFIG.sessionTimeout,
            requirePasswordChange: false,
            loginAttempts: 0,
            suspiciousActivityAlerts: true,
            dataEncryption: true,
            twoFactor: false
          }
        },
        security: {
          passwordHash: passwordHash.hash,
          salt: passwordHash.salt,
          securityQuestions: [],
          devices: [],
          sessions: [],
          loginAttempts: []
        }
      };

      // Store user
      await this.storeUser(user);

      // Create session
      const session = await this.createSession(user);

      // Send verification email (in a real app)
      if (this.DEFAULT_CONFIG.requireEmailVerification) {
        await this.sendVerificationEmail(user);
      }

      return {
        success: true,
        user,
        token: session,
        requiresEmailVerification: this.DEFAULT_CONFIG.requireEmailVerification
      };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Registration failed' };
    }
  }

  static async login(request: LoginRequest): Promise<AuthResponse> {
    try {
      // Check for account lockout
      const lockoutCheck = await this.checkAccountLockout(request.email);
      if (lockoutCheck.isLocked) {
        return { success: false, error: `Account locked. Try again in ${Math.ceil(lockoutCheck.remainingTime / 60000)} minutes` };
      }

      // Get user
      const user = await this.getUserByEmail(request.email);
      if (!user) {
        await this.recordLoginAttempt(request.email, false, 'User not found');
        return { success: false, error: 'Invalid email or password' };
      }

      // Verify password
      const passwordValid = await this.verifyPassword(user, request.password);
      if (!passwordValid) {
        await this.recordLoginAttempt(request.email, false, 'Invalid password');
        return { success: false, error: 'Invalid email or password' };
      }

      // Check if account is active
      if (user.status !== 'active') {
        return { success: false, error: 'Account is not active' };
      }

      // Check email verification
      if (this.DEFAULT_CONFIG.requireEmailVerification && !user.emailVerified) {
        return { success: false, requiresEmailVerification: true, error: 'Please verify your email address' };
      }

      // Handle two-factor authentication
      if (user.twoFactorEnabled) {
        if (!request.twoFactorCode) {
          return { success: false, requiresTwoFactor: true, error: 'Two-factor authentication required' };
        }

        const twoFactorValid = await this.verifyTwoFactor(user, request.twoFactorCode);
        if (!twoFactorValid) {
          await this.recordLoginAttempt(request.email, false, 'Invalid two-factor code');
          return { success: false, error: 'Invalid two-factor authentication code' };
        }
      }

      // Create session
      const session = await this.createSession(user);

      // Record successful login
      await this.recordLoginAttempt(request.email, true);

      // Update user info
      user.lastLoginAt = new Date().toISOString();
      await this.storeUser(user);

      // Send login alert
      await this.sendSecurityAlert(user.id, 'login_attempt', 'medium', 'New login detected', {
        device: request.deviceInfo?.name || 'Unknown device',
        timestamp: new Date().toISOString()
      });

      return {
        success: true,
        user,
        token: session
      };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Login failed' };
    }
  }

  static async logout(sessionId: string): Promise<boolean> {
    try {
      const sessions = await this.getAllSessions();
      const sessionIndex = sessions.findIndex(s => s.id === sessionId);

      if (sessionIndex !== -1) {
        sessions[sessionIndex].isActive = false;
        await this.storeSessions(sessions);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Logout error:', error);
      return false;
    }
  }

  static async refreshToken(refreshToken: string): Promise<AuthToken | null> {
    try {
      const sessions = await this.getAllSessions();
      const session = sessions.find(s => s.refreshToken === refreshToken && s.isActive);

      if (!session || new Date(session.expiresAt) < new Date()) {
        return null;
      }

      // Generate new access token
      const newToken = this.generateAuthToken(session.userId, session.expiresAt);
      session.token = newToken.accessToken;
      await this.storeSessions(sessions);

      return newToken;
    } catch (error) {
      console.error('Token refresh error:', error);
      return null;
    }
  }

  static async validateSession(sessionId: string): Promise<SessionInfo | null> {
    try {
      const sessions = await this.getAllSessions();
      const session = sessions.find(s => s.id === sessionId && s.isActive);

      if (!session || new Date(session.expiresAt) < new Date()) {
        return null;
      }

      const user = await this.getUserById(session.userId);
      if (!user || user.status !== 'active') {
        return null;
      }

      return {
        id: session.id,
        userId: session.userId,
        device: session.device,
        ipAddress: session.ipAddress,
        userAgent: session.userAgent,
        createdAt: session.createdAt,
        lastActivity: new Date().toISOString(),
        expiresAt: session.expiresAt,
        isActive: session.isActive
      };
    } catch (error) {
      console.error('Session validation error:', error);
      return null;
    }
  }

  static async requestPasswordReset(request: PasswordResetRequest): Promise<boolean> {
    try {
      const user = await this.getUserByEmail(request.email);
      if (!user) {
        return false; // Don't reveal if user exists
      }

      // Generate reset token
      const resetToken = EncryptionUtils.generateSecureToken(32);
      const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours

      // Store reset token (in a real app, this would be in a database)
      await SecureStorage.store(`password_reset_${user.id}`, {
        token: resetToken,
        expiresAt: expiresAt.toISOString()
      }, expiresAt);

      // Send reset email (in a real app)
      await this.sendPasswordResetEmail(user, resetToken);

      return true;
    } catch (error) {
      console.error('Password reset request error:', error);
      return false;
    }
  }

  static async confirmPasswordReset(request: PasswordResetConfirm): Promise<boolean> {
    try {
      // Find user by reset token
      const resetData = await this.findUserByResetToken(request.token);
      if (!resetData) {
        return false;
      }

      const user = resetData.user;

      // Validate new password
      const passwordError = this.validatePassword(request.newPassword);
      if (passwordError) {
        return false;
      }

      // Hash new password
      const passwordHash = await EncryptionUtils.hashPassword(request.newPassword);

      // Update user password
      user.security.passwordHash = passwordHash.hash;
      user.security.salt = passwordHash.salt;
      user.updatedAt = new Date().toISOString();

      await this.storeUser(user);

      // Invalidate all sessions
      await this.invalidateUserSessions(user.id);

      // Remove reset token
      await SecureStorage.remove(`password_reset_${user.id}`);

      return true;
    } catch (error) {
      console.error('Password reset confirmation error:', error);
      return false;
    }
  }

  static async changePassword(userId: string, request: ChangePasswordRequest): Promise<boolean> {
    try {
      const user = await this.getUserById(userId);
      if (!user) {
        return false;
      }

      // Verify current password
      const currentPasswordValid = await this.verifyPassword(user, request.currentPassword);
      if (!currentPasswordValid) {
        return false;
      }

      // Validate new password
      const passwordError = this.validatePassword(request.newPassword);
      if (passwordError) {
        return false;
      }

      // Check if new password is different from current
      if (request.currentPassword === request.newPassword) {
        return false;
      }

      // Hash new password
      const passwordHash = await EncryptionUtils.hashPassword(request.newPassword);

      // Update user password
      user.security.passwordHash = passwordHash.hash;
      user.security.salt = passwordHash.salt;
      user.updatedAt = new Date().toISOString();

      await this.storeUser(user);

      // Invalidate all sessions
      await this.invalidateUserSessions(userId);

      // Send security alert
      await this.sendSecurityAlert(userId, 'password_change', 'high', 'Password changed', {
        timestamp: new Date().toISOString()
      });

      return true;
    } catch (error) {
      console.error('Password change error:', error);
      return false;
    }
  }

  static async setupTwoFactor(userId: string, setup: TwoFactorSetup): Promise<{ success: boolean; secret?: string; backupCodes?: string[] }> {
    try {
      const user = await this.getUserById(userId);
      if (!user) {
        return { success: false };
      }

      const secret = setup.secret || EncryptionUtils.generateSecureToken(32);
      const backupCodes = Array.from({ length: 10 }, () => EncryptionUtils.generateSecureToken(8));

      user.security.twoFactorSecret = secret;
      user.security.backupCodes = backupCodes;
      user.twoFactorEnabled = true;
      user.updatedAt = new Date().toISOString();

      await this.storeUser(user);

      return { success: true, secret, backupCodes };
    } catch (error) {
      console.error('Two-factor setup error:', error);
      return { success: false };
    }
  }

  static async disableTwoFactor(userId: string): Promise<boolean> {
    try {
      const user = await this.getUserById(userId);
      if (!user) {
        return false;
      }

      user.security.twoFactorSecret = undefined;
      user.security.backupCodes = undefined;
      user.twoFactorEnabled = false;
      user.updatedAt = new Date().toISOString();

      await this.storeUser(user);

      return true;
    } catch (error) {
      console.error('Two-factor disable error:', error);
      return false;
    }
  }

  static async getSecurityAlerts(userId: string): Promise<SecurityAlert[]> {
    const alerts = await this.getAllSecurityAlerts();
    return alerts.filter(alert => alert.userId === userId);
  }

  static async markAlertAsRead(alertId: string): Promise<boolean> {
    const alerts = await this.getAllSecurityAlerts();
    const alert = alerts.find(a => a.id === alertId);

    if (alert) {
      alert.read = true;
      await this.storeSecurityAlerts(alerts);
      return true;
    }

    return false;
  }

  static async getUserSessions(userId: string): Promise<SessionInfo[]> {
    const sessions = await this.getAllSessions();
    return sessions
      .filter(s => s.userId === userId && s.isActive)
      .map(s => ({
        id: s.id,
        userId: s.userId,
        device: s.device,
        ipAddress: s.ipAddress,
        userAgent: s.userAgent,
        createdAt: s.createdAt,
        lastActivity: new Date().toISOString(),
        expiresAt: s.expiresAt,
        isActive: s.isActive
      }));
  }

  static async terminateSession(sessionId: string, userId: string): Promise<boolean> {
    const sessions = await this.getAllSessions();
    const session = sessions.find(s => s.id === sessionId && s.userId === userId);

    if (session) {
      session.isActive = false;
      await this.storeSessions(sessions);
      return true;
    }

    return false;
  }

  static async terminateAllSessions(userId: string): Promise<boolean> {
    const sessions = await this.getAllSessions();
    const userSessions = sessions.filter(s => s.userId === userId);

    userSessions.forEach(session => {
      session.isActive = false;
    });

    await this.storeSessions(sessions);
    return true;
  }

  // Private helper methods
  private static validateRegisterRequest(request: RegisterRequest): string | null {
    if (!request.email || !request.password || !request.fullName) {
      return 'Email, password, and full name are required';
    }

    if (!this.validateEmail(request.email)) {
      return 'Invalid email address';
    }

    const passwordError = this.validatePassword(request.password);
    if (passwordError) {
      return passwordError;
    }

    if (!request.agreeToTerms) {
      return 'You must agree to the terms and conditions';
    }

    return null;
  }

  private static validatePassword(password: string): string | null {
    const policy = this.DEFAULT_CONFIG.passwordPolicy;

    if (password.length < policy.minLength) {
      return `Password must be at least ${policy.minLength} characters long`;
    }

    if (policy.requireUppercase && !/[A-Z]/.test(password)) {
      return 'Password must contain at least one uppercase letter';
    }

    if (policy.requireLowercase && !/[a-z]/.test(password)) {
      return 'Password must contain at least one lowercase letter';
    }

    if (policy.requireNumbers && !/[0-9]/.test(password)) {
      return 'Password must contain at least one number';
    }

    if (policy.requireSpecialChars && !/[!@#$%^&*]/.test(password)) {
      return 'Password must contain at least one special character';
    }

    return null;
  }

  private static validateEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  private static async createSession(user: User): Promise<AuthToken> {
    const session: Session = {
      id: EncryptionUtils.generateSecureId('session'),
      token: EncryptionUtils.generateSecureToken(32),
      refreshToken: EncryptionUtils.generateSecureToken(32),
      device: {
        id: EncryptionUtils.generateSecureId('device'),
        name: 'Web Browser',
        type: 'desktop',
        platform: navigator.platform,
        browser: navigator.userAgent,
        ipAddress: 'unknown',
        lastUsed: new Date().toISOString(),
        isTrusted: false,
        createdAt: new Date().toISOString()
      },
      ipAddress: 'unknown',
      userAgent: navigator.userAgent,
      expiresAt: new Date(Date.now() + this.DEFAULT_CONFIG.sessionTimeout).toISOString(),
      createdAt: new Date().toISOString(),
      isActive: true
    };

    const sessions = await this.getAllSessions();
    sessions.push(session);
    await this.storeSessions(sessions);

    return {
      accessToken: session.token,
      refreshToken: session.refreshToken,
      tokenType: 'Bearer',
      expiresIn: this.DEFAULT_CONFIG.sessionTimeout / 1000,
      scope: ['read', 'write']
    };
  }

  private static async verifyPassword(user: User, password: string): Promise<boolean> {
    const passwordHash = {
      hash: user.security.passwordHash,
      salt: user.security.salt,
      algorithm: 'pbkdf2',
      iterations: 100000,
      version: '1'
    };

    return EncryptionUtils.verifyPassword(password, passwordHash);
  }

  private static async verifyTwoFactor(user: User, code: string): Promise<boolean> {
    // In a real implementation, this would verify against a TOTP app or SMS
    return user.security.backupCodes?.includes(code) || false;
  }

  private static async recordLoginAttempt(email: string, success: boolean, reason?: string): Promise<void> {
    const attempts = await this.getLoginAttempts();
    const attempt: LoginAttempt = {
      id: EncryptionUtils.generateSecureId('attempt'),
      email,
      ipAddress: 'unknown',
      userAgent: navigator.userAgent,
      success,
      timestamp: new Date().toISOString(),
      failureReason: reason
    };

    attempts.push(attempt);

    // Keep only last 100 attempts
    if (attempts.length > 100) {
      attempts.splice(0, attempts.length - 100);
    }

    await SecureStorage.store(this.LOGIN_ATTEMPTS_KEY, attempts);
  }

  private static async checkAccountLockout(email: string): Promise<{ isLocked: boolean; remainingTime: number }> {
    const attempts = await this.getLoginAttempts();
    const recentAttempts = attempts.filter(a =>
      a.email === email &&
      !a.success &&
      new Date(a.timestamp).getTime() > Date.now() - this.DEFAULT_CONFIG.lockoutDuration
    );

    if (recentAttempts.length >= this.DEFAULT_CONFIG.maxLoginAttempts) {
      const oldestAttempt = recentAttempts[0];
      const remainingTime = new Date(oldestAttempt.timestamp).getTime() + this.DEFAULT_CONFIG.lockoutDuration - Date.now();
      return { isLocked: true, remainingTime };
    }

    return { isLocked: false, remainingTime: 0 };
  }

  private static async sendVerificationEmail(user: User): Promise<void> {
    // In a real implementation, this would send an email
    console.log(`Verification email sent to ${user.email}`);
  }

  private static async sendPasswordResetEmail(user: User, token: string): Promise<void> {
    // In a real implementation, this would send an email
    console.log(`Password reset email sent to ${user.email}`);
  }

  private static async sendSecurityAlert(userId: string, type: SecurityAlert['type'], severity: SecurityAlert['severity'], title: string, details: Record<string, any>): Promise<void> {
    const alerts = await this.getAllSecurityAlerts();
    const alert: SecurityAlert = {
      id: EncryptionUtils.generateSecureId('alert'),
      userId,
      type,
      severity,
      title,
      message: title,
      details,
      timestamp: new Date().toISOString(),
      read: false
    };

    alerts.push(alert);
    await this.storeSecurityAlerts(alerts);
  }

  private static async findUserByResetToken(token: string): Promise<{ user: User; resetData: any } | null> {
    const users = await this.getAllUsers();

    for (const user of users) {
      const resetData = await SecureStorage.retrieve(`password_reset_${user.id}`);
      if (resetData && resetData.token === token && new Date(resetData.expiresAt) > new Date()) {
        return { user, resetData };
      }
    }

    return null;
  }

  private static async invalidateUserSessions(userId: string): Promise<void> {
    const sessions = await this.getAllSessions();
    sessions.forEach(session => {
      if (session.userId === userId) {
        session.isActive = false;
      }
    });
    await this.storeSessions(sessions);
  }

  private static generateAuthToken(userId: string, expiresAt: string): AuthToken {
    return {
      accessToken: EncryptionUtils.generateSecureToken(32),
      refreshToken: EncryptionUtils.generateSecureToken(32),
      tokenType: 'Bearer',
      expiresIn: Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000),
      scope: ['read', 'write']
    };
  }

  // Storage helper methods
  private static async storeUser(user: User): Promise<void> {
    const users = await this.getAllUsers();
    const existingIndex = users.findIndex(u => u.id === user.id);

    if (existingIndex >= 0) {
      users[existingIndex] = user;
    } else {
      users.push(user);
    }

    await SecureStorage.store(this.USERS_STORAGE_KEY, users);
  }

  private static async getAllUsers(): Promise<User[]> {
    return (await SecureStorage.retrieve<User[]>(this.USERS_STORAGE_KEY)) || [];
  }

  private static async getUserById(userId: string): Promise<User | null> {
    const users = await this.getAllUsers();
    return users.find(u => u.id === userId) || null;
  }

  private static async getUserByEmail(email: string): Promise<User | null> {
    const users = await this.getAllUsers();
    return users.find(u => u.email === email) || null;
  }

  private static async storeSessions(sessions: Session[]): Promise<void> {
    await SecureStorage.store(this.SESSIONS_STORAGE_KEY, sessions);
  }

  private static async getAllSessions(): Promise<Session[]> {
    return (await SecureStorage.retrieve<Session[]>(this.SESSIONS_STORAGE_KEY)) || [];
  }

  private static async getLoginAttempts(): Promise<LoginAttempt[]> {
    return (await SecureStorage.retrieve<LoginAttempt[]>(this.LOGIN_ATTEMPTS_KEY)) || [];
  }

  private static async getAllSecurityAlerts(): Promise<SecurityAlert[]> {
    return (await SecureStorage.retrieve<SecurityAlert[]>(this.SECURITY_ALERTS_KEY)) || [];
  }

  private static async storeSecurityAlerts(alerts: SecurityAlert[]): Promise<void> {
    await SecureStorage.store(this.SECURITY_ALERTS_KEY, alerts);
  }
}
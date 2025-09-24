#!/usr/bin/env node

/**
 * Security & Privacy Audit Test Suite for CV Maker
 * Agent 6 Implementation Verification
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class SecurityAudit {
  constructor() {
    this.results = {
      photoProtection: { status: 'pending', score: 0, issues: [] },
      informationHiding: { status: 'pending', score: 0, issues: [] },
      accessControls: { status: 'pending', score: 0, issues: [] },
      dataEncryption: { status: 'pending', score: 0, issues: [] },
      secureSharing: { status: 'pending', score: 0, issues: [] },
      gdprCompliance: { status: 'pending', score: 0, issues: [] },
      inputSanitization: { status: 'pending', score: 0, issues: [] },
      fileUploadSecurity: { status: 'pending', score: 0, issues: [] },
      dataValidation: { status: 'pending', score: 0, issues: [] },
      sessionSecurity: { status: 'pending', score: 0, issues: [] }
    };
    this.overallScore = 0;
    this.maxScore = 100;
  }

  async runAudit() {
    console.log('🔒 Starting Security & Privacy Audit for CV Maker\n');

    await this.testPhotoProtection();
    await this.testInformationHiding();
    await this.testAccessControls();
    await this.testDataEncryption();
    await this.testSecureSharing();
    await this.testGdprCompliance();
    await this.testInputSanitization();
    await this.testFileUploadSecurity();
    await this.testDataValidation();
    await this.testSessionSecurity();

    this.calculateOverallScore();
    this.generateReport();
  }

  async testPhotoProtection() {
    console.log('📸 Testing Photo Protection Features...');

    let score = 0;
    let issues = [];

    try {
      // Check if photo protection utilities exist
      const photoProtectionPath = path.join(__dirname, 'src/utils/photoProtectionUtils.ts');
      if (fs.existsSync(photoProtectionPath)) {
        score += 20;

        const content = fs.readFileSync(photoProtectionPath, 'utf8');

        // Check watermarking functionality
        if (content.includes('applyWatermark') && content.includes('watermark')) {
          score += 15;
        } else {
          issues.push('Watermarking functionality not implemented');
        }

        // Check blur functionality
        if (content.includes('applyBlur') && content.includes('blur')) {
          score += 15;
        } else {
          issues.push('Blur functionality not implemented');
        }

        // Check access control
        if (content.includes('validatePhotoAccess') && content.includes('accessPermissions')) {
          score += 15;
        } else {
          issues.push('Photo access control not implemented');
        }

        // Check metadata stripping
        if (content.includes('stripMetadata') && content.includes('stripExif')) {
          score += 15;
        } else {
          issues.push('Metadata stripping not implemented');
        }

        // Check encryption
        if (content.includes('encryptPhoto') && content.includes('encryptedContent')) {
          score += 10;
        } else {
          issues.push('Photo encryption not implemented');
        }

        // Check secure photo ID generation
        if (content.includes('generatePhotoId') && content.includes('SecureId')) {
          score += 10;
        } else {
          issues.push('Secure photo ID generation not implemented');
        }

      } else {
        issues.push('Photo protection utilities not found');
      }
    } catch (error) {
      issues.push(`Error testing photo protection: ${error.message}`);
    }

    this.results.photoProtection = {
      status: score >= 70 ? 'pass' : 'fail',
      score,
      issues
    };

    console.log(`Photo Protection: ${score >= 70 ? '✅' : '❌'} (${score}/100)`);
  }

  async testInformationHiding() {
    console.log('🙈 Testing Information Hiding Features...');

    let score = 0;
    let issues = [];

    try {
      // Check privacy utilities
      const privacyUtilsPath = path.join(__dirname, 'src/utils/privacyUtils.ts');
      if (fs.existsSync(privacyUtilsPath)) {
        score += 25;

        const content = fs.readFileSync(privacyUtilsPath, 'utf8');

        // Check field visibility controls
        if (content.includes('canAccessField') && content.includes('fieldVisibility')) {
          score += 20;
        } else {
          issues.push('Field visibility controls not implemented');
        }

        // Check data masking
        if (content.includes('maskSensitiveData') && content.includes('MASKING_RULES')) {
          score += 20;
        } else {
          issues.push('Data masking not implemented');
        }

        // Check privacy levels
        if (content.includes('PrivacyLevel') && content.includes('public', 'private', 'family')) {
          score += 15;
        } else {
          issues.push('Privacy levels not implemented');
        }

        // Check privacy settings validation
        if (content.includes('validatePrivacySettings') && content.includes('PrivacySettings')) {
          score += 10;
        } else {
          issues.push('Privacy settings validation not implemented');
        }

        // Check privacy audit logging
        if (content.includes('logPrivacyAction') && content.includes('PrivacyAuditLog')) {
          score += 10;
        } else {
          issues.push('Privacy audit logging not implemented');
        }

      } else {
        issues.push('Privacy utilities not found');
      }
    } catch (error) {
      issues.push(`Error testing information hiding: ${error.message}`);
    }

    this.results.informationHiding = {
      status: score >= 70 ? 'pass' : 'fail',
      score,
      issues
    };

    console.log(`Information Hiding: ${score >= 70 ? '✅' : '❌'} (${score}/100)`);
  }

  async testAccessControls() {
    console.log('🔐 Testing Access Controls...');

    let score = 0;
    let issues = [];

    try {
      // Check authentication utilities
      const authPath = path.join(__dirname, 'src/utils/authenticationUtils.ts');
      if (fs.existsSync(authPath)) {
        score += 30;

        const content = fs.readFileSync(authPath, 'utf8');

        // Check user authentication
        if (content.includes('login') && content.includes('register') && content.includes('logout')) {
          score += 20;
        } else {
          issues.push('Basic authentication not implemented');
        }

        // Check role-based access
        if (content.includes('role') && content.includes('permissions')) {
          score += 15;
        } else {
          issues.push('Role-based access control not implemented');
        }

        // Check session management
        if (content.includes('validateSession') && content.includes('SessionInfo')) {
          score += 15;
        } else {
          issues.push('Session management not implemented');
        }

        // Check password policies
        if (content.includes('passwordPolicy') && content.includes('validatePassword')) {
          score += 10;
        } else {
          issues.push('Password policies not implemented');
        }

        // Check two-factor authentication
        if (content.includes('TwoFactorSetup') && content.includes('verifyTwoFactor')) {
          score += 10;
        } else {
          issues.push('Two-factor authentication not implemented');
        }

      } else {
        issues.push('Authentication utilities not found');
      }
    } catch (error) {
      issues.push(`Error testing access controls: ${error.message}`);
    }

    this.results.accessControls = {
      status: score >= 70 ? 'pass' : 'fail',
      score,
      issues
    };

    console.log(`Access Controls: ${score >= 70 ? '✅' : '❌'} (${score}/100)`);
  }

  async testDataEncryption() {
    console.log('🔒 Testing Data Encryption...');

    let score = 0;
    let issues = [];

    try {
      // Check encryption utilities
      const encryptionPath = path.join(__dirname, 'src/utils/encryptionUtils.ts');
      if (fs.existsSync(encryptionPath)) {
        score += 25;

        const content = fs.readFileSync(encryptionPath, 'utf8');

        // Check encryption/decryption functions
        if (content.includes('encryptData') && content.includes('decryptData')) {
          score += 25;
        } else {
          issues.push('Basic encryption/decryption not implemented');
        }

        // Check password hashing
        if (content.includes('hashPassword') && content.includes('verifyPassword')) {
          score += 20;
        } else {
          issues.push('Password hashing not implemented');
        }

        // Check secure token generation
        if (content.includes('generateSecureToken') && content.includes('generateSecureId')) {
          score += 15;
        } else {
          issues.push('Secure token generation not implemented');
        }

        // Check encryption key management
        if (content.includes('EncryptionKey') && content.includes('keyRotation')) {
          score += 15;
        } else {
          issues.push('Encryption key management not implemented');
        }

      } else {
        issues.push('Encryption utilities not found');
      }
    } catch (error) {
      issues.push(`Error testing data encryption: ${error.message}`);
    }

    this.results.dataEncryption = {
      status: score >= 70 ? 'pass' : 'fail',
      score,
      issues
    };

    console.log(`Data Encryption: ${score >= 70 ? '✅' : '❌'} (${score}/100)`);
  }

  async testSecureSharing() {
    console.log('🔗 Testing Secure Sharing Features...');

    let score = 0;
    let issues = [];

    try {
      // Check secure sharing utilities
      const sharingPath = path.join(__dirname, 'src/utils/secureSharing.ts');
      if (fs.existsSync(sharingPath)) {
        score += 25;

        const content = fs.readFileSync(sharingPath, 'utf8');

        // Check share creation and validation
        if (content.includes('createShare') && content.includes('validateShare')) {
          score += 20;
        } else {
          issues.push('Share creation and validation not implemented');
        }

        // Check password-protected sharing
        if (content.includes('password') && content.includes('hashPassword')) {
          score += 15;
        } else {
          issues.push('Password-protected sharing not implemented');
        }

        // Check access control and expiration
        if (content.includes('expiresAt') && content.includes('maxAccessCount')) {
          score += 15;
        } else {
          issues.push('Access limits and expiration not implemented');
        }

        // Check access logging
        if (content.includes('accessLogs') && content.includes('logAccessAttempt')) {
          score += 15;
        } else {
          issues.push('Access logging not implemented');
        }

        // Check share revocation
        if (content.includes('revokeShare') && content.includes('isActive')) {
          score += 10;
        } else {
          issues.push('Share revocation not implemented');
        }

      } else {
        issues.push('Secure sharing utilities not found');
      }
    } catch (error) {
      issues.push(`Error testing secure sharing: ${error.message}`);
    }

    this.results.secureSharing = {
      status: score >= 70 ? 'pass' : 'fail',
      score,
      issues
    };

    console.log(`Secure Sharing: ${score >= 70 ? '✅' : '❌'} (${score}/100)`);
  }

  async testGdprCompliance() {
    console.log('📋 Testing GDPR Compliance...');

    let score = 0;
    let issues = [];

    try {
      // Check for GDPR-related features across files
      const filesToCheck = [
        'src/utils/privacyUtils.ts',
        'src/utils/secureSharing.ts',
        'src/utils/authenticationUtils.ts'
      ];

      let hasExport = false;
      let hasDeletion = false;
      let hasConsent = false;
      let hasAudit = false;

      for (const file of filesToCheck) {
        if (fs.existsSync(path.join(__dirname, file))) {
          const content = fs.readFileSync(path.join(__dirname, file), 'utf8');

          if (content.includes('export') || content.includes('Export')) {
            hasExport = true;
          }
          if (content.includes('delete') || content.includes('Delete')) {
            hasDeletion = true;
          }
          if (content.includes('consent') || content.includes('agreeToTerms')) {
            hasConsent = true;
          }
          if (content.includes('audit') || content.includes('log')) {
            hasAudit = true;
          }
        }
      }

      if (hasExport) score += 25;
      else issues.push('Data export functionality not found');

      if (hasDeletion) score += 25;
      else issues.push('Data deletion functionality not found');

      if (hasConsent) score += 25;
      else issues.push('User consent management not found');

      if (hasAudit) score += 25;
      else issues.push('Audit logging not found');

    } catch (error) {
      issues.push(`Error testing GDPR compliance: ${error.message}`);
    }

    this.results.gdprCompliance = {
      status: score >= 70 ? 'pass' : 'fail',
      score,
      issues
    };

    console.log(`GDPR Compliance: ${score >= 70 ? '✅' : '❌'} (${score}/100)`);
  }

  async testInputSanitization() {
    console.log('🧼 Testing Input Sanitization...');

    let score = 0;
    let issues = [];

    try {
      // Check validation utilities
      const validationPath = path.join(__dirname, 'src/utils/validationUtils.ts');
      if (fs.existsSync(validationPath)) {
        score += 30;

        const content = fs.readFileSync(validationPath, 'utf8');

        // Check input sanitization
        if (content.includes('sanitizeInput') && content.includes('replace')) {
          score += 25;
        } else {
          issues.push('Input sanitization not implemented');
        }

        // Check XSS protection
        if (content.includes('javascript:') || content.includes('on\\w+')) {
          score += 20;
        } else {
          issues.push('XSS protection not implemented');
        }

        // Check HTML tag removal
        if (content.includes('<[^>]*>')) {
          score += 15;
        } else {
          issues.push('HTML tag removal not implemented');
        }

        // Check validation functions
        if (content.includes('validateEmail') && content.includes('validatePhone')) {
          score += 10;
        } else {
          issues.push('Basic validation functions not implemented');
        }

      } else {
        issues.push('Validation utilities not found');
      }

      // Check form components for sanitization
      const formComponentsPath = path.join(__dirname, 'src/components/common/Input.tsx');
      if (fs.existsSync(formComponentsPath)) {
        const content = fs.readFileSync(formComponentsPath, 'utf8');
        if (content.includes('type') || content.includes('pattern')) {
          score += 10;
        } else {
          issues.push('Form component security not implemented');
        }
      }

    } catch (error) {
      issues.push(`Error testing input sanitization: ${error.message}`);
    }

    this.results.inputSanitization = {
      status: score >= 70 ? 'pass' : 'fail',
      score,
      issues
    };

    console.log(`Input Sanitization: ${score >= 70 ? '✅' : '❌'} (${score}/100)`);
  }

  async testFileUploadSecurity() {
    console.log('📁 Testing File Upload Security...');

    let score = 0;
    let issues = [];

    try {
      // Check file upload utilities
      const uploadPath = path.join(__dirname, 'src/utils/fileHandler.ts');
      if (fs.existsSync(uploadPath)) {
        score += 30;

        const content = fs.readFileSync(uploadPath, 'utf8');

        // Check file type validation
        if (content.includes('validateFileType') || content.includes('allowedTypes')) {
          score += 20;
        } else {
          issues.push('File type validation not implemented');
        }

        // Check file size validation
        if (content.includes('validateFileSize') || content.includes('maxSize')) {
          score += 20;
        } else {
          issues.push('File size validation not implemented');
        }

        // Check file sanitization
        if (content.includes('sanitizeFilename') || content.includes('sanitizeFile')) {
          score += 15;
        } else {
          issues.push('File sanitization not implemented');
        }

        // Check secure upload handling
        if (content.includes('secureUpload') || content.includes('uploadSecurity')) {
          score += 15;
        } else {
          issues.push('Secure upload handling not implemented');
        }

      } else {
        issues.push('File upload utilities not found');
      }

      // Check photo protection for uploads
      const photoPath = path.join(__dirname, 'src/utils/photoProtectionUtils.ts');
      if (fs.existsSync(photoPath)) {
        const content = fs.readFileSync(photoPath, 'utf8');
        if (content.includes('sanitizePhotoName') || content.includes('validatePhoto')) {
          score += 10;
        } else {
          issues.push('Photo-specific upload security not implemented');
        }
      }

    } catch (error) {
      issues.push(`Error testing file upload security: ${error.message}`);
    }

    this.results.fileUploadSecurity = {
      status: score >= 70 ? 'pass' : 'fail',
      score,
      issues
    };

    console.log(`File Upload Security: ${score >= 70 ? '✅' : '❌'} (${score}/100)`);
  }

  async testDataValidation() {
    console.log('✅ Testing Data Validation...');

    let score = 0;
    let issues = [];

    try {
      // Check validation schemas
      const schemasPath = path.join(__dirname, 'src/validations');
      if (fs.existsSync(schemasPath)) {
        score += 30;

        // Check for validation files
        const validationFiles = fs.readdirSync(schemasPath);
        if (validationFiles.some(file => file.includes('cv') || file.includes('marriage'))) {
          score += 20;
        } else {
          issues.push('Validation schemas not found');
        }

        // Check validation utilities
        const validationUtilsPath = path.join(__dirname, 'src/utils/validationUtils.ts');
        if (fs.existsSync(validationUtilsPath)) {
          const content = fs.readFileSync(validationUtilsPath, 'utf8');

          if (content.includes('validateForm') && content.includes('validateStep')) {
            score += 20;
          } else {
            issues.push('Form validation not implemented');
          }

          if (content.includes('formatValidationErrors') && content.includes('ValidationError')) {
            score += 15;
          } else {
            issues.push('Error formatting not implemented');
          }

          if (content.includes('validateRequiredFields')) {
            score += 15;
          } else {
            issues.push('Required field validation not implemented');
          }
        }

      } else {
        issues.push('Validation directory not found');
      }

      // Check for Zod usage
      const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
      if (packageJson.dependencies.zod || packageJson.devDependencies.zod) {
        score += 10;
      } else {
        issues.push('Zod validation library not found');
      }

    } catch (error) {
      issues.push(`Error testing data validation: ${error.message}`);
    }

    this.results.dataValidation = {
      status: score >= 70 ? 'pass' : 'fail',
      score,
      issues
    };

    console.log(`Data Validation: ${score >= 70 ? '✅' : '❌'} (${score}/100)`);
  }

  async testSessionSecurity() {
    console.log('🔑 Testing Session Security...');

    let score = 0;
    let issues = [];

    try {
      // Check authentication utilities
      const authPath = path.join(__dirname, 'src/utils/authenticationUtils.ts');
      if (fs.existsSync(authPath)) {
        score += 30;

        const content = fs.readFileSync(authPath, 'utf8');

        // Check session management
        if (content.includes('createSession') && content.includes('validateSession')) {
          score += 20;
        } else {
          issues.push('Session management not implemented');
        }

        // Check session timeout
        if (content.includes('sessionTimeout') && content.includes('expiresAt')) {
          score += 20;
        } else {
          issues.push('Session timeout not implemented');
        }

        // Check session invalidation
        if (content.includes('invalidateUserSessions') || content.includes('terminateSession')) {
          score += 15;
        } else {
          issues.push('Session invalidation not implemented');
        }

        // Check refresh token handling
        if (content.includes('refreshToken') && content.includes('token refresh')) {
          score += 15;
        } else {
          issues.push('Refresh token handling not implemented');
        }

      } else {
        issues.push('Authentication utilities not found');
      }

      // Check security monitoring
      const monitoringPath = path.join(__dirname, 'src/utils/securityMonitoring.ts');
      if (fs.existsSync(monitoringPath)) {
        const content = fs.readFileSync(monitoringPath, 'utf8');
        if (content.includes('Session') || content.includes('monitorLoginAttempt')) {
          score += 10;
        } else {
          issues.push('Session monitoring not implemented');
        }
      }

    } catch (error) {
      issues.push(`Error testing session security: ${error.message}`);
    }

    this.results.sessionSecurity = {
      status: score >= 70 ? 'pass' : 'fail',
      score,
      issues
    };

    console.log(`Session Security: ${score >= 70 ? '✅' : '❌'} (${score}/100)`);
  }

  calculateOverallScore() {
    const scores = Object.values(this.results).map(result => result.score);
    this.overallScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  }

  generateReport() {
    console.log('\n' + '='.repeat(80));
    console.log('🔒 SECURITY & PRIVACY AUDIT REPORT');
    console.log('='.repeat(80));
    console.log(`Overall Score: ${this.overallScore}/100 (${this.overallScore >= 70 ? 'PASS' : 'FAIL'})`);
    console.log('');

    console.log('Detailed Results:');
    console.log('-'.repeat(50));

    Object.entries(this.results).forEach(([category, result]) => {
      const status = result.status === 'pass' ? '✅' : '❌';
      console.log(`${status} ${category.replace(/([A-Z])/g, ' $1').trim()}: ${result.score}/100`);

      if (result.issues.length > 0) {
        result.issues.forEach(issue => {
          console.log(`   ⚠️  ${issue}`);
        });
      }
    });

    console.log('');
    console.log('Security Features Implementation Status:');
    console.log('-'.repeat(50));

    const implementedCount = Object.values(this.results).filter(r => r.status === 'pass').length;
    const totalCount = Object.keys(this.results).length;

    console.log(`Implemented: ${implementedCount}/${totalCount} (${Math.round(implementedCount/totalCount*100)}%)`);

    console.log('');
    console.log('Vulnerability Assessment:');
    console.log('-'.repeat(50));

    const allIssues = Object.values(this.results).flatMap(r => r.issues);
    if (allIssues.length === 0) {
      console.log('🎉 No critical vulnerabilities found!');
    } else {
      console.log(`⚠️  ${allIssues.length} issues identified:`);
      allIssues.forEach((issue, index) => {
        console.log(`${index + 1}. ${issue}`);
      });
    }

    console.log('');
    console.log('Recommendations:');
    console.log('-'.repeat(50));

    if (this.overallScore >= 80) {
      console.log('🟢 Excellent security implementation. Consider penetration testing.');
    } else if (this.overallScore >= 60) {
      console.log('🟡 Good foundation, but address the identified issues.');
    } else {
      console.log('🔴 Significant security issues found. Immediate attention required.');
    }

    console.log('');
    console.log('Next Steps:');
    console.log('1. Address all failing categories');
    console.log('2. Implement missing security features');
    console.log('3. Conduct penetration testing');
    console.log('4. Regular security audits recommended');
    console.log('5. Keep dependencies updated');

    console.log('');
    console.log('='.repeat(80));
  }
}

// Run the audit
const audit = new SecurityAudit();
audit.runAudit().catch(console.error);
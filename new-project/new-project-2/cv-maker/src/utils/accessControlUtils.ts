import {
  Permission,
  Role,
  UserRoleAssignment,
  AccessControlList,
  ACLEntry,
  FamilyGroup,
  FamilyMember,
  AccessRequest,
  AccessGrant,
  AccessLog,
  ResourcePermission,
  AccessPolicy,
  PolicyRule,
  PermissionTemplate
} from '../types/accessControl';
import { EncryptionUtils } from './encryptionUtils';

export interface AccessCheck {
  resourceId: string;
  resourceType: string;
  action: string;
  userId: string;
  userRole: string;
  context?: Record<string, any>;
}

export interface AccessResult {
  granted: boolean;
  reason?: string;
  policy?: string;
  conditions?: Record<string, any>;
}

export class AccessControlUtils {
  private static readonly DEFAULT_ROLES: Role[] = [
    {
      id: 'admin',
      name: 'Administrator',
      description: 'Full system access',
      permissions: [],
      isSystemRole: true,
      hierarchyLevel: 100,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    },
    {
      id: 'user',
      name: 'User',
      description: 'Regular user with standard access',
      permissions: [],
      isSystemRole: true,
      hierarchyLevel: 10,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    },
    {
      id: 'family_member',
      name: 'Family Member',
      description: 'Limited access to family-related data',
      permissions: [],
      isSystemRole: true,
      hierarchyLevel: 5,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    },
    {
      id: 'guest',
      name: 'Guest',
      description: 'Very limited access',
      permissions: [],
      isSystemRole: true,
      hierarchyLevel: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
  ];

  private static readonly DEFAULT_PERMISSIONS: Permission[] = [
    {
      id: 'read_own_profile',
      name: 'Read Own Profile',
      description: 'View own profile information',
      resource: 'profile',
      action: 'read',
      scope: 'global',
      conditions: []
    },
    {
      id: 'edit_own_profile',
      name: 'Edit Own Profile',
      description: 'Edit own profile information',
      resource: 'profile',
      action: 'update',
      scope: 'global',
      conditions: []
    },
    {
      id: 'read_family_data',
      name: 'Read Family Data',
      description: 'View family member information',
      resource: 'family',
      action: 'read',
      scope: 'global',
      conditions: []
    },
    {
      id: 'share_document',
      name: 'Share Document',
      description: 'Share documents with others',
      resource: 'document',
      action: 'share',
      scope: 'global',
      conditions: []
    },
    {
      id: 'admin_all',
      name: 'Admin All',
      description: 'Full administrative access',
      resource: '*',
      action: 'admin',
      scope: 'global',
      conditions: []
    }
  ];

  static async checkAccess(check: AccessCheck): Promise<AccessResult> {
    // Check if user has explicit permission
    const explicitPermission = await this.checkExplicitPermission(check);
    if (explicitPermission.granted) {
      return explicitPermission;
    }

    // Check role-based permissions
    const rolePermission = await this.checkRolePermission(check);
    if (rolePermission.granted) {
      return rolePermission;
    }

    // Check ACL permissions
    const aclPermission = await this.checkACLPermission(check);
    if (aclPermission.granted) {
      return aclPermission;
    }

    // Check policy-based permissions
    const policyPermission = await this.checkPolicyPermission(check);
    if (policyPermission.granted) {
      return policyPermission;
    }

    return {
      granted: false,
      reason: 'No matching permissions found'
    };
  }

  static async grantPermission(
    userId: string,
    roleId: string,
    resourceId?: string,
    grantedBy: string,
    expiresAt?: string,
    conditions?: Record<string, any>
  ): Promise<UserRoleAssignment> {
    const assignment: UserRoleAssignment = {
      id: EncryptionUtils.generateSecureId('assignment'),
      userId,
      roleId,
      resourceId,
      grantedBy,
      grantedAt: new Date().toISOString(),
      expiresAt,
      conditions: conditions || {},
      isActive: true
    };

    // Log the permission grant
    await this.logAccess({
      userId: grantedBy,
      action: 'access_granted',
      resourceId: resourceId || 'global',
      resourceType: 'permission',
      details: {
        targetUserId: userId,
        roleId,
        conditions,
        expiresAt
      },
      timestamp: new Date().toISOString(),
      ipAddress: '',
      userAgent: ''
    });

    return assignment;
  }

  static async revokePermission(
    assignmentId: string,
    revokedBy: string
  ): Promise<void> {
    // Log the permission revocation
    await this.logAccess({
      userId: revokedBy,
      action: 'access_revoked',
      resourceId: assignmentId,
      resourceType: 'permission',
      details: {
        assignmentId
      },
      timestamp: new Date().toISOString(),
      ipAddress: '',
      userAgent: ''
    });
  }

  static async createFamilyGroup(
    name: string,
    description: string,
    createdBy: string,
    maxMembers: number = 50
  ): Promise<FamilyGroup> {
    const familyGroup: FamilyGroup = {
      id: EncryptionUtils.generateSecureId('family'),
      name,
      description,
      createdBy,
      members: [],
      permissions: [],
      settings: {
        autoApproveMembers: false,
        allowMemberInvites: true,
        requireVerification: true,
        dataSharing: 'selected',
        maxMembers
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    // Add creator as first member
    familyGroup.members.push({
      id: EncryptionUtils.generateSecureId('member'),
      userId: createdBy,
      relationship: 'creator',
      permissions: ['admin'],
      joinedAt: new Date().toISOString(),
      invitedBy: createdBy,
      status: 'active'
    });

    return familyGroup;
  }

  static async addFamilyMember(
    familyGroup: FamilyGroup,
    userId: string,
    relationship: string,
    invitedBy: string,
    permissions: string[] = ['view']
  ): Promise<FamilyGroup> {
    if (familyGroup.members.length >= familyGroup.settings.maxMembers) {
      throw new Error('Family group has reached maximum capacity');
    }

    const newMember: FamilyMember = {
      id: EncryptionUtils.generateSecureId('member'),
      userId,
      relationship,
      permissions,
      joinedAt: new Date().toISOString(),
      invitedBy,
      status: familyGroup.settings.autoApproveMembers ? 'active' : 'pending'
    };

    familyGroup.members.push(newMember);
    familyGroup.updatedAt = new Date().toISOString();

    return familyGroup;
  }

  static async removeFamilyMember(
    familyGroup: FamilyGroup,
    userId: string,
    removedBy: string
  ): Promise<FamilyGroup> {
    const memberIndex = familyGroup.members.findIndex(m => m.userId === userId);
    if (memberIndex === -1) {
      throw new Error('Member not found');
    }

    familyGroup.members.splice(memberIndex, 1);
    familyGroup.updatedAt = new Date().toISOString();

    // Log the removal
    await this.logAccess({
      userId: removedBy,
      action: 'access_revoked',
      resourceId: familyGroup.id,
      resourceType: 'family_group',
      details: {
        removedUserId: userId,
        action: 'member_removed'
      },
      timestamp: new Date().toISOString(),
      ipAddress: '',
      userAgent: ''
    });

    return familyGroup;
  }

  static async requestAccess(
    requestedBy: string,
    resourceId: string,
    resourceType: string,
    permissions: string[],
    reason?: string
  ): Promise<AccessRequest> {
    const request: AccessRequest = {
      id: EncryptionUtils.generateSecureId('request'),
      requestedBy,
      resourceId,
      resourceType,
      permissions,
      reason,
      status: 'pending',
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days
      createdAt: new Date().toISOString()
    };

    return request;
  }

  static async approveAccessRequest(
    requestId: string,
    approvedBy: string,
    responseMessage?: string
  ): Promise<AccessGrant> {
    const request = this.getAccessRequest(requestId);
    if (!request) {
      throw new Error('Access request not found');
    }

    const accessGrant: AccessGrant = {
      id: EncryptionUtils.generateSecureId('grant'),
      grantedTo: request.requestedBy,
      grantedBy: approvedBy,
      resourceId: request.resourceId,
      resourceType: request.resourceType,
      permissions: request.permissions,
      conditions: [],
      expiresAt: request.expiresAt,
      isActive: true,
      createdAt: new Date().toISOString()
    };

    // Update request status
    request.status = 'approved';
    request.reviewedBy = approvedBy;
    request.reviewedAt = new Date().toISOString();
    request.responseMessage = responseMessage;

    // Log the approval
    await this.logAccess({
      userId: approvedBy,
      action: 'access_granted',
      resourceId: request.resourceId,
      resourceType: request.resourceType,
      details: {
        grantedTo: request.requestedBy,
        permissions: request.permissions,
        expiresAt: request.expiresAt
      },
      timestamp: new Date().toISOString(),
      ipAddress: '',
      userAgent: ''
    });

    return accessGrant;
  }

  static async createACL(
    resourceId: string,
    resourceType: string,
    defaultPermission: 'allow' | 'deny' = 'deny'
  ): Promise<AccessControlList> {
    const acl: AccessControlList = {
      id: EncryptionUtils.generateSecureId('acl'),
      resourceId,
      resourceType,
      entries: [],
      defaultPermission,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    return acl;
  }

  static async addACLEntry(
    acl: AccessControlList,
    principalId: string,
    principalType: 'user' | 'role' | 'family_group',
    permission: 'allow' | 'deny',
    permissions: string[],
    grantedBy: string,
    expiresAt?: string
  ): Promise<AccessControlList> {
    const entry: ACLEntry = {
      id: EncryptionUtils.generateSecureId('acl_entry'),
      principalId,
      principalType,
      permission,
      permissions,
      grantedBy,
      grantedAt: new Date().toISOString(),
      expiresAt,
      conditions: {},
      isActive: true
    };

    acl.entries.push(entry);
    acl.updatedAt = new Date().toISOString();

    return acl;
  }

  static async getUserPermissions(userId: string): Promise<string[]> {
    const permissions = new Set<string>();

    // Get role-based permissions
    const userRoles = await this.getUserRoles(userId);
    userRoles.forEach(role => {
      role.permissions.forEach(permission => {
        permissions.add(permission.id);
      });
    });

    // Get direct permissions
    const directPermissions = await this.getDirectPermissions(userId);
    directPermissions.forEach(permission => {
      permissions.add(permission);
    });

    return Array.from(permissions);
  }

  static async checkResourceOwnership(
    resourceId: string,
    userId: string
  ): Promise<boolean> {
    // This would typically check a database or storage system
    // For now, we'll implement a simple check
    return false;
  }

  static async createPermissionTemplate(
    name: string,
    description: string,
    permissions: string[],
    applicableTo: 'document' | 'user' | 'family_group',
    isDefault: boolean = false
  ): Promise<PermissionTemplate> {
    const template: PermissionTemplate = {
      id: EncryptionUtils.generateSecureId('template'),
      name,
      description,
      permissions,
      isDefault,
      applicableTo,
      createdAt: new Date().toISOString()
    };

    return template;
  }

  static async applyPermissionTemplate(
    templateId: string,
    targetId: string,
    appliedBy: string
  ): Promise<void> {
    // This would apply the template permissions to the target
    // Implementation would depend on the target type
  }

  private static async checkExplicitPermission(check: AccessCheck): Promise<AccessResult> {
    // Check if user has explicit permission through direct grants
    const userPermissions = await this.getUserPermissions(check.userId);
    const requiredPermission = `${check.action}_${check.resourceType}`;

    if (userPermissions.includes(requiredPermission) || userPermissions.includes('admin_all')) {
      return {
        granted: true,
        reason: 'Explicit permission granted',
        policy: 'explicit'
      };
    }

    return {
      granted: false,
      reason: 'No explicit permission found'
    };
  }

  private static async checkRolePermission(check: AccessCheck): Promise<AccessResult> {
    // Check role-based permissions
    const userRoles = await this.getUserRoles(check.userId);

    for (const role of userRoles) {
      for (const permission of role.permissions) {
        if (this.permissionMatches(permission, check)) {
          return {
            granted: true,
            reason: `Role-based permission granted via role: ${role.name}`,
            policy: 'role'
          };
        }
      }
    }

    return {
      granted: false,
      reason: 'No role-based permission found'
    };
  }

  private static async checkACLPermission(check: AccessCheck): Promise<AccessResult> {
    // Check ACL permissions
    const acl = await this.getACL(check.resourceId, check.resourceType);

    if (!acl) {
      return {
        granted: false,
        reason: 'No ACL found'
      };
    }

    // Check user-specific entries
    const userEntry = acl.entries.find(entry =>
      entry.principalId === check.userId &&
      entry.principalType === 'user' &&
      entry.isActive
    );

    if (userEntry) {
      if (userEntry.permissions.includes(check.action) || userEntry.permissions.includes('all')) {
        return {
          granted: userEntry.permission === 'allow',
          reason: 'ACL permission granted',
          policy: 'acl'
        };
      }
    }

    // Check role-based entries
    const userRoles = await this.getUserRoles(check.userId);
    for (const role of userRoles) {
      const roleEntry = acl.entries.find(entry =>
        entry.principalId === role.id &&
        entry.principalType === 'role' &&
        entry.isActive
      );

      if (roleEntry) {
        if (roleEntry.permissions.includes(check.action) || roleEntry.permissions.includes('all')) {
          return {
            granted: roleEntry.permission === 'allow',
            reason: 'ACL role permission granted',
            policy: 'acl'
          };
        }
      }
    }

    return {
      granted: acl.defaultPermission === 'allow',
      reason: `Default ACL permission: ${acl.defaultPermission}`,
      policy: 'acl'
    };
  }

  private static async checkPolicyPermission(check: AccessCheck): Promise<AccessResult> {
    // Check policy-based permissions
    const policies = await this.getApplicablePolicies(check.userId);

    for (const policy of policies) {
      if (!policy.isActive) continue;

      for (const rule of policy.rules) {
        if (this.policyRuleMatches(rule, check)) {
          return {
            granted: rule.effect === 'allow',
            reason: `Policy permission granted via policy: ${policy.name}`,
            policy: 'policy'
          };
        }
      }
    }

    return {
      granted: false,
      reason: 'No policy permission found'
    };
  }

  private static permissionMatches(permission: Permission, check: AccessCheck): boolean {
    if (permission.resource !== '*' && permission.resource !== check.resourceType) {
      return false;
    }

    if (permission.action !== '*' && permission.action !== check.action) {
      return false;
    }

    // Check conditions
    if (permission.conditions.length > 0) {
      return this.evaluateConditions(permission.conditions, check.context || {});
    }

    return true;
  }

  private static policyRuleMatches(rule: PolicyRule, check: AccessCheck): boolean {
    if (rule.resource !== '*' && rule.resource !== check.resourceType) {
      return false;
    }

    if (rule.action !== '*' && rule.action !== check.action) {
      return false;
    }

    // Check conditions
    if (rule.conditions.length > 0) {
      return this.evaluatePolicyConditions(rule.conditions, check.context || {});
    }

    return true;
  }

  private static evaluateConditions(
    conditions: any[],
    context: Record<string, any>
  ): boolean {
    // Simple condition evaluation - in a real implementation, this would be more sophisticated
    for (const condition of conditions) {
      const contextValue = context[condition.field];
      if (!contextValue) return false;

      switch (condition.operator) {
        case 'equals':
          if (contextValue !== condition.value) return false;
          break;
        case 'contains':
          if (!contextValue.includes(condition.value)) return false;
          break;
        case 'greater_than':
          if (contextValue <= condition.value) return false;
          break;
        case 'less_than':
          if (contextValue >= condition.value) return false;
          break;
      }
    }

    return true;
  }

  private static evaluatePolicyConditions(
    conditions: any[],
    context: Record<string, any>
  ): boolean {
    return this.evaluateConditions(conditions, context);
  }

  private static async getUserRoles(userId: string): Promise<Role[]> {
    // This would typically query a database
    // For now, return default roles
    return this.DEFAULT_ROLES;
  }

  private static async getDirectPermissions(userId: string): Promise<string[]> {
    // This would typically query a database for direct user permissions
    return [];
  }

  private static async getACL(resourceId: string, resourceType: string): Promise<AccessControlList | null> {
    // This would typically query a database
    return null;
  }

  private static async getApplicablePolicies(userId: string): Promise<AccessPolicy[]> {
    // This would typically query a database for applicable policies
    return [];
  }

  private static getAccessRequest(requestId: string): AccessRequest | null {
    // This would typically query a database
    return null;
  }

  private static async logAccess(log: AccessLog): Promise<void> {
    // This would typically save to a database or log file
    console.log('Access Log:', log);
  }
}
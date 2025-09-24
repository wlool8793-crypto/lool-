export interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: 'create' | 'read' | 'update' | 'delete' | 'share' | 'admin';
  scope: 'global' | 'document' | 'field';
  conditions: PermissionCondition[];
}

export interface PermissionCondition {
  field: string;
  operator: 'equals' | 'contains' | 'starts_with' | 'ends_with' | 'greater_than' | 'less_than';
  value: any;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
  isSystemRole: boolean;
  hierarchyLevel: number;
  createdAt: string;
  updatedAt: string;
}

export interface UserRoleAssignment {
  id: string;
  userId: string;
  roleId: string;
  documentId?: string;
  grantedBy: string;
  grantedAt: string;
  expiresAt?: string;
  conditions: Record<string, any>;
  isActive: boolean;
}

export interface AccessControlList {
  id: string;
  resourceId: string;
  resourceType: 'document' | 'field' | 'photo' | 'contact';
  entries: ACLEntry[];
  defaultPermission: 'deny' | 'allow';
  createdAt: string;
  updatedAt: string;
}

export interface ACLEntry {
  id: string;
  principalId: string;
  principalType: 'user' | 'role' | 'family_group';
  permission: 'allow' | 'deny';
  permissions: string[];
  conditions: Record<string, any>;
  grantedBy: string;
  grantedAt: string;
  expiresAt?: string;
  isActive: boolean;
}

export interface FamilyGroup {
  id: string;
  name: string;
  description?: string;
  createdBy: string;
  members: FamilyMember[];
  permissions: GroupPermission[];
  settings: GroupSettings;
  createdAt: string;
  updatedAt: string;
}

export interface FamilyMember {
  id: string;
  userId: string;
  relationship: string;
  permissions: string[];
  joinedAt: string;
  invitedBy: string;
  status: 'active' | 'pending' | 'suspended' | 'removed';
}

export interface GroupPermission {
  resource: string;
  actions: ('read' | 'write' | 'delete' | 'share')[];
  conditions: Record<string, any>;
}

export interface GroupSettings {
  autoApproveMembers: boolean;
  allowMemberInvites: boolean;
  requireVerification: boolean;
  dataSharing: 'none' | 'selected' | 'all';
  maxMembers: number;
}

export interface AccessRequest {
  id: string;
  requestedBy: string;
  resourceId: string;
  resourceType: 'document' | 'field' | 'photo';
  permissions: string[];
  reason?: string;
  status: 'pending' | 'approved' | 'denied' | 'expired';
  reviewedBy?: string;
  reviewedAt?: string;
  responseMessage?: string;
  expiresAt?: string;
  createdAt: string;
}

export interface AccessGrant {
  id: string;
  grantedTo: string;
  grantedBy: string;
  resourceId: string;
  resourceType: 'document' | 'field' | 'photo';
  permissions: string[];
  conditions: AccessCondition[];
  expiresAt?: string;
  maxAccessCount?: number;
  accessCount: number;
  isActive: boolean;
  createdAt: string;
  lastAccessed?: string;
}

export interface AccessCondition {
  type: 'time' | 'location' | 'device' | 'ip' | 'custom';
  field: string;
  operator: 'equals' | 'in' | 'contains' | 'between';
  value: any;
}

export interface AccessLog {
  id: string;
  userId: string;
  action: 'access_granted' | 'access_denied' | 'access_revoked' | 'permission_modified';
  resourceId: string;
  resourceType: 'document' | 'field' | 'photo';
  details: Record<string, any>;
  timestamp: string;
  ipAddress: string;
  userAgent: string;
  sessionId?: string;
}

export interface PermissionInheritance {
  id: string;
  parentId: string;
  childId: string;
  inheritanceType: 'full' | 'partial' | 'custom';
  inheritedPermissions: string[];
  conditions: Record<string, any>;
  isActive: boolean;
  createdAt: string;
}

export interface ResourcePermission {
  resourceId: string;
  resourceType: 'document' | 'field' | 'photo' | 'contact';
  userId: string;
  permissions: string[];
  grantedBy: string;
  grantedAt: string;
  expiresAt?: string;
  conditions: Record<string, any>;
  isActive: boolean;
}

export interface AccessPolicy {
  id: string;
  name: string;
  description: string;
  rules: PolicyRule[];
  priority: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface PolicyRule {
  id: string;
  resource: string;
  action: string;
  effect: 'allow' | 'deny';
  conditions: PolicyCondition[];
}

export interface PolicyCondition {
  field: string;
  operator: string;
  value: any;
}

export interface PermissionTemplate {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  isDefault: boolean;
  applicableTo: 'document' | 'user' | 'family_group';
  createdAt: string;
}
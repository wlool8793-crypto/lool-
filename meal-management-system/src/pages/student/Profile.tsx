import React, { useState, useEffect, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User as UserIcon,
  Mail,
  Phone,
  Home,
  Camera,
  Save,
  Loader2,
  AlertCircle,
  Lock,
  LogOut,
  CheckCircle,
  X,
} from 'lucide-react';
import { getCurrentUser, logout, updatePassword } from '../../services/auth.service';
import { updateUserProfile, uploadProfilePicture } from '../../services/users.service';
import { User } from '../../types/database.types';
import toast from 'react-hot-toast';

interface ProfileFormData {
  full_name: string;
  email: string;
  phone: string;
  room_number: string;
}

interface PasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<ProfileFormData>({
    full_name: '',
    email: '',
    phone: '',
    room_number: '',
  });
  const [passwordData, setPasswordData] = useState<PasswordFormData>({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [profileImage, setProfileImage] = useState<string | null>(null);

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    setIsLoading(true);

    try {
      const userResult = await getCurrentUser();
      if (!userResult.success || !userResult.data) {
        toast.error('Failed to load profile');
        navigate('/login');
        return;
      }

      const userData = userResult.data;
      setUser(userData);
      setFormData({
        full_name: userData.full_name,
        email: userData.email,
        phone: userData.phone || '',
        room_number: userData.room_number || '',
      });
      setProfileImage(userData.profile_picture_url || null);
    } catch (error) {
      console.error('Error loading profile:', error);
      toast.error('Failed to load profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setHasChanges(true);
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({ ...prev, [name]: value }));
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !user) return;

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image size should be less than 5MB');
      return;
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload a valid image file');
      return;
    }

    setIsUploadingImage(true);

    try {
      const result = await uploadProfilePicture(file, user.id);

      if (result.success && result.data) {
        // Update profile with new image URL
        const updateResult = await updateUserProfile(user.id, {
          profile_picture_url: result.data,
        });

        if (updateResult.success) {
          setProfileImage(result.data);
          toast.success('Profile picture updated successfully!');
        } else {
          toast.error('Failed to update profile picture');
        }
      } else {
        toast.error(result.error || 'Failed to upload image');
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      toast.error('Failed to upload image');
    } finally {
      setIsUploadingImage(false);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!user || !hasChanges) return;

    setIsSaving(true);

    try {
      const result = await updateUserProfile(user.id, {
        full_name: formData.full_name,
        phone: formData.phone || undefined,
        room_number: formData.room_number || undefined,
      });

      if (result.success) {
        toast.success('Profile updated successfully!');
        setHasChanges(false);
        await loadUserProfile();
      } else {
        toast.error(result.error || 'Failed to update profile');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePasswordSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Validate passwords
    if (passwordData.newPassword.length < 8) {
      toast.error('Password must be at least 8 characters long');
      return;
    }

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(passwordData.newPassword)) {
      toast.error('Password must contain uppercase, lowercase, and number');
      return;
    }

    setIsChangingPassword(true);

    try {
      const result = await updatePassword(passwordData.newPassword);

      if (result.success) {
        toast.success('Password changed successfully!');
        setPasswordData({
          currentPassword: '',
          newPassword: '',
          confirmPassword: '',
        });
        setShowPasswordForm(false);
      } else {
        toast.error(result.error || 'Failed to change password');
      }
    } catch (error) {
      console.error('Error changing password:', error);
      toast.error('Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleLogout = async () => {
    try {
      const result = await logout();
      if (result.success) {
        toast.success('Logged out successfully');
        navigate('/login');
      } else {
        toast.error('Failed to logout');
      }
    } catch (error) {
      console.error('Error logging out:', error);
      toast.error('Failed to logout');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <UserIcon className="w-7 h-7 mr-3 text-indigo-600" />
                My Profile
              </h1>
              <p className="text-gray-600 mt-1">Manage your account settings</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <LogOut className="w-5 h-5 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Picture Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Profile Picture</h2>
              <div className="flex flex-col items-center">
                <div className="relative">
                  <div className="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
                    {profileImage ? (
                      <img
                        src={profileImage}
                        alt="Profile"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <UserIcon className="w-16 h-16 text-gray-400" />
                    )}
                  </div>
                  <label
                    htmlFor="profile-image"
                    className="absolute bottom-0 right-0 p-2 bg-indigo-600 rounded-full cursor-pointer hover:bg-indigo-700 transition-colors"
                  >
                    {isUploadingImage ? (
                      <Loader2 className="w-5 h-5 text-white animate-spin" />
                    ) : (
                      <Camera className="w-5 h-5 text-white" />
                    )}
                  </label>
                  <input
                    type="file"
                    id="profile-image"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    disabled={isUploadingImage}
                  />
                </div>
                <p className="text-sm text-gray-500 mt-4 text-center">
                  Click the camera icon to upload a new photo
                </p>
                <p className="text-xs text-gray-400 mt-1">Max size: 5MB</p>
              </div>

              {/* User Info */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-gray-500">Role</p>
                    <p className="text-sm font-medium text-gray-900 capitalize">
                      {user?.role}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Account Status</p>
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        user?.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {user?.is_active ? (
                        <>
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Active
                        </>
                      ) : (
                        <>
                          <X className="w-3 h-3 mr-1" />
                          Inactive
                        </>
                      )}
                    </span>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Member Since</p>
                    <p className="text-sm font-medium text-gray-900">
                      {user?.created_at
                        ? new Date(user.created_at).toLocaleDateString()
                        : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Profile Form Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Profile Information
              </h2>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4">
                  {/* Full Name */}
                  <div>
                    <label
                      htmlFor="full_name"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Full Name
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <UserIcon className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        id="full_name"
                        name="full_name"
                        value={formData.full_name}
                        onChange={handleChange}
                        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        required
                      />
                    </div>
                  </div>

                  {/* Email (Read-only) */}
                  <div>
                    <label
                      htmlFor="email"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Email Address
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg bg-gray-50 cursor-not-allowed"
                        disabled
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Email cannot be changed
                    </p>
                  </div>

                  {/* Phone */}
                  <div>
                    <label
                      htmlFor="phone"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Phone Number
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Phone className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="tel"
                        id="phone"
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        placeholder="1234567890"
                      />
                    </div>
                  </div>

                  {/* Room Number */}
                  <div>
                    <label
                      htmlFor="room_number"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Room Number
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Home className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        id="room_number"
                        name="room_number"
                        value={formData.room_number}
                        onChange={handleChange}
                        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        placeholder="101"
                      />
                    </div>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={!hasChanges || isSaving}
                  className="mt-6 w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isSaving ? (
                    <>
                      <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="-ml-1 mr-2 h-5 w-5" />
                      Save Changes
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* Password Change Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Change Password</h2>
                {!showPasswordForm && (
                  <button
                    onClick={() => setShowPasswordForm(true)}
                    className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
                  >
                    Edit
                  </button>
                )}
              </div>

              {showPasswordForm ? (
                <form onSubmit={handlePasswordSubmit}>
                  <div className="space-y-4">
                    {/* Current Password */}
                    <div>
                      <label
                        htmlFor="currentPassword"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Current Password
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <Lock className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                          type="password"
                          id="currentPassword"
                          name="currentPassword"
                          value={passwordData.currentPassword}
                          onChange={handlePasswordChange}
                          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          required
                        />
                      </div>
                    </div>

                    {/* New Password */}
                    <div>
                      <label
                        htmlFor="newPassword"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        New Password
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <Lock className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                          type="password"
                          id="newPassword"
                          name="newPassword"
                          value={passwordData.newPassword}
                          onChange={handlePasswordChange}
                          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          required
                        />
                      </div>
                    </div>

                    {/* Confirm Password */}
                    <div>
                      <label
                        htmlFor="confirmPassword"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Confirm New Password
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <Lock className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                          type="password"
                          id="confirmPassword"
                          name="confirmPassword"
                          value={passwordData.confirmPassword}
                          onChange={handlePasswordChange}
                          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          required
                        />
                      </div>
                    </div>

                    {/* Password Requirements */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <div className="flex items-start">
                        <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
                        <div className="text-xs text-blue-700">
                          <p className="font-medium">Password requirements:</p>
                          <ul className="list-disc list-inside mt-1 space-y-0.5">
                            <li>At least 8 characters long</li>
                            <li>Contains uppercase and lowercase letters</li>
                            <li>Contains at least one number</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="mt-6 flex gap-3">
                    <button
                      type="submit"
                      disabled={isChangingPassword}
                      className="flex-1 flex items-center justify-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {isChangingPassword ? (
                        <>
                          <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />
                          Changing...
                        </>
                      ) : (
                        'Change Password'
                      )}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setShowPasswordForm(false);
                        setPasswordData({
                          currentPassword: '',
                          newPassword: '',
                          confirmPassword: '',
                        });
                      }}
                      className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <p className="text-sm text-gray-500">
                  Click "Edit" to change your password
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;

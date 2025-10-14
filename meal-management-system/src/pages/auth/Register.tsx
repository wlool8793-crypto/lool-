import React, { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, Mail, Lock, User, Phone, Home, AlertCircle, Loader2 } from 'lucide-react';
import { register } from '../../services/auth.service';
import toast from 'react-hot-toast';

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  full_name: string;
  room_number: string;
  phone: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  full_name?: string;
  room_number?: string;
  phone?: string;
}

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<RegisterFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    room_number: '',
    phone: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Full name validation
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    } else if (formData.full_name.trim().length < 2) {
      newErrors.full_name = 'Full name must be at least 2 characters';
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain uppercase, lowercase, and number';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Room number validation
    if (!formData.room_number.trim()) {
      newErrors.room_number = 'Room number is required';
    }

    // Phone validation (optional but validate if provided)
    if (formData.phone && !/^[0-9]{10}$/.test(formData.phone.replace(/\s/g, ''))) {
      newErrors.phone = 'Please enter a valid 10-digit phone number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const result = await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        role: 'student',
        room_number: formData.room_number,
        phone: formData.phone || undefined,
      });

      if (result.success) {
        toast.success('Registration successful! Please check your email to verify your account.');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        toast.error(result.error || 'Registration failed. Please try again.');
      }
    } catch (error) {
      toast.error('An unexpected error occurred. Please try again.');
      console.error('Registration error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-teal-100 px-4 py-8">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-teal-600 rounded-full mb-4">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Create Account</h1>
          <p className="text-gray-600 mt-2">Join our hostel meal management system</p>
        </div>

        {/* Registration Form Card */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          <form onSubmit={handleSubmit} noValidate>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Full Name Field */}
              <div className="md:col-span-2">
                <label
                  htmlFor="full_name"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Full Name <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    id="full_name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className={`block w-full pl-10 pr-3 py-2 border ${
                      errors.full_name ? 'border-red-500' : 'border-gray-300'
                    } rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent`}
                    placeholder="John Doe"
                    disabled={isLoading}
                  />
                </div>
                {errors.full_name && (
                  <div className="flex items-center mt-1 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.full_name}
                  </div>
                )}
              </div>

              {/* Email Field */}
              <div className="md:col-span-2">
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Email Address <span className="text-red-500">*</span>
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
                    onChange={handleChange}
                    className={`block w-full pl-10 pr-3 py-2 border ${
                      errors.email ? 'border-red-500' : 'border-gray-300'
                    } rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent`}
                    placeholder="you@example.com"
                    disabled={isLoading}
                  />
                </div>
                {errors.email && (
                  <div className="flex items-center mt-1 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.email}
                  </div>
                )}
              </div>

              {/* Password Field */}
              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Password <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className={`block w-full pl-10 pr-3 py-2 border ${
                      errors.password ? 'border-red-500' : 'border-gray-300'
                    } rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent`}
                    placeholder="Min. 8 characters"
                    disabled={isLoading}
                  />
                </div>
                {errors.password && (
                  <div className="flex items-center mt-1 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.password}
                  </div>
                )}
              </div>

              {/* Confirm Password Field */}
              <div>
                <label
                  htmlFor="confirmPassword"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Confirm Password <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className={`block w-full pl-10 pr-3 py-2 border ${
                      errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                    } rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent`}
                    placeholder="Confirm password"
                    disabled={isLoading}
                  />
                </div>
                {errors.confirmPassword && (
                  <div className="flex items-center mt-1 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.confirmPassword}
                  </div>
                )}
              </div>

              {/* Room Number Field */}
              <div>
                <label
                  htmlFor="room_number"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Room Number <span className="text-red-500">*</span>
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
                    className={`block w-full pl-10 pr-3 py-2 border ${
                      errors.room_number ? 'border-red-500' : 'border-gray-300'
                    } rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent`}
                    placeholder="101"
                    disabled={isLoading}
                  />
                </div>
                {errors.room_number && (
                  <div className="flex items-center mt-1 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.room_number}
                  </div>
                )}
              </div>

              {/* Phone Field */}
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
                    className={`block w-full pl-10 pr-3 py-2 border ${
                      errors.phone ? 'border-red-500' : 'border-gray-300'
                    } rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent`}
                    placeholder="1234567890"
                    disabled={isLoading}
                  />
                </div>
                {errors.phone && (
                  <div className="flex items-center mt-1 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.phone}
                  </div>
                )}
              </div>
            </div>

            {/* Terms and Conditions */}
            <div className="mt-6">
              <p className="text-xs text-gray-600">
                By creating an account, you agree to our{' '}
                <Link to="/terms" className="text-teal-600 hover:text-teal-700 font-medium">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/privacy" className="text-teal-600 hover:text-teal-700 font-medium">
                  Privacy Policy
                </Link>
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="mt-6 w-full flex items-center justify-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-teal-600 hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />
                  Creating Account...
                </>
              ) : (
                <>
                  <UserPlus className="-ml-1 mr-2 h-5 w-5" />
                  Create Account
                </>
              )}
            </button>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-medium text-teal-600 hover:text-teal-700"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;

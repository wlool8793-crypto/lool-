import React, { useState, useEffect } from 'react';
import {
  Plus,
  Edit,
  UserCheck,
  UserX,
  Search,
  Eye,
  Phone,
  Mail,
  Home,
  DollarSign,
  UtensilsCrossed,
  AlertCircle,
  X,
} from 'lucide-react';
import { Button } from '../../components/forms/Button';
import { Input } from '../../components/forms/Input';
import { Select } from '../../components/forms/Select';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import {
  getAllUsers,
  getUsersByRole,
  activateUser,
  deactivateUser,
  updateUserProfile,
  searchUsers,
} from '../../services/users.service';
import { getMealsByUser } from '../../services/meals.service';
import { getDepositsByUser } from '../../services/deposits.service';
import { User } from '../../types/database.types';
import { useAuth } from '../../contexts/AuthContext';

interface StudentWithStats extends User {
  totalMeals?: number;
  balance?: number;
}

export const Students: React.FC = () => {
  const { user: currentUser } = useAuth();
  const [students, setStudents] = useState<StudentWithStats[]>([]);
  const [filteredStudents, setFilteredStudents] = useState<StudentWithStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<StudentWithStats | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    room_number: '',
    phone: '',
  });

  const fetchStudents = async () => {
    try {
      setError(null);
      const result = await getUsersByRole('student');

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch students');
      }

      const studentsData = result.data || [];

      // Fetch additional stats for each student
      const studentsWithStats = await Promise.all(
        studentsData.map(async (student) => {
          try {
            // Get meal count for current month
            const currentMonth = new Date().toISOString().slice(0, 7);
            const startDate = `${currentMonth}-01`;
            const endDate = `${currentMonth}-31`;

            const mealsResult = await getMealsByUser(student.id, startDate, endDate);
            const meals = mealsResult.success ? mealsResult.data || [] : [];
            const totalMeals = meals.reduce(
              (sum, meal) =>
                sum +
                (meal.breakfast ? 1 : 0) +
                (meal.lunch ? 1 : 0) +
                (meal.dinner ? 1 : 0),
              0
            );

            // Get deposits to calculate balance (simplified)
            const depositsResult = await getDepositsByUser(student.id);
            const deposits = depositsResult.success ? depositsResult.data || [] : [];
            const totalDeposits = deposits.reduce((sum, d) => sum + d.amount, 0);

            return {
              ...student,
              totalMeals,
              balance: totalDeposits, // Simplified - should subtract meal costs
            };
          } catch {
            return {
              ...student,
              totalMeals: 0,
              balance: 0,
            };
          }
        })
      );

      setStudents(studentsWithStats);
      setFilteredStudents(studentsWithStats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch students');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (term: string) => {
    setSearchTerm(term);

    if (!term.trim()) {
      applyFilters(students, statusFilter);
      return;
    }

    try {
      const result = await searchUsers(term);
      if (result.success) {
        const studentResults = (result.data || []).filter((u) => u.role === 'student');
        applyFilters(studentResults as StudentWithStats[], statusFilter);
      }
    } catch (err) {
      console.error('Search error:', err);
    }
  };

  const applyFilters = (data: StudentWithStats[], status: string) => {
    let filtered = [...data];

    if (status === 'active') {
      filtered = filtered.filter((s) => s.is_active);
    } else if (status === 'inactive') {
      filtered = filtered.filter((s) => !s.is_active);
    }

    setFilteredStudents(filtered);
  };

  const handleStatusFilterChange = (status: 'all' | 'active' | 'inactive') => {
    setStatusFilter(status);
    applyFilters(students, status);
  };

  const handleActivateDeactivate = async (studentId: string, activate: boolean) => {
    setActionLoading(studentId);
    try {
      const result = activate ? await activateUser(studentId) : await deactivateUser(studentId);

      if (!result.success) {
        throw new Error(result.error || 'Failed to update student status');
      }

      await fetchStudents();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update student status');
    } finally {
      setActionLoading(null);
    }
  };

  const handleEditStudent = (student: StudentWithStats) => {
    setSelectedStudent(student);
    setFormData({
      full_name: student.full_name,
      email: student.email,
      room_number: student.room_number || '',
      phone: student.phone || '',
    });
    setShowEditModal(true);
  };

  const handleSaveEdit = async () => {
    if (!selectedStudent) return;

    setActionLoading('edit');
    try {
      const result = await updateUserProfile(selectedStudent.id, formData);

      if (!result.success) {
        throw new Error(result.error || 'Failed to update student');
      }

      setShowEditModal(false);
      setSelectedStudent(null);
      await fetchStudents();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update student');
    } finally {
      setActionLoading(null);
    }
  };

  const handleViewDetails = (student: StudentWithStats) => {
    setSelectedStudent(student);
    setShowDetailsModal(true);
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <EmptyState
          icon={AlertCircle}
          title="Error Loading Students"
          description={error}
          action={{
            label: 'Retry',
            onClick: fetchStudents,
          }}
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Student Management</h1>
          <p className="text-gray-600 mt-1">Manage student accounts and information</p>
        </div>
        <Button onClick={() => setShowAddModal(true)} leftIcon={<Plus className="w-4 h-4" />}>
          Add Student
        </Button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name or email..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="w-full md:w-48">
            <Select
              value={statusFilter}
              onChange={(e) =>
                handleStatusFilterChange(e.target.value as 'all' | 'active' | 'inactive')
              }
              options={[
                { value: 'all', label: 'All Students' },
                { value: 'active', label: 'Active Only' },
                { value: 'inactive', label: 'Inactive Only' },
              ]}
            />
          </div>
        </div>
      </div>

      {/* Students Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Student
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Room
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Phone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Balance
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Meals (Month)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredStudents.map((student) => (
                <tr key={student.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-sm">
                            {student.full_name
                              .split(' ')
                              .map((n) => n[0])
                              .join('')
                              .toUpperCase()}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{student.full_name}</div>
                        <div className="text-sm text-gray-500">{student.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{student.room_number || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{student.phone || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      ${(student.balance || 0).toFixed(2)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{student.totalMeals || 0}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {student.is_active ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Inactive
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleViewDetails(student)}
                        className="text-blue-600 hover:text-blue-900"
                        title="View Details"
                      >
                        <Eye className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleEditStudent(student)}
                        className="text-indigo-600 hover:text-indigo-900"
                        title="Edit"
                      >
                        <Edit className="w-5 h-5" />
                      </button>
                      {student.is_active ? (
                        <button
                          onClick={() => handleActivateDeactivate(student.id, false)}
                          disabled={actionLoading === student.id}
                          className="text-red-600 hover:text-red-900 disabled:opacity-50"
                          title="Deactivate"
                        >
                          <UserX className="w-5 h-5" />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleActivateDeactivate(student.id, true)}
                          disabled={actionLoading === student.id}
                          className="text-green-600 hover:text-green-900 disabled:opacity-50"
                          title="Activate"
                        >
                          <UserCheck className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredStudents.length === 0 && (
          <EmptyState
            icon={AlertCircle}
            title="No Students Found"
            description={
              searchTerm
                ? 'Try adjusting your search or filters'
                : 'Get started by adding your first student'
            }
            action={
              !searchTerm
                ? {
                    label: 'Add Student',
                    onClick: () => setShowAddModal(true),
                  }
                : undefined
            }
          />
        )}
      </div>

      {/* Edit Modal */}
      {showEditModal && selectedStudent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Edit Student</h2>
              <button
                onClick={() => setShowEditModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <Input
                label="Full Name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                placeholder="Enter full name"
              />

              <Input
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="Enter email"
                disabled
              />

              <Input
                label="Room Number"
                value={formData.room_number}
                onChange={(e) => setFormData({ ...formData, room_number: e.target.value })}
                placeholder="Enter room number"
              />

              <Input
                label="Phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="Enter phone number"
              />
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setShowEditModal(false)}>
                Cancel
              </Button>
              <Button onClick={handleSaveEdit} disabled={actionLoading === 'edit'}>
                {actionLoading === 'edit' ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Details Modal */}
      {showDetailsModal && selectedStudent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Student Details</h2>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Student Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-start gap-3">
                  <Mail className="w-5 h-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Email</p>
                    <p className="text-sm font-medium text-gray-900">{selectedStudent.email}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Phone className="w-5 h-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Phone</p>
                    <p className="text-sm font-medium text-gray-900">
                      {selectedStudent.phone || 'N/A'}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Home className="w-5 h-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Room Number</p>
                    <p className="text-sm font-medium text-gray-900">
                      {selectedStudent.room_number || 'N/A'}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <DollarSign className="w-5 h-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Balance</p>
                    <p className="text-sm font-medium text-gray-900">
                      ${(selectedStudent.balance || 0).toFixed(2)}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <UtensilsCrossed className="w-5 h-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Total Meals (This Month)</p>
                    <p className="text-sm font-medium text-gray-900">
                      {selectedStudent.totalMeals || 0}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <UserCheck className="w-5 h-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Status</p>
                    <p className="text-sm font-medium text-gray-900">
                      {selectedStudent.is_active ? 'Active' : 'Inactive'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Account Created */}
              <div className="pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-600">
                  Account created: {new Date(selectedStudent.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <Button onClick={() => setShowDetailsModal(false)}>Close</Button>
            </div>
          </div>
        </div>
      )}

      {/* Add Student Modal - Placeholder */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Add New Student</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="text-center py-8">
              <p className="text-gray-600">
                Student registration is handled through the registration page.
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Direct manager signup coming soon...
              </p>
            </div>

            <div className="flex justify-end mt-6">
              <Button onClick={() => setShowAddModal(false)}>Close</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Students;

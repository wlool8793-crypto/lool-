import React, { useState, useEffect } from 'react';
import {
  Plus,
  Download,
  Filter,
  DollarSign,
  Calendar,
  User,
  CreditCard,
  Search,
  AlertCircle,
  X,
  TrendingUp,
} from 'lucide-react';
import { Button } from '../../components/forms/Button';
import { Input } from '../../components/forms/Input';
import { Select } from '../../components/forms/Select';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import {
  getDepositsByMonth,
  getDepositsByDateRange,
  createDeposit,
  getTotalDepositsByMonth,
  getDepositStatsByPaymentMethod,
} from '../../services/deposits.service';
import { getUsersByRole } from '../../services/users.service';
import { Deposit, InsertDeposit, PaymentMethod, User as UserType } from '../../types/database.types';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';

interface PaymentMethodStat {
  method: PaymentMethod;
  total: number;
  count: number;
}

interface DepositWithUser extends Deposit {
  user?: UserType;
}

export const Deposits: React.FC = () => {
  const { user } = useAuth();
  const [deposits, setDeposits] = useState<DepositWithUser[]>([]);
  const [students, setStudents] = useState<UserType[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [totalDeposits, setTotalDeposits] = useState(0);
  const [paymentStats, setPaymentStats] = useState<PaymentMethodStat[]>([]);

  // Filters
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7));
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [studentFilter, setStudentFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Form state
  const [formData, setFormData] = useState<InsertDeposit>({
    user_id: '',
    amount: 0,
    deposit_date: new Date().toISOString().split('T')[0],
    month: new Date().toISOString().slice(0, 7),
    payment_method: 'cash',
    notes: '',
    recorded_by: user?.id || '',
  });

  const paymentMethodOptions = [
    { value: 'cash', label: 'Cash' },
    { value: 'online', label: 'Online' },
    { value: 'upi', label: 'UPI' },
  ];

  const fetchStudents = async () => {
    try {
      const result = await getUsersByRole('student');

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch students');
      }

      setStudents(result.data || []);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to fetch students');
    }
  };

  const fetchDeposits = async () => {
    try {
      setLoading(true);
      let result;

      if (startDate && endDate) {
        result = await getDepositsByDateRange(startDate, endDate);
      } else {
        result = await getDepositsByMonth(selectedMonth);
      }

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch deposits');
      }

      let depositsList = result.data || [];

      // Enrich deposits with user data
      const enrichedDeposits = depositsList.map((deposit) => ({
        ...deposit,
        user: students.find((s) => s.id === deposit.user_id),
      }));

      // Apply student filter
      if (studentFilter !== 'all') {
        enrichedDeposits.filter((d) => d.user_id === studentFilter);
      }

      // Apply search filter
      if (searchTerm) {
        const filtered = enrichedDeposits.filter(
          (d) =>
            d.user?.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            d.user?.email.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setDeposits(filtered);
      } else {
        setDeposits(enrichedDeposits);
      }

      // Fetch total and stats
      const totalResult = await getTotalDepositsByMonth(selectedMonth);
      if (totalResult.success) {
        setTotalDeposits(totalResult.data || 0);
      }

      const statsResult = await getDepositStatsByPaymentMethod(selectedMonth);
      if (statsResult.success) {
        setPaymentStats(statsResult.data || []);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to fetch deposits');
    } finally {
      setLoading(false);
    }
  };

  const handleAddDeposit = async () => {
    if (!formData.user_id || !formData.amount) {
      toast.error('Please fill in all required fields');
      return;
    }

    setActionLoading(true);
    try {
      const result = await createDeposit(formData);

      if (!result.success) {
        throw new Error(result.error || 'Failed to create deposit');
      }

      toast.success('Deposit added successfully');
      setShowAddModal(false);
      resetForm();
      await fetchDeposits();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to add deposit');
    } finally {
      setActionLoading(false);
    }
  };

  const handleExport = () => {
    const headers = ['Date', 'Student', 'Email', 'Amount', 'Payment Method', 'Notes'];
    const rows = deposits.map((d) => [
      d.deposit_date,
      d.user?.full_name || 'Unknown',
      d.user?.email || 'N/A',
      d.amount.toFixed(2),
      d.payment_method || 'N/A',
      d.notes || '',
    ]);

    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `deposits-${selectedMonth}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const resetForm = () => {
    setFormData({
      user_id: '',
      amount: 0,
      deposit_date: new Date().toISOString().split('T')[0],
      month: new Date().toISOString().slice(0, 7),
      payment_method: 'cash',
      notes: '',
      recorded_by: user?.id || '',
    });
  };

  useEffect(() => {
    if (user) {
      setFormData((prev) => ({ ...prev, recorded_by: user.id }));
    }
  }, [user]);

  useEffect(() => {
    fetchStudents();
  }, []);

  useEffect(() => {
    if (students.length > 0) {
      fetchDeposits();
    }
  }, [selectedMonth, startDate, endDate, studentFilter, searchTerm, students]);

  if (loading && students.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Deposit Management</h1>
          <p className="text-gray-600 mt-1">Track and manage student deposits</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleExport} leftIcon={<Download className="w-4 h-4" />}>
            Export CSV
          </Button>
          <Button onClick={() => setShowAddModal(true)} leftIcon={<Plus className="w-4 h-4" />}>
            Add Deposit
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Deposits</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">${totalDeposits.toFixed(2)}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-3">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Records</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{deposits.length}</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-3">
              <User className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Deposit</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                ${deposits.length > 0 ? (totalDeposits / deposits.length).toFixed(2) : '0.00'}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-3">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Payment Methods</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{paymentStats.length}</p>
            </div>
            <div className="bg-orange-50 rounded-lg p-3">
              <CreditCard className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Input
            type="month"
            label="Month"
            value={selectedMonth}
            onChange={(e) => {
              setSelectedMonth(e.target.value);
              setStartDate('');
              setEndDate('');
            }}
            leftIcon={<Calendar className="w-5 h-5" />}
          />
          <Input
            type="date"
            label="Start Date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            placeholder="Start date"
          />
          <Input
            type="date"
            label="End Date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            placeholder="End date"
          />
          <Select
            label="Student"
            value={studentFilter}
            onChange={(e) => setStudentFilter(e.target.value)}
            options={[
              { value: 'all', label: 'All Students' },
              ...students.map((s) => ({ value: s.id, label: s.full_name })),
            ]}
          />
          <div className="relative">
            <Input
              type="text"
              label="Search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name..."
              leftIcon={<Search className="w-5 h-5" />}
            />
          </div>
        </div>
      </div>

      {/* Payment Method Stats */}
      {paymentStats.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Deposits by Payment Method</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {paymentStats.map((stat) => (
              <div key={stat.method} className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm font-medium text-gray-600 capitalize">{stat.method}</p>
                <p className="text-xl font-bold text-gray-900 mt-1">${stat.total.toFixed(2)}</p>
                <p className="text-xs text-gray-500 mt-1">{stat.count} transactions</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Deposits Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Student
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Room
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Payment Method
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Notes
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {deposits.map((deposit) => (
                <tr key={deposit.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {new Date(deposit.deposit_date).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-8 w-8">
                        <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-xs">
                            {deposit.user?.full_name
                              ?.split(' ')
                              .map((n) => n[0])
                              .join('')
                              .toUpperCase() || '?'}
                          </span>
                        </div>
                      </div>
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">
                          {deposit.user?.full_name || 'Unknown'}
                        </div>
                        <div className="text-sm text-gray-500">{deposit.user?.email || 'N/A'}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{deposit.user?.room_number || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="text-sm font-medium text-gray-900">${deposit.amount.toFixed(2)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 capitalize">
                      {deposit.payment_method || 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs truncate">
                      {deposit.notes || '-'}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {deposits.length === 0 && (
          <EmptyState
            icon={DollarSign}
            title="No Deposits Found"
            description="No deposits recorded for the selected period"
            action={{
              label: 'Add Deposit',
              onClick: () => setShowAddModal(true),
            }}
          />
        )}
      </div>

      {/* Add Deposit Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Add New Deposit</h2>
              <button
                onClick={() => {
                  setShowAddModal(false);
                  resetForm();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <Select
                label="Student"
                value={formData.user_id}
                onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                options={[
                  { value: '', label: 'Select a student', disabled: true },
                  ...students.map((s) => ({
                    value: s.id,
                    label: `${s.full_name} (${s.room_number || 'No room'})`,
                  })),
                ]}
                required
              />

              <Input
                label="Amount"
                type="number"
                step="0.01"
                min="0"
                value={formData.amount || ''}
                onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                placeholder="Enter amount"
                required
                leftIcon={<DollarSign className="w-5 h-5" />}
              />

              <Input
                label="Date"
                type="date"
                value={formData.deposit_date}
                onChange={(e) => {
                  const date = e.target.value;
                  const month = date.slice(0, 7);
                  setFormData({ ...formData, deposit_date: date, month });
                }}
                required
                leftIcon={<Calendar className="w-5 h-5" />}
              />

              <Select
                label="Payment Method"
                value={formData.payment_method}
                onChange={(e) =>
                  setFormData({ ...formData, payment_method: e.target.value as PaymentMethod })
                }
                options={paymentMethodOptions}
                required
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Notes (optional)
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Add any additional notes"
                  rows={3}
                  className="block w-full px-4 py-2.5 text-gray-900 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button
                variant="outline"
                onClick={() => {
                  setShowAddModal(false);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleAddDeposit} disabled={actionLoading}>
                {actionLoading ? 'Adding...' : 'Add Deposit'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Deposits;

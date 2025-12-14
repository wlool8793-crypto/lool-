import React, { useState, useEffect } from 'react';
import {
  Save,
  Clock,
  DollarSign,
  AlertCircle,
  Calendar,
  Settings as SettingsIcon,
  Coffee,
  UtensilsCrossed,
  Moon,
  Users,
  TrendingUp,
  Copy,
  RefreshCw,
} from 'lucide-react';
import { Button } from '../../components/forms/Button';
import { Input } from '../../components/forms/Input';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import {
  getCurrentMonthSettings,
  upsertSettings,
  getOrCreateCurrentMonthSettings,
  copySettingsToMonth,
} from '../../services/settings.service';
import { MealSettings, InsertMealSettings } from '../../types/database.types';
import toast from 'react-hot-toast';

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<MealSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [currentMonth] = useState(new Date().toISOString().slice(0, 7));
  const [copyToMonth, setCopyToMonth] = useState('');

  // Form state
  const [formData, setFormData] = useState<InsertMealSettings>({
    month: currentMonth,
    breakfast_deadline_hour: 20,
    lunch_deadline_hour: 9,
    dinner_deadline_hour: 15,
    dinner_deadline_previous_day: false,
    fixed_meal_cost: undefined,
    late_cancellation_penalty: 10,
    guest_meal_price: 50,
  });

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const result = await getOrCreateCurrentMonthSettings();

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch settings');
      }

      const settingsData = result.data;
      setSettings(settingsData);

      if (settingsData) {
        setFormData({
          month: settingsData.month,
          breakfast_deadline_hour: settingsData.breakfast_deadline_hour,
          lunch_deadline_hour: settingsData.lunch_deadline_hour,
          dinner_deadline_hour: settingsData.dinner_deadline_hour,
          dinner_deadline_previous_day: settingsData.dinner_deadline_previous_day,
          fixed_meal_cost: settingsData.fixed_meal_cost,
          late_cancellation_penalty: settingsData.late_cancellation_penalty,
          guest_meal_price: settingsData.guest_meal_price,
        });
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to fetch settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    // Validate inputs
    if (
      formData.breakfast_deadline_hour < 0 ||
      formData.breakfast_deadline_hour > 23 ||
      formData.lunch_deadline_hour < 0 ||
      formData.lunch_deadline_hour > 23 ||
      formData.dinner_deadline_hour < 0 ||
      formData.dinner_deadline_hour > 23
    ) {
      toast.error('Deadline hours must be between 0 and 23');
      return;
    }

    if (formData.late_cancellation_penalty < 0) {
      toast.error('Late cancellation penalty cannot be negative');
      return;
    }

    if (formData.guest_meal_price && formData.guest_meal_price < 0) {
      toast.error('Guest meal price cannot be negative');
      return;
    }

    if (formData.fixed_meal_cost && formData.fixed_meal_cost < 0) {
      toast.error('Fixed meal cost cannot be negative');
      return;
    }

    setSaving(true);
    try {
      const result = await upsertSettings(formData);

      if (!result.success) {
        throw new Error(result.error || 'Failed to save settings');
      }

      toast.success('Settings saved successfully');
      await fetchSettings();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleCopySettings = async () => {
    if (!copyToMonth) {
      toast.error('Please select a month to copy settings to');
      return;
    }

    if (copyToMonth === currentMonth) {
      toast.error('Cannot copy to the same month');
      return;
    }

    setSaving(true);
    try {
      const result = await copySettingsToMonth(currentMonth, copyToMonth);

      if (!result.success) {
        throw new Error(result.error || 'Failed to copy settings');
      }

      toast.success(`Settings copied to ${copyToMonth} successfully`);
      setCopyToMonth('');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to copy settings');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (!confirm('Are you sure you want to reset to default values?')) {
      return;
    }

    setFormData({
      month: currentMonth,
      breakfast_deadline_hour: 20,
      lunch_deadline_hour: 9,
      dinner_deadline_hour: 15,
      dinner_deadline_previous_day: false,
      fixed_meal_cost: undefined,
      late_cancellation_penalty: 10,
      guest_meal_price: 50,
    });
    toast.success('Form reset to default values');
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  if (loading) {
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
          <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>
          <p className="text-gray-600 mt-1">Configure meal deadlines, costs, and penalties</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleReset} leftIcon={<RefreshCw className="w-4 h-4" />}>
            Reset to Defaults
          </Button>
          <Button onClick={handleSaveSettings} disabled={saving} leftIcon={<Save className="w-4 h-4" />}>
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>
      </div>

      {/* Current Month Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-900">
              Configuring settings for: {new Date(currentMonth + '-01').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </p>
            <p className="text-sm text-blue-700 mt-1">
              These settings will apply to all students for the current month. Changes take effect immediately.
            </p>
          </div>
        </div>
      </div>

      {/* Meal Deadlines Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-blue-50 rounded-lg p-3">
            <Clock className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Meal Deadlines</h2>
            <p className="text-sm text-gray-600">Set cutoff times for meal selections</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Breakfast Deadline */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Coffee className="w-5 h-5 text-yellow-600" />
              <h3 className="font-semibold text-gray-900">Breakfast</h3>
            </div>
            <Input
              type="number"
              min="0"
              max="23"
              value={formData.breakfast_deadline_hour}
              onChange={(e) =>
                setFormData({ ...formData, breakfast_deadline_hour: parseInt(e.target.value) || 0 })
              }
              label="Deadline Hour (24h format)"
              hint="Hour of previous day (e.g., 20 = 8 PM)"
            />
            <p className="text-xs text-gray-500 mt-2">
              Students must opt-in by {formData.breakfast_deadline_hour}:00 on the previous day
            </p>
          </div>

          {/* Lunch Deadline */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <UtensilsCrossed className="w-5 h-5 text-orange-600" />
              <h3 className="font-semibold text-gray-900">Lunch</h3>
            </div>
            <Input
              type="number"
              min="0"
              max="23"
              value={formData.lunch_deadline_hour}
              onChange={(e) =>
                setFormData({ ...formData, lunch_deadline_hour: parseInt(e.target.value) || 0 })
              }
              label="Deadline Hour (24h format)"
              hint="Hour of same day (e.g., 9 = 9 AM)"
            />
            <p className="text-xs text-gray-500 mt-2">
              Students must opt-in by {formData.lunch_deadline_hour}:00 on the same day
            </p>
          </div>

          {/* Dinner Deadline */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Moon className="w-5 h-5 text-indigo-600" />
              <h3 className="font-semibold text-gray-900">Dinner</h3>
            </div>
            <Input
              type="number"
              min="0"
              max="23"
              value={formData.dinner_deadline_hour}
              onChange={(e) =>
                setFormData({ ...formData, dinner_deadline_hour: parseInt(e.target.value) || 0 })
              }
              label="Deadline Hour (24h format)"
              hint="Hour of same/previous day"
            />
            <div className="mt-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.dinner_deadline_previous_day}
                  onChange={(e) =>
                    setFormData({ ...formData, dinner_deadline_previous_day: e.target.checked })
                  }
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Deadline is on previous day</span>
              </label>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Students must opt-in by {formData.dinner_deadline_hour}:00 on the{' '}
              {formData.dinner_deadline_previous_day ? 'previous' : 'same'} day
            </p>
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-green-50 rounded-lg p-3">
            <DollarSign className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Meal Pricing</h2>
            <p className="text-sm text-gray-600">Configure meal costs and penalties</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Input
            type="number"
            step="0.01"
            min="0"
            value={formData.fixed_meal_cost || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                fixed_meal_cost: e.target.value ? parseFloat(e.target.value) : undefined,
              })
            }
            label="Fixed Meal Cost"
            hint="Optional: Cost per meal (leave empty for variable pricing)"
            leftIcon={<DollarSign className="w-5 h-5" />}
          />

          <Input
            type="number"
            step="0.01"
            min="0"
            value={formData.guest_meal_price || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                guest_meal_price: e.target.value ? parseFloat(e.target.value) : undefined,
              })
            }
            label="Guest Meal Price"
            hint="Price per guest meal"
            leftIcon={<Users className="w-5 h-5" />}
            required
          />

          <Input
            type="number"
            step="0.01"
            min="0"
            value={formData.late_cancellation_penalty}
            onChange={(e) =>
              setFormData({
                ...formData,
                late_cancellation_penalty: parseFloat(e.target.value) || 0,
              })
            }
            label="Late Cancellation Penalty"
            hint="Penalty for canceling after deadline"
            leftIcon={<AlertCircle className="w-5 h-5" />}
            required
          />
        </div>

        {/* Pricing Summary */}
        <div className="mt-6 bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Pricing Summary</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Fixed Meal Cost</p>
              <p className="text-lg font-bold text-gray-900">
                {formData.fixed_meal_cost ? `$${formData.fixed_meal_cost.toFixed(2)}` : 'Variable'}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Guest Meal Price</p>
              <p className="text-lg font-bold text-gray-900">
                ${(formData.guest_meal_price || 0).toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Late Penalty</p>
              <p className="text-lg font-bold text-gray-900">
                ${formData.late_cancellation_penalty.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Copy Settings Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-purple-50 rounded-lg p-3">
            <Copy className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Copy Settings</h2>
            <p className="text-sm text-gray-600">Copy current settings to another month</p>
          </div>
        </div>

        <div className="flex items-end gap-4">
          <div className="flex-1">
            <Input
              type="month"
              label="Target Month"
              value={copyToMonth}
              onChange={(e) => setCopyToMonth(e.target.value)}
              placeholder="Select month"
              leftIcon={<Calendar className="w-5 h-5" />}
            />
          </div>
          <Button
            variant="outline"
            onClick={handleCopySettings}
            disabled={!copyToMonth || saving}
            leftIcon={<Copy className="w-4 h-4" />}
          >
            Copy Settings
          </Button>
        </div>

        <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <p className="text-sm text-yellow-800">
            This will copy all current settings to the selected month. Existing settings for that month will be overwritten.
          </p>
        </div>
      </div>

      {/* Settings Preview */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-gray-50 rounded-lg p-3">
            <SettingsIcon className="w-6 h-6 text-gray-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Current Configuration</h2>
            <p className="text-sm text-gray-600">Review your settings before saving</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900 mb-3">Deadlines</h3>
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-gray-700">Breakfast Deadline</span>
              <span className="font-medium text-gray-900">
                {formData.breakfast_deadline_hour}:00 (previous day)
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-gray-700">Lunch Deadline</span>
              <span className="font-medium text-gray-900">
                {formData.lunch_deadline_hour}:00 (same day)
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-gray-700">Dinner Deadline</span>
              <span className="font-medium text-gray-900">
                {formData.dinner_deadline_hour}:00 (
                {formData.dinner_deadline_previous_day ? 'previous' : 'same'} day)
              </span>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900 mb-3">Pricing</h3>
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-gray-700">Fixed Meal Cost</span>
              <span className="font-medium text-gray-900">
                {formData.fixed_meal_cost ? `$${formData.fixed_meal_cost.toFixed(2)}` : 'Variable'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-gray-700">Guest Meal Price</span>
              <span className="font-medium text-gray-900">
                ${(formData.guest_meal_price || 0).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-gray-700">Late Cancellation Penalty</span>
              <span className="font-medium text-gray-900">
                ${formData.late_cancellation_penalty.toFixed(2)}
              </span>
            </div>
          </div>
        </div>

        {settings && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Last updated: {new Date(settings.updated_at).toLocaleString()}
            </p>
          </div>
        )}
      </div>

      {/* Save Button (Bottom) */}
      <div className="flex justify-end">
        <Button onClick={handleSaveSettings} disabled={saving} size="lg" leftIcon={<Save className="w-5 h-5" />}>
          {saving ? 'Saving Settings...' : 'Save All Settings'}
        </Button>
      </div>
    </div>
  );
};

export default Settings;

import React, { useState } from 'react';
import { Calendar, Copy, Moon, Zap } from 'lucide-react';
import { Button } from '../forms/Button';

export interface BulkActionsProps {
  onTurnOffWeekends: () => void;
  onHolidayMode: (startDate: string, endDate: string) => void;
  onCopyLastWeek: () => void;
  onQuickPattern?: (pattern: 'workdays' | 'everyday' | 'custom') => void;
  disabled?: boolean;
}

export const BulkActions: React.FC<BulkActionsProps> = ({
  onTurnOffWeekends,
  onHolidayMode,
  onCopyLastWeek,
  onQuickPattern,
  disabled = false,
}) => {
  const [showHolidayPicker, setShowHolidayPicker] = useState(false);
  const [holidayStart, setHolidayStart] = useState('');
  const [holidayEnd, setHolidayEnd] = useState('');
  const [showConfirmWeekends, setShowConfirmWeekends] = useState(false);
  const [showConfirmCopy, setShowConfirmCopy] = useState(false);

  const handleTurnOffWeekends = () => {
    setShowConfirmWeekends(true);
  };

  const confirmTurnOffWeekends = () => {
    onTurnOffWeekends();
    setShowConfirmWeekends(false);
  };

  const handleCopyLastWeek = () => {
    setShowConfirmCopy(true);
  };

  const confirmCopyLastWeek = () => {
    onCopyLastWeek();
    setShowConfirmCopy(false);
  };

  const handleHolidaySubmit = () => {
    if (holidayStart && holidayEnd) {
      onHolidayMode(holidayStart, holidayEnd);
      setShowHolidayPicker(false);
      setHolidayStart('');
      setHolidayEnd('');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Zap className="w-5 h-5 text-blue-600" />
        Bulk Actions
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Turn Off Weekends */}
        <div className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
          <div className="flex items-start gap-3 mb-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Calendar className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">Turn Off Weekends</h4>
              <p className="text-xs text-gray-600 mt-1">
                Disable all meals for Saturdays and Sundays this month
              </p>
            </div>
          </div>
          <Button
            onClick={handleTurnOffWeekends}
            disabled={disabled}
            variant="outline"
            size="sm"
            fullWidth
          >
            Turn Off Weekends
          </Button>
        </div>

        {/* Holiday Mode */}
        <div className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
          <div className="flex items-start gap-3 mb-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Moon className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">Holiday Mode</h4>
              <p className="text-xs text-gray-600 mt-1">
                Turn off meals for a date range
              </p>
            </div>
          </div>
          <Button
            onClick={() => setShowHolidayPicker(!showHolidayPicker)}
            disabled={disabled}
            variant="outline"
            size="sm"
            fullWidth
          >
            Set Holiday Dates
          </Button>
        </div>

        {/* Copy Last Week */}
        <div className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
          <div className="flex items-start gap-3 mb-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Copy className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">Copy Last Week</h4>
              <p className="text-xs text-gray-600 mt-1">
                Apply last week's meal pattern to this week
              </p>
            </div>
          </div>
          <Button
            onClick={handleCopyLastWeek}
            disabled={disabled}
            variant="outline"
            size="sm"
            fullWidth
          >
            Copy Pattern
          </Button>
        </div>
      </div>

      {/* Quick Patterns */}
      {onQuickPattern && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-3">Quick Patterns</h4>
          <div className="flex flex-wrap gap-2">
            <Button
              onClick={() => onQuickPattern('workdays')}
              disabled={disabled}
              variant="ghost"
              size="sm"
            >
              Weekdays Only
            </Button>
            <Button
              onClick={() => onQuickPattern('everyday')}
              disabled={disabled}
              variant="ghost"
              size="sm"
            >
              Every Day
            </Button>
          </div>
        </div>
      )}

      {/* Holiday Date Picker Modal */}
      {showHolidayPicker && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Set Holiday Dates</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={holidayStart}
                  onChange={(e) => setHolidayStart(e.target.value)}
                  className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={holidayEnd}
                  onChange={(e) => setHolidayEnd(e.target.value)}
                  min={holidayStart}
                  className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="flex gap-3 mt-6">
                <Button
                  onClick={() => setShowHolidayPicker(false)}
                  variant="outline"
                  fullWidth
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleHolidaySubmit}
                  disabled={!holidayStart || !holidayEnd}
                  fullWidth
                >
                  Apply
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Confirm Weekend Dialog */}
      {showConfirmWeekends && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Confirm Action</h3>
            <p className="text-gray-600 mb-6">
              This will turn off all meals for all Saturdays and Sundays in the current month.
              Are you sure you want to continue?
            </p>
            <div className="flex gap-3">
              <Button
                onClick={() => setShowConfirmWeekends(false)}
                variant="outline"
                fullWidth
              >
                Cancel
              </Button>
              <Button
                onClick={confirmTurnOffWeekends}
                variant="primary"
                fullWidth
              >
                Confirm
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Confirm Copy Dialog */}
      {showConfirmCopy && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Confirm Action</h3>
            <p className="text-gray-600 mb-6">
              This will copy last week's meal pattern to this week, overwriting any existing selections.
              Are you sure you want to continue?
            </p>
            <div className="flex gap-3">
              <Button
                onClick={() => setShowConfirmCopy(false)}
                variant="outline"
                fullWidth
              >
                Cancel
              </Button>
              <Button
                onClick={confirmCopyLastWeek}
                variant="primary"
                fullWidth
              >
                Confirm
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BulkActions;

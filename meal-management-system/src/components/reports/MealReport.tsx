import React, { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { Download, FileText, Table, Loader2, UtensilsCrossed } from 'lucide-react';
import { toast } from 'react-hot-toast';
import {
  generateMealReportPDF,
  exportMealReportExcel
} from '../../services/reports.service';
import { getMealsByDateRange } from '../../services/meals.service';

interface MealReportProps {
  initialMonth?: string;
}

export const MealReport: React.FC<MealReportProps> = ({ initialMonth }) => {
  const [selectedMonth, setSelectedMonth] = useState<string>(
    initialMonth || format(new Date(), 'yyyy-MM')
  );
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [useCustomRange, setUseCustomRange] = useState(false);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [summary, setSummary] = useState({
    totalBreakfast: 0,
    totalLunch: 0,
    totalDinner: 0,
    totalGuestBreakfast: 0,
    totalGuestLunch: 0,
    totalGuestDinner: 0,
    totalMeals: 0
  });

  // Calculate date range
  useEffect(() => {
    if (!useCustomRange && selectedMonth) {
      const monthDate = new Date(selectedMonth + '-01');
      const start = format(startOfMonth(monthDate), 'yyyy-MM-dd');
      const end = format(endOfMonth(monthDate), 'yyyy-MM-dd');
      setStartDate(start);
      setEndDate(end);
    }
  }, [selectedMonth, useCustomRange]);

  // Fetch summary data
  useEffect(() => {
    if (startDate && endDate) {
      fetchSummary();
    }
  }, [startDate, endDate]);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const mealsResponse = await getMealsByDateRange(startDate, endDate);

      if (mealsResponse.success) {
        const meals = mealsResponse.data || [];

        let totalBreakfast = 0;
        let totalLunch = 0;
        let totalDinner = 0;
        let totalGuestBreakfast = 0;
        let totalGuestLunch = 0;
        let totalGuestDinner = 0;

        meals.forEach(meal => {
          if (meal.breakfast) totalBreakfast++;
          if (meal.lunch) totalLunch++;
          if (meal.dinner) totalDinner++;
          totalGuestBreakfast += meal.guest_breakfast || 0;
          totalGuestLunch += meal.guest_lunch || 0;
          totalGuestDinner += meal.guest_dinner || 0;
        });

        setSummary({
          totalBreakfast,
          totalLunch,
          totalDinner,
          totalGuestBreakfast,
          totalGuestLunch,
          totalGuestDinner,
          totalMeals: totalBreakfast + totalLunch + totalDinner
        });
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
      toast.error('Failed to fetch meal summary');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePDF = async () => {
    setGenerating(true);
    try {
      await generateMealReportPDF(
        startDate,
        endDate,
        useCustomRange ? undefined : selectedMonth
      );
      toast.success('PDF report generated successfully!');
    } catch (error) {
      console.error('Error generating PDF:', error);
      toast.error('Failed to generate PDF report');
    } finally {
      setGenerating(false);
    }
  };

  const handleExportExcel = async () => {
    setGenerating(true);
    try {
      await exportMealReportExcel(
        startDate,
        endDate,
        useCustomRange ? undefined : selectedMonth
      );
      toast.success('Excel file exported successfully!');
    } catch (error) {
      console.error('Error exporting Excel:', error);
      toast.error('Failed to export Excel file');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Meal Statistics Report
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            View meal consumption statistics and trends
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleGeneratePDF}
            disabled={generating || loading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {generating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <FileText className="w-4 h-4" />
            )}
            Export PDF
          </button>
          <button
            onClick={handleExportExcel}
            disabled={generating || loading}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {generating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Table className="w-4 h-4" />
            )}
            Export Excel
          </button>
        </div>
      </div>

      {/* Date Selection */}
      <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
          Select Period
        </h3>
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="useCustomRange"
              checked={useCustomRange}
              onChange={(e) => setUseCustomRange(e.target.checked)}
              className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
            />
            <label
              htmlFor="useCustomRange"
              className="text-sm text-slate-700 dark:text-slate-300"
            >
              Use custom date range
            </label>
          </div>

          {useCustomRange ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-slate-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-slate-100"
                />
              </div>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Select Month
              </label>
              <input
                type="month"
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="w-full sm:w-64 px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-slate-100"
              />
            </div>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : (
        <>
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
              Regular Meals
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Breakfast */}
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <p className="text-sm font-medium text-yellow-800 dark:text-yellow-300">
                  Breakfast
                </p>
                <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-200 mt-2">
                  {summary.totalBreakfast}
                </p>
              </div>

              {/* Lunch */}
              <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                <p className="text-sm font-medium text-orange-800 dark:text-orange-300">
                  Lunch
                </p>
                <p className="text-2xl font-bold text-orange-900 dark:text-orange-200 mt-2">
                  {summary.totalLunch}
                </p>
              </div>

              {/* Dinner */}
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                <p className="text-sm font-medium text-purple-800 dark:text-purple-300">
                  Dinner
                </p>
                <p className="text-2xl font-bold text-purple-900 dark:text-purple-200 mt-2">
                  {summary.totalDinner}
                </p>
              </div>

              {/* Total */}
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-sm font-medium text-blue-800 dark:text-blue-300">
                  Total Meals
                </p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-200 mt-2">
                  {summary.totalMeals}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
              Guest Meals
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Guest Breakfast */}
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <p className="text-sm font-medium text-green-800 dark:text-green-300">
                  Guest Breakfast
                </p>
                <p className="text-2xl font-bold text-green-900 dark:text-green-200 mt-2">
                  {summary.totalGuestBreakfast}
                </p>
              </div>

              {/* Guest Lunch */}
              <div className="p-4 bg-teal-50 dark:bg-teal-900/20 rounded-lg border border-teal-200 dark:border-teal-800">
                <p className="text-sm font-medium text-teal-800 dark:text-teal-300">
                  Guest Lunch
                </p>
                <p className="text-2xl font-bold text-teal-900 dark:text-teal-200 mt-2">
                  {summary.totalGuestLunch}
                </p>
              </div>

              {/* Guest Dinner */}
              <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                <p className="text-sm font-medium text-indigo-800 dark:text-indigo-300">
                  Guest Dinner
                </p>
                <p className="text-2xl font-bold text-indigo-900 dark:text-indigo-200 mt-2">
                  {summary.totalGuestDinner}
                </p>
              </div>

              {/* Total Guests */}
              <div className="p-4 bg-slate-50 dark:bg-slate-700/20 rounded-lg border border-slate-200 dark:border-slate-600">
                <p className="text-sm font-medium text-slate-800 dark:text-slate-300">
                  Total Guests
                </p>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-200 mt-2">
                  {summary.totalGuestBreakfast + summary.totalGuestLunch + summary.totalGuestDinner}
                </p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Info Section */}
      <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
        <div className="flex gap-3">
          <UtensilsCrossed className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-green-800 dark:text-green-300">
            <p className="font-medium mb-1">About Meal Reports</p>
            <p>
              Meal reports provide comprehensive statistics about meal consumption patterns,
              including regular meals and guest meals. Use these reports to analyze trends
              and plan better for future meal requirements.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MealReport;

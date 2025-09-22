'use client';

import { ExpenseSummary, ExpenseCategory } from '@/types/expense';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatCurrency } from '@/lib/utils';
import { TrendingUp, DollarSign, Calendar, Target, Download } from 'lucide-react';

interface DashboardProps {
  summary: ExpenseSummary;
  onExportClick: () => void;
}

const categoryIcons: Record<ExpenseCategory, React.ReactNode> = {
  Food: <Target className="h-4 w-4" />,
  Transportation: <TrendingUp className="h-4 w-4" />,
  Entertainment: <Calendar className="h-4 w-4" />,
  Shopping: <DollarSign className="h-4 w-4" />,
  Bills: <DollarSign className="h-4 w-4" />,
  Other: <Target className="h-4 w-4" />,
};

const categoryColors: Record<ExpenseCategory, string> = {
  Food: 'text-green-600',
  Transportation: 'text-blue-600',
  Entertainment: 'text-purple-600',
  Shopping: 'text-pink-600',
  Bills: 'text-orange-600',
  Other: 'text-gray-600',
};

export function Dashboard({ summary, onExportClick }: DashboardProps) {
  const topCategories = Object.entries(summary.categoryTotals)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Export Action Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Download className="h-5 w-5" />
              Export Data
            </span>
            <Button onClick={onExportClick} className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Advanced Export
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">
            Export your expense data with custom filters, multiple formats (CSV, JSON, PDF),
            and advanced options for professional reporting.
          </p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Spent</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(summary.total)}</div>
          <p className="text-xs text-muted-foreground">
            Across all expenses
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">This Month</CardTitle>
          <Calendar className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(summary.monthlyTotal)}</div>
          <p className="text-xs text-muted-foreground">
            Current month spending
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Top Category</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{summary.topCategory}</div>
          <p className="text-xs text-muted-foreground">
            {formatCurrency(summary.categoryTotals[summary.topCategory])}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Average Expense</CardTitle>
          <Target className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(summary.averageExpense)}</div>
          <p className="text-xs text-muted-foreground">
            Per transaction
          </p>
        </CardContent>
      </Card>

      <Card className="md:col-span-2 lg:col-span-4">
        <CardHeader>
          <CardTitle>Category Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topCategories.map(([category, amount]) => {
              const percentage = summary.total > 0 ? (amount / summary.total) * 100 : 0;
              return (
                <div key={category} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={categoryColors[category as ExpenseCategory]}>
                        {categoryIcons[category as ExpenseCategory]}
                      </span>
                      <span className="font-medium">{category}</span>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">{formatCurrency(amount)}</div>
                      <div className="text-sm text-muted-foreground">
                        {percentage.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
      </div>
    </div>
  );
}
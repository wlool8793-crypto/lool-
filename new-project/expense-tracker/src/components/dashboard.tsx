'use client';
import { ExpenseSummary, ExpenseCategory } from '@/types/expense';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatCurrency } from '@/lib/utils';
import {
  TrendingUp,
  DollarSign,
  Calendar,
  Target,
  Cloud,
  Share2,
  Zap,
  Clock,
  CheckCircle,
} from 'lucide-react';

interface DashboardProps {
  summary: ExpenseSummary;
  onCloudExportClick: () => void;
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

export function Dashboard({ summary, onCloudExportClick }: DashboardProps) {
  const topCategories = Object.entries(summary.categoryTotals)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Cloud Export Hub */}
      <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Cloud className="h-6 w-6 text-blue-600" />
                <span className="text-xl">Cloud Export Hub</span>
              </div>
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                <Zap className="h-3 w-3 mr-1" />
                NEW
              </Badge>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center p-4 bg-white rounded-lg border">
              <Share2 className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <h3 className="font-semibold text-sm">Share & Collaborate</h3>
              <p className="text-xs text-gray-600 mt-1">
                Generate shareable links and QR codes
              </p>
            </div>
            <div className="text-center p-4 bg-white rounded-lg border">
              <Cloud className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h3 className="font-semibold text-sm">Cloud Integrations</h3>
              <p className="text-xs text-gray-600 mt-1">
                Google Sheets, Drive, Dropbox & more
              </p>
            </div>
            <div className="text-center p-4 bg-white rounded-lg border">
              <Clock className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold text-sm">Automated Scheduling</h3>
              <p className="text-xs text-gray-600 mt-1">
                Set up recurring exports
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-700 font-medium">
                Modern cloud-powered export system
              </p>
              <div className="flex items-center gap-2 mt-1">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-xs text-gray-600">
                  Real-time sync • Multiple formats • Share anywhere
                </span>
              </div>
            </div>
            <Button
              onClick={onCloudExportClick}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
            >
              <Cloud className="h-4 w-4 mr-2" />
              Open Cloud Hub
            </Button>
          </div>
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
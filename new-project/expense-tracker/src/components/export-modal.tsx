'use client';

import { useState, useMemo } from 'react';
import { Expense, ExpenseCategory } from '@/types/expense';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  ExportFormat,
  ExportOptions,
  generateExportData,
  generateExportSummary,
  exportToCSV,
  exportToJSON,
  exportToPDF,
  downloadFile,
  generateDefaultFilename,
} from '@/lib/export-utils';
import { formatCurrency, formatDate } from '@/lib/utils';
import {
  Download,
  FileText,
  FileJson,
  File,
  Calendar,
  Filter,
  CheckCircle,
  Loader2,
  Eye,
} from 'lucide-react';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  expenses: Expense[];
}

const categories: ExpenseCategory[] = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Other'];

const formatIcons = {
  csv: FileText,
  json: FileJson,
  pdf: File,
};

const formatDescriptions = {
  csv: 'Comma-separated values for spreadsheet applications',
  json: 'Structured data format for developers and APIs',
  pdf: 'Portable document format for reports and printing',
};

export function ExportModal({ isOpen, onClose, expenses }: ExportModalProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('csv');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [selectedCategories, setSelectedCategories] = useState<ExpenseCategory[]>(categories);
  const [customFilename, setCustomFilename] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const exportData = useMemo(() => {
    const options: ExportOptions = {
      format: selectedFormat,
      dateRange: dateRange.start && dateRange.end ? dateRange : undefined,
      categories: selectedCategories.length < categories.length ? selectedCategories : undefined,
    };
    return generateExportData(expenses, options);
  }, [expenses, selectedFormat, dateRange, selectedCategories]);

  const exportSummary = useMemo(() => {
    return generateExportSummary(expenses, exportData);
  }, [expenses, exportData]);

  const finalFilename = customFilename || generateDefaultFilename(selectedFormat);

  const handleCategoryChange = (category: ExpenseCategory, checked: boolean) => {
    setSelectedCategories(prev =>
      checked
        ? [...prev, category]
        : prev.filter(c => c !== category)
    );
  };

  const handleSelectAllCategories = (checked: boolean) => {
    setSelectedCategories(checked ? categories : []);
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      switch (selectedFormat) {
        case 'csv':
          const csvContent = exportToCSV(exportData);
          downloadFile(csvContent, finalFilename, 'text/csv');
          break;
        case 'json':
          const jsonContent = exportToJSON(exportData);
          downloadFile(jsonContent, finalFilename, 'application/json');
          break;
        case 'pdf':
          const pdfBlob = await exportToPDF(exportData);
          downloadFile(pdfBlob, finalFilename, 'application/pdf');
          break;
      }
      onClose();
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const isExportDisabled = exportData.length === 0 || isExporting;

  const previewData = exportData.slice(0, 10); // Show first 10 records for preview

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Advanced Data Export
          </DialogTitle>
          <DialogDescription>
            Export your expense data with custom filters and multiple format options
          </DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Export Options */}
          <div className="space-y-6">
            {/* Format Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <File className="h-4 w-4" />
                  Export Format
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {Object.entries(formatIcons).map(([format, Icon]) => (
                  <div
                    key={format}
                    className={`flex items-start space-x-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedFormat === format
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedFormat(format as ExportFormat)}
                  >
                    <Icon className="h-5 w-5 mt-0.5 text-gray-600" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium uppercase">{format}</span>
                        {selectedFormat === format && (
                          <CheckCircle className="h-4 w-4 text-blue-500" />
                        )}
                      </div>
                      <p className="text-sm text-gray-600">
                        {formatDescriptions[format as ExportFormat]}
                      </p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Date Range Filter */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Date Range Filter
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor="start-date">Start Date</Label>
                    <Input
                      id="start-date"
                      type="date"
                      value={dateRange.start}
                      onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="end-date">End Date</Label>
                    <Input
                      id="end-date"
                      type="date"
                      value={dateRange.end}
                      onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Category Filter */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  Category Filter
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="select-all"
                    checked={selectedCategories.length === categories.length}
                    onCheckedChange={handleSelectAllCategories}
                  />
                  <Label htmlFor="select-all" className="font-medium">
                    Select All Categories
                  </Label>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {categories.map((category) => (
                    <div key={category} className="flex items-center space-x-2">
                      <Checkbox
                        id={category}
                        checked={selectedCategories.includes(category)}
                        onCheckedChange={(checked) =>
                          handleCategoryChange(category, checked as boolean)
                        }
                      />
                      <Label htmlFor={category} className="text-sm">
                        {category}
                      </Label>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Filename */}
            <Card>
              <CardHeader>
                <CardTitle>Filename</CardTitle>
              </CardHeader>
              <CardContent>
                <Input
                  placeholder={generateDefaultFilename(selectedFormat)}
                  value={customFilename}
                  onChange={(e) => setCustomFilename(e.target.value)}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty for auto-generated filename
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Summary and Preview */}
          <div className="space-y-6">
            {/* Export Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Export Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Records</p>
                    <p className="text-lg font-semibold">{exportSummary.totalRecords}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Total Amount</p>
                    <p className="text-lg font-semibold">{formatCurrency(exportSummary.filteredAmount)}</p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Date Range</p>
                  <p className="text-sm">{exportSummary.dateRange}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Categories</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {exportSummary.categories.map((category) => (
                      <span
                        key={category}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs"
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Preview Toggle */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Data Preview
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowPreview(!showPreview)}
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    {showPreview ? 'Hide' : 'Show'} Preview
                  </Button>
                </CardTitle>
              </CardHeader>
              {showPreview && (
                <CardContent>
                  {previewData.length > 0 ? (
                    <div className="space-y-2">
                      <div className="grid grid-cols-4 gap-2 text-xs font-medium text-gray-500 border-b pb-1">
                        <div>Date</div>
                        <div>Description</div>
                        <div>Category</div>
                        <div className="text-right">Amount</div>
                      </div>
                      {previewData.map((expense) => (
                        <div key={expense.id} className="grid grid-cols-4 gap-2 text-xs">
                          <div>{formatDate(expense.date)}</div>
                          <div className="truncate">{expense.description}</div>
                          <div>{expense.category}</div>
                          <div className="text-right">{formatCurrency(expense.amount)}</div>
                        </div>
                      ))}
                      {exportData.length > 10 && (
                        <p className="text-xs text-gray-500 text-center pt-2">
                          ...and {exportData.length - 10} more records
                        </p>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500 text-center py-4">
                      No data matches your filter criteria
                    </p>
                  )}
                </CardContent>
              )}
            </Card>
          </div>
        </div>

        <DialogFooter className="flex justify-between">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleExport}
            disabled={isExportDisabled}
            className="min-w-[120px]"
          >
            {isExporting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Exporting...
              </>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Export {exportData.length} Records
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
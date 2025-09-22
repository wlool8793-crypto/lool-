import { Expense, ExpenseCategory } from '@/types/expense';
import { format } from 'date-fns';
import jsPDF from 'jspdf';

export type ExportFormat = 'csv' | 'json' | 'pdf';

export interface ExportOptions {
  format: ExportFormat;
  dateRange?: {
    start: string;
    end: string;
  };
  categories?: ExpenseCategory[];
  filename?: string;
}

export interface ExportSummary {
  totalRecords: number;
  dateRange: string;
  categories: string[];
  totalAmount: number;
  filteredAmount: number;
}

export function generateExportData(
  expenses: Expense[],
  options: ExportOptions
): Expense[] {
  let filtered = [...expenses];

  // Apply date range filter
  if (options.dateRange) {
    filtered = filtered.filter(expense => {
      const expenseDate = new Date(expense.date);
      const startDate = new Date(options.dateRange!.start);
      const endDate = new Date(options.dateRange!.end);
      return expenseDate >= startDate && expenseDate <= endDate;
    });
  }

  // Apply category filter
  if (options.categories && options.categories.length > 0) {
    filtered = filtered.filter(expense =>
      options.categories!.includes(expense.category)
    );
  }

  return filtered;
}

export function generateExportSummary(
  allExpenses: Expense[],
  filteredExpenses: Expense[]
): ExportSummary {
  const totalAmount = allExpenses.reduce((sum, expense) => sum + expense.amount, 0);
  const filteredAmount = filteredExpenses.reduce((sum, expense) => sum + expense.amount, 0);

  const categories = Array.from(new Set(filteredExpenses.map(e => e.category)));

  const dates = filteredExpenses.map(e => new Date(e.date));
  const minDate = dates.length > 0 ? new Date(Math.min(...dates.map(d => d.getTime()))) : null;
  const maxDate = dates.length > 0 ? new Date(Math.max(...dates.map(d => d.getTime()))) : null;

  let dateRange = 'No data';
  if (minDate && maxDate) {
    dateRange = `${format(minDate, 'MMM dd, yyyy')} - ${format(maxDate, 'MMM dd, yyyy')}`;
  }

  return {
    totalRecords: filteredExpenses.length,
    dateRange,
    categories,
    totalAmount,
    filteredAmount,
  };
}

export function exportToCSV(expenses: Expense[]): string {
  const headers = ['Date', 'Description', 'Category', 'Amount'];
  const rows = expenses.map(expense => [
    format(new Date(expense.date), 'yyyy-MM-dd'),
    expense.description,
    expense.category,
    expense.amount.toFixed(2),
  ]);

  const csvContent = [headers, ...rows]
    .map(row => row.map(cell => `"${cell}"`).join(','))
    .join('\n');

  return csvContent;
}

export function exportToJSON(expenses: Expense[]): string {
  return JSON.stringify(expenses, null, 2);
}

export async function exportToPDF(expenses: Expense[]): Promise<Blob> {
  const pdf = new jsPDF();

  // Add title
  pdf.setFontSize(20);
  pdf.text('Expense Report', 20, 20);

  // Add date
  pdf.setFontSize(12);
  pdf.text(`Generated: ${format(new Date(), 'MMM dd, yyyy')}`, 20, 30);
  pdf.text(`Total Records: ${expenses.length}`, 20, 40);

  // Calculate total
  const total = expenses.reduce((sum, expense) => sum + expense.amount, 0);
  pdf.text(`Total Amount: $${total.toFixed(2)}`, 20, 50);

  // Add table headers
  let yPosition = 70;
  pdf.setFontSize(10);
  pdf.text('Date', 20, yPosition);
  pdf.text('Description', 50, yPosition);
  pdf.text('Category', 100, yPosition);
  pdf.text('Amount', 140, yPosition);

  // Add separator line
  pdf.line(20, yPosition + 2, 180, yPosition + 2);
  yPosition += 10;

  // Add expense rows
  expenses.forEach((expense) => {
    if (yPosition > 270) {
      pdf.addPage();
      yPosition = 20;
    }

    pdf.text(format(new Date(expense.date), 'MM/dd/yyyy'), 20, yPosition);
    pdf.text(expense.description.substring(0, 25), 50, yPosition);
    pdf.text(expense.category, 100, yPosition);
    pdf.text(`$${expense.amount.toFixed(2)}`, 140, yPosition);

    yPosition += 8;
  });

  return pdf.output('blob');
}

export function downloadFile(
  content: string | Blob,
  filename: string,
  mimeType: string
): void {
  const blob = content instanceof Blob ? content : new Blob([content], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export function generateDefaultFilename(exportFormat: ExportFormat): string {
  const date = format(new Date(), 'yyyy-MM-dd');
  return `expense-report-${date}.${exportFormat}`;
}
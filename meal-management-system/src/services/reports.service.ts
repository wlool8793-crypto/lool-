import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { format } from 'date-fns';
import {
  getExpensesByDateRange,
  getExpenseStatsByCategory
} from './expenses.service';
import {
  getDepositsByDateRange
} from './deposits.service';
import {
  getMealsByDateRange
} from './meals.service';
import {
  getAllUsers,
  getUserById
} from './users.service';

// Types for report data
export interface FinancialSummary {
  totalDeposits: number;
  totalExpenses: number;
  balance: number;
  depositsCount: number;
  expensesCount: number;
  period: string;
}

export interface MealSummary {
  totalBreakfast: number;
  totalLunch: number;
  totalDinner: number;
  totalGuestBreakfast: number;
  totalGuestLunch: number;
  totalGuestDinner: number;
  period: string;
}

export interface ExpenseSummary {
  categoryBreakdown: { category: string; amount: number; percentage: number }[];
  totalAmount: number;
  period: string;
}

export interface StudentSummary {
  userId: string;
  userName: string;
  totalDeposits: number;
  totalMeals: number;
  mealBreakdown: {
    breakfast: number;
    lunch: number;
    dinner: number;
  };
  period: string;
}

/**
 * Add PDF header with logo and title
 */
const addPDFHeader = (doc: jsPDF, title: string, subtitle?: string) => {
  // Add title
  doc.setFontSize(20);
  doc.setTextColor(30, 41, 59); // slate-800
  doc.text(title, 14, 22);

  if (subtitle) {
    doc.setFontSize(11);
    doc.setTextColor(100, 116, 139); // slate-500
    doc.text(subtitle, 14, 29);
  }

  // Add generation date
  doc.setFontSize(9);
  doc.setTextColor(148, 163, 184); // slate-400
  doc.text(`Generated: ${format(new Date(), 'PPpp')}`, 14, subtitle ? 35 : 29);

  // Add line separator
  doc.setDrawColor(226, 232, 240); // slate-200
  doc.setLineWidth(0.5);
  doc.line(14, subtitle ? 38 : 32, 196, subtitle ? 38 : 32);

  return subtitle ? 42 : 36;
};

/**
 * Add PDF footer with page numbers
 */
const addPDFFooter = (doc: jsPDF) => {
  const pageCount = doc.getNumberOfPages();
  doc.setFontSize(9);
  doc.setTextColor(148, 163, 184); // slate-400

  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.text(
      `Page ${i} of ${pageCount}`,
      doc.internal.pageSize.getWidth() / 2,
      doc.internal.pageSize.getHeight() - 10,
      { align: 'center' }
    );
    doc.text(
      'Hostel Meal Management System',
      14,
      doc.internal.pageSize.getHeight() - 10
    );
  }
};

/**
 * Generate Financial Report PDF
 */
export const generateFinancialReportPDF = async (
  startDate: string,
  endDate: string,
  month?: string
): Promise<void> => {
  try {
    // Fetch data
    const depositsResponse = await getDepositsByDateRange(startDate, endDate);
    const expensesResponse = await getExpensesByDateRange(startDate, endDate);

    if (!depositsResponse.success || !expensesResponse.success) {
      throw new Error('Failed to fetch financial data');
    }

    const deposits = depositsResponse.data || [];
    const expenses = expensesResponse.data || [];

    // Calculate totals
    const totalDeposits = deposits.reduce((sum, d) => sum + d.amount, 0);
    const totalExpenses = expenses.reduce((sum, e) => sum + e.amount, 0);
    const balance = totalDeposits - totalExpenses;

    // Create PDF
    const doc = new jsPDF();

    const periodStr = month || `${format(new Date(startDate), 'MMM dd, yyyy')} - ${format(new Date(endDate), 'MMM dd, yyyy')}`;
    let yPos = addPDFHeader(
      doc,
      'Financial Report',
      `Period: ${periodStr}`
    );

    // Summary section
    yPos += 10;
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Summary', 14, yPos);
    yPos += 8;

    // Summary boxes
    const summaryData = [
      ['Total Deposits', `Rs. ${totalDeposits.toFixed(2)}`, deposits.length.toString()],
      ['Total Expenses', `Rs. ${totalExpenses.toFixed(2)}`, expenses.length.toString()],
      ['Balance', `Rs. ${balance.toFixed(2)}`, balance >= 0 ? 'Surplus' : 'Deficit']
    ];

    autoTable(doc, {
      startY: yPos,
      head: [['Category', 'Amount', 'Count/Status']],
      body: summaryData,
      theme: 'grid',
      headStyles: { fillColor: [30, 41, 59], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [248, 250, 252] },
      styles: { fontSize: 10 },
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;

    // Deposits table
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Deposits', 14, yPos);
    yPos += 5;

    const depositsTableData = deposits.map(d => [
      format(new Date(d.deposit_date), 'MMM dd, yyyy'),
      d.month,
      `Rs. ${d.amount.toFixed(2)}`,
      d.payment_method || 'N/A',
      d.notes || '-'
    ]);

    autoTable(doc, {
      startY: yPos,
      head: [['Date', 'Month', 'Amount', 'Method', 'Notes']],
      body: depositsTableData.length > 0 ? depositsTableData : [['No deposits found', '', '', '', '']],
      theme: 'striped',
      headStyles: { fillColor: [59, 130, 246], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [239, 246, 255] },
      styles: { fontSize: 9 },
    });

    // Add new page for expenses
    doc.addPage();
    yPos = 20;

    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Expenses', 14, yPos);
    yPos += 5;

    const expensesTableData = expenses.map(e => [
      format(new Date(e.expense_date), 'MMM dd, yyyy'),
      e.category || 'N/A',
      `Rs. ${e.amount.toFixed(2)}`,
      e.description || '-'
    ]);

    autoTable(doc, {
      startY: yPos,
      head: [['Date', 'Category', 'Amount', 'Description']],
      body: expensesTableData.length > 0 ? expensesTableData : [['No expenses found', '', '', '']],
      theme: 'striped',
      headStyles: { fillColor: [239, 68, 68], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [254, 242, 242] },
      styles: { fontSize: 9 },
    });

    // Add footer
    addPDFFooter(doc);

    // Download
    const filename = `financial-report-${month || format(new Date(startDate), 'yyyy-MM')}.pdf`;
    doc.save(filename);
  } catch (error) {
    console.error('Error generating financial report:', error);
    throw error;
  }
};

/**
 * Generate Meal Report PDF
 */
export const generateMealReportPDF = async (
  startDate: string,
  endDate: string,
  month?: string
): Promise<void> => {
  try {
    // Fetch data
    const mealsResponse = await getMealsByDateRange(startDate, endDate);
    const usersResponse = await getAllUsers();

    if (!mealsResponse.success || !usersResponse.success) {
      throw new Error('Failed to fetch meal data');
    }

    const meals = mealsResponse.data || [];
    const users = usersResponse.data || [];

    // Create user map for quick lookup
    const userMap = new Map(users.map(u => [u.id, u]));

    // Calculate statistics
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

    // Create PDF
    const doc = new jsPDF();

    const periodStr = month || `${format(new Date(startDate), 'MMM dd, yyyy')} - ${format(new Date(endDate), 'MMM dd, yyyy')}`;
    let yPos = addPDFHeader(
      doc,
      'Meal Statistics Report',
      `Period: ${periodStr}`
    );

    // Summary section
    yPos += 10;
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Summary', 14, yPos);
    yPos += 8;

    const summaryData = [
      ['Breakfast', totalBreakfast.toString(), totalGuestBreakfast.toString()],
      ['Lunch', totalLunch.toString(), totalGuestLunch.toString()],
      ['Dinner', totalDinner.toString(), totalGuestDinner.toString()],
      ['Total', (totalBreakfast + totalLunch + totalDinner).toString(), (totalGuestBreakfast + totalGuestLunch + totalGuestDinner).toString()]
    ];

    autoTable(doc, {
      startY: yPos,
      head: [['Meal Type', 'Regular Meals', 'Guest Meals']],
      body: summaryData,
      theme: 'grid',
      headStyles: { fillColor: [30, 41, 59], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [248, 250, 252] },
      styles: { fontSize: 10 },
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;

    // Group meals by user
    const userMealMap = new Map<string, any[]>();
    meals.forEach(meal => {
      if (!userMealMap.has(meal.user_id)) {
        userMealMap.set(meal.user_id, []);
      }
      userMealMap.get(meal.user_id)!.push(meal);
    });

    // User breakdown table
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('User Breakdown', 14, yPos);
    yPos += 5;

    const userBreakdownData: any[] = [];
    userMealMap.forEach((userMeals, userId) => {
      const user = userMap.get(userId);
      const userName = user ? user.full_name : 'Unknown User';

      const breakfastCount = userMeals.filter(m => m.breakfast).length;
      const lunchCount = userMeals.filter(m => m.lunch).length;
      const dinnerCount = userMeals.filter(m => m.dinner).length;
      const totalCount = breakfastCount + lunchCount + dinnerCount;

      userBreakdownData.push([
        userName,
        breakfastCount.toString(),
        lunchCount.toString(),
        dinnerCount.toString(),
        totalCount.toString()
      ]);
    });

    autoTable(doc, {
      startY: yPos,
      head: [['Student Name', 'Breakfast', 'Lunch', 'Dinner', 'Total']],
      body: userBreakdownData.length > 0 ? userBreakdownData : [['No meal data found', '', '', '', '']],
      theme: 'striped',
      headStyles: { fillColor: [16, 185, 129], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [236, 253, 245] },
      styles: { fontSize: 9 },
    });

    // Add footer
    addPDFFooter(doc);

    // Download
    const filename = `meal-report-${month || format(new Date(startDate), 'yyyy-MM')}.pdf`;
    doc.save(filename);
  } catch (error) {
    console.error('Error generating meal report:', error);
    throw error;
  }
};

/**
 * Generate Expense Report PDF
 */
export const generateExpenseReportPDF = async (
  startDate: string,
  endDate: string,
  month?: string
): Promise<void> => {
  try {
    // Fetch data
    const expensesResponse = await getExpensesByDateRange(startDate, endDate);

    if (!expensesResponse.success) {
      throw new Error('Failed to fetch expense data');
    }

    const expenses = expensesResponse.data || [];

    // Calculate category breakdown
    const categoryMap = new Map<string, number>();
    expenses.forEach(expense => {
      const category = expense.category || 'other';
      categoryMap.set(category, (categoryMap.get(category) || 0) + expense.amount);
    });

    const totalExpenses = expenses.reduce((sum, e) => sum + e.amount, 0);

    // Create PDF
    const doc = new jsPDF();

    const periodStr = month || `${format(new Date(startDate), 'MMM dd, yyyy')} - ${format(new Date(endDate), 'MMM dd, yyyy')}`;
    let yPos = addPDFHeader(
      doc,
      'Expense Analysis Report',
      `Period: ${periodStr}`
    );

    // Summary section
    yPos += 10;
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Summary', 14, yPos);
    yPos += 8;

    doc.setFontSize(11);
    doc.setTextColor(100, 116, 139);
    doc.text(`Total Expenses: Rs. ${totalExpenses.toFixed(2)}`, 14, yPos);
    doc.text(`Number of Expenses: ${expenses.length}`, 14, yPos + 6);
    yPos += 20;

    // Category breakdown
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Category Breakdown', 14, yPos);
    yPos += 5;

    const categoryData: any[] = [];
    categoryMap.forEach((amount, category) => {
      const percentage = totalExpenses > 0 ? (amount / totalExpenses * 100).toFixed(1) : '0';
      categoryData.push([
        category.charAt(0).toUpperCase() + category.slice(1),
        `Rs. ${amount.toFixed(2)}`,
        `${percentage}%`
      ]);
    });

    // Sort by amount descending
    categoryData.sort((a, b) => parseFloat(b[1].replace('Rs. ', '')) - parseFloat(a[1].replace('Rs. ', '')));

    autoTable(doc, {
      startY: yPos,
      head: [['Category', 'Amount', 'Percentage']],
      body: categoryData.length > 0 ? categoryData : [['No expenses found', '', '']],
      theme: 'grid',
      headStyles: { fillColor: [139, 92, 246], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [245, 243, 255] },
      styles: { fontSize: 10 },
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;

    // Detailed expenses table
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Detailed Expenses', 14, yPos);
    yPos += 5;

    const expenseData = expenses.map(e => [
      format(new Date(e.expense_date), 'MMM dd, yyyy'),
      (e.category || 'other').charAt(0).toUpperCase() + (e.category || 'other').slice(1),
      `Rs. ${e.amount.toFixed(2)}`,
      e.description.length > 40 ? e.description.substring(0, 37) + '...' : e.description
    ]);

    autoTable(doc, {
      startY: yPos,
      head: [['Date', 'Category', 'Amount', 'Description']],
      body: expenseData.length > 0 ? expenseData : [['No expenses found', '', '', '']],
      theme: 'striped',
      headStyles: { fillColor: [239, 68, 68], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [254, 242, 242] },
      styles: { fontSize: 9 },
    });

    // Add footer
    addPDFFooter(doc);

    // Download
    const filename = `expense-report-${month || format(new Date(startDate), 'yyyy-MM')}.pdf`;
    doc.save(filename);
  } catch (error) {
    console.error('Error generating expense report:', error);
    throw error;
  }
};

/**
 * Generate Student Report PDF
 */
export const generateStudentReportPDF = async (
  userId: string,
  startDate: string,
  endDate: string,
  month?: string
): Promise<void> => {
  try {
    // Fetch data
    const userResponse = await getUserById(userId);
    const depositsResponse = await getDepositsByDateRange(startDate, endDate);
    const mealsResponse = await getMealsByDateRange(startDate, endDate);

    if (!userResponse.success || !depositsResponse.success || !mealsResponse.success) {
      throw new Error('Failed to fetch student data');
    }

    const user = userResponse.data;
    const allDeposits = depositsResponse.data || [];
    const allMeals = mealsResponse.data || [];

    // Filter user-specific data
    const userDeposits = allDeposits.filter(d => d.user_id === userId);
    const userMeals = allMeals.filter(m => m.user_id === userId);

    // Calculate statistics
    const totalDeposits = userDeposits.reduce((sum, d) => sum + d.amount, 0);

    let breakfastCount = 0;
    let lunchCount = 0;
    let dinnerCount = 0;

    userMeals.forEach(meal => {
      if (meal.breakfast) breakfastCount++;
      if (meal.lunch) lunchCount++;
      if (meal.dinner) dinnerCount++;
    });

    const totalMeals = breakfastCount + lunchCount + dinnerCount;

    // Create PDF
    const doc = new jsPDF();

    const periodStr = month || `${format(new Date(startDate), 'MMM dd, yyyy')} - ${format(new Date(endDate), 'MMM dd, yyyy')}`;
    let yPos = addPDFHeader(
      doc,
      'Student Report',
      `${user?.full_name || 'Unknown'} - ${periodStr}`
    );

    // Student info
    yPos += 10;
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Student Information', 14, yPos);
    yPos += 8;

    doc.setFontSize(11);
    doc.setTextColor(100, 116, 139);
    doc.text(`Name: ${user?.full_name || 'Unknown'}`, 14, yPos);
    doc.text(`Email: ${user?.email || 'N/A'}`, 14, yPos + 6);
    if (user?.room_number) {
      doc.text(`Room: ${user.room_number}`, 14, yPos + 12);
      yPos += 18;
    } else {
      yPos += 12;
    }

    yPos += 8;

    // Summary section
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Summary', 14, yPos);
    yPos += 8;

    const summaryData = [
      ['Total Deposits', `Rs. ${totalDeposits.toFixed(2)}`],
      ['Total Meals', totalMeals.toString()],
      ['Breakfast Count', breakfastCount.toString()],
      ['Lunch Count', lunchCount.toString()],
      ['Dinner Count', dinnerCount.toString()]
    ];

    autoTable(doc, {
      startY: yPos,
      head: [['Metric', 'Value']],
      body: summaryData,
      theme: 'grid',
      headStyles: { fillColor: [30, 41, 59], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [248, 250, 252] },
      styles: { fontSize: 10 },
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;

    // Deposits table
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Deposits', 14, yPos);
    yPos += 5;

    const depositsData = userDeposits.map(d => [
      format(new Date(d.deposit_date), 'MMM dd, yyyy'),
      `Rs. ${d.amount.toFixed(2)}`,
      d.payment_method || 'N/A',
      d.notes || '-'
    ]);

    autoTable(doc, {
      startY: yPos,
      head: [['Date', 'Amount', 'Method', 'Notes']],
      body: depositsData.length > 0 ? depositsData : [['No deposits found', '', '', '']],
      theme: 'striped',
      headStyles: { fillColor: [59, 130, 246], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [239, 246, 255] },
      styles: { fontSize: 9 },
    });

    // Add new page for meals if needed
    if (userMeals.length > 10) {
      doc.addPage();
      yPos = 20;
    } else {
      yPos = (doc as any).lastAutoTable.finalY + 15;
    }

    // Meals table
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text('Meals', 14, yPos);
    yPos += 5;

    const mealsData = userMeals.map(m => [
      format(new Date(m.meal_date), 'MMM dd, yyyy'),
      m.breakfast ? 'Yes' : 'No',
      m.lunch ? 'Yes' : 'No',
      m.dinner ? 'Yes' : 'No'
    ]);

    autoTable(doc, {
      startY: yPos,
      head: [['Date', 'Breakfast', 'Lunch', 'Dinner']],
      body: mealsData.length > 0 ? mealsData : [['No meals found', '', '', '']],
      theme: 'striped',
      headStyles: { fillColor: [16, 185, 129], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [236, 253, 245] },
      styles: { fontSize: 9 },
    });

    // Add footer
    addPDFFooter(doc);

    // Download
    const filename = `student-report-${(user?.full_name || 'unknown').replace(/\s+/g, '-').toLowerCase()}-${month || format(new Date(startDate), 'yyyy-MM')}.pdf`;
    doc.save(filename);
  } catch (error) {
    console.error('Error generating student report:', error);
    throw error;
  }
};

/**
 * Export data to Excel
 */
export const exportToExcel = async (
  data: any[],
  sheetName: string,
  filename: string
): Promise<void> => {
  try {
    // Create a new workbook
    const wb = XLSX.utils.book_new();

    // Convert data to worksheet
    const ws = XLSX.utils.json_to_sheet(data);

    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, sheetName);

    // Generate Excel file
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });

    // Create blob and download
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(blob, `${filename}.xlsx`);
  } catch (error) {
    console.error('Error exporting to Excel:', error);
    throw error;
  }
};

/**
 * Export multiple sheets to Excel
 */
export const exportMultiSheetExcel = async (
  sheets: { data: any[]; sheetName: string }[],
  filename: string
): Promise<void> => {
  try {
    // Create a new workbook
    const wb = XLSX.utils.book_new();

    // Add each sheet
    sheets.forEach(({ data, sheetName }) => {
      const ws = XLSX.utils.json_to_sheet(data);
      XLSX.utils.book_append_sheet(wb, ws, sheetName);
    });

    // Generate Excel file
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });

    // Create blob and download
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(blob, `${filename}.xlsx`);
  } catch (error) {
    console.error('Error exporting to Excel:', error);
    throw error;
  }
};

/**
 * Export comprehensive financial report to Excel
 */
export const exportFinancialReportExcel = async (
  startDate: string,
  endDate: string,
  month?: string
): Promise<void> => {
  try {
    // Fetch data
    const depositsResponse = await getDepositsByDateRange(startDate, endDate);
    const expensesResponse = await getExpensesByDateRange(startDate, endDate);

    if (!depositsResponse.success || !expensesResponse.success) {
      throw new Error('Failed to fetch financial data');
    }

    const deposits = depositsResponse.data || [];
    const expenses = expensesResponse.data || [];

    // Format deposits data
    const depositsData = deposits.map(d => ({
      Date: format(new Date(d.deposit_date), 'yyyy-MM-dd'),
      Month: d.month,
      Amount: d.amount,
      'Payment Method': d.payment_method || 'N/A',
      Notes: d.notes || '-'
    }));

    // Format expenses data
    const expensesData = expenses.map(e => ({
      Date: format(new Date(e.expense_date), 'yyyy-MM-dd'),
      Category: (e.category || 'other').charAt(0).toUpperCase() + (e.category || 'other').slice(1),
      Amount: e.amount,
      Description: e.description
    }));

    // Create summary data
    const totalDeposits = deposits.reduce((sum, d) => sum + d.amount, 0);
    const totalExpenses = expenses.reduce((sum, e) => sum + e.amount, 0);
    const balance = totalDeposits - totalExpenses;

    const summaryData = [
      { Metric: 'Total Deposits', Value: totalDeposits },
      { Metric: 'Total Expenses', Value: totalExpenses },
      { Metric: 'Balance', Value: balance },
      { Metric: 'Deposits Count', Value: deposits.length },
      { Metric: 'Expenses Count', Value: expenses.length }
    ];

    // Export to Excel
    await exportMultiSheetExcel(
      [
        { data: summaryData, sheetName: 'Summary' },
        { data: depositsData, sheetName: 'Deposits' },
        { data: expensesData, sheetName: 'Expenses' }
      ],
      `financial-report-${month || format(new Date(startDate), 'yyyy-MM')}`
    );
  } catch (error) {
    console.error('Error exporting financial report to Excel:', error);
    throw error;
  }
};

/**
 * Export meal report to Excel
 */
export const exportMealReportExcel = async (
  startDate: string,
  endDate: string,
  month?: string
): Promise<void> => {
  try {
    // Fetch data
    const mealsResponse = await getMealsByDateRange(startDate, endDate);
    const usersResponse = await getAllUsers();

    if (!mealsResponse.success || !usersResponse.success) {
      throw new Error('Failed to fetch meal data');
    }

    const meals = mealsResponse.data || [];
    const users = usersResponse.data || [];

    // Create user map
    const userMap = new Map(users.map(u => [u.id, u]));

    // Format meals data
    const mealsData = meals.map(m => {
      const user = userMap.get(m.user_id);
      return {
        Date: format(new Date(m.meal_date), 'yyyy-MM-dd'),
        'Student Name': user ? user.full_name : 'Unknown',
        Breakfast: m.breakfast ? 'Yes' : 'No',
        Lunch: m.lunch ? 'Yes' : 'No',
        Dinner: m.dinner ? 'Yes' : 'No',
        'Guest Breakfast': m.guest_breakfast || 0,
        'Guest Lunch': m.guest_lunch || 0,
        'Guest Dinner': m.guest_dinner || 0
      };
    });

    // Calculate summary
    const summary = {
      'Total Breakfast': meals.filter(m => m.breakfast).length,
      'Total Lunch': meals.filter(m => m.lunch).length,
      'Total Dinner': meals.filter(m => m.dinner).length,
      'Total Guest Breakfast': meals.reduce((sum, m) => sum + (m.guest_breakfast || 0), 0),
      'Total Guest Lunch': meals.reduce((sum, m) => sum + (m.guest_lunch || 0), 0),
      'Total Guest Dinner': meals.reduce((sum, m) => sum + (m.guest_dinner || 0), 0)
    };

    const summaryData = Object.entries(summary).map(([key, value]) => ({
      Metric: key,
      Value: value
    }));

    // Export to Excel
    await exportMultiSheetExcel(
      [
        { data: summaryData, sheetName: 'Summary' },
        { data: mealsData, sheetName: 'Meals' }
      ],
      `meal-report-${month || format(new Date(startDate), 'yyyy-MM')}`
    );
  } catch (error) {
    console.error('Error exporting meal report to Excel:', error);
    throw error;
  }
};

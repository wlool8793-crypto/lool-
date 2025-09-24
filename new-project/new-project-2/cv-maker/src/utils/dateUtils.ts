import { format, parseISO, isValid, addYears, differenceInYears } from 'date-fns';

export class DateUtils {
  static formatDate(date: Date | string, formatString: string = 'MMM yyyy'): string {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return isValid(dateObj) ? format(dateObj, formatString) : '';
  }

  static formatFullDate(date: Date | string): string {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return isValid(dateObj) ? format(dateObj, 'MMM dd, yyyy') : '';
  }

  static getCurrentDate(): string {
    return format(new Date(), 'yyyy-MM-dd');
  }

  static calculateAge(birthDate: Date | string): number {
    const birth = typeof birthDate === 'string' ? parseISO(birthDate) : birthDate;
    return differenceInYears(new Date(), birth);
  }

  static addYearsToDate(date: Date | string, years: number): string {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(addYears(dateObj, years), 'yyyy-MM-dd');
  }

  static isValidDate(dateString: string): boolean {
    return isValid(parseISO(dateString));
  }

  static getAgeFromDateOfBirth(dateOfBirth: string): number {
    if (!this.isValidDate(dateOfBirth)) return 0;
    return this.calculateAge(dateOfBirth);
  }

  static getDuration(startDate: Date | string, endDate?: Date | string): string {
    const start = typeof startDate === 'string' ? parseISO(startDate) : startDate;
    const end = endDate ? (typeof endDate === 'string' ? parseISO(endDate) : endDate) : new Date();

    const years = differenceInYears(end, start);
    const months = differenceInYears(addYears(start, years), end);

    if (years === 0) {
      return `${months} month${months !== 1 ? 's' : ''}`;
    } else if (months === 0) {
      return `${years} year${years !== 1 ? 's' : ''}`;
    } else {
      return `${years} year${years !== 1 ? 's' : ''} ${months} month${months !== 1 ? 's' : ''}`;
    }
  }

  static getFormattedDuration(startDate: Date | string, endDate?: Date | string): string {
    const start = typeof startDate === 'string' ? parseISO(startDate) : startDate;
    const end = endDate ? (typeof endDate === 'string' ? parseISO(endDate) : endDate) : new Date();

    const months = Math.abs(differenceInYears(end, start) * 12);
    const years = Math.floor(months / 12);
    const remainingMonths = months % 12;

    if (years === 0) {
      return `${remainingMonths} month${remainingMonths !== 1 ? 's' : ''}`;
    } else if (remainingMonths === 0) {
      return `${years} year${years !== 1 ? 's' : ''}`;
    } else {
      return `${years} year${years !== 1 ? 's' : ''} ${remainingMonths} month${remainingMonths !== 1 ? 's' : ''}`;
    }
  }

  static parseDate(dateString: string): Date | null {
    const parsed = parseISO(dateString);
    return isValid(parsed) ? parsed : null;
  }

  static getYearFromDate(date: Date | string): number {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return dateObj.getFullYear();
  }

  static getMonthFromDate(date: Date | string): number {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return dateObj.getMonth() + 1;
  }

  static getMonthName(date: Date | string): string {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'MMMM');
  }

  static getMonthYearString(date: Date | string): string {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'MMM yyyy');
  }

  static isDateInFuture(date: Date | string): boolean {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return dateObj > new Date();
  }

  static isDateInPast(date: Date | string): boolean {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return dateObj < new Date();
  }

  static getDaysBetweenDates(startDate: Date | string, endDate: Date | string): number {
    const start = typeof startDate === 'string' ? parseISO(startDate) : startDate;
    const end = typeof endDate === 'string' ? parseISO(endDate) : endDate;
    return Math.floor((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
  }
}
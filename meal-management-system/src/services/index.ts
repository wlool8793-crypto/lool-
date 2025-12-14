// Export Supabase client and helpers
export { supabase, createSuccessResponse, createErrorResponse } from './supabase';
export type { ServiceResponse } from './supabase';

// Export auth service
export * as authService from './auth.service';

// Export meals service
export * as mealsService from './meals.service';

// Export deposits service
export * as depositsService from './deposits.service';

// Export expenses service
export * as expensesService from './expenses.service';

// Export users service
export * as usersService from './users.service';

// Export notifications service
export * as notificationsService from './notifications.service';

// Export menu service
export * as menuService from './menu.service';

// Export settings service
export * as settingsService from './settings.service';

// Export announcements service
export * as announcementsService from './announcements.service';

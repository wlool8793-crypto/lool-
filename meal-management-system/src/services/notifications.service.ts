import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { Notification, InsertNotification, NotificationType } from '../types/database.types';

/**
 * Get all notifications for a specific user
 */
export const getNotificationsByUser = async (
  userId: string
): Promise<ServiceResponse<Notification[]>> => {
  try {
    const { data, error } = await supabase
      .from('notifications')
      .select('*')
      .or(`user_id.eq.${userId},user_id.is.null`)
      .order('created_at', { ascending: false });

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get unread notifications for a specific user
 */
export const getUnreadNotificationsByUser = async (
  userId: string
): Promise<ServiceResponse<Notification[]>> => {
  try {
    const { data, error } = await supabase
      .from('notifications')
      .select('*')
      .or(`user_id.eq.${userId},user_id.is.null`)
      .eq('is_read', false)
      .order('created_at', { ascending: false });

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get notification count for a user
 */
export const getUnreadNotificationCount = async (
  userId: string
): Promise<ServiceResponse<number>> => {
  try {
    const { count, error } = await supabase
      .from('notifications')
      .select('*', { count: 'exact', head: true })
      .or(`user_id.eq.${userId},user_id.is.null`)
      .eq('is_read', false);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(count || 0);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Get notifications by type
 */
export const getNotificationsByType = async (
  userId: string,
  type: NotificationType
): Promise<ServiceResponse<Notification[]>> => {
  try {
    const { data, error } = await supabase
      .from('notifications')
      .select('*')
      .or(`user_id.eq.${userId},user_id.is.null`)
      .eq('type', type)
      .order('created_at', { ascending: false });

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Create a notification for a specific user
 */
export const createNotification = async (
  notification: InsertNotification
): Promise<ServiceResponse<Notification>> => {
  try {
    const { data, error } = await supabase
      .from('notifications')
      .insert(notification)
      .select()
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Create broadcast notification (for all users)
 */
export const createBroadcastNotification = async (
  notification: Omit<InsertNotification, 'user_id'>
): Promise<ServiceResponse<Notification>> => {
  try {
    const { data, error } = await supabase
      .from('notifications')
      .insert({ ...notification, user_id: null })
      .select()
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Mark notification as read
 */
export const markNotificationAsRead = async (
  id: string
): Promise<ServiceResponse<Notification>> => {
  try {
    const { data, error } = await supabase
      .from('notifications')
      .update({ is_read: true })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Mark all notifications as read for a user
 */
export const markAllNotificationsAsRead = async (
  userId: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('notifications')
      .update({ is_read: true })
      .or(`user_id.eq.${userId},user_id.is.null`)
      .eq('is_read', false);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(null);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Delete a notification
 */
export const deleteNotification = async (
  id: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('notifications')
      .delete()
      .eq('id', id);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(null);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Delete all read notifications for a user
 */
export const deleteReadNotifications = async (
  userId: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('notifications')
      .delete()
      .or(`user_id.eq.${userId},user_id.is.null`)
      .eq('is_read', true);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(null);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Bulk create notifications for multiple users
 */
export const bulkCreateNotifications = async (
  userIds: string[],
  notificationData: Omit<InsertNotification, 'user_id'>
): Promise<ServiceResponse<Notification[]>> => {
  try {
    const notifications = userIds.map(userId => ({
      ...notificationData,
      user_id: userId,
    }));

    const { data, error } = await supabase
      .from('notifications')
      .insert(notifications)
      .select();

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

/**
 * Subscribe to real-time notifications
 */
export const subscribeToNotifications = (
  userId: string,
  callback: (notification: Notification) => void
) => {
  const channel = supabase
    .channel('notifications')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'notifications',
        filter: `user_id=eq.${userId}`,
      },
      (payload) => {
        callback(payload.new as Notification);
      }
    )
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'notifications',
        filter: 'user_id=is.null',
      },
      (payload) => {
        callback(payload.new as Notification);
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
};

/**
 * Get recent notifications (last N notifications)
 */
export const getRecentNotifications = async (
  userId: string,
  limit: number = 10
): Promise<ServiceResponse<Notification[]>> => {
  try {
    const { data, error } = await supabase
      .from('notifications')
      .select('*')
      .or(`user_id.eq.${userId},user_id.is.null`)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'An unexpected error occurred'
    );
  }
};

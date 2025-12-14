import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { Announcement, InsertAnnouncement, Priority } from '../types/database.types';

/**
 * Get all active announcements (not expired)
 */
export const getActiveAnnouncements = async (): Promise<
  ServiceResponse<Announcement[]>
> => {
  try {
    const now = new Date().toISOString();
    const { data, error } = await supabase
      .from('announcements')
      .select('*')
      .or(`expires_at.is.null,expires_at.gt.${now}`)
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
 * Get all announcements (including expired)
 */
export const getAllAnnouncements = async (): Promise<
  ServiceResponse<Announcement[]>
> => {
  try {
    const { data, error } = await supabase
      .from('announcements')
      .select('*')
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
 * Get announcements by priority
 */
export const getAnnouncementsByPriority = async (
  priority: Priority
): Promise<ServiceResponse<Announcement[]>> => {
  try {
    const now = new Date().toISOString();
    const { data, error } = await supabase
      .from('announcements')
      .select('*')
      .eq('priority', priority)
      .or(`expires_at.is.null,expires_at.gt.${now}`)
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
 * Get high priority active announcements
 */
export const getHighPriorityAnnouncements = async (): Promise<
  ServiceResponse<Announcement[]>
> => {
  return getAnnouncementsByPriority('high');
};

/**
 * Get announcement by ID
 */
export const getAnnouncementById = async (
  id: string
): Promise<ServiceResponse<Announcement>> => {
  try {
    const { data, error } = await supabase
      .from('announcements')
      .select('*')
      .eq('id', id)
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
 * Create a new announcement
 */
export const createAnnouncement = async (
  announcement: InsertAnnouncement
): Promise<ServiceResponse<Announcement>> => {
  try {
    const { data, error } = await supabase
      .from('announcements')
      .insert(announcement)
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
 * Update an announcement
 */
export const updateAnnouncement = async (
  id: string,
  updates: Partial<Omit<Announcement, 'id' | 'created_at'>>
): Promise<ServiceResponse<Announcement>> => {
  try {
    const { data, error } = await supabase
      .from('announcements')
      .update(updates)
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
 * Delete an announcement
 */
export const deleteAnnouncement = async (
  id: string
): Promise<ServiceResponse<null>> => {
  try {
    const { error } = await supabase
      .from('announcements')
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
 * Get announcements created by a specific user
 */
export const getAnnouncementsByCreator = async (
  createdBy: string
): Promise<ServiceResponse<Announcement[]>> => {
  try {
    const { data, error } = await supabase
      .from('announcements')
      .select('*')
      .eq('created_by', createdBy)
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
 * Get recent announcements (last N announcements)
 */
export const getRecentAnnouncements = async (
  limit: number = 5
): Promise<ServiceResponse<Announcement[]>> => {
  try {
    const now = new Date().toISOString();
    const { data, error } = await supabase
      .from('announcements')
      .select('*')
      .or(`expires_at.is.null,expires_at.gt.${now}`)
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

/**
 * Get expired announcements
 */
export const getExpiredAnnouncements = async (): Promise<
  ServiceResponse<Announcement[]>
> => {
  try {
    const now = new Date().toISOString();
    const { data, error } = await supabase
      .from('announcements')
      .select('*')
      .not('expires_at', 'is', null)
      .lt('expires_at', now)
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
 * Extend announcement expiration
 */
export const extendAnnouncementExpiration = async (
  id: string,
  daysToAdd: number
): Promise<ServiceResponse<Announcement>> => {
  try {
    // Get current announcement
    const { data: announcement, error: fetchError } = await supabase
      .from('announcements')
      .select('*')
      .eq('id', id)
      .single();

    if (fetchError) {
      return createErrorResponse(fetchError.message);
    }

    // Calculate new expiration date
    const currentExpiry = announcement.expires_at
      ? new Date(announcement.expires_at)
      : new Date();
    currentExpiry.setDate(currentExpiry.getDate() + daysToAdd);
    const newExpiryDate = currentExpiry.toISOString();

    // Update announcement
    const { data, error } = await supabase
      .from('announcements')
      .update({ expires_at: newExpiryDate })
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
 * Set announcement to never expire
 */
export const setAnnouncementNeverExpire = async (
  id: string
): Promise<ServiceResponse<Announcement>> => {
  try {
    const { data, error } = await supabase
      .from('announcements')
      .update({ expires_at: null })
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
 * Bulk delete expired announcements
 */
export const deleteExpiredAnnouncements = async (): Promise<
  ServiceResponse<null>
> => {
  try {
    const now = new Date().toISOString();
    const { error } = await supabase
      .from('announcements')
      .delete()
      .not('expires_at', 'is', null)
      .lt('expires_at', now);

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
 * Search announcements by title or message
 */
export const searchAnnouncements = async (
  searchTerm: string
): Promise<ServiceResponse<Announcement[]>> => {
  try {
    const { data, error } = await supabase
      .from('announcements')
      .select('*')
      .or(`title.ilike.%${searchTerm}%,message.ilike.%${searchTerm}%`)
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
 * Subscribe to real-time announcement updates
 */
export const subscribeToAnnouncements = (
  callback: (announcement: Announcement) => void
) => {
  const channel = supabase
    .channel('announcements')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'announcements',
      },
      (payload) => {
        if (payload.eventType === 'INSERT' || payload.eventType === 'UPDATE') {
          callback(payload.new as Announcement);
        }
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
};

import { useEffect, useCallback, useRef } from 'react';
import { RealtimeChannel, RealtimePostgresChangesPayload } from '@supabase/supabase-js';
import { supabase } from '../services/supabase';

type DatabaseTable = 'meals' | 'deposits' | 'expenses' | 'notifications' | 'announcements' | 'menu' | 'meal_settings' | 'users';

type DatabaseChangeEvent = 'INSERT' | 'UPDATE' | 'DELETE' | '*';

interface UseRealtimeOptions<T extends Record<string, any> = any> {
  table: DatabaseTable;
  event?: DatabaseChangeEvent;
  filter?: string;
  onInsert?: (payload: RealtimePostgresChangesPayload<T>) => void;
  onUpdate?: (payload: RealtimePostgresChangesPayload<T>) => void;
  onDelete?: (payload: RealtimePostgresChangesPayload<T>) => void;
  onChange?: (payload: RealtimePostgresChangesPayload<T>) => void;
  enabled?: boolean;
}

/**
 * Custom hook for Supabase realtime subscriptions
 * Automatically subscribes to table changes and cleans up on unmount
 */
export const useRealtime = <T extends Record<string, any> = any>(options: UseRealtimeOptions<T>) => {
  const {
    table,
    event = '*',
    filter,
    onInsert,
    onUpdate,
    onDelete,
    onChange,
    enabled = true,
  } = options;

  const channelRef = useRef<RealtimeChannel | null>(null);

  const handleChange = useCallback(
    (payload: RealtimePostgresChangesPayload<T>) => {
      if (onChange) {
        onChange(payload);
      }

      switch (payload.eventType) {
        case 'INSERT':
          if (onInsert) onInsert(payload);
          break;
        case 'UPDATE':
          if (onUpdate) onUpdate(payload);
          break;
        case 'DELETE':
          if (onDelete) onDelete(payload);
          break;
      }
    },
    [onChange, onInsert, onUpdate, onDelete]
  );

  useEffect(() => {
    if (!enabled) return;

    // Create channel name
    const channelName = `realtime:${table}:${event}${filter ? `:${filter}` : ''}`;

    // Subscribe to changes
    const channel = supabase
      .channel(channelName)
      .on(
        'postgres_changes' as any,
        {
          event,
          schema: 'public',
          table,
          filter,
        },
        handleChange as any
      )
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          console.log(`Subscribed to ${table} realtime updates`);
        } else if (status === 'CHANNEL_ERROR') {
          console.error(`Error subscribing to ${table} realtime updates`);
        }
      });

    channelRef.current = channel;

    // Cleanup on unmount
    return () => {
      if (channelRef.current) {
        console.log(`Unsubscribing from ${table} realtime updates`);
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
    };
  }, [table, event, filter, handleChange, enabled]);

  return {
    channel: channelRef.current,
  };
};

/**
 * Hook for subscribing to user-specific notifications
 */
export const useNotificationRealtime = (
  userId: string | undefined,
  onNewNotification: (notification: any) => void,
  enabled = true
) => {
  return useRealtime({
    table: 'notifications',
    event: 'INSERT',
    filter: userId ? `user_id=eq.${userId}` : undefined,
    onInsert: (payload) => {
      if (payload.new) {
        onNewNotification(payload.new);
      }
    },
    enabled: enabled && !!userId,
  });
};

/**
 * Hook for subscribing to meal updates for a specific user
 */
export const useMealRealtime = (
  userId: string | undefined,
  onMealChange: (meal: any) => void,
  enabled = true
) => {
  return useRealtime({
    table: 'meals',
    event: '*',
    filter: userId ? `user_id=eq.${userId}` : undefined,
    onChange: (payload) => {
      if (payload.new) {
        onMealChange(payload.new);
      }
    },
    enabled: enabled && !!userId,
  });
};

/**
 * Hook for subscribing to announcements
 */
export const useAnnouncementRealtime = (
  onNewAnnouncement: (announcement: any) => void,
  enabled = true
) => {
  return useRealtime({
    table: 'announcements',
    event: 'INSERT',
    onInsert: (payload) => {
      if (payload.new) {
        onNewAnnouncement(payload.new);
      }
    },
    enabled,
  });
};

/**
 * Hook for subscribing to menu updates
 */
export const useMenuRealtime = (
  onMenuChange: (menu: any) => void,
  enabled = true
) => {
  return useRealtime({
    table: 'menu',
    event: '*',
    onChange: (payload) => {
      if (payload.new) {
        onMenuChange(payload.new);
      }
    },
    enabled,
  });
};

/**
 * Hook for subscribing to meal settings updates
 */
export const useMealSettingsRealtime = (
  onSettingsChange: (settings: any) => void,
  enabled = true
) => {
  return useRealtime({
    table: 'meal_settings',
    event: '*',
    onChange: (payload) => {
      if (payload.new) {
        onSettingsChange(payload.new);
      }
    },
    enabled,
  });
};

import { ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import { EmailPayload, EmailQueueItem, EmailStatus } from '../types/email.types';
import { sendEmail } from './email.service';

/**
 * In-memory email queue
 * For production, consider using a proper queue system like BullMQ or Supabase Queue
 */
class EmailQueue {
  private queue: Map<string, EmailQueueItem> = new Map();
  private processing = false;
  private processInterval: ReturnType<typeof setInterval> | null = null;

  /**
   * Add email to queue
   */
  async enqueue(payload: EmailPayload, maxAttempts: number = 3): Promise<string> {
    const id = this.generateId();
    const now = new Date();

    const queueItem: EmailQueueItem = {
      id,
      payload,
      status: 'pending',
      attempts: 0,
      maxAttempts,
      createdAt: now,
      updatedAt: now,
      scheduledFor: payload.scheduledFor,
    };

    this.queue.set(id, queueItem);

    // Start processing if not already running
    if (!this.processing) {
      this.startProcessing();
    }

    return id;
  }

  /**
   * Add multiple emails to queue
   */
  async enqueueBulk(payloads: EmailPayload[], maxAttempts: number = 3): Promise<string[]> {
    const ids: string[] = [];

    for (const payload of payloads) {
      const id = await this.enqueue(payload, maxAttempts);
      ids.push(id);
    }

    return ids;
  }

  /**
   * Get queue item by ID
   */
  getQueueItem(id: string): EmailQueueItem | undefined {
    return this.queue.get(id);
  }

  /**
   * Get all queue items
   */
  getAllQueueItems(): EmailQueueItem[] {
    return Array.from(this.queue.values());
  }

  /**
   * Get queue items by status
   */
  getQueueItemsByStatus(status: EmailStatus): EmailQueueItem[] {
    return Array.from(this.queue.values()).filter(item => item.status === status);
  }

  /**
   * Cancel queue item
   */
  cancelQueueItem(id: string): boolean {
    const item = this.queue.get(id);
    if (!item) return false;

    if (item.status === 'pending' || item.status === 'failed') {
      item.status = 'cancelled';
      item.updatedAt = new Date();
      this.queue.set(id, item);
      return true;
    }

    return false;
  }

  /**
   * Remove queue item
   */
  removeQueueItem(id: string): boolean {
    return this.queue.delete(id);
  }

  /**
   * Clear completed items from queue
   */
  clearCompleted(): number {
    let count = 0;
    for (const [id, item] of this.queue.entries()) {
      if (item.status === 'sent' || item.status === 'cancelled') {
        this.queue.delete(id);
        count++;
      }
    }
    return count;
  }

  /**
   * Start processing queue
   */
  private startProcessing(): void {
    if (this.processing) return;

    this.processing = true;
    this.processInterval = setInterval(() => {
      this.processQueue();
    }, 5000); // Process every 5 seconds

    // Initial process
    this.processQueue();
  }

  /**
   * Stop processing queue
   */
  stopProcessing(): void {
    if (this.processInterval) {
      clearInterval(this.processInterval);
      this.processInterval = null;
    }
    this.processing = false;
  }

  /**
   * Process queue
   */
  private async processQueue(): Promise<void> {
    const now = new Date();

    // Get pending items that are ready to be sent
    const pendingItems = Array.from(this.queue.values()).filter(item => {
      if (item.status !== 'pending') return false;
      if (item.scheduledFor && item.scheduledFor > now) return false;
      return true;
    });

    // Process items in parallel (with limit)
    const CONCURRENT_LIMIT = 3;
    for (let i = 0; i < pendingItems.length; i += CONCURRENT_LIMIT) {
      const batch = pendingItems.slice(i, i + CONCURRENT_LIMIT);
      await Promise.all(batch.map(item => this.processQueueItem(item)));
    }

    // Retry failed items
    const failedItems = Array.from(this.queue.values()).filter(
      item => item.status === 'failed' && item.attempts < item.maxAttempts
    );

    for (const item of failedItems) {
      // Exponential backoff
      const backoffDelay = Math.pow(2, item.attempts) * 1000; // 2^n seconds
      const timeSinceUpdate = now.getTime() - item.updatedAt.getTime();

      if (timeSinceUpdate >= backoffDelay) {
        await this.processQueueItem(item);
      }
    }

    // Auto-clear old completed items (older than 1 hour)
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    for (const [id, item] of this.queue.entries()) {
      if (
        (item.status === 'sent' || item.status === 'cancelled') &&
        item.updatedAt < oneHourAgo
      ) {
        this.queue.delete(id);
      }
    }
  }

  /**
   * Process a single queue item
   */
  private async processQueueItem(item: EmailQueueItem): Promise<void> {
    try {
      // Update status to processing
      item.status = 'processing';
      item.attempts++;
      item.updatedAt = new Date();
      this.queue.set(item.id, item);

      // Send email
      const result = await sendEmail(item.payload);

      if (result.success) {
        item.status = 'sent';
        item.sentAt = new Date();
        item.error = undefined;
      } else {
        throw new Error(result.error || 'Failed to send email');
      }
    } catch (error) {
      item.status = 'failed';
      item.error = error instanceof Error ? error.message : 'Unknown error';

      // If max attempts reached, mark as permanently failed
      if (item.attempts >= item.maxAttempts) {
        console.error(`Email ${item.id} failed after ${item.attempts} attempts:`, item.error);
      }
    } finally {
      item.updatedAt = new Date();
      this.queue.set(item.id, item);
    }
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `email_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }

  /**
   * Get queue statistics
   */
  getStats() {
    const items = Array.from(this.queue.values());
    return {
      total: items.length,
      pending: items.filter(i => i.status === 'pending').length,
      processing: items.filter(i => i.status === 'processing').length,
      sent: items.filter(i => i.status === 'sent').length,
      failed: items.filter(i => i.status === 'failed').length,
      cancelled: items.filter(i => i.status === 'cancelled').length,
    };
  }
}

// Singleton instance
const emailQueue = new EmailQueue();

/**
 * Add email to queue
 */
export const queueEmail = async (
  payload: EmailPayload,
  maxAttempts: number = 3
): Promise<ServiceResponse<string>> => {
  try {
    const id = await emailQueue.enqueue(payload, maxAttempts);
    return createSuccessResponse(id);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to queue email'
    );
  }
};

/**
 * Add multiple emails to queue
 */
export const queueBulkEmails = async (
  payloads: EmailPayload[],
  maxAttempts: number = 3
): Promise<ServiceResponse<string[]>> => {
  try {
    const ids = await emailQueue.enqueueBulk(payloads, maxAttempts);
    return createSuccessResponse(ids);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to queue bulk emails'
    );
  }
};

/**
 * Get queue item by ID
 */
export const getQueueItem = (id: string): ServiceResponse<EmailQueueItem | null> => {
  try {
    const item = emailQueue.getQueueItem(id);
    return createSuccessResponse(item || null);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to get queue item'
    );
  }
};

/**
 * Get all queue items
 */
export const getAllQueueItems = (): ServiceResponse<EmailQueueItem[]> => {
  try {
    const items = emailQueue.getAllQueueItems();
    return createSuccessResponse(items);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to get queue items'
    );
  }
};

/**
 * Get queue items by status
 */
export const getQueueItemsByStatus = (
  status: EmailStatus
): ServiceResponse<EmailQueueItem[]> => {
  try {
    const items = emailQueue.getQueueItemsByStatus(status);
    return createSuccessResponse(items);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to get queue items by status'
    );
  }
};

/**
 * Cancel queue item
 */
export const cancelQueueItem = (id: string): ServiceResponse<boolean> => {
  try {
    const cancelled = emailQueue.cancelQueueItem(id);
    return createSuccessResponse(cancelled);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to cancel queue item'
    );
  }
};

/**
 * Clear completed items
 */
export const clearCompletedQueueItems = (): ServiceResponse<number> => {
  try {
    const count = emailQueue.clearCompleted();
    return createSuccessResponse(count);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to clear completed items'
    );
  }
};

/**
 * Get queue statistics
 */
export const getQueueStats = (): ServiceResponse<any> => {
  try {
    const stats = emailQueue.getStats();
    return createSuccessResponse(stats);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to get queue statistics'
    );
  }
};

/**
 * Stop queue processing (useful for cleanup)
 */
export const stopQueueProcessing = (): void => {
  emailQueue.stopProcessing();
};

// Export singleton instance for advanced usage
export { emailQueue };

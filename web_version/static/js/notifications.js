/**
 * Web Notification Manager
 * Handles browser notifications, sound alerts, and reminder system
 */

class WebNotificationManager {
    constructor() {
        this.permission = 'default';
        this.settings = this.loadSettings();
        this.checkInterval = null;
        this.lastCheck = new Date();
        this.audioContext = null;
        this.init();
    }

    init() {
        this.checkPermission();
        this.startNotificationMonitoring();
        this.setupAudioContext();
    }

    loadSettings() {
        const defaultSettings = {
            browserNotificationsEnabled: true,
            soundAlertsEnabled: true,
            reminderMinutes: 15,
            notificationCheckInterval: 60,
            taskDueNotifications: true,
            overdueNotifications: true,
            completionNotifications: true,
            dailySummaryNotifications: false
        };

        try {
            const saved = localStorage.getItem('taskPlannerSettings');
            const allSettings = saved ? JSON.parse(saved) : {};
            return { ...defaultSettings, ...allSettings };
        } catch (error) {
            console.error('Error loading notification settings:', error);
            return defaultSettings;
        }
    }

    async checkPermission() {
        if ('Notification' in window) {
            this.permission = Notification.permission;
        } else {
            this.permission = 'not-supported';
        }
        return this.permission;
    }

    async requestPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            this.permission = permission;
            return permission;
        }
        return 'not-supported';
    }

    setupAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (error) {
            console.warn('Audio context not available:', error);
        }
    }

    playNotificationSound(type = 'default') {
        if (!this.settings.soundAlertsEnabled || !this.audioContext) {
            return;
        }

        try {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            // Different sounds for different notification types
            switch (type) {
                case 'urgent':
                    oscillator.frequency.value = 1000;
                    gainNode.gain.setValueAtTime(0.4, this.audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                    oscillator.start(this.audioContext.currentTime);
                    oscillator.stop(this.audioContext.currentTime + 0.3);
                    
                    // Second beep
                    setTimeout(() => {
                        const osc2 = this.audioContext.createOscillator();
                        const gain2 = this.audioContext.createGain();
                        osc2.connect(gain2);
                        gain2.connect(this.audioContext.destination);
                        osc2.frequency.value = 1200;
                        gain2.gain.setValueAtTime(0.4, this.audioContext.currentTime);
                        gain2.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                        osc2.start(this.audioContext.currentTime);
                        osc2.stop(this.audioContext.currentTime + 0.3);
                    }, 400);
                    break;
                    
                case 'complete':
                    // Pleasant completion sound
                    oscillator.frequency.value = 600;
                    gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.8);
                    oscillator.start(this.audioContext.currentTime);
                    oscillator.stop(this.audioContext.currentTime + 0.8);
                    break;
                    
                default:
                    // Default notification sound
                    oscillator.frequency.value = 800;
                    gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5);
                    oscillator.start(this.audioContext.currentTime);
                    oscillator.stop(this.audioContext.currentTime + 0.5);
                    break;
            }
        } catch (error) {
            console.error('Error playing notification sound:', error);
        }
    }

    showNotification(title, message, options = {}) {
        if (!this.settings.browserNotificationsEnabled || this.permission !== 'granted') {
            // Fallback to toast notification
            this.showToastNotification(title, message, options.type || 'info');
            return;
        }

        try {
            const notification = new Notification(title, {
                body: message,
                icon: options.icon || '/static/favicon.ico',
                tag: options.tag || 'task-planner',
                requireInteraction: options.requireInteraction || false,
                silent: !this.settings.soundAlertsEnabled,
                ...options
            });

            // Auto close after timeout
            if (options.timeout) {
                setTimeout(() => {
                    notification.close();
                }, options.timeout);
            }

            // Play sound if enabled
            if (this.settings.soundAlertsEnabled) {
                this.playNotificationSound(options.soundType);
            }

            // Handle click events
            notification.onclick = () => {
                window.focus();
                if (options.onClick) {
                    options.onClick();
                }
                notification.close();
            };

            return notification;
        } catch (error) {
            console.error('Error showing notification:', error);
            this.showToastNotification(title, message, options.type || 'info');
        }
    }

    showToastNotification(title, message, type = 'info') {
        // Create toast element
        const toastContainer = document.querySelector('.toast-container') || this.createToastContainer();
        
        const toastId = 'toast-' + Date.now();
        const iconMap = {
            success: 'bi-check-circle-fill text-success',
            error: 'bi-exclamation-circle-fill text-danger',
            warning: 'bi-exclamation-triangle-fill text-warning',
            info: 'bi-info-circle-fill text-primary'
        };

        const toastHTML = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="${iconMap[type] || iconMap.info} me-2"></i>
                    <strong class="me-auto">${title}</strong>
                    <small class="text-muted">now</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000
        });
        
        toast.show();

        // Remove element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });

        // Play sound
        if (this.settings.soundAlertsEnabled) {
            this.playNotificationSound(type === 'error' ? 'urgent' : 'default');
        }
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    startNotificationMonitoring() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }

        const intervalMs = this.settings.notificationCheckInterval * 1000;
        
        this.checkInterval = setInterval(() => {
            this.checkForNotifications();
        }, intervalMs);

        // Initial check
        this.checkForNotifications();
    }

    stopNotificationMonitoring() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
    }

    async checkForNotifications() {
        try {
            const response = await fetch('/api/notifications/check');
            const data = await response.json();

            if (data.success && data.notifications) {
                data.notifications.forEach(notification => {
                    this.processNotification(notification);
                });
            }
        } catch (error) {
            console.error('Error checking for notifications:', error);
        }
    }

    processNotification(notification) {
        const { type, title, message, task } = notification;

        switch (type) {
            case 'task_due':
                if (this.settings.taskDueNotifications) {
                    this.showNotification(
                        '⏰ Task Due Soon',
                        `"${task.title}" is due in ${this.settings.reminderMinutes} minutes`,
                        {
                            tag: `task-due-${task.id}`,
                            requireInteraction: true,
                            soundType: 'default',
                            onClick: () => this.openTask(task.id)
                        }
                    );
                }
                break;

            case 'task_overdue':
                if (this.settings.overdueNotifications) {
                    this.showNotification(
                        '⚠️ Task Overdue',
                        `"${task.title}" is overdue!`,
                        {
                            tag: `task-overdue-${task.id}`,
                            requireInteraction: true,
                            soundType: 'urgent',
                            onClick: () => this.openTask(task.id)
                        }
                    );
                }
                break;

            case 'task_completed':
                if (this.settings.completionNotifications) {
                    this.showNotification(
                        '✅ Task Completed',
                        `Great job! You completed "${task.title}"`,
                        {
                            tag: `task-complete-${task.id}`,
                            soundType: 'complete',
                            timeout: 5000
                        }
                    );
                }
                break;

            case 'daily_summary':
                if (this.settings.dailySummaryNotifications) {
                    this.showNotification(
                        '📊 Daily Summary',
                        message,
                        {
                            tag: 'daily-summary',
                            timeout: 10000
                        }
                    );
                }
                break;

            default:
                this.showNotification(title, message, {
                    tag: 'general-notification'
                });
                break;
        }
    }

    openTask(taskId) {
        // Navigate to task or open task modal
        if (window.location.pathname === '/') {
            // On main page, trigger task modal
            if (window.taskManager && window.taskManager.editTask) {
                window.taskManager.editTask(taskId);
            }
        } else {
            // Navigate to main page with task focus
            window.location.href = `/?task=${taskId}`;
        }
    }

    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
        
        // Restart monitoring with new interval if changed
        if (newSettings.notificationCheckInterval) {
            this.startNotificationMonitoring();
        }
    }

    // Public methods for manual notifications
    notifyTaskDue(task, minutesUntilDue) {
        this.processNotification({
            type: 'task_due',
            title: '⏰ Task Due Soon',
            message: `"${task.title}" is due in ${minutesUntilDue} minutes`,
            task: task
        });
    }

    notifyTaskOverdue(task) {
        this.processNotification({
            type: 'task_overdue',
            title: '⚠️ Task Overdue',
            message: `"${task.title}" is overdue!`,
            task: task
        });
    }

    notifyTaskCompleted(task) {
        this.processNotification({
            type: 'task_completed',
            title: '✅ Task Completed',
            message: `Great job! You completed "${task.title}"`,
            task: task
        });
    }

    sendTestNotification() {
        this.showNotification(
            'Task Planner Test',
            'This is a test notification from Task Planner Web!',
            {
                tag: 'test-notification',
                timeout: 5000
            }
        );
    }

    testSound() {
        this.playNotificationSound('default');
    }
}

// Initialize notification manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = new WebNotificationManager();
});

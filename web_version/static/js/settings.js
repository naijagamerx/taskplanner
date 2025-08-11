/**
 * Settings Page JavaScript
 * Handles all settings functionality including themes, notifications, database, etc.
 */

class SettingsManager {
    constructor() {
        this.settings = this.loadSettings();
        this.notificationPermission = 'default';
        this.notificationInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadCurrentSettings();
        this.checkNotificationPermission();
        this.loadDatabaseInfo();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(tab.dataset.tab);
            });
        });

        // Theme selection
        document.querySelectorAll('input[name="theme"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.changeTheme(radio.value);
            });
        });

        // Color scheme selection
        document.querySelectorAll('.color-option').forEach(option => {
            option.addEventListener('click', () => {
                this.changeColorScheme(option.dataset.color);
            });
        });

        // Database type selection
        const dbTypeSelect = document.getElementById('dbTypeSelect');
        if (dbTypeSelect) {
            dbTypeSelect.addEventListener('change', () => {
                this.toggleDatabaseConfig(dbTypeSelect.value);
            });
        }

        // Notification permission request
        const requestBtn = document.getElementById('requestNotificationPermission');
        if (requestBtn) {
            requestBtn.addEventListener('click', () => {
                this.requestNotificationPermission();
            });
        }

        // Test notifications
        const testNotificationBtn = document.getElementById('testNotification');
        if (testNotificationBtn) {
            testNotificationBtn.addEventListener('click', () => {
                this.sendTestNotification();
            });
        }

        const testSoundBtn = document.getElementById('testSoundAlert');
        if (testSoundBtn) {
            testSoundBtn.addEventListener('click', () => {
                this.playTestSound();
            });
        }

        // Database actions
        document.getElementById('testConnection')?.addEventListener('click', () => {
            this.testDatabaseConnection();
        });

        document.getElementById('optimizeDatabase')?.addEventListener('click', () => {
            this.optimizeDatabase();
        });

        document.getElementById('exportDatabase')?.addEventListener('click', () => {
            this.exportDatabase();
        });

        // Export/Import actions
        document.getElementById('exportTasks')?.addEventListener('click', () => {
            this.exportData('tasks', 'json');
        });

        document.getElementById('exportTasksCSV')?.addEventListener('click', () => {
            this.exportData('tasks', 'csv');
        });

        document.getElementById('exportCategories')?.addEventListener('click', () => {
            this.exportData('categories', 'json');
        });

        document.getElementById('exportSettings')?.addEventListener('click', () => {
            this.exportSettings();
        });

        document.getElementById('importData')?.addEventListener('click', () => {
            this.importData();
        });

        // Save all settings
        document.getElementById('saveAllSettings')?.addEventListener('click', () => {
            this.saveAllSettings();
        });

        // Save database configuration
        document.getElementById('saveDatabaseConfig')?.addEventListener('click', () => {
            this.saveDatabaseConfiguration();
        });

        // Category management
        document.getElementById('addCategoryBtn')?.addEventListener('click', () => {
            this.addCategory();
        });

        // Color picker synchronization
        const colorPicker = document.getElementById('newCategoryColor');
        const colorText = document.getElementById('newCategoryColorText');

        if (colorPicker && colorText) {
            colorPicker.addEventListener('input', function() {
                colorText.value = this.value;
            });

            colorText.addEventListener('input', function() {
                if (/^#[0-9A-F]{6}$/i.test(this.value)) {
                    colorPicker.value = this.value;
                }
            });
        }

        // Auto-save on input changes
        document.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('change', () => {
                this.autoSave();
            });
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update panels
        document.querySelectorAll('.settings-panel').forEach(panel => {
            panel.classList.remove('active');
            panel.style.display = 'none';
        });

        const targetPanel = document.getElementById(`${tabName}-settings`);
        if (targetPanel) {
            targetPanel.classList.add('active');
            targetPanel.style.display = 'block';

            // Load categories when categories panel is shown
            if (tabName === 'categories') {
                console.log('Categories tab clicked, loading categories...');
                setTimeout(() => {
                    this.loadCategories();
                }, 100);
            }
        }
    }

    loadSettings() {
        const defaultSettings = {
            theme: 'light',
            colorScheme: 'blue',
            fontSize: 'medium',
            compactMode: false,
            showAnimations: true,
            defaultPriority: 2,
            taskSortOrder: 'due_date',
            showCompletedTasks: true,
            autoMarkOverdue: true,
            dateFormat: 'YYYY-MM-DD',
            weekStartsOn: 'monday',
            browserNotificationsEnabled: true,
            soundAlertsEnabled: true,
            reminderMinutes: 15,
            notificationCheckInterval: 60,
            taskDueNotifications: true,
            overdueNotifications: true,
            completionNotifications: true,
            dailySummaryNotifications: false,
            autoBackupEnabled: false,
            backupFrequency: 'weekly',
            maxBackupFiles: 10
        };

        try {
            const saved = localStorage.getItem('taskPlannerSettings');
            return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
        } catch (error) {
            console.error('Error loading settings:', error);
            return defaultSettings;
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('taskPlannerSettings', JSON.stringify(this.settings));
            this.showToast('Settings saved successfully', 'success');
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showToast('Error saving settings', 'error');
        }
    }

    loadCurrentSettings() {
        // Load general settings
        document.getElementById('defaultPriority').value = this.settings.defaultPriority;
        document.getElementById('taskSortOrder').value = this.settings.taskSortOrder;
        document.getElementById('showCompletedTasks').checked = this.settings.showCompletedTasks;
        document.getElementById('autoMarkOverdue').checked = this.settings.autoMarkOverdue;
        document.getElementById('dateFormat').value = this.settings.dateFormat;
        document.getElementById('weekStartsOn').value = this.settings.weekStartsOn;

        // Load appearance settings
        document.querySelector(`input[name="theme"][value="${this.settings.theme}"]`).checked = true;
        document.getElementById('fontSize').value = this.settings.fontSize;
        document.getElementById('compactMode').checked = this.settings.compactMode;
        document.getElementById('showAnimations').checked = this.settings.showAnimations;

        // Load notification settings
        document.getElementById('browserNotificationsEnabled').checked = this.settings.browserNotificationsEnabled;
        document.getElementById('soundAlertsEnabled').checked = this.settings.soundAlertsEnabled;
        document.getElementById('reminderMinutes').value = this.settings.reminderMinutes;
        document.getElementById('notificationCheckInterval').value = this.settings.notificationCheckInterval;
        document.getElementById('taskDueNotifications').checked = this.settings.taskDueNotifications;
        document.getElementById('overdueNotifications').checked = this.settings.overdueNotifications;
        document.getElementById('completionNotifications').checked = this.settings.completionNotifications;
        document.getElementById('dailySummaryNotifications').checked = this.settings.dailySummaryNotifications;

        // Load backup settings
        document.getElementById('autoBackupEnabled').checked = this.settings.autoBackupEnabled;
        document.getElementById('backupFrequency').value = this.settings.backupFrequency;
        document.getElementById('maxBackupFiles').value = this.settings.maxBackupFiles;

        // Apply current theme
        this.applyTheme(this.settings.theme);
        this.applyColorScheme(this.settings.colorScheme);
    }

    changeTheme(theme) {
        this.settings.theme = theme;
        this.applyTheme(theme);
        this.saveSettings();
    }

    applyTheme(theme) {
        const html = document.documentElement;

        if (theme === 'dark') {
            html.setAttribute('data-bs-theme', 'dark');
        } else if (theme === 'light') {
            html.setAttribute('data-bs-theme', 'light');
        } else if (theme === 'auto') {
            // Use system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            html.setAttribute('data-bs-theme', prefersDark ? 'dark' : 'light');
        }
    }

    changeColorScheme(color) {
        this.settings.colorScheme = color;
        this.applyColorScheme(color);
        this.saveSettings();

        // Update active color option
        document.querySelectorAll('.color-option').forEach(option => {
            option.classList.remove('active');
        });
        document.querySelector(`[data-color="${color}"]`).classList.add('active');
    }

    applyColorScheme(color) {
        const colorMap = {
            blue: '#007bff',
            green: '#28a745',
            purple: '#6f42c1',
            orange: '#fd7e14'
        };

        if (colorMap[color]) {
            document.documentElement.style.setProperty('--primary-color', colorMap[color]);
        }
    }

    toggleDatabaseConfig(type) {
        const mysqlConfig = document.getElementById('mysqlConfig');
        if (mysqlConfig) {
            mysqlConfig.style.display = type === 'mysql' ? 'block' : 'none';
        }
    }

    async checkNotificationPermission() {
        if ('Notification' in window) {
            this.notificationPermission = Notification.permission;
            this.updateNotificationStatus();
        } else {
            this.updateNotificationStatus('not-supported');
        }
    }

    updateNotificationStatus(status = null) {
        const statusDot = document.getElementById('notificationStatus');
        const statusText = document.getElementById('notificationStatusText');
        const requestBtn = document.getElementById('requestNotificationPermission');

        const permission = status || this.notificationPermission;

        switch (permission) {
            case 'granted':
                statusDot.className = 'status-dot connected';
                statusText.textContent = 'Notifications enabled';
                requestBtn.style.display = 'none';
                break;
            case 'denied':
                statusDot.className = 'status-dot';
                statusText.textContent = 'Notifications blocked';
                requestBtn.style.display = 'none';
                break;
            case 'default':
                statusDot.className = 'status-dot connecting';
                statusText.textContent = 'Permission not granted';
                requestBtn.style.display = 'inline-block';
                break;
            case 'not-supported':
                statusDot.className = 'status-dot';
                statusText.textContent = 'Notifications not supported';
                requestBtn.style.display = 'none';
                break;
        }
    }

    async requestNotificationPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            this.notificationPermission = permission;
            this.updateNotificationStatus();

            if (permission === 'granted') {
                this.showToast('Notifications enabled successfully!', 'success');
            } else {
                this.showToast('Notification permission denied', 'warning');
            }
        }
    }

    sendTestNotification() {
        if (this.notificationPermission === 'granted') {
            new Notification('Task Planner Test', {
                body: 'This is a test notification from Task Planner Web!',
                icon: '/static/favicon.ico',
                tag: 'test-notification'
            });
        } else {
            this.showToast('Notifications not enabled', 'warning');
        }
    }

    playTestSound() {
        // Create a simple beep sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);

        this.showToast('Test sound played', 'info');
    }

    async loadDatabaseInfo() {
        try {
            const response = await fetch('/api/database/info');
            const data = await response.json();

            if (data.success) {
                document.getElementById('dbType').textContent = data.type || 'SQLite';
                document.getElementById('dbLocation').textContent = data.location || 'task_planner.db';
                document.getElementById('dbSize').textContent = data.size || 'Unknown';
                document.getElementById('dbLastModified').textContent = data.lastModified || 'Unknown';
            }
        } catch (error) {
            console.error('Error loading database info:', error);
        }
    }

    async updateDatabaseConnectionDisplay() {
        try {
            const response = await fetch('/api/database/info');
            const data = await response.json();

            if (data.success) {
                // Update the connection status badge
                const statusBadge = document.querySelector('.badge.bg-success');
                if (statusBadge) {
                    statusBadge.innerHTML = `<i class="bi bi-check-circle"></i> Connected to ${data.type} Database`;
                }

                // Update all database info fields consistently
                document.getElementById('dbType').textContent = data.type || 'SQLite';
                document.getElementById('dbLocation').textContent = data.location || 'Unknown';
                document.getElementById('dbSize').textContent = data.size || 'Unknown';
                document.getElementById('dbLastModified').textContent = data.lastModified || 'Unknown';

                // Update the database type selector to match current connection
                const dbTypeSelect = document.getElementById('dbTypeSelect');
                if (dbTypeSelect) {
                    dbTypeSelect.value = data.type.toLowerCase();
                    this.toggleDatabaseConfig(data.type.toLowerCase());
                }
            }
        } catch (error) {
            console.error('Error updating database connection display:', error);
        }
    }

    async testDatabaseConnection() {
        try {
            const response = await fetch('/api/database/test');
            const data = await response.json();

            if (data.success) {
                this.showToast('Database connection successful!', 'success');
            } else {
                this.showToast('Database connection failed: ' + data.error, 'error');
            }
        } catch (error) {
            this.showToast('Error testing database connection', 'error');
        }
    }

    async optimizeDatabase() {
        try {
            const response = await fetch('/api/database/optimize', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.showToast('Database optimized successfully!', 'success');
                this.loadDatabaseInfo(); // Refresh info
            } else {
                this.showToast('Database optimization failed: ' + data.error, 'error');
            }
        } catch (error) {
            this.showToast('Error optimizing database', 'error');
        }
    }

    async exportDatabase() {
        try {
            const response = await fetch('/api/database/export');
            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `task_planner_backup_${new Date().toISOString().split('T')[0]}.db`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.showToast('Database exported successfully!', 'success');
        } catch (error) {
            this.showToast('Error exporting database', 'error');
        }
    }

    async saveDatabaseConfiguration() {
        const dbType = document.getElementById('dbTypeSelect').value;

        const config = {
            type: dbType
        };

        if (dbType === 'mysql') {
            config.host = document.getElementById('dbHost').value;
            config.port = parseInt(document.getElementById('dbPort').value);
            config.database = document.getElementById('dbName').value;
            config.username = document.getElementById('dbUser').value;
            config.password = document.getElementById('dbPassword').value;

            // Validate required fields
            if (!config.host || !config.database || !config.username) {
                this.showToast('Please fill in all required database fields', 'warning');
                return;
            }
        }

        try {
            const response = await fetch('/api/database/configure', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Database configuration saved successfully!', 'success');
                // Refresh database info to show updated connection details
                this.loadDatabaseInfo();
                this.updateDatabaseConnectionDisplay();
            } else {
                this.showToast('Failed to save database configuration: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error saving database configuration:', error);
            this.showToast('Error saving database configuration', 'error');
        }
    }

    async exportData(type, format) {
        try {
            const response = await fetch(`/api/export/${type}?format=${format}`);
            const data = await response.json();

            if (data.success) {
                const content = format === 'csv' ? data.csv : JSON.stringify(data.data, null, 2);
                const mimeType = format === 'csv' ? 'text/csv' : 'application/json';
                const extension = format === 'csv' ? 'csv' : 'json';

                const blob = new Blob([content], { type: mimeType });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${type}_${new Date().toISOString().split('T')[0]}.${extension}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                this.showToast(`${type} exported successfully!`, 'success');
            } else {
                this.showToast(`Export failed: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showToast(`Error exporting ${type}`, 'error');
        }
    }

    exportSettings() {
        const settingsData = {
            settings: this.settings,
            exportDate: new Date().toISOString(),
            version: '1.0'
        };

        const blob = new Blob([JSON.stringify(settingsData, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `task_planner_settings_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        this.showToast('Settings exported successfully!', 'success');
    }

    importData() {
        const fileInput = document.getElementById('importFile');
        const file = fileInput.files[0];

        if (!file) {
            this.showToast('Please select a file to import', 'warning');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);

                if (data.settings) {
                    // Import settings
                    this.settings = { ...this.settings, ...data.settings };
                    this.saveSettings();
                    this.loadCurrentSettings();
                    this.showToast('Settings imported successfully!', 'success');
                } else {
                    // Import tasks/categories
                    this.importTaskData(data);
                }
            } catch (error) {
                this.showToast('Error parsing import file', 'error');
            }
        };

        reader.readAsText(file);
    }

    async importTaskData(data) {
        try {
            const response = await fetch('/api/import', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.showToast('Data imported successfully!', 'success');
            } else {
                this.showToast(`Import failed: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showToast('Error importing data', 'error');
        }
    }

    autoSave() {
        // Collect current form values
        this.settings.defaultPriority = parseInt(document.getElementById('defaultPriority').value);
        this.settings.taskSortOrder = document.getElementById('taskSortOrder').value;
        this.settings.showCompletedTasks = document.getElementById('showCompletedTasks').checked;
        this.settings.autoMarkOverdue = document.getElementById('autoMarkOverdue').checked;
        this.settings.dateFormat = document.getElementById('dateFormat').value;
        this.settings.weekStartsOn = document.getElementById('weekStartsOn').value;

        this.settings.fontSize = document.getElementById('fontSize').value;
        this.settings.compactMode = document.getElementById('compactMode').checked;
        this.settings.showAnimations = document.getElementById('showAnimations').checked;

        this.settings.browserNotificationsEnabled = document.getElementById('browserNotificationsEnabled').checked;
        this.settings.soundAlertsEnabled = document.getElementById('soundAlertsEnabled').checked;
        this.settings.reminderMinutes = parseInt(document.getElementById('reminderMinutes').value);
        this.settings.notificationCheckInterval = parseInt(document.getElementById('notificationCheckInterval').value);
        this.settings.taskDueNotifications = document.getElementById('taskDueNotifications').checked;
        this.settings.overdueNotifications = document.getElementById('overdueNotifications').checked;
        this.settings.completionNotifications = document.getElementById('completionNotifications').checked;
        this.settings.dailySummaryNotifications = document.getElementById('dailySummaryNotifications').checked;

        this.settings.autoBackupEnabled = document.getElementById('autoBackupEnabled').checked;
        this.settings.backupFrequency = document.getElementById('backupFrequency').value;
        this.settings.maxBackupFiles = parseInt(document.getElementById('maxBackupFiles').value);

        // Save to localStorage
        this.saveSettings();
    }

    saveAllSettings() {
        this.autoSave();
        this.showToast('All settings saved successfully!', 'success');
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            ${message}
        `;

        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    }

    // Category Management Functions
    async loadCategories() {
        console.log('loadCategories() called');
        const categoriesList = document.getElementById('categoriesList');
        console.log('categoriesList element:', categoriesList);

        if (!categoriesList) {
            console.error('categoriesList element not found!');
            return;
        }

        console.log('Fetching categories...');
        try {
            const response = await fetch('/api/categories');
            const data = await response.json();
            console.log('Categories API response:', data);

            if (data.success) {
                console.log('Calling displayCategories with', data.categories.length, 'categories');
                this.displayCategories(data.categories);
            } else {
                console.error('API returned success=false');
                categoriesList.innerHTML = '<div class="alert alert-danger">Failed to load categories</div>';
            }
        } catch (error) {
            console.error('Error loading categories:', error);
            categoriesList.innerHTML = '<div class="alert alert-danger">Error loading categories</div>';
        }
    }

    displayCategories(categories) {
        console.log('displayCategories() called with', categories.length, 'categories');
        const categoriesList = document.getElementById('categoriesList');
        console.log('categoriesList element in displayCategories:', categoriesList);

        if (categories.length === 0) {
            console.log('No categories to display');
            categoriesList.innerHTML = '<div class="text-muted text-center py-3">No categories found</div>';
            return;
        }

        let html = '';
        categories.forEach(category => {
            console.log('Processing category:', category.name);
            html += `
                <div class="category-item d-flex align-items-center p-3 mb-2">
                    <div class="category-color me-3" style="width: 24px; height: 24px; background-color: ${category.color}; border-radius: 4px;"></div>
                    <div class="flex-grow-1">
                        <strong class="category-name">${category.name}</strong>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="window.settingsManager.deleteCategory(${category.id})" title="Delete category">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `;
        });

        console.log('Setting innerHTML with HTML length:', html.length);
        categoriesList.innerHTML = html;
        console.log('Categories displayed successfully');
    }

    async addCategory() {
        const name = document.getElementById('newCategoryName').value.trim();
        const color = document.getElementById('newCategoryColor').value;
        const description = document.getElementById('newCategoryDescription').value.trim();

        if (!name) {
            this.showToast('Category name is required!', 'warning');
            return;
        }

        const categoryData = {
            name: name,
            color: color,
            description: description
        };

        try {
            const response = await fetch('/api/categories', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(categoryData)
            });

            const data = await response.json();

            if (data.success) {
                // Clear form
                document.getElementById('newCategoryName').value = '';
                document.getElementById('newCategoryColor').value = '#3498db';
                document.getElementById('newCategoryColorText').value = '#3498db';
                document.getElementById('newCategoryDescription').value = '';

                // Reload categories
                this.loadCategories();

                // Show success message
                this.showToast('Category added successfully!', 'success');
            } else {
                this.showToast('Failed to add category: ' + (data.message || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Error adding category:', error);
            this.showToast('Error adding category', 'error');
        }
    }

    async deleteCategory(categoryId) {
        if (!confirm('Are you sure you want to delete this category?')) {
            return;
        }

        try {
            const response = await fetch(`/api/categories/${categoryId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.loadCategories();
                this.showToast('Category deleted successfully!', 'success');
            } else {
                this.showToast('Failed to delete category: ' + (data.message || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Error deleting category:', error);
            this.showToast('Error deleting category', 'error');
        }
    }
}

// Initialize settings manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});

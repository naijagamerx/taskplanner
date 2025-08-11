// Task Planner Web Application - Main JavaScript

// Global variables
let currentTasks = [];
let currentCategories = [];
let currentPriorities = [];
let currentView = 'list';
let currentFilters = {
    status: '',
    category: '',
    priority: ''
};

// Pagination variables
let currentPage = 1;
let itemsPerPage = 5;
let totalPages = 1;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

function initializeApp() {
    // Initialize theme
    const savedTheme = localStorage.getItem('taskplanner-theme') || 'light';
    setTheme(savedTheme);

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupEventListeners() {
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', refreshData);

    // Global search
    const globalSearch = document.getElementById('globalSearch');
    if (globalSearch) {
        globalSearch.addEventListener('input', debounce(handleGlobalSearch, 300));
        document.getElementById('searchBtn').addEventListener('click', () => {
            handleGlobalSearch();
        });
    }

    // Add task buttons
    const addTaskBtn = document.getElementById('addTaskBtn');
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', showAddTaskModal);
    }

    const addFirstTaskBtn = document.getElementById('addFirstTaskBtn');
    if (addFirstTaskBtn) {
        addFirstTaskBtn.addEventListener('click', showAddTaskModal);
    }

    // Save task button
    document.getElementById('saveTaskBtn').addEventListener('click', saveTask);

    // Filter controls
    const statusFilter = document.getElementById('statusFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const priorityFilter = document.getElementById('priorityFilter');
    const clearFilters = document.getElementById('clearFilters');

    if (statusFilter) statusFilter.addEventListener('change', applyFilters);
    if (categoryFilter) categoryFilter.addEventListener('change', applyFilters);
    if (priorityFilter) priorityFilter.addEventListener('change', applyFilters);
    if (clearFilters) clearFilters.addEventListener('click', clearAllFilters);

    // View toggle buttons
    const listViewBtn = document.getElementById('listViewBtn');
    const gridViewBtn = document.getElementById('gridViewBtn');

    if (listViewBtn) {
        listViewBtn.addEventListener('click', () => switchView('list'));
    }
    if (gridViewBtn) {
        gridViewBtn.addEventListener('click', () => switchView('grid'));
    }

    // Pagination controls
    const itemsPerPageSelect = document.getElementById('itemsPerPageSelect');
    if (itemsPerPageSelect) {
        itemsPerPageSelect.addEventListener('change', changeItemsPerPage);
    }

    // Recurring task checkbox
    const recurringCheckbox = document.getElementById('taskIsRecurring');
    if (recurringCheckbox) {
        recurringCheckbox.addEventListener('change', toggleRecurringOptions);
    }
}

function loadInitialData() {
    Promise.all([
        loadTasks(),
        loadCategories(),
        loadPriorities(),
        loadAnalytics()
    ]).then(() => {
        console.log('✅ Initial data loaded successfully');
    }).catch(error => {
        console.error('❌ Error loading initial data:', error);
        showToast('Error loading application data', 'error');
    });
}

// API Functions
async function loadTasks() {
    try {
        showLoading(true);
        const response = await fetch('/api/tasks');
        const data = await response.json();

        if (response.ok) {
            currentTasks = data.tasks || [];
            renderTasks(currentTasks);
            updateQuickStats();
        } else {
            throw new Error(data.error || 'Failed to load tasks');
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
        showToast('Error loading tasks', 'error');
    } finally {
        showLoading(false);
    }
}

async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();

        if (response.ok) {
            currentCategories = data.categories || [];
            populateCategoryFilters();
        } else {
            console.warn('Categories not available:', data.error);
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadPriorities() {
    try {
        const response = await fetch('/api/priorities');
        const data = await response.json();

        if (response.ok) {
            currentPriorities = data.priorities || [];
        } else {
            console.warn('Priorities not available:', data.error);
        }
    } catch (error) {
        console.error('Error loading priorities:', error);
    }
}

async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics/overview');
        const data = await response.json();

        if (response.ok) {
            updateAnalyticsDisplay(data);
        } else {
            console.warn('Analytics not available:', data.error);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Task Management Functions
function renderTasks(tasks, view = currentView) {
    const container = document.getElementById('tasksContainer');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const emptyState = document.getElementById('emptyState');

    if (!container) return;

    // Update current view
    currentView = view;

    // Apply current filters
    const filteredTasks = applyCurrentFilters(tasks);

    if (filteredTasks.length === 0) {
        container.style.display = 'none';
        loadingSpinner.style.display = 'none';
        emptyState.style.display = 'block';
        renderPagination(0);
        return;
    }

    // Show tasks container
    container.style.display = 'block';
    loadingSpinner.style.display = 'none';
    emptyState.style.display = 'none';

    // Calculate pagination
    totalPages = Math.ceil(filteredTasks.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedTasks = filteredTasks.slice(startIndex, endIndex);

    // Render based on view type
    if (view === 'grid') {
        container.className = 'task-grid';
        container.innerHTML = `<div class="row">${paginatedTasks.map(task => createTaskCardHTML(task, 'grid')).join('')}</div>`;
    } else {
        container.className = '';
        container.innerHTML = paginatedTasks.map(task => createTaskCardHTML(task, 'list')).join('');
    }

    // Render pagination controls
    renderPagination(filteredTasks.length);

    // Add event listeners to task cards
    addTaskEventListeners();
}

function createTaskCardHTML(task, viewType = 'list') {
    const priorityClass = getPriorityClass(task.priority_id);
    const statusClass = `status-${task.status}`;
    const priorityName = getPriorityName(task.priority_id);
    const categoryName = getCategoryName(task.category_id);
    const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : '';

    const cardClass = viewType === 'grid' ? 'col-md-6 col-lg-4 mb-3' : 'mb-3';

    return `
        <div class="${cardClass}">
            <div class="card task-card ${priorityClass} ${statusClass}" data-task-id="${task.id}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title task-title mb-1">${escapeHtml(task.title)}</h6>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                <i class="bi bi-three-dots"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item edit-task" href="#" data-task-id="${task.id}">
                                    <i class="bi bi-pencil"></i> Edit
                                </a></li>
                                <li><a class="dropdown-item toggle-status" href="#" data-task-id="${task.id}">
                                    <i class="bi bi-check-circle"></i> ${task.status === 'completed' ? 'Mark Pending' : 'Mark Complete'}
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger delete-task" href="#" data-task-id="${task.id}">
                                    <i class="bi bi-trash"></i> Delete
                                </a></li>
                            </ul>
                        </div>
                    </div>

                    ${task.description ? `<p class="card-text text-muted small text-truncate-2">${escapeHtml(task.description)}</p>` : ''}

                    <div class="d-flex flex-wrap gap-1 mb-2">
                        <span class="badge priority-${priorityName.toLowerCase()}">${priorityName}</span>
                        <span class="badge status-${task.status}">${formatStatus(task.status)}</span>
                        ${categoryName ? `<span class="badge bg-secondary">${categoryName}</span>` : ''}
                    </div>

                    ${dueDate || task.estimated_duration ? `
                        <div class="small text-muted">
                            ${dueDate ? `<i class="bi bi-calendar"></i> Due: ${dueDate}` : ''}
                            ${task.estimated_duration ? `<i class="bi bi-clock ms-2"></i> ${task.estimated_duration}min` : ''}
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function addTaskEventListeners() {
    // Edit task buttons
    document.querySelectorAll('.edit-task').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const taskId = parseInt(this.dataset.taskId);
            editTask(taskId);
        });
    });

    // Toggle status buttons
    document.querySelectorAll('.toggle-status').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const taskId = parseInt(this.dataset.taskId);
            toggleTaskStatus(taskId);
        });
    });

    // Delete task buttons
    document.querySelectorAll('.delete-task').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const taskId = parseInt(this.dataset.taskId);
            deleteTask(taskId);
        });
    });
}

async function saveTask() {
    const taskId = document.getElementById('taskId').value;
    const isEdit = taskId && taskId !== '';

    const taskData = {
        title: document.getElementById('taskTitle').value.trim(),
        description: document.getElementById('taskDescription').value.trim(),
        category_id: document.getElementById('taskCategory').value || null,
        priority_id: parseInt(document.getElementById('taskPriority').value),
        due_date: document.getElementById('taskDueDate').value || null,
        due_time: document.getElementById('taskDueTime').value || null,
        estimated_duration: document.getElementById('taskDuration').value ? parseInt(document.getElementById('taskDuration').value) : null,
        status: document.getElementById('taskStatus').value,
        is_recurring: document.getElementById('taskIsRecurring').checked,
        recurrence_pattern: document.getElementById('taskIsRecurring').checked ? document.getElementById('taskRecurrencePattern').value : null,
        recurrence_interval: document.getElementById('taskIsRecurring').checked ? parseInt(document.getElementById('taskRecurrenceInterval').value) : null,
        recurrence_end_date: document.getElementById('taskIsRecurring').checked ? (document.getElementById('taskRecurrenceEndDate').value || null) : null
    };

    // Validation
    if (!taskData.title) {
        showToast('Please enter a task title', 'error');
        return;
    }

    try {
        const url = isEdit ? `/api/tasks/${taskId}` : '/api/tasks';
        const method = isEdit ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });

        const result = await response.json();

        if (response.ok) {
            showToast(isEdit ? 'Task updated successfully' : 'Task created successfully', 'success');
            hideTaskModal();
            loadTasks(); // Refresh tasks
        } else {
            throw new Error(result.error || 'Failed to save task');
        }
    } catch (error) {
        console.error('Error saving task:', error);
        showToast('Error saving task: ' + error.message, 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok) {
            showToast('Task deleted successfully', 'success');
            loadTasks(); // Refresh tasks
        } else {
            throw new Error(result.error || 'Failed to delete task');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showToast('Error deleting task: ' + error.message, 'error');
    }
}

async function toggleTaskStatus(taskId) {
    const task = currentTasks.find(t => t.id === taskId);
    if (!task) return;

    const newStatus = task.status === 'completed' ? 'pending' : 'completed';

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });

        const result = await response.json();

        if (response.ok) {
            showToast(`Task marked as ${newStatus}`, 'success');
            loadTasks(); // Refresh tasks
        } else {
            throw new Error(result.error || 'Failed to update task status');
        }
    } catch (error) {
        console.error('Error updating task status:', error);
        showToast('Error updating task status: ' + error.message, 'error');
    }
}

// UI Helper Functions
function showAddTaskModal() {
    clearTaskForm();
    document.getElementById('taskModalTitle').innerHTML = '<i class="bi bi-plus-circle"></i> Add New Task';
    const taskModal = new bootstrap.Modal(document.getElementById('taskModal'));
    taskModal.show();
}

function editTask(taskId) {
    const task = currentTasks.find(t => t.id === taskId);
    if (!task) return;

    // Populate form with task data
    document.getElementById('taskId').value = task.id;
    document.getElementById('taskTitle').value = task.title;
    document.getElementById('taskDescription').value = task.description || '';
    document.getElementById('taskCategory').value = task.category_id || '';
    document.getElementById('taskPriority').value = task.priority_id || 2;
    document.getElementById('taskDueDate').value = task.due_date || '';
    document.getElementById('taskDueTime').value = task.due_time || '';
    document.getElementById('taskDuration').value = task.estimated_duration || '';
    document.getElementById('taskStatus').value = task.status;
    document.getElementById('taskIsRecurring').checked = task.is_recurring || false;
    document.getElementById('taskRecurrencePattern').value = task.recurrence_pattern || 'daily';
    document.getElementById('taskRecurrenceInterval').value = task.recurrence_interval || 1;
    document.getElementById('taskRecurrenceEndDate').value = task.recurrence_end_date || '';
    toggleRecurringOptions(); // Show/hide recurring options based on checkbox

    document.getElementById('taskModalTitle').innerHTML = '<i class="bi bi-pencil"></i> Edit Task';
    const taskModal = new bootstrap.Modal(document.getElementById('taskModal'));
    taskModal.show();
}

function clearTaskForm() {
    document.getElementById('taskId').value = '';
    document.getElementById('taskTitle').value = '';
    document.getElementById('taskDescription').value = '';
    document.getElementById('taskCategory').value = '';
    document.getElementById('taskPriority').value = '2';
    document.getElementById('taskDueDate').value = '';
    document.getElementById('taskDueTime').value = '';
    document.getElementById('taskDuration').value = '';
    document.getElementById('taskStatus').value = 'pending';
    document.getElementById('taskIsRecurring').checked = false;
    document.getElementById('taskRecurrencePattern').value = 'daily';
    document.getElementById('taskRecurrenceInterval').value = '1';
    document.getElementById('taskRecurrenceEndDate').value = '';
    toggleRecurringOptions(); // Hide recurring options
}

function hideTaskModal() {
    const taskModal = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
    if (taskModal) {
        taskModal.hide();
    }
}

// Search Functions
async function handleGlobalSearch() {
    const query = document.getElementById('globalSearch').value.trim();

    if (query.length < 2) {
        return;
    }

    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (response.ok) {
            showSearchResults(data.results, query);
        } else {
            throw new Error(data.error || 'Search failed');
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search error: ' + error.message, 'error');
    }
}

function showSearchResults(results, query) {
    const modal = new bootstrap.Modal(document.getElementById('searchModal'));
    const resultsContainer = document.getElementById('searchResults');

    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-search display-4 text-muted"></i>
                <h5 class="mt-3 text-muted">No results found</h5>
                <p class="text-muted">Try different keywords or check your spelling.</p>
            </div>
        `;
    } else {
        resultsContainer.innerHTML = `
            <div class="mb-3">
                <small class="text-muted">Found ${results.length} results for "${query}"</small>
            </div>
            ${results.map(result => `
                <div class="search-result-item" data-type="${result.type}" data-id="${result.id}">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="search-result-type text-primary">${result.type}</div>
                            <h6 class="mb-1">${escapeHtml(result.title)}</h6>
                            ${result.description ? `<p class="mb-0 small text-muted text-truncate-2">${escapeHtml(result.description)}</p>` : ''}
                        </div>
                        <div class="ms-2">
                            ${result.status ? `<span class="badge status-${result.status}">${formatStatus(result.status)}</span>` : ''}
                        </div>
                    </div>
                </div>
            `).join('')}
        `;

        // Add click handlers to search results
        document.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', function() {
                const type = this.dataset.type;
                const id = this.dataset.id;

                if (type === 'task') {
                    modal.hide();
                    editTask(parseInt(id));
                }
                // Add handlers for other types as needed
            });
        });
    }

    modal.show();
}

// Filter Functions
function applyFilters() {
    currentFilters.status = document.getElementById('statusFilter').value;
    currentFilters.category = document.getElementById('categoryFilter').value;
    currentFilters.priority = document.getElementById('priorityFilter').value;

    renderTasks(currentTasks);
}

function applyCurrentFilters(tasks) {
    return tasks.filter(task => {
        if (currentFilters.status && task.status !== currentFilters.status) return false;
        if (currentFilters.category && task.category_id != currentFilters.category) return false;
        if (currentFilters.priority && task.priority_id != currentFilters.priority) return false;
        return true;
    });
}

function clearAllFilters() {
    document.getElementById('statusFilter').value = '';
    document.getElementById('categoryFilter').value = '';
    document.getElementById('priorityFilter').value = '';

    currentFilters = { status: '', category: '', priority: '' };
    renderTasks(currentTasks);
}

function populateCategoryFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const taskCategory = document.getElementById('taskCategory');

    if (categoryFilter) {
        categoryFilter.innerHTML = '<option value="">All Categories</option>' +
            currentCategories.map(cat => `<option value="${cat.id}">${escapeHtml(cat.name)}</option>`).join('');
    }

    if (taskCategory) {
        taskCategory.innerHTML = '<option value="">Select Category</option>' +
            currentCategories.map(cat => `<option value="${cat.id}">${escapeHtml(cat.name)}</option>`).join('');
    }
}

// Analytics Functions
function updateQuickStats() {
    const totalTasks = currentTasks.length;
    const completedTasks = currentTasks.filter(t => t.status === 'completed').length;
    const pendingTasks = currentTasks.filter(t => t.status === 'pending').length;
    const today = new Date().toISOString().split('T')[0];
    const overdueTasks = currentTasks.filter(t =>
        t.due_date && t.due_date < today && t.status !== 'completed'
    ).length;

    const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    // Update elements if they exist
    const elements = {
        'totalTasks': totalTasks,
        'completedTasks': completedTasks,
        'pendingTasks': pendingTasks,
        'overdueTasks': overdueTasks,
        'completionRate': completionRate + '%'
    };

    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    });

    // Update progress bar
    const progressBar = document.getElementById('completionProgress');
    if (progressBar) {
        progressBar.style.width = completionRate + '%';
        progressBar.setAttribute('aria-valuenow', completionRate);
    }
}

function updateAnalyticsDisplay(data) {
    // Update dashboard metrics if on dashboard page
    const dashElements = {
        'dashTotalTasks': data.total_tasks,
        'dashCompletedTasks': data.completed_tasks,
        'dashPendingTasks': data.pending_tasks,
        'dashCompletionRate': data.completion_rate + '%'
    };

    Object.entries(dashElements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    });
}

// Theme Functions
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function setTheme(theme) {
    document.body.setAttribute('data-bs-theme', theme);
    localStorage.setItem('taskplanner-theme', theme);

    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    }
}

// Utility Functions
function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const container = document.getElementById('tasksContainer');

    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }
    if (container) {
        container.style.display = show ? 'none' : 'block';
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('notificationToast');
    const toastMessage = document.getElementById('toastMessage');

    if (toast && toastMessage) {
        toastMessage.textContent = message;

        // Update toast styling based on type
        toast.className = `toast ${type === 'error' ? 'bg-danger text-white' : type === 'success' ? 'bg-success text-white' : ''}`;

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
}

function refreshData() {
    loadInitialData();
    showToast('Data refreshed', 'success');
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatStatus(status) {
    return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getPriorityClass(priorityId) {
    const priorityMap = {
        1: 'priority-low',
        2: 'priority-medium',
        3: 'priority-high',
        4: 'priority-critical'
    };
    return priorityMap[priorityId] || 'priority-medium';
}

function getPriorityName(priorityId) {
    const priorityMap = {
        1: 'Low',
        2: 'Medium',
        3: 'High',
        4: 'Critical'
    };
    return priorityMap[priorityId] || 'Medium';
}

function getCategoryName(categoryId) {
    if (!categoryId) return '';
    const category = currentCategories.find(c => c.id == categoryId);
    return category ? category.name : '';
}

// Pagination Functions
function renderPagination(totalItems) {
    const paginationContainer = document.getElementById('paginationContainer');
    if (!paginationContainer) return;

    if (totalItems === 0 || totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }

    const startItem = (currentPage - 1) * itemsPerPage + 1;
    const endItem = Math.min(currentPage * itemsPerPage, totalItems);

    let paginationHTML = `
        <div class="d-flex justify-content-between align-items-center mt-3">
            <div class="pagination-info">
                <small class="text-muted">
                    Showing ${startItem}-${endItem} of ${totalItems} tasks
                </small>
            </div>
            <div class="d-flex align-items-center gap-2">
                <div class="pagination-controls">
                    <select id="itemsPerPageSelect" class="form-select form-select-sm" style="width: auto;">
                        <option value="5" ${itemsPerPage === 5 ? 'selected' : ''}>5 per page</option>
                        <option value="10" ${itemsPerPage === 10 ? 'selected' : ''}>10 per page</option>
                        <option value="20" ${itemsPerPage === 20 ? 'selected' : ''}>20 per page</option>
                        <option value="50" ${itemsPerPage === 50 ? 'selected' : ''}>50 per page</option>
                    </select>
                </div>
                <nav aria-label="Task pagination">
                    <ul class="pagination pagination-sm mb-0">
                        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                            <a class="page-link" href="#" onclick="changePage(${currentPage - 1}); return false;">
                                <i class="bi bi-chevron-left"></i>
                            </a>
                        </li>
    `;

    // Page numbers
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i}); return false;">${i}</a>
            </li>
        `;
    }

    paginationHTML += `
                        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                            <a class="page-link" href="#" onclick="changePage(${currentPage + 1}); return false;">
                                <i class="bi bi-chevron-right"></i>
                            </a>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>
    `;

    paginationContainer.innerHTML = paginationHTML;

    // Re-attach event listener for items per page select
    const itemsPerPageSelect = document.getElementById('itemsPerPageSelect');
    if (itemsPerPageSelect) {
        itemsPerPageSelect.addEventListener('change', changeItemsPerPage);
    }
}

function changePage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    renderTasks(currentTasks);
}

function changeItemsPerPage() {
    const select = document.getElementById('itemsPerPageSelect');
    if (select) {
        itemsPerPage = parseInt(select.value);
        currentPage = 1; // Reset to first page
        renderTasks(currentTasks);
    }
}

// View Switching Functions
function switchView(view) {
    const listBtn = document.getElementById('listViewBtn');
    const gridBtn = document.getElementById('gridViewBtn');

    if (view === 'list') {
        listBtn?.classList.add('active');
        gridBtn?.classList.remove('active');
    } else {
        gridBtn?.classList.add('active');
        listBtn?.classList.remove('active');
    }

    renderTasks(currentTasks, view);
}

// Recurring Task Functions
function toggleRecurringOptions() {
    const isRecurring = document.getElementById('taskIsRecurring').checked;
    const recurringOptions = document.getElementById('recurringOptions');

    if (recurringOptions) {
        recurringOptions.style.display = isRecurring ? 'block' : 'none';
    }
}

// Export functions for global access
window.loadTasks = loadTasks;
window.loadCategories = loadCategories;
window.loadAnalytics = loadAnalytics;
window.renderTasks = renderTasks;
window.currentTasks = currentTasks;
window.changePage = changePage;
window.switchView = switchView;

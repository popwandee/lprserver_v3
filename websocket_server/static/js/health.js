class HealthTable {
    constructor() {
        this.currentPage = 1;
        this.perPage = 20;
        this.componentFilter = '';
        this.statusFilter = '';
        this.isLoading = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCurrentStatus();
        this.loadData();
    }

    bindEvents() {
        // Filter events
        document.getElementById('componentFilter').addEventListener('change', (e) => {
            this.componentFilter = e.target.value;
            this.currentPage = 1;
            this.loadData();
        });

        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.statusFilter = e.target.value;
            this.currentPage = 1;
            this.loadData();
        });

        document.getElementById('perPageSelect').addEventListener('change', (e) => {
            this.perPage = parseInt(e.target.value);
            this.currentPage = 1;
            this.loadData();
        });
    }

    async loadCurrentStatus() {
        try {
            const response = await fetch('/api/health_status');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateCurrentStatus(data.health_checks);
            }
        } catch (error) {
            console.error('Error loading current status:', error);
            this.showError('Failed to load current health status');
        }
    }

    updateCurrentStatus(healthChecks) {
        // Group checks by component and get latest status
        const componentStatus = {};
        
        healthChecks.forEach(check => {
            if (!componentStatus[check.component] || 
                new Date(check.timestamp) > new Date(componentStatus[check.component].timestamp)) {
                componentStatus[check.component] = check;
            }
        });

        // Update status cards
        this.updateStatusCard('overall', this.getOverallStatus(componentStatus));
        this.updateStatusCard('camera', componentStatus['Camera'] || { status: 'UNKNOWN', message: 'No data' });
        this.updateStatusCard('cpu', componentStatus['CPU & RAM'] || { status: 'UNKNOWN', message: 'No data' });
        this.updateStatusCard('disk', componentStatus['Disk Space'] || { status: 'UNKNOWN', message: 'No data' });
        this.updateStatusCard('network', componentStatus['Network Connectivity'] || { status: 'UNKNOWN', message: 'No data' });
        this.updateStatusCard('models', componentStatus['Detection Models'] || { status: 'UNKNOWN', message: 'No data' });
    }

    getOverallStatus(componentStatus) {
        const components = Object.values(componentStatus);
        const failed = components.filter(c => c.status === 'FAIL').length;
        const total = components.length;
        
        if (failed === 0) {
            return { status: 'PASS', message: 'All systems operational' };
        } else if (failed === total) {
            return { status: 'FAIL', message: 'All systems failed' };
        } else {
            return { status: 'WARNING', message: `${failed}/${total} components failed` };
        }
    }

    updateStatusCard(type, check) {
        const statusElement = document.getElementById(`${type}Status`);
        const iconElement = document.getElementById(`${type}StatusIcon`);
        
        if (statusElement && iconElement) {
            statusElement.textContent = this.formatStatusMessage(check.message);
            
            // Update icon and colors
            iconElement.className = 'status-icon';
            if (check.status === 'PASS') {
                iconElement.classList.add('pass');
            } else if (check.status === 'FAIL') {
                iconElement.classList.add('fail');
            } else if (check.status === 'WARNING') {
                iconElement.classList.add('warning');
            }
        }
    }

    formatStatusMessage(message) {
        // Clarify RAM usage meaning
        if (message.includes('RAM') && message.includes('%')) {
            return message.replace('RAM', 'RAM Usage') + ' (used)';
        }
        return message;
    }

    async loadData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.perPage,
                component: this.componentFilter,
                status: this.statusFilter
            });
            
            const response = await fetch(`/api/health_data?${params}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderTable(data);
                this.renderPagination(data);
                this.updateTableInfo(data);
            } else {
                this.showError(data.message || 'Failed to load health data');
            }
        } catch (error) {
            console.error('Error loading health data:', error);
            this.showError('Failed to load health data');
        } finally {
            this.isLoading = false;
        }
    }

    renderTable(data) {
        const tbody = document.getElementById('tableBody');
        
        if (data.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">No health data found</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.data.map(item => this.renderTableRow(item)).join('');
    }

    renderTableRow(item) {
        const statusClass = item.status === 'PASS' ? 'status-pass' : 'status-fail';
        const timestamp = new Date(item.timestamp).toLocaleString();
        
        return `
            <tr>
                <td>${item.id}</td>
                <td>${timestamp}</td>
                <td>${this.escapeHtml(item.component)}</td>
                <td class="${statusClass}">${item.status}</td>
                <td>${this.escapeHtml(this.formatStatusMessage(item.message))}</td>
            </tr>
        `;
    }

    renderPagination(data) {
        const container = document.getElementById('paginationContainer');
        
        if (data.total_pages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let pagination = '<div class="pagination">';
        
        // Previous button
        pagination += `<button onclick="healthTable.goToPage(${this.currentPage - 1})" 
                                ${this.currentPage === 1 ? 'disabled' : ''}>
                            Previous
                        </button>`;
        
        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(data.total_pages, this.currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            pagination += `<button onclick="healthTable.goToPage(${i})" 
                                   class="${i === this.currentPage ? 'active' : ''}">
                                ${i}
                            </button>`;
        }
        
        // Next button
        pagination += `<button onclick="healthTable.goToPage(${this.currentPage + 1})" 
                                ${this.currentPage === data.total_pages ? 'disabled' : ''}>
                            Next
                        </button>`;
        
        pagination += '</div>';
        container.innerHTML = pagination;
    }

    updateTableInfo(data) {
        const infoElement = document.getElementById('tableInfo');
        const start = (this.currentPage - 1) * this.perPage + 1;
        const end = Math.min(this.currentPage * this.perPage, data.total);
        
        infoElement.textContent = `Showing ${start} to ${end} of ${data.total} health checks`;
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadData();
    }

    clearFilters() {
        document.getElementById('componentFilter').value = '';
        document.getElementById('statusFilter').value = '';
        document.getElementById('perPageSelect').value = '20';
        
        this.componentFilter = '';
        this.statusFilter = '';
        this.perPage = 20;
        this.currentPage = 1;
        this.loadData();
    }

    showLoading() {
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Loading health data...</td></tr>';
    }

    showError(message) {
        const container = document.getElementById('alertContainer');
        container.innerHTML = `<div class="alert alert-error">${this.escapeHtml(message)}</div>`;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            container.innerHTML = '';
        }, 5000);
    }

    showSuccess(message) {
        const container = document.getElementById('alertContainer');
        container.innerHTML = `<div class="alert alert-success">${this.escapeHtml(message)}</div>`;
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            container.innerHTML = '';
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global function for clear filters button
function clearFilters() {
    if (healthTable) {
        healthTable.clearFilters();
    }
}

// Initialize health table when page loads
let healthTable;
document.addEventListener('DOMContentLoaded', function() {
    healthTable = new HealthTable();
    
    // Auto-refresh current status every 30 seconds
    setInterval(() => {
        healthTable.loadCurrentStatus();
    }, 30000);
}); 
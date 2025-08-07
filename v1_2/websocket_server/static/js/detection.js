// Detection Template JavaScript
class DetectionTable {
    constructor() {
        this.currentPage = 1;
        this.perPage = 10;
        this.sortBy = 'timestamp';
        this.sortOrder = 'desc';
        this.searchTerm = '';
        this.dateFrom = '';
        this.dateTo = '';
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadStats();
        this.loadData();
    }
    
    bindEvents() {
        // Search and filter events
        document.getElementById('searchInput')?.addEventListener('input', (e) => {
            this.searchTerm = e.target.value;
            this.debounce(() => this.loadData(), 500);
        });
        
        document.getElementById('dateFrom')?.addEventListener('change', (e) => {
            this.dateFrom = e.target.value;
            this.loadData();
        });
        
        document.getElementById('dateTo')?.addEventListener('change', (e) => {
            this.dateTo = e.target.value;
            this.loadData();
        });
        
        document.getElementById('perPageSelect')?.addEventListener('change', (e) => {
            this.perPage = parseInt(e.target.value);
            this.currentPage = 1;
            this.loadData();
        });
        
        // Clear filters
        document.getElementById('clearFilters')?.addEventListener('click', () => {
            this.clearFilters();
        });
        
        // Export data
        document.getElementById('exportData')?.addEventListener('click', () => {
            this.exportData();
        });
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/detection_stats');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateStats(data.stats);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    updateStats(stats) {
        const statsContainer = document.getElementById('statsContainer');
        if (!statsContainer) return;
        
        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-number">${stats.total_detections || 0}</div>
                <div class="stat-label">Total Detections</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.today_detections || 0}</div>
                <div class="stat-label">Today's Detections</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.avg_confidence || 0}%</div>
                <div class="stat-label">Avg Confidence</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.top_plates?.length || 0}</div>
                <div class="stat-label">Unique Plates</div>
            </div>
        `;
    }
    
    async loadData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.perPage,
                sort_by: this.sortBy,
                sort_order: this.sortOrder,
                search: this.searchTerm,
                date_from: this.dateFrom,
                date_to: this.dateTo
            });
            
            const response = await fetch(`/api/detection_data?${params}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderTable(data);
            } else {
                this.showError(data.message || 'Failed to load data');
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Network error occurred');
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    renderTable(data) {
        const tableBody = document.getElementById('tableBody');
        const paginationContainer = document.getElementById('paginationContainer');
        
        if (!tableBody || !paginationContainer) return;
        
        // Render table rows
        if (data.data.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="empty-state">
                        <i>📷</i>
                        <h3>No detections found</h3>
                        <p>Try adjusting your search criteria or filters</p>
                    </td>
                </tr>
            `;
        } else {
            tableBody.innerHTML = data.data.map(item => this.renderTableRow(item)).join('');
        }
        
        // Render pagination
        this.renderPagination(data);
        
        // Update table info
        this.updateTableInfo(data);
        
        // Bind table events
        this.bindTableEvents();
    }
    
    renderTableRow(item) {
        const confidenceClass = item.lp_confidence >= 80 ? 'badge-success' : 
                               item.lp_confidence >= 60 ? 'badge-warning' : 'badge-danger';
        
        return `
            <tr data-id="${item.id}">
                <td>
                    ${item.license_plate_text || '<span class="text-muted">N/A</span>'}
                </td>
                <td>
                    <span class="badge ${confidenceClass}">${item.lp_confidence || 0}%</span>
                </td>
                <td>${this.formatDateTime(item.timestamp)}</td>
                <td>${item.exposure_time || 'N/A'}</td>
                <td>${item.analog_gain || 'N/A'}</td>
                <td>${item.lux || 'N/A'}</td>
                <td>
                    ${item.lp_image_filename ? 
                        `<img src="/static/images/${item.lp_image_filename}" class="image-preview" 
                              onclick="detectionTable.showImageModal('/static/images/${item.lp_image_filename}')" 
                              alt="License Plate">` : 
                        '<span class="text-muted">No image</span>'
                    }
                </td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-secondary btn-sm" onclick="detectionTable.viewDetails(${item.id})">
                            View
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="detectionTable.downloadImage('${item.lp_image_filename}')">
                            Download
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }
    
    renderPagination(data) {
        const paginationContainer = document.getElementById('paginationContainer');
        if (!paginationContainer) return;
        
        const totalPages = data.total_pages;
        const currentPage = data.page;
        
        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }
        
        let paginationHTML = '<div class="pagination">';
        
        // Previous button
        paginationHTML += `
            <button class="btn btn-secondary" 
                    onclick="detectionTable.goToPage(${currentPage - 1})"
                    ${currentPage <= 1 ? 'disabled' : ''}>
                Previous
            </button>
        `;
        
        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <button class="btn ${i === currentPage ? 'active' : 'btn-secondary'}" 
                        onclick="detectionTable.goToPage(${i})">
                    ${i}
                </button>
            `;
        }
        
        // Next button
        paginationHTML += `
            <button class="btn btn-secondary" 
                    onclick="detectionTable.goToPage(${currentPage + 1})"
                    ${currentPage >= totalPages ? 'disabled' : ''}>
                Next
            </button>
        `;
        
        paginationHTML += '</div>';
        paginationContainer.innerHTML = paginationHTML;
    }
    
    updateTableInfo(data) {
        const tableInfo = document.getElementById('tableInfo');
        if (!tableInfo) return;
        
        const start = (data.page - 1) * data.per_page + 1;
        const end = Math.min(data.page * data.per_page, data.total);
        
        tableInfo.textContent = `Showing ${start} to ${end} of ${data.total} detections`;
    }
    
    bindTableEvents() {
        // Sortable headers
        document.querySelectorAll('.detection-table th.sortable').forEach(header => {
            header.addEventListener('click', () => {
                const field = header.dataset.field;
                if (this.sortBy === field) {
                    this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
                } else {
                    this.sortBy = field;
                    this.sortOrder = 'asc';
                }
                this.updateSortIndicators();
                this.loadData();
            });
        });
    }
    
    updateSortIndicators() {
        document.querySelectorAll('.detection-table th.sortable').forEach(header => {
            header.classList.remove('asc', 'desc');
            if (header.dataset.field === this.sortBy) {
                header.classList.add(this.sortOrder);
            }
        });
    }
    
    goToPage(page) {
        this.currentPage = page;
        this.loadData();
    }
    
    clearFilters() {
        this.searchTerm = '';
        this.dateFrom = '';
        this.dateTo = '';
        this.currentPage = 1;
        
        // Reset form inputs
        document.getElementById('searchInput').value = '';
        document.getElementById('dateFrom').value = '';
        document.getElementById('dateTo').value = '';
        
        this.loadData();
    }
    
    async exportData() {
        try {
            const params = new URLSearchParams({
                sort_by: this.sortBy,
                sort_order: this.sortOrder,
                search: this.searchTerm,
                date_from: this.dateFrom,
                date_to: this.dateTo
            });
            
            const response = await fetch(`/api/export_detection_data?${params}`);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `detection_data_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showSuccess('Data exported successfully');
        } catch (error) {
            console.error('Error exporting data:', error);
            this.showError('Failed to export data');
        }
    }
    
    showImageModal(imageSrc) {
        const modal = document.getElementById('imageModal');
        const modalImg = document.getElementById('modalImage');
        
        if (modal && modalImg) {
            modalImg.src = imageSrc;
            modal.style.display = 'block';
        }
    }
    
    closeImageModal() {
        const modal = document.getElementById('imageModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    viewDetails(id) {
        // Navigate to detection detail page
        window.location.href = `/detection/${id}`;
    }
    
    downloadImage(filename) {
        if (!filename) return;
        
        // Use the download endpoint for better security
        const link = document.createElement('a');
        link.href = `/download/${filename}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    showLoading() {
        const tableBody = document.getElementById('tableBody');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="loading">
                        <div class="spinner"></div>
                        <p>Loading detections...</p>
                    </td>
                </tr>
            `;
        }
    }
    
    hideLoading() {
        // Loading state is handled by renderTable
    }
    
    showError(message) {
        const alertContainer = document.getElementById('alertContainer');
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error:</strong> ${message}
                    <button type="button" class="close" onclick="this.parentElement.remove()">&times;</button>
                </div>
            `;
        }
    }
    
    showSuccess(message) {
        const alertContainer = document.getElementById('alertContainer');
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="alert alert-success">
                    <strong>Success:</strong> ${message}
                    <button type="button" class="close" onclick="this.parentElement.remove()">&times;</button>
                </div>
            `;
        }
    }
    
    formatDateTime(timestamp) {
        if (!timestamp) return 'N/A';
        
        const date = new Date(timestamp);
        return date.toLocaleString();
    }
    
    debounce(func, wait) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(func, wait);
    }
}

// Initialize the detection table when DOM is loaded
let detectionTable;

document.addEventListener('DOMContentLoaded', function() {
    detectionTable = new DetectionTable();
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('imageModal');
        if (event.target === modal) {
            detectionTable.closeImageModal();
        }
    });
    
    // Close modal with escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            detectionTable.closeImageModal();
        }
    });
});

// Global functions for HTML onclick handlers
function closeImageModal() {
    if (detectionTable) {
        detectionTable.closeImageModal();
    }
} 
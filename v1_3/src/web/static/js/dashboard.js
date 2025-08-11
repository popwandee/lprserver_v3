/**
 * AI Camera v1.3 - Dashboard JavaScript
 * Main dashboard specific functionality
 */

// Dashboard state management
const DashboardManager = {
    statusUpdateInterval: null,
    
    /**
     * Initialize dashboard
     */
    init: function() {
        // Add initial log message
        AICameraUtils.addLogMessage('main-system-log', 'AI Camera Dashboard initialized', 'success');
        AICameraUtils.addLogMessage('main-system-log', 'Loading system status...', 'info');
        
        this.setupWebSocket();
        this.setupStatusUpdates();
        this.loadInitialStatus();
        
        // Test camera elements after a short delay
        setTimeout(() => {
            console.log('Testing camera elements...');
            const featureResolutionElement = document.getElementById('feature-camera-resolution');
            const featureFpsElement = document.getElementById('feature-camera-fps');
            const featureModelElement = document.getElementById('feature-camera-model');
            const aiAcceleratorElement = document.getElementById('system-info-ai-accelerator');
            
            console.log('Camera elements found:', {
                resolution: featureResolutionElement,
                fps: featureFpsElement,
                model: featureModelElement,
                aiAccelerator: aiAcceleratorElement
            });
            
            if (featureResolutionElement) featureResolutionElement.textContent = 'Test Resolution';
            if (featureFpsElement) featureFpsElement.textContent = 'Test FPS';
            if (featureModelElement) featureModelElement.textContent = 'Test Model';
            if (aiAcceleratorElement) aiAcceleratorElement.textContent = 'Test AI Accelerator';
        }, 1000);
        
        console.log('Dashboard Manager initialized');
    },

    /**
     * Setup WebSocket connection for real-time updates
     */
    setupWebSocket: function() {
        if (typeof io !== 'undefined') {
            WebSocketManager.init();
            if (WebSocketManager.socket) {
                WebSocketManager.socket.on('camera_status_update', (status) => {
                    this.updateCameraStatus(status);
                });
                
                WebSocketManager.socket.on('detection_status_update', (status) => {
                    this.updateDetectionStatus(status);
                });
            }
        }
    },

    /**
     * Setup periodic status updates
     */
    setupStatusUpdates: function() {
        // Update status immediately
        this.updateSystemStatus();
        
        // Setup periodic updates every 5 seconds
        this.statusUpdateInterval = setInterval(() => {
            this.updateSystemStatus();
        }, 5000);
    },

    /**
     * Load initial system status
     */
    loadInitialStatus: function() {
        // Set initial loading states
        const elements = [
            'main-system-uptime', 'feature-camera-status',
            'feature-camera-model', 'feature-camera-resolution', 'feature-camera-fps',
            'system-info-cpu', 'system-info-ram', 'system-info-disk', 'system-info-os', 'system-info-ai-accelerator'
        ];
        
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element && element.textContent === 'Loading...') {
                element.textContent = 'Loading...';
            }
        });
        
        this.updateSystemStatus();
    },

    /**
     * Update system status
     */
    updateSystemStatus: function() {
        AICameraUtils.addLogMessage('main-system-log', 'Updating system status...', 'info');
        
        // Update camera status
        console.log('Making camera status API request...');
        AICameraUtils.apiRequest('/camera/status')
            .then(data => {
                console.log('Camera status API response:', data);
                if (data && data.success) {
                    this.updateCameraStatus(data.status);
                } else {
                    this.updateCameraStatus(null);
                }
            })
            .catch(error => {
                console.error('Camera API request failed:', error);
                console.warn('Camera status not available:', error.message);
                // Set default offline status with proper structure
                this.updateCameraStatus({
                    streaming: false, 
                    initialized: false,
                    config: null,
                    camera_handler: null,
                    uptime: 0
                });
                AICameraUtils.addLogMessage('main-system-log', 'Failed to get camera status: ' + error.message, 'error');
            });

        // Update detection status
        AICameraUtils.apiRequest('/detection/status')
            .then(data => {
                if (data && data.success) {
                    this.updateDetectionStatus(data.status);
                }
            })
            .catch(error => {
                console.warn('Detection status not available:', error.message);
                // Set default inactive status
                this.updateDetectionStatus({service_running: false});
                AICameraUtils.addLogMessage('main-system-log', 'Failed to get detection status: ' + error.message, 'error');
            });

        // Update system health
        AICameraUtils.apiRequest('/health/system')
            .then(data => {
                if (data && data.success) {
                    this.updateSystemHealth(data);
                    this.updateSystemInfo(data);
                }
            })
            .catch(error => {
                console.warn('Health status not available:', error.message);
                // Set default healthy status
                this.updateSystemHealth({data: {overall_status: 'unknown', components: {}}});
                AICameraUtils.addLogMessage('main-system-log', 'Failed to get system health: ' + error.message, 'error');
            });

        // Update WebSocket sender status
        this.updateServerStatus();
    },

    /**
     * Update camera status display
     */
    updateCameraStatus: function(status) {
        console.log('updateCameraStatus called with:', status);
        
        let cameraOnline = false;
        let statusText = 'Offline';

        if (status && status.streaming) {
            cameraOnline = true;
            statusText = 'Online';
            AICameraUtils.addLogMessage('main-system-log', 'Camera is streaming', 'success');
        } else if (status && status.initialized) {
            statusText = 'Ready';
            AICameraUtils.addLogMessage('main-system-log', 'Camera initialized but not streaming', 'info');
        } else {
            AICameraUtils.addLogMessage('main-system-log', 'Camera not available', 'warning');
        }

        AICameraUtils.updateStatusIndicator('main-camera-status', cameraOnline, statusText);

        // Feature section elements (duplicate IDs fixed)
        const featureResolutionElement = document.getElementById('feature-camera-resolution');
        const featureFpsElement = document.getElementById('feature-camera-fps');
        const featureModelElement = document.getElementById('feature-camera-model');
        
        console.log('Found elements:', {
            resolution: featureResolutionElement,
            fps: featureFpsElement,
            model: featureModelElement
        });
        
        // Get resolution from camera_handler.current_config.main.size or config
        let resolution = null;
        
        console.log('Camera handler config:', status?.camera_handler?.current_config);
        
        // Try to get from current_config first (most accurate)
        if (status && status.camera_handler && status.camera_handler.current_config && status.camera_handler.current_config.main && status.camera_handler.current_config.main.size) {
            const size = status.camera_handler.current_config.main.size;
            resolution = `${size[0]}x${size[1]}`;
            console.log('Resolution from current_config:', resolution);
        }
        // Fallback to config object
        else if (status && status.config && status.config.resolution) {
            resolution = `${status.config.resolution[0]}x${status.config.resolution[1]}`;
            console.log('Resolution from config:', resolution);
        }
        
        // Update feature section
        if (featureResolutionElement) {
            featureResolutionElement.textContent = resolution || 'Unknown';
            console.log('Updated resolution element with:', resolution || 'Unknown');
        }

        // Get FPS from camera_handler.current_config.controls.FrameDurationLimits or config
        let fps = null;
        
        console.log('Camera controls:', status?.camera_handler?.current_config?.controls);
        
        // Try to get from current_config first (most accurate)
        if (status && status.camera_handler && status.camera_handler.current_config && status.camera_handler.current_config.controls && status.camera_handler.current_config.controls.FrameDurationLimits) {
            const frameDuration = status.camera_handler.current_config.controls.FrameDurationLimits[0];
            fps = `${Math.round(1000000 / frameDuration)} FPS`; // Convert microseconds to FPS
            console.log('FPS from current_config:', fps);
        }
        // Fallback to config object
        else if (status && status.config && status.config.framerate) {
            fps = `${status.config.framerate} FPS`;
            console.log('FPS from config:', fps);
        }
        
        // Update feature section
        if (featureFpsElement) {
            featureFpsElement.textContent = fps || 'Unknown';
            console.log('Updated FPS element with:', fps || 'Unknown');
        }

        // Update camera model with fallback
        const cameraModel = (status && status.camera_handler && status.camera_handler.camera_properties && status.camera_handler.camera_properties.Model) || 'Unknown';
        
        console.log('Camera model:', cameraModel);
        
        // Update feature section
        if (featureModelElement) {
            featureModelElement.textContent = cameraModel;
            console.log('Updated model element with:', cameraModel);
        }



        // Update uptime with fallback
        const uptimeElement = document.getElementById('main-system-uptime');
        if (uptimeElement) {
            if (status && status.uptime) {
                uptimeElement.textContent = AICameraUtils.formatDuration(status.uptime);
            } else {
                uptimeElement.textContent = 'Unknown';
            }
        }

        // Update feature status (duplicate element in features section)
        const featureStatusElement = document.getElementById('feature-camera-status');
        if (featureStatusElement) {
            if (status && status.streaming) {
                featureStatusElement.textContent = 'Streaming';
            } else if (status && status.initialized) {
                featureStatusElement.textContent = 'Initialized';
            } else {
                featureStatusElement.textContent = 'Not initialized';
            }
        }
    },

    /**
     * Update detection status display
     */
    updateDetectionStatus: function(status) {
        const detectionActive = status && status.service_running || false;
        AICameraUtils.updateStatusIndicator('main-detection-status', detectionActive, 
            detectionActive ? 'Active' : 'Inactive');
        
        // Add log message for detection status
        if (detectionActive) {
            AICameraUtils.addLogMessage('main-system-log', 'AI Detection service is running', 'success');
        } else {
            AICameraUtils.addLogMessage('main-system-log', 'AI Detection service is stopped', 'info');
        }
    },

    /**
     * Update system health display
     */
    updateSystemHealth: function(healthData) {
        console.log('Updating system health with data:', healthData);
        
        // Extract health data from new format
        const health = healthData.data || healthData;
        const overallStatus = health.overall_status || 'unknown';
        const components = health.components || {};
        
        // Determine system health based on overall status
        const systemHealthy = overallStatus === 'healthy';
        const systemStatusText = overallStatus.charAt(0).toUpperCase() + overallStatus.slice(1);
        
        AICameraUtils.updateStatusIndicator('main-system-status', systemHealthy, systemStatusText);

        // Database status from components
        const databaseComponent = components.database || {};
        const databaseHealthy = databaseComponent.status === 'healthy';
        const databaseStatusText = databaseComponent.status ? 
            databaseComponent.status.charAt(0).toUpperCase() + databaseComponent.status.slice(1) : 
            'Unknown';
            
        AICameraUtils.updateStatusIndicator('main-database-status', databaseHealthy, databaseStatusText);
        
        // Log system health status
        if (overallStatus === 'healthy') {
            AICameraUtils.addLogMessage('main-system-log', 'System health: ' + systemStatusText, 'success');
        } else {
            AICameraUtils.addLogMessage('main-system-log', 'System health: ' + systemStatusText, 'warning');
        }
    },

    /**
     * Update system information display
     */
    updateSystemInfo: function(healthData) {
        console.log('Updating system info with data:', healthData);
        
        // Extract system info from health data
        const health = healthData.data || healthData;
        const systemInfo = health.system || {};
        console.log('Extracted systemInfo:', systemInfo);
        
        // Update CPU architecture information
        const cpuElement = document.getElementById('system-info-cpu');
        if (cpuElement && systemInfo.cpu_info) {
            const cpuInfo = systemInfo.cpu_info;
            let cpuText = 'Unknown';
            
            if (cpuInfo.model && cpuInfo.model !== 'Unknown') {
                // For Raspberry Pi, show model and architecture
                if (cpuInfo.model.includes('Raspberry Pi')) {
                    cpuText = `${cpuInfo.model} ${cpuInfo.architecture}`;
                } else {
                    cpuText = `${cpuInfo.model} ${cpuInfo.architecture}`;
                }
            } else if (cpuInfo.architecture) {
                cpuText = cpuInfo.architecture;
            }
            
            cpuElement.textContent = cpuText;
        }
        
        // Update RAM information
        const ramElement = document.getElementById('system-info-ram');
        if (ramElement && systemInfo.memory_usage) {
            const totalGB = systemInfo.memory_usage.total;
            ramElement.textContent = `${totalGB} GB`;
        }
        
        // Update disk information
        const diskElement = document.getElementById('system-info-disk');
        if (diskElement && systemInfo.disk_usage) {
            const totalGB = systemInfo.disk_usage.total;
            diskElement.textContent = `${totalGB} GB`;
        }
        
        // Update OS information
        const osElement = document.getElementById('system-info-os');
        if (osElement && systemInfo.os_info) {
            const osInfo = systemInfo.os_info;
            let osText = 'Unknown';
            
            if (osInfo.distribution && osInfo.distribution !== 'Unknown') {
                // Show distribution name and kernel version
                if (osInfo.kernel_version && osInfo.kernel_version !== 'Unknown') {
                    osText = `${osInfo.distribution} (Kernel ${osInfo.kernel_version})`;
                } else {
                    osText = osInfo.distribution;
                }
            } else if (osInfo.name && osInfo.release) {
                osText = `${osInfo.name} ${osInfo.release}`;
            } else if (osInfo.name) {
                osText = osInfo.name;
            }
            
            osElement.textContent = osText;
        }
        
        // Update AI Accelerator information
        const aiAcceleratorElement = document.getElementById('system-info-ai-accelerator');
        console.log('AI Accelerator element found:', aiAcceleratorElement);
        console.log('AI Accelerator info in systemInfo:', systemInfo.ai_accelerator_info);
        
        if (aiAcceleratorElement && systemInfo.ai_accelerator_info) {
            const aiInfo = systemInfo.ai_accelerator_info;
            console.log('AI Info object:', aiInfo);
            let aiText = 'Unknown';
            
            if (aiInfo.device_architecture && aiInfo.device_architecture !== 'Unknown' && 
                aiInfo.firmware_version && aiInfo.firmware_version !== 'Unknown') {
                aiText = `${aiInfo.device_architecture} (FW ${aiInfo.firmware_version})`;
            } else if (aiInfo.device_architecture && aiInfo.device_architecture !== 'Unknown') {
                aiText = aiInfo.device_architecture;
            } else if (aiInfo.board_name && aiInfo.board_name !== 'Unknown') {
                aiText = aiInfo.board_name;
            }
            
            console.log('Setting AI Accelerator text to:', aiText);
            aiAcceleratorElement.textContent = aiText;
        } else {
            console.log('AI Accelerator element or info not found');
        }
    },

    /**
     * Update server connection status
     */
    updateServerStatus: function() {
        // Get WebSocket sender status
        AICameraUtils.apiRequest('/websocket-sender/status')
            .then(data => {
                if (data && data.success) {
                    this.updateServerConnectionDisplay(data.status);
                } else {
                    this.updateServerConnectionDisplay(null);
                }
            })
            .catch(error => {
                console.warn('WebSocket sender status not available:', error.message);
                this.updateServerConnectionDisplay(null);
            });

        // Get server communication logs
        AICameraUtils.apiRequest('/websocket-sender/logs?limit=10')
            .then(data => {
                if (data && data.success) {
                    this.updateServerLogs(data.logs);
                }
            })
            .catch(error => {
                console.warn('WebSocket sender logs not available:', error.message);
            });
    },

    /**
     * Update server connection status display
     */
    updateServerConnectionDisplay: function(status) {
        let connected = false;
        let connectionText = 'Disconnected';
        let dataActive = false;
        let dataText = 'Inactive';
        let lastSync = 'Never';

        if (status) {
            // Server connection status
            if (status.connected) {
                connected = true;
                connectionText = 'Connected';
            }

            // Data sending status
            if (status.running && (status.detection_thread_alive || status.health_thread_alive)) {
                dataActive = true;
                dataText = 'Active';
            }

            // Last sync time
            if (status.last_detection_check || status.last_health_check) {
                const lastDetectionCheck = status.last_detection_check ? new Date(status.last_detection_check) : null;
                const lastHealthCheck = status.last_health_check ? new Date(status.last_health_check) : null;
                
                let latestSync = null;
                if (lastDetectionCheck && lastHealthCheck) {
                    latestSync = lastDetectionCheck > lastHealthCheck ? lastDetectionCheck : lastHealthCheck;
                } else if (lastDetectionCheck) {
                    latestSync = lastDetectionCheck;
                } else if (lastHealthCheck) {
                    latestSync = lastHealthCheck;
                }
                
                if (latestSync) {
                    lastSync = latestSync.toLocaleString();
                }
            }
        }

        // Update UI elements
        AICameraUtils.updateStatusIndicator('main-server-connection-status', connected, connectionText);
        AICameraUtils.updateStatusIndicator('main-data-sending-status', dataActive, dataText);
        
        const lastSyncElement = document.getElementById('main-last-sync-time');
        if (lastSyncElement) {
            lastSyncElement.textContent = lastSync;
        }
    },

    /**
     * Update server communication logs display
     */
    updateServerLogs: function(logs) {
        const logsContainer = document.getElementById('main-server-logs');
        if (!logsContainer) return;

        // Clear existing logs
        logsContainer.innerHTML = '';

        if (!logs || logs.length === 0) {
            logsContainer.innerHTML = '<div class="text-muted p-3">No server communication logs available</div>';
            return;
        }

        // Add logs
        logs.forEach(log => {
            const logElement = document.createElement('div');
            logElement.className = 'log-entry p-2 border-bottom';
            
            // Determine log type class
            let logClass = 'text-muted';
            if (log.status === 'success') {
                logClass = 'text-success';
            } else if (log.status === 'failed') {
                logClass = 'text-danger';
            } else if (log.status === 'no_data') {
                logClass = 'text-info';
            }

            // Format message
            let message = '';
            if (log.status === 'no_data') {
                message = `${log.timestamp}: no data to send`;
            } else if (log.status === 'success' && log.action === 'send_detection') {
                message = `${log.timestamp}: send lpr detection completed (${log.record_count} records)`;
            } else if (log.status === 'success' && log.action === 'send_health') {
                message = `${log.timestamp}: send health status completed (${log.record_count} records)`;
            } else {
                message = `${log.timestamp}: ${log.message || log.action}`;
            }

            logElement.innerHTML = `<small class="${logClass}">${message}</small>`;
            logsContainer.appendChild(logElement);
        });

        // Auto-scroll to bottom
        logsContainer.scrollTop = logsContainer.scrollHeight;
    },

    /**
     * Cleanup when leaving page
     */
    cleanup: function() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
        }
    }
};

// Quick action handlers
function handleQuickAction(action) {
    switch(action) {
        case 'camera-control':
            window.location.href = '/camera';
            break;
        case 'capture-image':
            captureImage();
            break;
        case 'system-health':
            window.location.href = '/health';
            break;
        case 'ai-detection':
            window.location.href = '/detection';
            break;
        default:
            console.warn('Unknown quick action:', action);
    }
}

/**
 * Capture image function
 */
function captureImage() {
    const button = event.target.closest('.quick-action-btn');
    const originalText = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i><br><strong>Capturing...</strong><br><small>Please wait</small>';
    button.disabled = true;

    AICameraUtils.apiRequest('/camera/capture', { method: 'POST' })
        .then(data => {
            if (data.success) {
                AICameraUtils.showToast('Image captured successfully!', 'success');
            } else {
                throw new Error(data.error || 'Capture failed');
            }
        })
        .catch(error => {
            AICameraUtils.showToast(`Capture failed: ${error.message}`, 'error');
        })
        .finally(() => {
            // Restore button state
            button.innerHTML = originalText;
            button.disabled = false;
        });
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard JavaScript: DOM loaded, initializing...');
    
    DashboardManager.init();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        DashboardManager.cleanup();
    });
    
    console.log('Dashboard JavaScript: Initialization complete');
});

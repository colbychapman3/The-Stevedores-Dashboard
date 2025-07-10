// Offline Storage Manager for Stevedores Dashboard
class OfflineStorageManager {
    constructor() {
        this.storageKeys = {
            ships: 'ships_data',
            analytics: 'analytics_data',
            settings: 'app_settings',
            lastSync: 'last_sync_time'
        };
        this.init();
    }

    init() {
        // Initialize storage if not exists
        if (!localStorage.getItem(this.storageKeys.ships)) {
            localStorage.setItem(this.storageKeys.ships, JSON.stringify([]));
        }
        if (!localStorage.getItem(this.storageKeys.analytics)) {
            localStorage.setItem(this.storageKeys.analytics, JSON.stringify({}));
        }
        if (!localStorage.getItem(this.storageKeys.settings)) {
            localStorage.setItem(this.storageKeys.settings, JSON.stringify({
                theme: 'light',
                autoRefresh: true,
                refreshInterval: 30000
            }));
        }
    }

    // Ship data management
    saveShips(ships) {
        localStorage.setItem(this.storageKeys.ships, JSON.stringify(ships));
        this.updateLastSync();
    }

    getShips() {
        const data = localStorage.getItem(this.storageKeys.ships);
        return data ? JSON.parse(data) : [];
    }

    addShip(ship) {
        const ships = this.getShips();
        ships.push(ship);
        this.saveShips(ships);
    }

    updateShip(shipId, updates) {
        const ships = this.getShips();
        const index = ships.findIndex(s => s.id === shipId);
        if (index !== -1) {
            ships[index] = { ...ships[index], ...updates };
            this.saveShips(ships);
        }
    }

    deleteShip(shipId) {
        const ships = this.getShips();
        const filteredShips = ships.filter(s => s.id !== shipId);
        this.saveShips(filteredShips);
    }

    // Analytics data management
    saveAnalytics(analytics) {
        localStorage.setItem(this.storageKeys.analytics, JSON.stringify(analytics));
        this.updateLastSync();
    }

    getAnalytics() {
        const data = localStorage.getItem(this.storageKeys.analytics);
        return data ? JSON.parse(data) : {};
    }

    // Settings management
    saveSettings(settings) {
        localStorage.setItem(this.storageKeys.settings, JSON.stringify(settings));
    }

    getSettings() {
        const data = localStorage.getItem(this.storageKeys.settings);
        return data ? JSON.parse(data) : {};
    }

    // Sync management
    updateLastSync() {
        localStorage.setItem(this.storageKeys.lastSync, new Date().toISOString());
    }

    getLastSync() {
        return localStorage.getItem(this.storageKeys.lastSync);
    }

    // Check if we're online
    isOnline() {
        return navigator.onLine;
    }

    // Queue operations for when we're back online
    queueOperation(operation) {
        const queue = this.getOperationQueue();
        queue.push({
            ...operation,
            timestamp: new Date().toISOString()
        });
        localStorage.setItem('operation_queue', JSON.stringify(queue));
    }

    getOperationQueue() {
        const data = localStorage.getItem('operation_queue');
        return data ? JSON.parse(data) : [];
    }

    clearOperationQueue() {
        localStorage.removeItem('operation_queue');
    }

    // Process queued operations when back online
    async processQueuedOperations() {
        if (!this.isOnline()) return;

        const queue = this.getOperationQueue();
        const processedOperations = [];

        for (const operation of queue) {
            try {
                const response = await fetch(operation.url, {
                    method: operation.method,
                    headers: {
                        'Content-Type': 'application/json',
                        ...operation.headers
                    },
                    body: operation.body ? JSON.stringify(operation.body) : null
                });

                if (response.ok) {
                    processedOperations.push(operation);
                }
            } catch (error) {
                console.error('Failed to process queued operation:', error);
            }
        }

        // Remove processed operations from queue
        const remainingQueue = queue.filter(op => !processedOperations.includes(op));
        localStorage.setItem('operation_queue', JSON.stringify(remainingQueue));

        return processedOperations;
    }

    // Enhanced API call with offline fallback
    async apiCall(url, options = {}) {
        try {
            const response = await fetch(url, options);
            
            if (response.ok) {
                const data = await response.json();
                
                // Cache successful responses
                if (url.includes('/api/ships') && options.method !== 'POST') {
                    this.saveShips(data);
                } else if (url.includes('/api/analytics')) {
                    this.saveAnalytics(data);
                }
                
                return data;
            }
            
            throw new Error(`HTTP ${response.status}`);
        } catch (error) {
            console.warn('API call failed, using cached data:', error);
            
            // Queue the operation for later if it's a write operation
            if (options.method && options.method !== 'GET') {
                this.queueOperation({
                    url,
                    method: options.method,
                    headers: options.headers,
                    body: options.body
                });
            }
            
            // Return cached data for read operations
            if (url.includes('/api/ships')) {
                return this.getShips();
            } else if (url.includes('/api/analytics')) {
                return this.getAnalytics();
            }
            
            throw error;
        }
    }

    // Export data for backup
    exportData() {
        return {
            ships: this.getShips(),
            analytics: this.getAnalytics(),
            settings: this.getSettings(),
            lastSync: this.getLastSync(),
            exportDate: new Date().toISOString()
        };
    }

    // Import data from backup
    importData(data) {
        if (data.ships) this.saveShips(data.ships);
        if (data.analytics) this.saveAnalytics(data.analytics);
        if (data.settings) this.saveSettings(data.settings);
    }

    // Clear all data
    clearAllData() {
        Object.values(this.storageKeys).forEach(key => {
            localStorage.removeItem(key);
        });
        localStorage.removeItem('operation_queue');
        this.init();
    }
}

// Initialize global storage manager
window.offlineStorage = new OfflineStorageManager();

// Handle online/offline events
window.addEventListener('online', async () => {
    console.log('Back online! Processing queued operations...');
    document.body.classList.remove('offline');
    
    try {
        const processed = await window.offlineStorage.processQueuedOperations();
        console.log(`Processed ${processed.length} queued operations`);
    } catch (error) {
        console.error('Error processing queued operations:', error);
    }
});

window.addEventListener('offline', () => {
    console.log('Gone offline! Switching to cached data...');
    document.body.classList.add('offline');
});

// Add offline indicator styles
const offlineStyles = `
    .offline-indicator {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #f59e0b;
        color: white;
        text-align: center;
        padding: 8px;
        font-size: 14px;
        z-index: 1000;
        transform: translateY(-100%);
        transition: transform 0.3s ease;
    }
    
    .offline .offline-indicator {
        transform: translateY(0);
    }
    
    .offline-data {
        border-left: 4px solid #f59e0b;
        background: #fef3c7;
        padding: 8px;
        margin: 8px 0;
        border-radius: 4px;
    }
`;

// Add styles to page
const styleSheet = document.createElement('style');
styleSheet.textContent = offlineStyles;
document.head.appendChild(styleSheet);

// Add offline indicator to body
const offlineIndicator = document.createElement('div');
offlineIndicator.className = 'offline-indicator';
offlineIndicator.innerHTML = '⚠️ You are currently offline. Some features may not be available.';
document.body.appendChild(offlineIndicator);
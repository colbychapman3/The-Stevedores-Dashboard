const CACHE_NAME = 'stevedore-dashboard-v1';
const OFFLINE_URL = '/offline';

// Critical resources for offline functionality
const CACHE_URLS = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/ship-status',
  '/berth-management', // Covers "berth-assignments"
  '/vessel-schedules',
  '/safety-protocols',
  '/emergency-contacts',
  '/tide-tables',
  OFFLINE_URL
];

// Install event - cache critical resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match(OFFLINE_URL))
    );
  } else {
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
  }
});

// Background sync for offline data
self.addEventListener('sync', event => {
  if (event.tag === 'ship-status-sync') {
    event.waitUntil(syncShipStatus());
  }
});

async function syncShipStatus() {
  // Sync offline ship status updates when connection returns
  const offlineData = await getOfflineData(); // This function needs to be defined
  for (const update of offlineData) {
    try {
      await fetch('/api/ship-status', {
        method: 'POST',
        body: JSON.stringify(update),
        headers: {'Content-Type': 'application/json'}
      });
      await removeOfflineData(update.id); // This function needs to be defined
    } catch (error) {
      console.log('Sync failed, will retry:', error);
    }
  }
}

const DB_NAME = 'StevedoreDB';
const DB_VERSION = 1;
const SHIP_UPDATES_STORE_NAME = 'shipUpdates';

// --- IndexedDB Helper Functions for Service Worker ---

function openStevedoreDB() {
  return new Promise((resolve, reject) => {
    const request = self.indexedDB.open(DB_NAME, DB_VERSION);
    request.onerror = event => {
      console.error('SW DB Error:', event.target.error);
      reject('Error opening DB in SW');
    };
    request.onsuccess = event => {
      resolve(event.target.result);
    };
    // onupgradeneeded is handled by the main app's OfflineStorage class,
    // but SW needs to be aware of the store.
    // If SW is activated before main app creates DB, this could be an issue.
    // However, typically main app runs first.
    request.onupgradeneeded = event => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(SHIP_UPDATES_STORE_NAME)) {
        db.createObjectStore(SHIP_UPDATES_STORE_NAME, { keyPath: 'id' });
        // Note: If 'id' is auto-incremented in main.js but not here, ensure consistency.
        // The current setup in main.js uses { keyPath: 'id' } and expects 'id' to be provided.
        // If main.js uses autoIncrement: true, then the keyPath here should match that behavior,
        // or this onupgradeneeded should ideally not run if main app already set up the DB.
      }
       // Add other stores if SW needs to interact with them, e.g., 'berthStatus'
       if (!db.objectStoreNames.contains('berthStatus')) {
        db.createObjectStore('berthStatus', { keyPath: 'id' });
      }
    };
  });
}

async function getOfflineData() {
  console.log('SW: Attempting to get offline data from IndexedDB.');
  try {
    const db = await openStevedoreDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([SHIP_UPDATES_STORE_NAME], 'readonly');
      const store = transaction.objectStore(SHIP_UPDATES_STORE_NAME);
      const request = store.getAll();
      request.onerror = event => {
        console.error('SW DB getAll error:', event.target.error);
        reject('Error fetching data in SW');
      };
      request.onsuccess = event => {
        console.log('SW: Successfully fetched offline data:', event.target.result);
        resolve(event.target.result);
      };
    });
  } catch (error) {
    console.error('SW: Error opening DB for getOfflineData:', error);
    return []; // Return empty array on error to prevent sync loop issues
  }
}

async function removeOfflineData(id) {
  console.log(`SW: Attempting to remove offline data with id: ${id}`);
  try {
    const db = await openStevedoreDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([SHIP_UPDATES_STORE_NAME], 'readwrite');
      const store = transaction.objectStore(SHIP_UPDATES_STORE_NAME);
      const request = store.delete(id);
      request.onerror = event => {
        console.error('SW DB delete error:', event.target.error);
        reject('Error deleting data in SW');
      };
      request.onsuccess = () => {
        console.log(`SW: Successfully removed offline data with id: ${id}`);
        resolve();
      };
    });
  } catch (error) {
    console.error('SW: Error opening DB for removeOfflineData:', error);
    // Decide if to reject or resolve to avoid breaking sync loop
    return Promise.reject('Failed to open DB for removing data');
  }
}

// --- Push Event Listener ---
self.addEventListener('push', event => {
  console.log('SW: Push event received.', event);

  let title = 'Stevedore Alert';
  let options = {
    body: 'You have a new message.',
    icon: '/static/icons/icon-192.png', // Default icon
    badge: '/static/icons/ship-icon.png', // Small icon for notification bar (Android)
    tag: 'stevedore-notification-tag', // Notifications with same tag will replace each other
    // data: { url: '/' } // Custom data to use when notification is clicked
  };

  if (event.data) {
    try {
      const data = event.data.json();
      console.log('SW: Push event data:', data);
      title = data.title || title;
      options.body = data.body || options.body;
      options.icon = data.icon || options.icon;
      options.badge = data.badge || options.badge;
      options.data = data.data || options.data; // e.g. { url: '/ship-status/123' }
      if(data.image) options.image = data.image; // Large image in notification
    } catch (e) {
      console.log('SW: Push event data is text, not JSON.');
      options.body = event.data.text();
    }
  }

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// --- Notification Click Event Listener ---
self.addEventListener('notificationclick', event => {
  console.log('SW: Notification clicked.', event.notification);
  event.notification.close(); // Close the notification

  // Example: Open a specific URL or focus an existing window
  let targetUrl = '/'; // Default URL to open
  if (event.notification.data && event.notification.data.url) {
    targetUrl = event.notification.data.url;
  }

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(windowClients => {
        // Check if there is already a window/tab open with the target URL
        for (let i = 0; i < windowClients.length; i++) {
          const client = windowClients[i];
          // If client URL is the targetURL, focus it.
          // Note: URL matching can be tricky due to query params, hashes etc.
          // Simple check for now:
          if (client.url && client.url.includes(targetUrl) && 'focus' in client) {
            return client.focus();
          }
        }
        // If no client is open or found, open a new tab/window.
        if (clients.openWindow) {
          return clients.openWindow(targetUrl);
        }
      })
  );
});

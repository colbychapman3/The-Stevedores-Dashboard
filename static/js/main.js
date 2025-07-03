// Placeholder for main JavaScript file
console.log("Main JavaScript file loaded.");

// PWA Install button logic is primarily in base.html, but can be enhanced here.

// Add any global helper functions or initializations here.

/**
 * IndexedDB for offline data storage.
 * This class is referenced by ship_status.html and sw.js (implicitly for getOfflineData/removeOfflineData).
 */
class OfflineStorage {
  constructor() {
    this.dbName = 'StevedoreDB';
    this.version = 1; // Increment this if schema changes
    this.db = null;
    console.log("OfflineStorage instance created.");
  }

  async init() {
    // console.log("OfflineStorage init called.");
    if (this.db) {
      // console.log("DB connection already exists.");
      return this.db;
    }
    return new Promise((resolve, reject) => {
      // console.log(`Attempting to open IndexedDB: ${this.dbName} version ${this.version}`);
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = (event) => {
        console.error('OfflineStorage IndexedDB error:', event.target.error);
        reject(event.target.error);
      };

      request.onsuccess = (event) => {
        this.db = event.target.result;
        // console.log('OfflineStorage initialized, DB connection successful.');
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        console.log('OfflineStorage: Upgrading DB...');
        const db = event.target.result;
        // Object store for ship status updates
        if (!db.objectStoreNames.contains('shipUpdates')) {
          console.log('OfflineStorage: Creating shipUpdates object store.');
          db.createObjectStore('shipUpdates', { keyPath: 'id', autoIncrement: true });
        } else {
          console.log('OfflineStorage: shipUpdates store already exists.');
        }
        // Object store for berth status (as per original example)
        if (!db.objectStoreNames.contains('berthStatus')) {
          console.log('OfflineStorage: Creating berthStatus object store.');
          db.createObjectStore('berthStatus', { keyPath: 'id', autoIncrement: true });
        } else {
          console.log('OfflineStorage: berthStatus store already exists.');
        }
        console.log('OfflineStorage: DB upgrade complete.');
      };
    });
  }

  /**
   * Stores a ship update.
   * @param {object} data - The ship update data. 'id' will be auto-generated.
   */
  async storeShipUpdate(data) {
    console.log("OfflineStorage: storeShipUpdate called with data:", data);
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['shipUpdates'], 'readwrite');
      transaction.onerror = event => {
        console.error("OfflineStorage: Transaction error in storeShipUpdate:", event.target.error);
        reject(event.target.error);
      };
      transaction.onabort = event => {
        console.error("OfflineStorage: Transaction aborted in storeShipUpdate:", event.target.error);
        reject(new Error("Transaction aborted: " + event.target.error));
      };
      const store = transaction.objectStore('shipUpdates');

      // Data should not contain 'id' if keyPath is 'id' and autoIncrement is true,
      // unless you want to overwrite. For 'add', it's better to let DB generate it.
      // If 'id' is present in data, 'add' might fail if an entry with that id exists.
      // 'put' would update/insert. Let's assume data does not have 'id'.
      const dataToStore = { ...data };
      if ('id' in dataToStore && dataToStore.id === undefined) { // Or some other check if id should be auto-generated
          delete dataToStore.id; // Remove id if it's undefined, to allow auto-increment
      }

      const request = store.add(dataToStore);

      request.onsuccess = (event) => {
        console.log("OfflineStorage: Ship update stored successfully. Generated ID:", event.target.result);
        resolve(event.target.result); // Returns the key of the new object
      };
      request.onerror = (event) => {
        console.error("OfflineStorage: Error storing ship update:", event.target.error);
        reject(event.target.error);
      };
    });
  }

  /**
   * Retrieves all stored ship updates.
   */
  async getAllShipUpdates() {
    console.log("OfflineStorage: getAllShipUpdates called.");
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['shipUpdates'], 'readonly');
      const store = transaction.objectStore('shipUpdates');
      const request = store.getAll();
      request.onsuccess = (event) => {
        console.log("OfflineStorage: Retrieved all ship updates:", event.target.result);
        resolve(event.target.result);
      };
      request.onerror = (event) => {
        console.error("OfflineStorage: Error retrieving all ship updates:", event.target.error);
        reject(event.target.error);
      };
    });
  }

  /**
   * Deletes a ship update by its ID.
   * @param {any} id - The ID of the ship update to delete.
   */
  async deleteShipUpdate(id) {
    console.log("OfflineStorage: deleteShipUpdate called for ID:", id);
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['shipUpdates'], 'readwrite');
      const store = transaction.objectStore('shipUpdates');
      const request = store.delete(id);
      request.onsuccess = () => {
        console.log("OfflineStorage: Ship update deleted successfully for ID:", id);
        resolve(); // delete operation does not return a value on success other than undefined
      };
      request.onerror = (event) => {
        console.error("OfflineStorage: Error deleting ship update for ID:", id, event.target.error);
        reject(event.target.error);
      };
    });
  }

  // Add similar methods for 'berthStatus' or other stores as needed
  // e.g., storeBerthStatus, getAllBerthStatus, deleteBerthStatus
}

// Make OfflineStorage available to other scripts if needed, e.g., for sw.js or inline scripts.
// window.OfflineStorage = OfflineStorage; // This makes it globally accessible.

// Functions for sw.js background sync (implementing getOfflineData and removeOfflineData)
// These need to be accessible by the service worker.
// However, sw.js runs in a different context and cannot directly access 'window' or this 'OfflineStorage' instance.
// The sync logic in sw.js will need its own IndexedDB access.
// For now, the stubs in sw.js will remain, and actual IndexedDB operations for sync
// need to be written directly within sw.js or in a script it imports.

// The `syncShipStatus` function in `sw.js` will need to implement its own IndexedDB logic.
// Let's refine `sw.js` in a later step to include this.
// For now, this `OfflineStorage` class is primarily for the client-side app logic (e.g., in `ship_status.html`).

document.addEventListener('DOMContentLoaded', () => {
    // Initialize any components or event listeners here
    console.log("DOM fully loaded and parsed");

    // Example: Initialize OfflineStorage if needed globally, though it's often better
    // to instantiate it where specifically required.
    // const offlineDB = new OfflineStorage();
    // offlineDB.init().then(() => console.log("OfflineDB ready on main page load"))
    //          .catch(err => console.error("Failed to init OfflineDB on main page load", err));

    initializePushNotifications();
});

// --- Push Notification Logic ---

// IMPORTANT: Replace this with your actual VAPID public key
const VAPID_PUBLIC_KEY = 'YOUR_VAPID_PUBLIC_KEY_HERE_REPLACE_ME';

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

async function initializePushNotifications() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Push messaging is not supported');
        return;
    }

    try {
        const registration = await navigator.serviceWorker.ready;
        console.log('Service Worker for Push is ready.');

        // Check current permission status
        const permissionStatus = await Notification.requestPermission();
        if (permissionStatus !== 'granted') {
            console.log('Permission for notifications not granted.');
            // Optionally, guide user on how to enable notifications
            // You could display a button here to trigger requestPermission again upon user interaction
            // For now, we just log and exit if not granted.
            return;
        }

        console.log('Notification permission granted.');

        // Check if already subscribed
        let subscription = await registration.pushManager.getSubscription();
        if (subscription === null) {
            console.log('Not subscribed to push, attempting to subscribe...');
            if (!VAPID_PUBLIC_KEY || VAPID_PUBLIC_KEY === 'YOUR_VAPID_PUBLIC_KEY_HERE_REPLACE_ME') {
                console.error("VAPID_PUBLIC_KEY is not set. Please generate and set it.");
                alert("Push notification setup error: VAPID public key missing. See console.");
                return;
            }
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true, // Required
                applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
            });
            console.log('New Push Subscription: ', subscription);
            // TODO: Send this subscription to your application server
            // For example:
            // await sendSubscriptionToServer(subscription);
            alert('Subscribed to push notifications! (Check console for subscription object)');
        } else {
            console.log('Already subscribed to push:', subscription);
            // Optionally, ensure the server has this subscription
            // await sendSubscriptionToServer(subscription);
        }
    } catch (error) {
        console.error('Error during push notification initialization:', error);
    }
}

// Example function to simulate sending subscription to server
async function sendSubscriptionToServer(subscription) {
    // In a real app, you would send this to your backend
    console.log('Sending subscription to server (mock):', JSON.stringify(subscription));
    // Example fetch:
    // try {
    //     const response = await fetch('/api/subscribe-push', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json',
    //         },
    //         body: JSON.stringify(subscription),
    //     });
    //     if (!response.ok) {
    //         throw new Error('Failed to send subscription to server');
    //     }
    //     console.log('Subscription sent to server successfully.');
    // } catch (error) {
    //     console.error('Error sending subscription to server:', error);
    // }
}

// Optional: Add a button in HTML to trigger permission request if not granted on load
// Example:
// <button id="enable-notifications-button">Enable Notifications</button>
// document.getElementById('enable-notifications-button')?.addEventListener('click', async () => {
//     const permission = await Notification.requestPermission();
//     if (permission === 'granted') {
//         console.log('Notification permission granted by user action.');
//         initializePushNotifications(); // Re-run init to subscribe
//     } else {
//         console.log('Notification permission denied by user action.');
//     }
// });

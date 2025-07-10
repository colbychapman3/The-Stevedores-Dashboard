const CACHE_NAME = 'stevedores-dashboard-v2';
const urlsToCache = [
  '/',
  '/master',
  '/wizard',
  '/calendar',
  '/analytics',
  '/ship-info',
  '/static/manifest.json',
  '/static/index.html',
  '/static/master-dashboard.html',
  '/static/calendar.html',
  '/static/analytics.html',
  '/static/ship-info.html',
  '/static/dist/output.css',
  '/static/sw.js',
  // External CDN resources for offline functionality
  'https://cdn.tailwindcss.com',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        
        // For API requests, try network first, then fallback to cache
        if (event.request.url.includes('/api/')) {
          return fetch(event.request)
            .then(function(networkResponse) {
              // Cache successful API responses
              if (networkResponse && networkResponse.status === 200) {
                const responseToCache = networkResponse.clone();
                caches.open(CACHE_NAME)
                  .then(function(cache) {
                    cache.put(event.request, responseToCache);
                  });
              }
              return networkResponse;
            })
            .catch(function() {
              // If network fails, return cached response or offline fallback
              return caches.match(event.request)
                .then(function(cachedResponse) {
                  if (cachedResponse) {
                    return cachedResponse;
                  }
                  // Return offline fallback for API requests
                  return new Response(JSON.stringify({
                    error: 'Offline',
                    message: 'You are currently offline. Some features may not be available.'
                  }), {
                    status: 503,
                    headers: {
                      'Content-Type': 'application/json'
                    }
                  });
                });
            });
        }
        
        // For non-API requests, try network first
        return fetch(event.request)
          .catch(function() {
            return caches.match(event.request);
          });
      }
    )
  );
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
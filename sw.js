// Service Worker for offline support and caching
// Enables the app to work offline and install on home screen

const CACHE_NAME = 'constrcutions-v1';
const urlsToCache = [
  '/',
  '/login',
  '/dashboard',
  '/static/manifest.json',
  '/templates/login.html',
  '/templates/dashboard.html'
];

// Install Service Worker and cache files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
  self.skipWaiting();
});

// Activate Service Worker and clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  // Only cache GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached response if available
        if (response) {
          return response;
        }

        // Otherwise fetch from network
        return fetch(event.request).then(response => {
          // Check if valid response
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }

          // Clone and cache the response
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });

          return response;
        });
      })
      .catch(() => {
        // Return offline page if needed
        return caches.match('/')
          .then(response => response || new Response('Offline - Please check your connection'));
      })
  );
});

// Background sync for offline data submission
self.addEventListener('sync', event => {
  if (event.tag === 'sync-entries') {
    event.waitUntil(
      // Sync entries when connection returns
      fetch('/api/sync', { method: 'POST' })
        .catch(err => console.log('Sync failed:', err))
    );
  }
});

console.log('Service Worker registered');

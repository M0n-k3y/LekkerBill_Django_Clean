// Version 3: A more robust and intelligent service worker

const CACHE_NAME = 'lekkerbill-cache-v2'; // Increment cache name to force update

// Core assets that are always needed.
const CORE_ASSETS = [
    '/', // The landing/dashboard page
    '/static/invoices/manifest.json',
    '/static/invoices/images/icons/icon-192x192.png',
    '/static/invoices/images/icons/icon-512x512.png',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css',
    'https://bootswatch.com/5/minty/bootstrap.min.css',
    'https://bootswatch.com/5/superhero/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/tom-select@2.3.1/dist/js/tom-select.complete.min.js'
];

// Install event: opens a cache and adds the core assets to it.
self.addEventListener('install', event => {
    console.log('[ServiceWorker] Install event triggered');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[ServiceWorker] Caching core assets');
                return cache.addAll(CORE_ASSETS);
            })
            .then(() => self.skipWaiting()) // Activate the new service worker immediately
    );
});

// Activate event: cleans up old caches.
self.addEventListener('activate', event => {
    console.log('[ServiceWorker] Activate event triggered');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[ServiceWorker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    return self.clients.claim(); // Take control of all open clients
});


// Fetch event: serves assets from the cache first (cache-first strategy).
self.addEventListener('fetch', event => {
    // We only want to cache GET requests.
    if (event.request.method !== 'GET') {
        return;
    }

    event.respondWith(
        caches.open(CACHE_NAME).then(cache => {
            return cache.match(event.request).then(response => {
                // Return the cached response if it exists.
                if (response) {
                    // console.log(`[ServiceWorker] Returning from cache: ${event.request.url}`);
                    return response;
                }

                // If not in cache, fetch from the network.
                // console.log(`[ServiceWorker] Fetching from network: ${event.request.url}`);
                return fetch(event.request).then(networkResponse => {
                    // Don't cache opaque responses (from CDNs without CORS) or errors
                    if (networkResponse.status === 200) {
                         // Clone the response to put it in the cache.
                        cache.put(event.request, networkResponse.clone());
                    }
                    return networkResponse;
                });
            });
        })
    );
});

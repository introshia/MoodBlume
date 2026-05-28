const CACHE_NAME = 'moodblume-cache-v7';

self.addEventListener('install', (e) => {
    console.log('[Service Worker] Installed v2');
    self.skipWaiting(); 
});

self.addEventListener('activate', (e) => {
    console.log('[Service Worker] Activated v2');
    
    e.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[Service Worker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    return self.clients.claim(); 
});

self.addEventListener('fetch', (e) => {
    
    if (e.request.url.startsWith('chrome-extension') || e.request.url.includes('com.chrome.devtools')) {
        return;
    }

    if (e.request.mode === 'navigate') {
        e.respondWith(fetch(e.request));
        return;
    }

    e.respondWith(
        caches.match(e.request).then((response) => {
            return response || fetch(e.request);
        })
    );
});

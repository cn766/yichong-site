// 异宠指南 - Service Worker
const CACHE_NAME = 'yichong-zhinan-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/species.html',
  '/blog.html',
  '/about.html',
  '/favorites.html',
  '/styles/global.css',
  '/site.webmanifest',
  '/favicon.svg'
];

// 安装：缓存静态资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('缓存静态资源');
        return cache.addAll(STATIC_ASSETS);
      })
      .catch((err) => {
        console.log('缓存失败:', err);
      })
  );
  self.skipWaiting();
});

// 激活：清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// 拦截请求：缓存优先策略
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 跳过非GET请求
  if (request.method !== 'GET') {
    return;
  }

  // 跳过Chrome扩展请求
  if (url.protocol === 'chrome-extension:') {
    return;
  }

  // 跳过API和外部请求
  if (url.origin !== self.location.origin) {
    return;
  }

  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        // 返回缓存或发起网络请求
        if (cachedResponse) {
          // 后台更新缓存
          fetch(request)
            .then((networkResponse) => {
              if (networkResponse.ok) {
                caches.open(CACHE_NAME).then((cache) => {
                  cache.put(request, networkResponse.clone());
                });
              }
            })
            .catch(() => {
              // 网络失败，使用缓存
            });
          return cachedResponse;
        }

        // 无缓存，发起网络请求
        return fetch(request)
          .then((networkResponse) => {
            if (!networkResponse || networkResponse.status !== 200) {
              return networkResponse;
            }

            // 缓存新资源
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseToCache);
            });

            return networkResponse;
          })
          .catch(() => {
            // 网络失败，返回离线页面
            if (request.mode === 'navigate') {
              return caches.match('/index.html');
            }
            return new Response('离线中，请检查网络连接', {
              status: 503,
              statusText: 'Service Unavailable'
            });
          });
      })
  );
});

// 后台同步（用于离线评论）
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-comments') {
    event.waitUntil(syncComments());
  }
});

// 推送通知
self.addEventListener('push', (event) => {
  const options = {
    body: event.data?.text() || '新文章发布了！',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    tag: 'new-article',
    requireInteraction: true,
    actions: [
      { action: 'open', title: '查看' },
      { action: 'close', title: '关闭' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('异宠指南', options)
  );
});

// 通知点击
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'open' || !event.action) {
    event.waitUntil(
      clients.openWindow('/blog.html')
    );
  }
});

// 同步评论（示例函数）
async function syncComments() {
  // 从IndexedDB获取离线评论并发送
  console.log('同步离线评论...');
}

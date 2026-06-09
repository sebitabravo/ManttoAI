// Service Worker de ManttoAI
// Cache Strategy: Network First para API calls, Cache First para assets estaticos

const CACHE_NAME = "manttoai-v1";

// Archivos precacheados al instalar
const PRECACHE_URLS = [
  "/",
  "/index.html",
];

// Assets estaticos tipicos de Vite — se cachean al primer fetch
const STATIC_ASSET_PATTERNS = [
  /\.(js|css|woff2?|png|jpg|jpeg|gif|svg|ico)(\?.*)?$/,
];

// Rutas de API del backend
const API_PATTERNS = [
  /^\/api\//,
  /^\/auth\//,
];

// --- INSTALL ---
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_URLS);
    })
  );
  // Activar inmediatamente sin esperar a que se cierren todas las pestanias
  self.skipWaiting();
});

// --- ACTIVATE ---
self.addEventListener("activate", (event) => {
  // Limpiar caches viejas que no coincidan con la version actual
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  // Tomar control de todas las pestanias abiertas
  self.clients.claim();
});

// --- FETCH ---
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Solo interceptar requests del mismo origen
  if (url.origin !== self.location.origin) {
    return;
  }

  // Determinar estrategia segun el tipo de request
  if (isApiRequest(url.pathname)) {
    // Network First para llamadas API
    event.respondWith(networkFirst(request));
  } else if (isStaticAsset(url.pathname)) {
    // Cache First para assets estaticos (JS, CSS, imagenes, fuentes)
    event.respondWith(cacheFirst(request));
  } else if (request.mode === "navigate") {
    // Network First para navegacion — siempre servir pagina fresca si hay red
    event.respondWith(networkFirst(request));
  } else {
    // Cache First para todo lo demas
    event.respondWith(cacheFirst(request));
  }
});

/**
 * Estrategia Network First: intenta red, cae a cache si falla.
 * Util para API calls y navegacion donde queremos datos frescos.
 */
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    // Solo cachear respuestas exitosas
    if (response.ok) {
      const clone = response.clone();
      caches.open(CACHE_NAME).then((cache) => {
        cache.put(request, clone);
      });
    }
    return response;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    // Si no hay red ni cache, devolver respuesta offline generica
    return new Response(
      JSON.stringify({ error: "Sin conexion", message: "No hay acceso a internet" }),
      { status: 503, headers: { "Content-Type": "application/json" } }
    );
  }
}

/**
 * Estrategia Cache First: sirve desde cache, actualiza en background si hay red.
 * Util para assets estaticos que rara vez cambian.
 */
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    // Actualizar cache en background (stale-while-revalidate)
    fetch(request).then((response) => {
      if (response.ok) {
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, response);
        });
      }
    }).catch(() => {});
    return cached;
  }

  try {
    const response = await fetch(request);
    if (response.ok) {
      const clone = response.clone();
      caches.open(CACHE_NAME).then((cache) => {
        cache.put(request, clone);
      });
    }
    return response;
  } catch (err) {
    return new Response(
      JSON.stringify({ error: "Sin conexion", message: "No hay acceso a internet" }),
      { status: 503, headers: { "Content-Type": "application/json" } }
    );
  }
}

function isApiRequest(pathname) {
  return API_PATTERNS.some((pattern) => pattern.test(pathname));
}

function isStaticAsset(pathname) {
  return STATIC_ASSET_PATTERNS.some((pattern) => pattern.test(pathname));
}

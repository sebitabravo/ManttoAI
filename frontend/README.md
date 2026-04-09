# Frontend ManttoAI

Frontend React + Vite para el dashboard de mantenimiento predictivo.

## Requisitos

- Node.js 20+
- npm 10+
- Backend disponible (`http://localhost:8000` en desarrollo local)

## Variables de entorno

Archivo: `.env.example`

```env
VITE_API_URL=/api/v1
```

Para desarrollo local con backend directo:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Ejecutar local

```bash
npm install
npm run dev
```

## Build de producción

```bash
npm run build
npm run preview
```

## Calidad y pruebas

```bash
npm run lint
npm run test:unit
npm run test:e2e
```

## Estructura principal

- `src/api/`: cliente Axios + módulos por dominio
- `src/context/`: contexto de autenticación
- `src/hooks/`: polling, fetch y utilitarios de estado
- `src/pages/`: vistas principales
- `src/components/`: layout, dashboard y UI base

## Notas de autenticación

- El login usa cookie HttpOnly + token CSRF para mutaciones.
- Si el backend retorna `401`, el cliente redirige automáticamente a `/login`.

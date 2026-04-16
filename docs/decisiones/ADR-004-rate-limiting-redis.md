# ADR-004: Rate Limiting con Redis

## Estado: Aceptado

## Fecha: 2026-04-16

## Contexto

El sistema enfrentaba errores 429 (Too Many Requests) frecuentemente durante desarrollo y testing. Los problemas identificados:

1. **Sin persistencia**: Redis sin volumen perdía contadores al reiniciar
2. **Sin autenticación**: Puerto 6379 expuesto sin password
3. **Límites bajos**: 600/hour era muy bajo para polling del frontend
4. **Rate limits por endpoint**: Cada endpoint tenía límites específicos inconsistentes

## Decisiones

1. **Usar Redis para rate limiting** - Configuración de producción:
   - Volumen `redis_data` para persistencia AOF
   - Autenticación con `requirepass`
   - Bind solo a localhost (127.0.0.1)

2. **Centralizar límites** - Una sola variable de entorno:
   - `RATE_LIMIT_API=60000/hour` (desarrollo)
   - `RATE_LIMIT_API=1500/hour` (producción)

3. **Remover límites por endpoint** - Usar solo el global

4. **Optimizar frontend**:
   - Polling intervals: 60s (desde 15-30s)
   - Retry con exponential backoff (2s, 4s, 8s)
   - Stale-while-revalidate

## Consecuencias

### Positivas
- ✅ Sin errores 429 en desarrollo
- ✅ Persistencia de contadores entre reinicios
- ✅ Configuración centralizada
- ✅ UX mejor con retry automático

### Negativas
- ❌ Redis puede fallar en producción (fallback a memoria)
- ❌ Password por defecto en docker-compose (para production usar secrets)

## Notas

- Los límites específicos para auth/onboarding (5-10/min) se mantuvieron por seguridad
- MQTT subscriber no pasa por rate limiter (directo con paho-mqtt)
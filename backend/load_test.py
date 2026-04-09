#!/usr/bin/env python3
"""
Script de pruebas de carga para validar que ManttoAI soporta 50 usuarios concurrentes.

Este script simula múltiples usuarios concurrentes accediendo a diferentes endpoints
y mide el tiempo de respuesta, errores, y degradación de performance.
"""

import asyncio
import json
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import aiohttp


@dataclass
class LoadTestResult:
    """Resultados de una prueba de carga."""

    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    requests_per_second: float
    error_rate: float


async def make_request(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    token: str | None = None,
    data: dict | None = None,
    timeout: float = 10.0,
) -> tuple[bool, float, int]:
    """
    Realiza un request HTTP y retorna (success, response_time_ms, status_code).
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data:
        headers["Content-Type"] = "application/json"

    start_time = time.time()
    try:
        async with session.request(
            method=method, url=url, headers=headers, json=data, timeout=timeout
        ) as response:
            response_time_ms = (time.time() - start_time) * 1000
            success = 200 <= response.status < 300
            return success, response_time_ms, response.status
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        print(f"Error en request: {e}")
        return False, response_time_ms, 0


async def simulate_concurrent_users(
    base_url: str,
    num_users: int = 50,
    requests_per_user: int = 10,
    admin_token: str | None = None,
) -> Dict[str, LoadTestResult]:
    """
    Simula múltiples usuarios concurrentes realizando requests.

    Args:
        base_url: URL base de la API
        num_users: Número de usuarios concurrentes
        requests_per_user: Requests por usuario
        admin_token: Token de autenticación

    Returns:
        Dict de resultados por endpoint
    """

    # Definir endpoints a probar
    endpoints_to_test = [
        ("GET", "/api/v1/health", None, 20),  # Endpoint público, más requests
        ("GET", "/api/v1/dashboard/resumen", None, 15),
        ("GET", "/api/v1/equipos", None, 10),
        ("GET", "/api/v1/alertas", None, 10),
        ("GET", "/api/v1/lecturas", None, 10),
        ("GET", "/api/v1/usuarios", admin_token, 5),  # Solo admin
    ]

    results: Dict[str, List[tuple[bool, float]]] = {
        f"{method} {path}": [] for method, path, _, _ in endpoints_to_test
    }

    async with aiohttp.ClientSession() as session:
        tasks = []

        # Crear tasks para cada usuario
        for user_id in range(num_users):
            for method, path, token, weight in endpoints_to_test:
                url = f"{base_url}{path}"
                # Cada usuario hace weighted requests por endpoint
                for _ in range(weight):
                    task = make_request(session, method, url, token)
                    tasks.append((f"{method} {path}", task))

        # Ejecutar todos los requests concurrentemente
        print(f"\n⏱️  Ejecutando {len(tasks)} requests concurrentes...")
        print(f"👥 Usuarios: {num_users}")
        print(f"📊 Requests por usuario: {requests_per_user}")

        start_time = time.time()

        # Ejecutar tasks y recolectar resultados
        task_results = await asyncio.gather(*[task for _, task in tasks])

        total_time = time.time() - start_time

        # Organizar resultados por endpoint
        task_index = 0
        for endpoint_key, _ in endpoints_to_test:
            for _ in range(weight * num_users):
                result = task_results[task_index]
                results[endpoint_key].append(result)
                task_index += 1

    # Calcular métricas por endpoint
    final_results: Dict[str, LoadTestResult] = {}

    for endpoint_key, responses in results.items():
        if not responses:
            continue

        successes = [r for r in responses if r[0]]
        failures = [r for r in responses if not r[0]]
        response_times = [r[1] for r in responses if r[0]] or [0]

        successful_requests = len(successes)
        failed_requests = len(failures)
        total_requests = len(responses)

        if response_times:
            avg_response_time_ms = statistics.mean(response_times)
            p50_response_time_ms = statistics.median(response_times)
            p95_response_time_ms = (
                sorted(response_times)[int(len(response_times) * 0.95)]
                if len(response_times) > 1
                else response_times[0]
            )
            p99_response_time_ms = (
                sorted(response_times)[int(len(response_times) * 0.99)]
                if len(response_times) > 1
                else response_times[-1]
            )
            min_response_time_ms = min(response_times)
            max_response_time_ms = max(response_times)
        else:
            avg_response_time_ms = 0
            p50_response_time_ms = 0
            p95_response_time_ms = 0
            p99_response_time_ms = 0
            min_response_time_ms = 0
            max_response_time_ms = 0

        requests_per_second = total_requests / total_time if total_time > 0 else 0
        error_rate = (
            (failed_requests / total_requests * 100) if total_requests > 0 else 0
        )

        final_results[endpoint_key] = LoadTestResult(
            endpoint=endpoint_key,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=round(avg_response_time_ms, 2),
            p50_response_time_ms=round(p50_response_time_ms, 2),
            p95_response_time_ms=round(p95_response_time_ms, 2),
            p99_response_time_ms=round(p99_response_time_ms, 2),
            min_response_time_ms=round(min_response_time_ms, 2),
            max_response_time_ms=round(max_response_time_ms, 2),
            requests_per_second=round(requests_per_second, 2),
            error_rate=round(error_rate, 2),
        )

    return final_results


def print_results(results: Dict[str, LoadTestResult]):
    """Imprime los resultados de las pruebas de carga."""

    print("\n" + "=" * 80)
    print("📊 RESULTADOS DE PRUEBAS DE CARGA")
    print("=" * 80)

    for endpoint, result in results.items():
        print(f"\n🔹 {endpoint}")
        print(f"   Total requests: {result.total_requests}")
        print(f"   ✅ Exitosos: {result.successful_requests}")
        print(f"   ❌ Fallidos: {result.failed_requests}")
        print(f"   📈 Error rate: {result.error_rate}%")
        print(f"   ⚡ Requests/seg: {result.requests_per_second}")
        print(f"\n   🕐 Tiempos de respuesta (ms):")
        print(f"   Promedio: {result.avg_response_time_ms}ms")
        print(f"   P50: {result.p50_response_time_ms}ms")
        print(f"   P95: {result.p95_response_time_ms}ms")
        print(f"   P99: {result.p99_response_time_ms}ms")
        print(f"   Mín: {result.min_response_time_ms}ms")
        print(f"   Máx: {result.max_response_time_ms}ms")

        # Evaluación de performance
        if result.error_rate > 5:
            print(f"   ⚠️  WARNING: Error rate alto (>5%)")
        if result.avg_response_time_ms > 1000:
            print(f"   ⚠️  WARNING: Tiempo promedio alto (>1000ms)")
        if result.p95_response_time_ms > 2000:
            print(f"   ⚠️  WARNING: P95 alto (>2000ms)")

    # Resumen general
    print("\n" + "=" * 80)
    print("📋 RESUMEN GENERAL")
    print("=" * 80)

    total_requests = sum(r.total_requests for r in results.values())
    total_successful = sum(r.successful_requests for r in results.values())
    total_failed = sum(r.failed_requests for r in results.values())
    avg_error_rate = statistics.mean([r.error_rate for r in results.values()])
    avg_response_time = statistics.mean(
        [r.avg_response_time_ms for r in results.values()]
    )
    max_response_time = max([r.p99_response_time_ms for r in results.values()])

    print(f"Total requests: {total_requests}")
    print(f"Total exitosos: {total_successful}")
    print(f"Total fallidos: {total_failed}")
    print(f"Error rate promedio: {avg_error_rate:.2f}%")
    print(f"Tiempo promedio respuesta: {avg_response_time:.2f}ms")
    print(f"Peor caso (P99): {max_response_time:.2f}ms")

    # Criterios de aceptación
    print("\n" + "=" * 80)
    print("✅ CRITERIOS DE ACEPTACIÓN")
    print("=" * 80)

    criteria_met = []

    if avg_error_rate < 1:
        print("✅ Error rate < 1%: CUMPLIDO")
        criteria_met.append(True)
    else:
        print(f"❌ Error rate < 1%: NO CUMPLIDO ({avg_error_rate:.2f}%)")
        criteria_met.append(False)

    if avg_response_time < 500:
        print("✅ Tiempo promedio < 500ms: CUMPLIDO")
        criteria_met.append(True)
    else:
        print(f"❌ Tiempo promedio < 500ms: NO CUMPLIDO ({avg_response_time:.2f}ms)")
        criteria_met.append(False)

    if max_response_time < 2000:
        print("✅ Peor caso < 2000ms: CUMPLIDO")
        criteria_met.append(True)
    else:
        print(f"❌ Peor caso < 2000ms: NO CUMPLIDO ({max_response_time:.2f}ms)")
        criteria_met.append(False)

    print("\n" + "=" * 80)
    if all(criteria_met):
        print(
            "🎉 TODOS LOS CRITERIOS CUMPLIDOS - SISTEMA OPTIMIZADO PARA 50 USUARIOS CONCURRENTES"
        )
    else:
        print("⚠️  ALGUNOS CRITERIOS NO CUMPLIDOS - REVISAR OPTIMIZACIONES")
    print("=" * 80)

    return all(criteria_met)


def save_results_to_json(
    results: Dict[str, LoadTestResult], output_path: str = "load_test_results.json"
):
    """Guarda los resultados en formato JSON."""

    results_dict = {}
    for endpoint, result in results.items():
        results_dict[endpoint] = {
            "total_requests": result.total_requests,
            "successful_requests": result.successful_requests,
            "failed_requests": result.failed_requests,
            "avg_response_time_ms": result.avg_response_time_ms,
            "p50_response_time_ms": result.p50_response_time_ms,
            "p95_response_time_ms": result.p95_response_time_ms,
            "p99_response_time_ms": result.p99_response_time_ms,
            "min_response_time_ms": result.min_response_time_ms,
            "max_response_time_ms": result.max_response_time_ms,
            "requests_per_second": result.requests_per_second,
            "error_rate": result.error_rate,
            "timestamp": datetime.utcnow().isoformat(),
        }

    with open(output_path, "w") as f:
        json.dump(results_dict, f, indent=2)

    print(f"\n💾 Resultados guardados en: {output_path}")


async def main():
    """Función principal."""

    # Configuración
    BASE_URL = "http://localhost:8000"
    NUM_USERS = 50
    REQUESTS_PER_USER = 10

    print("🚀 Iniciando pruebas de carga para ManttoAI")
    print(f"📍 URL base: {BASE_URL}")
    print(f"👥 Usuarios concurrentes: {NUM_USERS}")
    print(f"📊 Requests por usuario: {REQUESTS_PER_USER}")

    # Intentar obtener token admin
    admin_token = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"email": "admin@manttoai.local", "password": "admin123"},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    admin_token = data.get("access_token")
                    print("✅ Token admin obtenido")
                else:
                    print(
                        "⚠️  No se pudo obtener token admin - usando endpoints públicos"
                    )
    except Exception as e:
        print(f"⚠️  Error obteniendo token admin: {e}")

    # Ejecutar pruebas
    results = await simulate_concurrent_users(
        base_url=BASE_URL,
        num_users=NUM_USERS,
        requests_per_user=REQUESTS_PER_USER,
        admin_token=admin_token,
    )

    # Imprimir resultados
    all_passed = print_results(results)

    # Guardar resultados
    save_results_to_json(results)

    # Exit code
    import sys

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())

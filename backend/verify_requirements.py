#!/usr/bin/env python3
"""
Script para verificar que el sistema cumple con los requisitos del informe de título.

Requisitos a verificar:
1. Accuracy ML: 85% (F1-Score)
2. Cobertura tests: 70%
3. Carga: 50 usuarios concurrentes
"""

import subprocess
import sys
from pathlib import Path


def check_ml_metrics():
    """Verifica que el modelo ML cumpla con los requisitos de accuracy y F1-Score."""

    print("\n" + "=" * 80)
    print("🤖 VERIFICANDO MÉTRICAS ML")
    print("=" * 80)

    try:
        # Importar y ejecutar evaluación del modelo
        sys.path.insert(0, str(Path(__file__).parent))
        from app.ml.evaluate import evaluate_model
        from app.ml.generate_dataset import generate_synthetic_dataset

        # Generar dataset y evaluar
        dataset = generate_synthetic_dataset(size=500, seed=42)
        metrics = evaluate_model(dataframe=dataset, test_size=0.2, random_state=42)

        print(f"\n📊 Métricas del modelo:")
        print(f"   Accuracy: {metrics['accuracy']:.2%}")
        print(f"   Precision: {metrics['precision']:.2%}")
        print(f"   Recall: {metrics['recall']:.2%}")
        print(f"   F1-Score: {metrics['f1']:.2%}")
        print(
            f"   CV F1-Score: {metrics['cv_f1_mean']:.2%} (±{metrics['cv_f1_std']:.2%})"
        )

        # Verificar requisitos
        required_accuracy = 0.85
        required_f1 = 0.85

        accuracy_ok = metrics["accuracy"] >= required_accuracy
        f1_ok = metrics["f1"] >= required_f1

        print("\n" + "=" * 80)
        print("✅ VERIFICACIÓN MÉTRICAS ML")
        print("=" * 80)

        if accuracy_ok:
            print(
                f"✅ Accuracy >= {required_accuracy:.0%}: CUMPLIDO ({metrics['accuracy']:.2%})"
            )
        else:
            print(
                f"❌ Accuracy >= {required_accuracy:.0%}: NO CUMPLIDO ({metrics['accuracy']:.2%})"
            )

        if f1_ok:
            print(f"✅ F1-Score >= {required_f1:.0%}: CUMPLIDO ({metrics['f1']:.2%})")
        else:
            print(
                f"❌ F1-Score >= {required_f1:.0%}: NO CUMPLIDO ({metrics['f1']:.2%})"
            )

        return accuracy_ok and f1_ok

    except Exception as e:
        print(f"❌ Error evaluando modelo ML: {e}")
        return False


def check_test_coverage():
    """Verifica que la cobertura de tests cumpla con el 70%."""

    print("\n" + "=" * 80)
    print("🧪 VERIFICANDO COBERTURA DE TESTS")
    print("=" * 80)

    try:
        # Ejecutar tests con coverage
        result = subprocess.run(
            [
                "pytest",
                "tests/",
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=json",
                "-v",
                "--tb=short",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        # Leer resultados de coverage desde JSON
        coverage_file = Path(__file__).parent / "coverage.json"
        if coverage_file.exists():
            import json

            with open(coverage_file) as f:
                coverage_data = json.load(f)

            total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)

            print(f"\n📊 Cobertura total: {total_coverage:.1f}%")

            # Mostrar cobertura por módulo
            print(f"\n📦 Cobertura por módulo:")
            for file_path, file_data in coverage_data.get("files", {}).items():
                if file_path.startswith("app/"):
                    module_name = file_path.replace("app/", "").replace(".py", "")
                    summary = file_data.get("summary", {})
                    covered = summary.get("num_statements", 0)
                    missing = summary.get("num_missing", 0)
                    total = covered + missing
                    if total > 0:
                        percent = (covered / total) * 100
                        print(f"   {module_name}: {percent:.1f}% ({covered}/{total})")

            # Verificar requisito
            required_coverage = 70.0
            coverage_ok = total_coverage >= required_coverage

            print("\n" + "=" * 80)
            print("✅ VERIFICACIÓN COBERTURA TESTS")
            print("=" * 80)

            if coverage_ok:
                print(
                    f"✅ Cobertura >= {required_coverage:.0%}: CUMPLIDO ({total_coverage:.1f}%)"
                )
            else:
                print(
                    f"❌ Cobertura >= {required_coverage:.0%}: NO CUMPLIDO ({total_coverage:.1f}%)"
                )

            if total_coverage < required_coverage:
                print(f"\n⚠️  Módulos con baja cobertura:")
                for file_path, file_data in coverage_data.get("files", {}).items():
                    if file_path.startswith("app/"):
                        module_name = file_path.replace("app/", "").replace(".py", "")
                        summary = file_data.get("summary", {})
                        covered = summary.get("num_statements", 0)
                        missing = summary.get("num_missing", 0)
                        total = covered + missing
                        if total > 0:
                            percent = (covered / total) * 100
                            if percent < required_coverage:
                                print(f"   ❌ {module_name}: {percent:.1f}%")

            return coverage_ok

        else:
            print("❌ No se pudo generar reporte de coverage")
            return False

    except Exception as e:
        print(f"❌ Error verificando cobertura: {e}")
        return False


def check_load_capacity():
    """Verifica que el sistema soporte 50 usuarios concurrentes."""

    print("\n" + "=" * 80)
    print("⚡ VERIFICANDO CAPACIDAD DE CARGA (50 usuarios concurrentes)")
    print("=" * 80)

    try:
        # Ejecutar script de carga
        result = subprocess.run(
            [sys.executable, "load_test.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error ejecutando pruebas de carga: {e}")
        return False


def main():
    """Función principal."""

    print("🔍 VERIFICACIÓN DE REQUISITOS DEL INFORME DE TÍTULO")
    print("=" * 80)

    # Verificar cada requisito
    ml_ok = check_ml_metrics()
    coverage_ok = check_test_coverage()
    load_ok = check_load_capacity()

    # Resumen final
    print("\n" + "=" * 80)
    print("📋 RESUMEN FINAL")
    print("=" * 80)

    requirements = [
        ("Accuracy ML >= 85% (F1-Score)", ml_ok),
        ("Cobertura tests >= 70%", coverage_ok),
        ("Carga 50 usuarios concurrentes", load_ok),
    ]

    for requirement, passed in requirements:
        status = "✅" if passed else "❌"
        print(f"{status} {requirement}")

    all_passed = all(passed)

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 TODOS LOS REQUISITOS CUMPLIDOS - INFORME DE TÍTULO APROBADO")
    else:
        print("⚠️  ALGUNOS REQUISITOS NO CUMPLIDOS - REVISAR ANTES DE LA DEFENSA")
    print("=" * 80)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

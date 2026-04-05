"""Evaluación simple del modelo MVP."""

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from app.ml.generate_dataset import generate_synthetic_dataset
from app.ml.train import FEATURES


def evaluate_model() -> dict[str, float]:
    """Retorna métricas básicas del modelo."""

    dataset = generate_synthetic_dataset()
    x_train, x_test, y_train, y_test = train_test_split(
        dataset[FEATURES], dataset["riesgo"], test_size=0.2, random_state=42
    )
    model = RandomForestClassifier(n_estimators=25, random_state=42)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
    }


if __name__ == "__main__":
    print(evaluate_model())

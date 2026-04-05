"""Tests de predicciones y utilidades ML."""

from app.ml.generate_dataset import generate_synthetic_dataset
from app.ml.predict import predict_from_record


def test_get_prediction_endpoint(client):
    """Valida la respuesta demo de predicción."""

    response = client.get("/predicciones/1")
    assert response.status_code == 200
    assert response.json()["clasificacion"] in {"normal", "alerta", "falla"}


def test_ml_helpers_generate_and_predict():
    """Valida el pipeline mínimo de dataset y predicción."""

    dataset = generate_synthetic_dataset(size=20)
    record = dataset.iloc[0].to_dict()
    prediction = predict_from_record(record)
    assert prediction in {0, 1}

"""Endpoints de umbrales."""

from fastapi import APIRouter

from app.schemas.umbral import UmbralCreate, UmbralResponse, UmbralUpdate

router = APIRouter(prefix="/umbrales", tags=["umbrales"])


@router.get("", response_model=list[UmbralResponse])
def get_umbrales() -> list[UmbralResponse]:
    """Lista umbrales demo."""

    return [
        UmbralResponse(
            id=1, equipo_id=1, variable="temperatura", valor_min=10.0, valor_max=50.0
        )
    ]


@router.post("", response_model=UmbralResponse)
def post_umbral(payload: UmbralCreate) -> UmbralResponse:
    """Crea un umbral demo."""

    return UmbralResponse(id=2, **payload.model_dump())


@router.put("/{umbral_id}", response_model=UmbralResponse)
def put_umbral(umbral_id: int, payload: UmbralUpdate) -> UmbralResponse:
    """Actualiza un umbral demo."""

    data = {
        "equipo_id": 1,
        "variable": "temperatura",
        "valor_min": 10.0,
        "valor_max": 50.0,
    }
    data.update(
        {key: value for key, value in payload.model_dump().items() if value is not None}
    )
    return UmbralResponse(id=umbral_id, **data)

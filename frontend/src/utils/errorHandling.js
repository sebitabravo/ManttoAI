export function getApiErrorMessage(error, fallbackMessage) {
  const backendDetail = error?.response?.data?.detail;

  if (typeof backendDetail === "string" && backendDetail.trim()) {
    return backendDetail;
  }

  if (Array.isArray(backendDetail) && backendDetail.length > 0) {
    // FastAPI devuelve errores de validación como array; mostrar el primer mensaje legible
    const first = backendDetail[0];
    if (typeof first === "string" && first.trim()) return first;
    if (typeof first?.msg === "string" && first.msg.trim()) return first.msg;
    return fallbackMessage;
  }

  if (typeof error?.message === "string" && error.message.trim()) {
    return error.message;
  }

  return fallbackMessage;
}

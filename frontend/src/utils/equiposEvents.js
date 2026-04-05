export const EQUIPOS_REFRESH_EVENT = "manttoai:equipos:refresh";

export function notifyEquiposRefresh() {
  if (typeof window === "undefined") {
    return;
  }

  window.dispatchEvent(new Event(EQUIPOS_REFRESH_EVENT));
}

export function subscribeEquiposRefresh(listener) {
  if (typeof window === "undefined") {
    return () => {};
  }

  window.addEventListener(EQUIPOS_REFRESH_EVENT, listener);

  return () => {
    window.removeEventListener(EQUIPOS_REFRESH_EVENT, listener);
  };
}

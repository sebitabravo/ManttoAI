export const MANTENCIONES_REFRESH_EVENT = "manttoai:mantenciones:refresh";

export function notifyMantencionesRefresh() {
  if (typeof window === "undefined") {
    return;
  }

  window.dispatchEvent(new Event(MANTENCIONES_REFRESH_EVENT));
}

export function subscribeMantencionesRefresh(listener) {
  if (typeof window === "undefined") {
    return () => {};
  }

  window.addEventListener(MANTENCIONES_REFRESH_EVENT, listener);

  return () => {
    window.removeEventListener(MANTENCIONES_REFRESH_EVENT, listener);
  };
}

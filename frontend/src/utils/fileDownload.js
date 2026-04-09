/**
 * Dispara la descarga de un Blob en el navegador.
 */
export function triggerFileDownload(blob, filename) {
  const safeFilename =
    typeof filename === "string"
      ? filename.replace(/[\r\n"]/g, "_")
      : "reporte";
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = downloadUrl;
  link.download = safeFilename;
  link.style.display = "none";
  link.setAttribute("aria-hidden", "true");
  document.body.appendChild(link);
  link.click();

  // En algunos navegadores (ej. Safari), revocar inmediatamente puede
  // generar descargas vacías/corruptas. Se difiere la limpieza.
  window.setTimeout(() => {
    window.URL.revokeObjectURL(downloadUrl);
    link.remove();
  }, 1500);
}

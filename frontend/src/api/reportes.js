import client from "./client";

function resolveFilename(contentDisposition, fallbackFilename) {
  if (!contentDisposition) {
    return fallbackFilename;
  }

  const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match?.[1]) {
    return decodeURIComponent(utf8Match[1]);
  }

  const simpleMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
  if (simpleMatch?.[1]) {
    return simpleMatch[1];
  }

  return fallbackFilename;
}

async function downloadReportFile(url, { params = {}, fallbackFilename }) {
  const response = await client.get(url, {
    params,
    responseType: "blob",
  });

  return {
    blob: response.data,
    filename: resolveFilename(
      response.headers?.["content-disposition"],
      fallbackFilename
    ),
  };
}

export async function downloadLecturasCsv({ equipoId = null, limit = 5000 } = {}) {
  const params = { limit };
  if (equipoId !== null && equipoId !== undefined) {
    params.equipo_id = equipoId;
  }

  return downloadReportFile("/reportes/lecturas.csv", {
    params,
    fallbackFilename: "manttoai_lecturas.csv",
  });
}

export async function downloadAlertasCsv({
  equipoId = null,
  soloNoLeidas = false,
  limit = 5000,
} = {}) {
  const params = {
    solo_no_leidas: soloNoLeidas,
    limit,
  };
  if (equipoId !== null && equipoId !== undefined) {
    params.equipo_id = equipoId;
  }

  return downloadReportFile("/reportes/alertas.csv", {
    params,
    fallbackFilename: "manttoai_alertas.csv",
  });
}

export async function downloadMantencionesCsv({
  equipoId = null,
  limit = 5000,
  order = "desc",
} = {}) {
  const params = {
    limit,
    order,
  };
  if (equipoId !== null && equipoId !== undefined) {
    params.equipo_id = equipoId;
  }

  return downloadReportFile("/reportes/mantenciones.csv", {
    params,
    fallbackFilename: "manttoai_mantenciones.csv",
  });
}

export async function downloadInformeEjecutivoPdf() {
  return downloadReportFile("/reportes/ejecutivo.pdf", {
    fallbackFilename: "manttoai_informe_ejecutivo.pdf",
  });
}

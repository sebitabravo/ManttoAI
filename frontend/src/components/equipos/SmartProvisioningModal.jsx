import { useState, useEffect } from "react";
import Modal from "../ui/Modal";
import Button from "../ui/Button";
import client from "../../api/client";

export default function SmartProvisioningModal({ open, onClose }) {
  const [token, setToken] = useState(null);
  const [qrUrl, setQrUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open) return;

    setLoading(true);
    setError(null);
    // Obtener token desde backend
    client
      .get("/equipos/provisioning-token")
      .then((res) => {
        const t = res.data?.token;
        setToken(t);
        // Construir payload que el ESP32 deberá leer del QR.
        // Usamos formato simple JSON con token; el dispositivo se encargará de usarlo.
        const payload = encodeURIComponent(JSON.stringify({ token: t }));
        const url = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${payload}`;
        setQrUrl(url);
      })
      .catch((err) => {
        setError("No se pudo generar token. Revisá permisos.");
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, [open]);

  return (
    <Modal open={open} title="Smart Provisioning" onClose={onClose}>
      <div>
        <p className="text-sm text-neutral-700 mb-3">
          Escaneá este QR con el asistente de provisioning del dispositivo (SoftAP).
        </p>

        {loading ? (
          <p>Cargando...</p>
        ) : error ? (
          <div className="text-sm text-warning-700">{error}</div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            {qrUrl ? (
              <img src={qrUrl} alt="QR provisioning" width={200} height={200} />
            ) : (
              <div className="h-[200px] w-[200px] bg-neutral-100 flex items-center justify-center">QR</div>
            )}

            <div className="text-xs text-neutral-500">
              Token (solo para registro): <code className="break-all">{token}</code>
            </div>

            <div className="flex gap-2">
              <Button onClick={onClose} variant="outline">Cerrar</Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}

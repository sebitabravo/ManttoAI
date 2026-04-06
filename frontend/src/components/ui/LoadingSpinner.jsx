export default function LoadingSpinner({ label = "Cargando..." }) {
  return (
    <div role="status" aria-live="polite" aria-busy="true">
      {label}
    </div>
  );
}

export default function LoadingSpinner({ label = "Cargando..." }) {
  return <div aria-busy="true">{label}</div>;
}

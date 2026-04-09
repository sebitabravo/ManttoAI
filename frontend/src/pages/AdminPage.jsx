import { useState, useEffect } from "react";
import useAuth from "../hooks/useAuth";
import { getUsers, createUser, updateUser, deleteUser } from "../api/admin";
import { getApiKeys, createApiKey, revokeApiKey } from "../api/admin";
import { getAuditLogs } from "../api/admin";
import Button from "../components/ui/Button";
import Modal from "../components/ui/Modal";
import Input from "../components/ui/Input";
import EmptyState from "../components/ui/EmptyState";

function AdminPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("usuarios");
  const [users, setUsers] = useState([]);
  const [apiKeys, setApiKeys] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [newApiKey, setNewApiKey] = useState(null);
  const [userForm, setUserForm] = useState({ nombre: "", email: "", password: "", rol: "visualizador" });
  const [apiKeyForm, setApiKeyForm] = useState({ device_id: "" });

  // Cargar datos según tab activa
  useEffect(() => {
    if (activeTab === "usuarios") loadUsers();
    if (activeTab === "api-keys") loadApiKeys();
    if (activeTab === "audit-logs") loadAuditLogs();
  }, [activeTab]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await getUsers();
      setUsers(data.usuarios || []);
    } catch (error) {
      console.error("Error cargando usuarios:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadApiKeys = async () => {
    try {
      setLoading(true);
      const data = await getApiKeys();
      setApiKeys(data || []);
    } catch (error) {
      console.error("Error cargando API keys:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadAuditLogs = async () => {
    try {
      setLoading(true);
      const data = await getAuditLogs();
      setAuditLogs(data.logs || []);
    } catch (error) {
      console.error("Error cargando audit logs:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await createUser(userForm);
      setShowUserModal(false);
      setUserForm({ nombre: "", email: "", password: "", rol: "visualizador" });
      loadUsers();
    } catch (error) {
      alert("Error creando usuario: " + error.message);
    }
  };

  const handleCreateApiKey = async (e) => {
    e.preventDefault();
    try {
      const data = await createApiKey(apiKeyForm);
      setNewApiKey(data.key);
      setShowApiKeyModal(false);
      setApiKeyForm({ device_id: "" });
      loadApiKeys();
    } catch (error) {
      alert("Error creando API key: " + error.message);
    }
  };

  const handleRevokeApiKey = async (keyId) => {
    if (!confirm("¿Estás seguro de revocar esta API key?")) return;
    try {
      await revokeApiKey(keyId);
      loadApiKeys();
    } catch (error) {
      alert("Error revocando API key: " + error.message);
    }
  };

  const getRoleBadgeClass = (rol) => {
    switch (rol) {
      case "admin":
        return "bg-red-100 text-red-800";
      case "tecnico":
        return "bg-yellow-100 text-yellow-800";
      case "visualizador":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading && users.length === 0 && apiKeys.length === 0) {
    return <div className="p-8 text-center text-sm text-neutral-600">Cargando...</div>;
  }

  return (
    <section className="grid grid-cols-1 gap-4">
      <div>
        <h1 className="m-0 text-xl font-semibold text-neutral-900">Panel de Administración</h1>
        <p className="mb-0 mt-1.5 text-sm text-neutral-600">
          Gestión de usuarios, API keys y auditoría.
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-neutral-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab("usuarios")}
            className={`${
              activeTab === "usuarios"
                ? "border-primary-500 text-primary-600"
                : "border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Usuarios
          </button>
          <button
            onClick={() => setActiveTab("api-keys")}
            className={`${
              activeTab === "api-keys"
                ? "border-primary-500 text-primary-600"
                : "border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            API Keys
          </button>
          <button
            onClick={() => setActiveTab("audit-logs")}
            className={`${
              activeTab === "audit-logs"
                ? "border-primary-500 text-primary-600"
                : "border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300"
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Audit Logs
          </button>
        </nav>
      </div>

      {/* Tab Content: Usuarios */}
      {activeTab === "usuarios" && (
        <div className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
          <div className="mb-4 flex justify-end">
            <Button onClick={() => setShowUserModal(true)}>Nuevo Usuario</Button>
          </div>

          {users.length === 0 ? (
            <EmptyState title="No hay usuarios" description="Crea tu primer usuario" />
          ) : (
            <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
              <table className="min-w-full divide-y divide-neutral-200">
                <thead className="bg-neutral-100">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Nombre</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Rol</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Creado</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">Acciones</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-neutral-200">
                  {users.map((usuario) => (
                    <tr key={usuario.id}>
                      <td className="px-6 py-4 whitespace-nowrap">{usuario.nombre}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{usuario.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadgeClass(usuario.rol)}`}>
                          {usuario.rol}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                        {usuario.created_at
                          ? new Date(usuario.created_at).toLocaleDateString()
                          : "-"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => {
                            const nuevoRol = usuario.rol === "admin" ? "visualizador" : "admin";
                            updateUser(usuario.id, { rol: nuevoRol }).then(loadUsers);
                          }}
                          className="text-indigo-600 hover:text-indigo-900 mr-4"
                        >
                          Cambiar Rol
                        </button>
                        {usuario.id !== user.id && (
                          <button
                            onClick={() => {
                              if (confirm("¿Eliminar usuario?")) {
                                deleteUser(usuario.id).then(loadUsers);
                              }
                            }}
                            className="text-red-600 hover:text-red-900"
                          >
                            Eliminar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab Content: API Keys */}
      {activeTab === "api-keys" && (
        <div className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
          <div className="mb-4 flex justify-end">
            <Button onClick={() => setShowApiKeyModal(true)}>Nueva API Key</Button>
          </div>

          {apiKeys.length === 0 ? (
            <EmptyState title="No hay API keys" description="Crea tu primera API key para dispositivos IoT" />
          ) : (
            <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
              <table className="min-w-full divide-y divide-neutral-200">
                <thead className="bg-neutral-100">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Prefix</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Device ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Estado</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Creado</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">Acciones</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-neutral-200">
                  {apiKeys.map((apiKey) => (
                    <tr key={apiKey.id}>
                      <td className="px-6 py-4 whitespace-nowrap font-mono text-sm">{apiKey.key_prefix}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{apiKey.device_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${apiKey.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                          {apiKey.is_active ? "Activo" : "Revocado"}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                        {new Date(apiKey.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {apiKey.is_active && (
                          <button
                            onClick={() => handleRevokeApiKey(apiKey.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Revocar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab Content: Audit Logs */}
      {activeTab === "audit-logs" && (
        <div className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
          {auditLogs.length === 0 ? (
            <EmptyState title="No hay audit logs" description="Los logs de auditoría aparecerán aquí" />
          ) : (
            <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
              <table className="min-w-full divide-y divide-neutral-200">
                <thead className="bg-neutral-100">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Fecha</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Acción</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Entidad</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Usuario ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">IP</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-neutral-200">
                  {auditLogs.map((log) => (
                    <tr key={log.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                          {log.action}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {log.entity_type}{log.entity_id && ` #${log.entity_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                        {log.usuario_id || "-"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                        {log.ip_address || "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Modal: Nuevo Usuario */}
      <Modal open={showUserModal} onClose={() => setShowUserModal(false)} title="Nuevo Usuario">
        <form onSubmit={handleCreateUser} className="space-y-4">
          <div>
              <label className="block text-sm font-medium text-neutral-700">Nombre</label>
            <Input
              type="text"
              value={userForm.nombre}
              onChange={(e) => setUserForm({ ...userForm, nombre: e.target.value })}
              required
            />
          </div>
          <div>
              <label className="block text-sm font-medium text-neutral-700">Email</label>
            <Input
              type="email"
              value={userForm.email}
              onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
              required
            />
          </div>
          <div>
              <label className="block text-sm font-medium text-neutral-700">Contraseña</label>
            <Input
              type="password"
              value={userForm.password}
              onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
              required
              minLength={8}
            />
          </div>
          <div>
              <label className="block text-sm font-medium text-neutral-700">Rol</label>
            <select
              value={userForm.rol}
              onChange={(e) => setUserForm({ ...userForm, rol: e.target.value })}
               className="mt-1 block w-full rounded-md border-neutral-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm border p-2"
            >
              <option value="admin">Admin</option>
              <option value="tecnico">Técnico</option>
              <option value="visualizador">Visualizador</option>
            </select>
          </div>
          <div className="flex justify-end space-x-3">
            <Button type="button" variant="secondary" onClick={() => setShowUserModal(false)}>
              Cancelar
            </Button>
            <Button type="submit">Crear Usuario</Button>
          </div>
        </form>
      </Modal>

      {/* Modal: Nueva API Key */}
      <Modal open={showApiKeyModal} onClose={() => setShowApiKeyModal(false)} title="Nueva API Key">
        <form onSubmit={handleCreateApiKey} className="space-y-4">
          <div>
              <label className="block text-sm font-medium text-neutral-700">Device ID</label>
            <Input
              type="text"
              value={apiKeyForm.device_id}
              onChange={(e) => setApiKeyForm({ ...apiKeyForm, device_id: e.target.value })}
              placeholder="ej: esp32_001"
              required
            />
            <p className="mt-1 text-sm text-neutral-500">Identificador único del dispositivo IoT</p>
          </div>
          <div className="flex justify-end space-x-3">
            <Button type="button" variant="secondary" onClick={() => setShowApiKeyModal(false)}>
              Cancelar
            </Button>
            <Button type="submit">Crear API Key</Button>
          </div>
        </form>
      </Modal>

      {/* Modal: API Key Creada */}
      <Modal open={!!newApiKey} onClose={() => setNewApiKey(null)} title="API Key Creada">
        <div className="space-y-4">
          <p className="text-sm text-neutral-600">
            Esta es tu API key. <strong className="text-red-600">Guárdala ahora</strong>, no se volverá a mostrar.
          </p>
          <div className="bg-neutral-100 p-4 rounded-md">
            <code className="text-sm font-mono break-all">{newApiKey}</code>
          </div>
          <div className="flex justify-end space-x-3">
            <Button
              onClick={() => {
                navigator.clipboard.writeText(newApiKey);
                alert("API Key copiada al portapapeles");
              }}
            >
              Copiar
            </Button>
            <Button variant="secondary" onClick={() => setNewApiKey(null)}>
              Cerrar
            </Button>
          </div>
        </div>
      </Modal>
    </section>
  );
}

export default AdminPage;

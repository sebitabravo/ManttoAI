import { useState, useEffect, useCallback, useRef } from "react";
import useAuth from "../hooks/useAuth";
import { getUsers, createUser, updateUser, deleteUser } from "../api/admin";
import { getApiKeys, createApiKey, revokeApiKey } from "../api/admin";
import { getAuditLogs } from "../api/admin";
import Button from "../components/ui/Button";
import Modal from "../components/ui/Modal";
import Input from "../components/ui/Input";
import EmptyState from "../components/ui/EmptyState";
import { selectClassName } from "../utils/formStyles";

// Lista de prefijos telefónicos de Latinoamérica
const PAISES_TELEFONO = [
  { codigo: "+54", pais: "Argentina", bandera: "🇦🇷" },
  { codigo: "+56", pais: "Chile", bandera: "🇨🇱" },
  { codigo: "+51", pais: "Perú", bandera: "🇵🇪" },
  { codigo: "+57", pais: "Colombia", bandera: "🇨🇴" },
  { codigo: "+55", pais: "Brasil", bandera: "🇧🇷" },
];

function AdminPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("usuarios");
  const [users, setUsers] = useState([]);
  const [apiKeys, setApiKeys] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loadingByTab, setLoadingByTab] = useState({
    usuarios: true,
    "api-keys": true,
    "audit-logs": true,
  });
  const [showUserModal, setShowUserModal] = useState(false);
  const [showEditUserModal, setShowEditUserModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [newApiKey, setNewApiKey] = useState(null);
  const [userForm, setUserForm] = useState({ nombre: "", email: "", password: "", telefono: "", prefijo: "+56", rol: "visualizador" });
  const [editUserForm, setEditUserForm] = useState({ nombre: "", email: "", telefono: "", prefijo: "+56", rol: "visualizador" });
  const [apiKeyForm, setApiKeyForm] = useState({ device_id: "" });
  const [feedback, setFeedback] = useState({ type: "", message: "" });
  const [confirmDeleteUser, setConfirmDeleteUser] = useState(null);
  const [confirmRevokeKey, setConfirmRevokeKey] = useState(null);
  const [isDeletingUser, setIsDeletingUser] = useState(false);
  const [isRevokingApiKey, setIsRevokingApiKey] = useState(false);
  const pendingLoadsRef = useRef({
    usuarios: 0,
    "api-keys": 0,
    "audit-logs": 0,
  });

  // Auto-dismiss feedback después de 4 segundos
  useEffect(() => {
    if (!feedback.message) return;
    const timer = setTimeout(() => setFeedback({ type: "", message: "" }), 4000);
    return () => clearTimeout(timer);
  }, [feedback]);

  const showFeedback = useCallback((type, message) => {
    setFeedback({ type, message });
  }, []);

  const beginTabLoad = useCallback((tab) => {
    pendingLoadsRef.current[tab] = (pendingLoadsRef.current[tab] || 0) + 1;
    setLoadingByTab((current) => ({ ...current, [tab]: true }));
  }, []);

  const endTabLoad = useCallback((tab) => {
    const nextCount = Math.max((pendingLoadsRef.current[tab] || 1) - 1, 0);
    pendingLoadsRef.current[tab] = nextCount;

    if (nextCount === 0) {
      setLoadingByTab((current) => ({ ...current, [tab]: false }));
    }
  }, []);

  const loadUsers = useCallback(async () => {
    beginTabLoad("usuarios");
    try {
      const data = await getUsers();
      setUsers(data.usuarios || []);
    } catch (error) {
      showFeedback("error", "Error cargando usuarios: " + (error.message || "desconocido"));
    } finally {
      endTabLoad("usuarios");
    }
  }, [beginTabLoad, endTabLoad, showFeedback]);

  const loadApiKeys = useCallback(async () => {
    beginTabLoad("api-keys");
    try {
      const data = await getApiKeys();
      setApiKeys(data || []);
    } catch (error) {
      showFeedback("error", "Error cargando API keys: " + (error.message || "desconocido"));
    } finally {
      endTabLoad("api-keys");
    }
  }, [beginTabLoad, endTabLoad, showFeedback]);

  const loadAuditLogs = useCallback(async () => {
    beginTabLoad("audit-logs");
    try {
      const data = await getAuditLogs();
      setAuditLogs(data.logs || []);
    } catch (error) {
      showFeedback("error", "Error cargando audit logs: " + (error.message || "desconocido"));
    } finally {
      endTabLoad("audit-logs");
    }
  }, [beginTabLoad, endTabLoad, showFeedback]);

  // Cargar datos según tab activa
  useEffect(() => {
    if (activeTab === "usuarios") loadUsers();
    if (activeTab === "api-keys") loadApiKeys();
    if (activeTab === "audit-logs") loadAuditLogs();
  }, [activeTab, loadUsers, loadApiKeys, loadAuditLogs]);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      // Validar teléfono si se proporciona
      const telefono = userForm.telefono?.trim();
      if (telefono) {
        const telefonoRegex = /^(\+56\s?)?9\d{8}$|^\+56\s?9\s?\d{4}\s?\d{4}$/;
        if (!telefonoRegex.test(telefono)) {
          showFeedback("error", "Teléfono inválido. Formato: +56 9XXXXXXXX (ej: +56912345678)");
          return;
        }
      }
      // Combinar prefijo + teléfono para crear usuario
      const telefonoCompleto = userForm.telefono ? `${userForm.prefijo}${userForm.telefono}` : "";
      await createUser({ ...userForm, telefono: telefonoCompleto });
      setShowUserModal(false);
      setUserForm({ nombre: "", email: "", password: "", telefono: "", prefijo: "+56", rol: "visualizador" });
      showFeedback("success", "Usuario creado exitosamente");
      loadUsers();
    } catch (error) {
      showFeedback("error", "Error creando usuario: " + (error.message || "desconocido"));
    }
  };

  // Abrir modal de edición de usuario
  const handleEditUserClick = (usuario) => {
    // Extraer prefijo del teléfono existente o usar Chile por defecto
    let prefijo = "+56";
    let telefonoLimpio = usuario.telefono || "";
    
    for (const pais of PAISES_TELEFONO) {
      if (usuario.telefono?.startsWith(pais.codigo)) {
        prefijo = pais.codigo;
        telefonoLimpio = usuario.telefono.slice(pais.codigo.length).trim();
        break;
      }
    }
    
    setEditingUser(usuario);
    setEditUserForm({
      nombre: usuario.nombre || "",
      email: usuario.email || "",
      telefono: telefonoLimpio,
      prefijo: prefijo,
      rol: usuario.rol || "visualizador",
    });
    setShowEditUserModal(true);
  };

  // Guardar cambios del usuario
  const handleUpdateUser = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    // Validar teléfono si se proporciona
    const telefono = editUserForm.telefono?.trim();
    if (telefono) {
      // Validar según el prefijo seleccionado (8-9 dígitos según el país)
      const digitosEsperados = editUserForm.prefijo === "+55" ? 9 : 8; // Brasil 9 dígitos, resto 8
      const digitosRegex = new RegExp(`^\\d{${digitosEsperados}}$`);
      
      if (!digitosRegex.test(telefono)) {
        const pais = PAISES_TELEFONO.find(p => p.codigo === editUserForm.prefijo);
        showFeedback("error", `Teléfono inválido para ${pais?.pais || editUserForm.prefijo}. Necesitas ${digitosEsperados} dígitos.`);
        return;
      }
    }

    try {
      // Combinar prefijo + teléfono
      const telefonoCompleto = telefono ? `${editUserForm.prefijo}${telefono}` : null;
      const dataToUpdate = {
        nombre: editUserForm.nombre,
        email: editUserForm.email,
        telefono: telefonoCompleto,
        rol: editUserForm.rol,
      };
      await updateUser(editingUser.id, dataToUpdate);
      setShowEditUserModal(false);
      setEditingUser(null);
      showFeedback("success", "Usuario actualizado exitosamente");
      loadUsers();
    } catch (error) {
      showFeedback("error", "Error actualizando usuario: " + (error.message || "desconocido"));
    }
  };

  const handleCreateApiKey = async (e) => {
    e.preventDefault();
    try {
      const data = await createApiKey(apiKeyForm);
      setNewApiKey(data.key);
      setShowApiKeyModal(false);
      setApiKeyForm({ device_id: "" });
      showFeedback("success", "API Key creada exitosamente");
      loadApiKeys();
    } catch (error) {
      showFeedback("error", "Error creando API key: " + (error.message || "desconocido"));
    }
  };

  const handleRevokeApiKey = async (keyId) => {
    if (!keyId || isRevokingApiKey) return;

    setIsRevokingApiKey(true);
    try {
      await revokeApiKey(keyId);
      setConfirmRevokeKey(null);
      showFeedback("success", "API Key revocada exitosamente");
      loadApiKeys();
    } catch (error) {
      showFeedback("error", "Error revocando API key: " + (error.message || "desconocido"));
    } finally {
      setIsRevokingApiKey(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!userId || isDeletingUser) return;

    setIsDeletingUser(true);
    try {
      await deleteUser(userId);
      setConfirmDeleteUser(null);
      showFeedback("success", "Usuario eliminado exitosamente");
      loadUsers();
    } catch (error) {
      showFeedback("error", "Error eliminando usuario: " + (error.message || "desconocido"));
    } finally {
      setIsDeletingUser(false);
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

  return (
    <section data-tour="admin-contenido" className="grid grid-cols-1 gap-4">
      <div>
        <h1 className="m-0 text-xl font-semibold text-neutral-900">Panel de Administración</h1>
        <p className="mb-0 mt-1.5 text-sm text-neutral-600">
          Gestión de usuarios, API keys y auditoría.
        </p>
      </div>

      {/* Feedback banner */}
      {feedback.message ? (
        <div
          role="alert"
          className={`rounded-lg border px-3 py-2 text-sm ${
            feedback.type === "error"
              ? "border-danger-300 bg-danger-50 text-danger-800"
              : "border-success-300 bg-success-50 text-success-800"
          }`}
        >
          {feedback.message}
        </div>
      ) : null}

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

          {loadingByTab.usuarios && users.length === 0 ? (
            <div className="rounded-lg border border-neutral-200 bg-white p-8 text-center text-sm text-neutral-600">
              Cargando usuarios...
            </div>
          ) : users.length === 0 ? (
            <EmptyState title="No hay usuarios" description="Crea tu primer usuario" />
          ) : (
            <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
              <table className="min-w-full divide-y divide-neutral-200">
                <thead className="bg-neutral-100">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Nombre</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Teléfono</th>
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
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                        {usuario.telefono || "-"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleEditUserClick(usuario)}
                          className="text-indigo-600 hover:text-indigo-900 mr-4"
                        >
                          Editar
                        </button>
                        {usuario.id !== user.id && (
                          <button
                            onClick={() => setConfirmDeleteUser(usuario.id)}
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

          {loadingByTab["api-keys"] && apiKeys.length === 0 ? (
            <div className="rounded-lg border border-neutral-200 bg-white p-8 text-center text-sm text-neutral-600">
              Cargando API keys...
            </div>
          ) : apiKeys.length === 0 ? (
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
                            onClick={() => setConfirmRevokeKey(apiKey.id)}
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
          {loadingByTab["audit-logs"] && auditLogs.length === 0 ? (
            <div className="rounded-lg border border-neutral-200 bg-white p-8 text-center text-sm text-neutral-600">
              Cargando audit logs...
            </div>
          ) : auditLogs.length === 0 ? (
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
            <label htmlFor="user-rol" className="block text-sm font-medium text-neutral-700">Rol</label>
            <select
              id="user-rol"
              value={userForm.rol}
              onChange={(e) => setUserForm({ ...userForm, rol: e.target.value })}
              className={`${selectClassName} mt-1`}
            >
              <option value="admin">Admin</option>
              <option value="tecnico">Técnico</option>
              <option value="visualizador">Visualizador</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700">Teléfono (opcional)</label>
            <div className="flex gap-2">
              <select
                value={userForm.prefijo}
                onChange={(e) => setUserForm({ ...userForm, prefijo: e.target.value })}
                className={`${selectClassName} w-24`}
              >
                {PAISES_TELEFONO.map((pais) => (
                  <option key={pais.codigo} value={pais.codigo}>
                    {pais.bandera} {pais.codigo}
                  </option>
                ))}
              </select>
              <Input
                type="tel"
                value={userForm.telefono}
                onChange={(e) => setUserForm({ ...userForm, telefono: e.target.value })}
                placeholder="9XXXXXXX"
                className="flex-1"
              />
            </div>
          </div>
          <div className="flex justify-end space-x-3">
            <Button type="button" variant="secondary" onClick={() => setShowUserModal(false)}>
              Cancelar
            </Button>
            <Button type="submit">Crear Usuario</Button>
          </div>
        </form>
      </Modal>

      {/* Modal: Editar Usuario */}
      <Modal open={showEditUserModal} onClose={() => setShowEditUserModal(false)} title="Editar Usuario">
        <form onSubmit={handleUpdateUser} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700">Nombre</label>
            <Input
              type="text"
              value={editUserForm.nombre}
              onChange={(e) => setEditUserForm({ ...editUserForm, nombre: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700">Email</label>
            <Input
              type="email"
              value={editUserForm.email}
              onChange={(e) => setEditUserForm({ ...editUserForm, email: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700">Teléfono</label>
            <div className="flex gap-2">
              <select
                value={editUserForm.prefijo}
                onChange={(e) => setEditUserForm({ ...editUserForm, prefijo: e.target.value })}
                className={`${selectClassName} w-24`}
              >
                {PAISES_TELEFONO.map((pais) => (
                  <option key={pais.codigo} value={pais.codigo}>
                    {pais.bandera} {pais.codigo}
                  </option>
                ))}
              </select>
              <Input
                type="tel"
                value={editUserForm.telefono}
                onChange={(e) => setEditUserForm({ ...editUserForm, telefono: e.target.value })}
                placeholder="9XXXXXXX"
                className="flex-1"
              />
            </div>
          </div>
          <div>
            <label htmlFor="edit-user-rol" className="block text-sm font-medium text-neutral-700">Rol</label>
            <select
              id="edit-user-rol"
              value={editUserForm.rol}
              onChange={(e) => setEditUserForm({ ...editUserForm, rol: e.target.value })}
              className={`${selectClassName} mt-1`}
            >
              <option value="admin">Admin</option>
              <option value="tecnico">Técnico</option>
              <option value="visualizador">Visualizador</option>
            </select>
          </div>
          <div className="flex justify-end space-x-3">
            <Button type="button" variant="secondary" onClick={() => setShowEditUserModal(false)}>
              Cancelar
            </Button>
            <Button type="submit">Guardar Cambios</Button>
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
                showFeedback("success", "API Key copiada al portapapeles");
                setNewApiKey(null);
              }}
            >
              Copiar y cerrar
            </Button>
          </div>
        </div>
      </Modal>

      {/* Modal: Confirmar eliminación de usuario */}
      <Modal
        open={!!confirmDeleteUser}
        onClose={() => {
          if (!isDeletingUser) {
            setConfirmDeleteUser(null);
          }
        }}
        title="Eliminar usuario"
      >
        <div className="space-y-4">
          <p className="text-sm text-neutral-600">
            ¿Estás seguro de que querés eliminar este usuario? Esta acción no se puede deshacer.
          </p>
          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => setConfirmDeleteUser(null)}
              disabled={isDeletingUser}
            >
              Cancelar
            </Button>
            <Button
              type="button"
              variant="danger"
              onClick={() => handleDeleteUser(confirmDeleteUser)}
              disabled={isDeletingUser}
            >
              {isDeletingUser ? "Eliminando..." : "Eliminar"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Modal: Confirmar revocar API key */}
      <Modal
        open={!!confirmRevokeKey}
        onClose={() => {
          if (!isRevokingApiKey) {
            setConfirmRevokeKey(null);
          }
        }}
        title="Revocar API Key"
      >
        <div className="space-y-4">
          <p className="text-sm text-neutral-600">
            ¿Estás seguro de que querés revocar esta API key? El dispositivo asociado perderá acceso inmediatamente.
          </p>
          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => setConfirmRevokeKey(null)}
              disabled={isRevokingApiKey}
            >
              Cancelar
            </Button>
            <Button
              type="button"
              variant="danger"
              onClick={() => handleRevokeApiKey(confirmRevokeKey)}
              disabled={isRevokingApiKey}
            >
              {isRevokingApiKey ? "Revocando..." : "Revocar"}
            </Button>
          </div>
        </div>
      </Modal>
    </section>
  );
}

export default AdminPage;

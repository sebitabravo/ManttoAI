// Avatares disponibles para selección de perfil de usuario.
// Usado por ProfilePage.jsx (selector) y UserMenu.jsx (mapa de emojis).

export const AVATARES = [
  { id: "user", emoji: "👤", label: "Usuario" },
  { id: "person", emoji: "🧑", label: "Persona" },
  { id: "man", emoji: "👨", label: "Hombre" },
  { id: "woman", emoji: "👩", label: "Mujer" },
  { id: "robot", emoji: "🤖", label: "Robot" },
  { id: "alien", emoji: "👽", label: "Alien" },
  { id: "cat", emoji: "🐱", label: "Gato" },
  { id: "dog", emoji: "🐶", label: "Perro" },
];

// Mapa rápido para buscar emoji por ID
export const AVATAR_MAP = AVATARES.reduce((acc, av) => {
  acc[av.id] = av.emoji;
  return acc;
}, {});

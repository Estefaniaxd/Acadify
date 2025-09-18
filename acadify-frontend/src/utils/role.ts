// Definimos los roles válidos
export type Role = "admin" | "coordinador" | "profesor" | "estudiante";

// Lista de roles (por si necesitas recorrerlos en un menú, etc.)
export const Role: Role[] = ["admin", "coordinador", "profesor", "estudiante"];

// Descripciones amigables de los roles
export const ROLE_LABELS: Record<Role, string> = {
  admin: "Administrador",
  coordinador: "Coordinador",
  profesor: "Profesor",
  estudiante: "Estudiante",
};

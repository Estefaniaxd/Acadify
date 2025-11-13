/**
 * Transformadores de datos entre frontend (camelCase) y backend (snake_case)
 * 
 * Uso:
 * - toSnakeCase: Antes de enviar datos al backend
 * - toCamelCase: Después de recibir datos del backend
 */

/**
 * Convierte una cadena de camelCase a snake_case
 * Ejemplo: "colorPrimario" → "color_primario"
 */
function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
}

/**
 * Convierte una cadena de snake_case a camelCase
 * Ejemplo: "color_primario" → "colorPrimario"
 */
function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

/**
 * Convierte las claves de un objeto de camelCase a snake_case recursivamente
 * @param obj - Objeto a convertir
 * @returns Objeto con claves en snake_case
 */
export function toSnakeCase<T = unknown>(obj: unknown): T {
  if (obj === null || obj === undefined) {
    return obj as T;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => toSnakeCase(item)) as T;
  }

  // Para Dates, Blobs y otros objetos especiales, retornar tal cual
  if (obj instanceof Date) {
    return obj.toISOString() as T;
  }

  if (obj instanceof Blob) {
    return obj as T;
  }

  if (typeof obj !== 'object') {
    return obj as T;
  }

  const result: Record<string, unknown> = {};

  for (const key in obj as Record<string, unknown>) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const snakeKey = camelToSnake(key);
      result[snakeKey] = toSnakeCase((obj as Record<string, unknown>)[key]);
    }
  }

  return result as T;
}

/**
 * Convierte un objeto completo de snake_case a camelCase (recursivo)
 * 
 * @param obj - Objeto a convertir
 * @returns Objeto con keys en camelCase
 */
export function toCamelCase<T = unknown>(obj: unknown): T {
  if (obj === null || obj === undefined) {
    return obj as T;
  }

  // Si es un array, transformar cada elemento
  if (Array.isArray(obj)) {
    return obj.map((item) => toCamelCase(item)) as T;
  }

  // Si es un objeto Date o string de fecha ISO, mantener
  if (obj instanceof Date) {
    return obj as T;
  }

  // Si no es un objeto plano, retornar sin transformar
  if (typeof obj !== 'object') {
    return obj as T;
  }

  // Transformar keys del objeto
  const result: Record<string, unknown> = {};
  for (const key in obj as Record<string, unknown>) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const camelKey = snakeToCamel(key);
      const value = (obj as Record<string, unknown>)[key];

      // Recursivamente transformar el valor si es un objeto
      result[camelKey] = toCamelCase(value);
    }
  }

  return result as T;
}

/**
 * Convierte los parámetros de query (filtros) a snake_case
 * Útil para construir query strings para el backend
 * 
 * @param params - Objeto con parámetros en camelCase
 * @returns URLSearchParams con keys en snake_case
 */
export function toSnakeCaseParams(params: Record<string, unknown>): URLSearchParams {
  const searchParams = new URLSearchParams();
  const snakeCaseParams = toSnakeCase<Record<string, unknown>>(params);

  for (const [key, value] of Object.entries(snakeCaseParams)) {
    if (value !== undefined && value !== null) {
      // Si es un array, agregar cada elemento
      if (Array.isArray(value)) {
        value.forEach((item) => searchParams.append(key, String(item)));
      } else {
        searchParams.append(key, String(value));
      }
    }
  }

  return searchParams;
}

/**
 * Wrapper para axios que automáticamente transforma datos
 * Transforma request data a snake_case y response data a camelCase
 */
export function createTransformingAxiosConfig() {
  return {
    transformRequest: [
      (data: unknown) => {
        if (!data) return data;
        return toSnakeCase(data);
      },
      ...(Array.isArray(axios.defaults.transformRequest)
        ? axios.defaults.transformRequest
        : []),
    ],
    transformResponse: [
      ...(Array.isArray(axios.defaults.transformResponse)
        ? axios.defaults.transformResponse
        : []),
      (data: unknown) => {
        if (!data) return data;
        return toCamelCase(data);
      },
    ],
  };
}

// Para usar con axios
import axios from 'axios';

/**
 * Ejemplos de uso:
 * 
 * // 1. Transformar antes de enviar al backend
 * const dataParaBackend = toSnakeCase({
 *   colorPrimario: '#FF0000',
 *   numeroEstudiantes: 100
 * });
 * // Resultado: { color_primario: '#FF0000', numero_estudiantes: 100 }
 * 
 * // 2. Transformar después de recibir del backend
 * const dataDelBackend = {
 *   color_primario: '#FF0000',
 *   numero_estudiantes: 100
 * };
 * const dataParaFrontend = toCamelCase(dataDelBackend);
 * // Resultado: { colorPrimario: '#FF0000', numeroEstudiantes: 100 }
 * 
 * // 3. Construir query params
 * const filtros = {
 *   ordenarPor: 'nombre',
 *   numeroEstudiantes: 100
 * };
 * const params = toSnakeCaseParams(filtros);
 * // URL: ?ordenar_por=nombre&numero_estudiantes=100
 */

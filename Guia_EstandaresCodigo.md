# Guía de Estándares de Código

En esta guía vamos a establecer los estándares de codificación para nuestro proyecto formativo "Acadify. Nuestro actual stacik se compone de las siguientes tecnologías:

- **Python con FastAPI**
- **TypeScript**
- **React**
- **TailwindCSS**

## 1. Reglas de Nomenclatura

### Variables
- **Python y TypeScript**: Usamos `snake_case`
- **React (JSX/TSX)**: Usamos `camelCase` para variables locales

### Clases
- **Todas las tecnologías**: Utilizamos `PascalCase`

### Métodos/Funciones
- **Python**: Utilizamos `snake_case`
- **TypeScript/React**: Utilizamos `camelCase`

### Constantes
- **Todas las tecnologías**: Utilizamos `UPPER_SNAKE_CASE`

### Archivos
- **Python**: `snake_case.py`
- **TypeScript/React**: `PascalCase.tsx` para componentes, `camelCase.ts` para utilidades

## 2. Comentarios y Documentación

### Backend (Python)
- **Comentarios de varias líneas**: `"""Comentario"""`
- **Comentarios de una línea**: `# Comentario`
- **Docstrings**: Utilizamos formato Google o NumPy

### Frontend (TypeScript/React)
- **Comentarios de varias líneas**: `/* Comentario */`
- **Comentarios de una línea**: `// Comentario`
- **JSDoc**: Para documentar funciones y componentes

## 3. Indentación y Estilo

### Reglas Generales
- **Indentación**: 4 espacios (NO tabs)
- **Longitud máxima de línea**: 88 caracteres para Python, 100 para TypeScript/React
- **Líneas en blanco**: 2 líneas entre clases, 1 línea entre métodos

### Llaves y Paréntesis
- **Python**: Seguir PEP 8
- **TypeScript/React**: Estilo Allman modificado (llave de apertura en la misma línea)

## 4. Ejemplos Aceptados y No Aceptados

### Nomenclatura

#### ✅ ACEPTADO
```python
# Python
user_name = "Juan"
MAX_CONNECTIONS = 100

class UserManager:
    def get_user_data(self):
        pass
```

```typescript
// TypeScript/React
const userName = "Juan";
const MAX_CONNECTIONS = 100;

class UserManager {
    getUserData() {
        return userData;
    }
}

const UserProfile: React.FC = () => {
    return <div>Profile</div>;
};
```

#### ❌ NO ACEPTADO
```python
# Python
userName = "Juan"  # Debería ser snake_case
maxConnections = 100  # Constantes deben ser UPPER_SNAKE_CASE

class userManager:  # Debería ser PascalCase
    def GetUserData(self):  # Debería ser snake_case
        pass
```

```typescript
// TypeScript/React
const user_name = "Juan";  // Debería ser camelCase
const maxConnections = 100;  // Constantes deben ser UPPER_SNAKE_CASE

class userManager {  // Debería ser PascalCase
    get_user_data() {  // Debería ser camelCase
        return userData;
    }
}
```

### Comentarios y Documentación

#### ✅ ACEPTADO
```python
# Python
def calculate_total(items: list) -> float:
    """
    Calcula el total de una lista de items.
    
    Args:
        items: Lista de items con precio
        
    Returns:
        Total calculado como float
    """
    # Inicializar total
    total = 0.0
    return total
```

```typescript
// TypeScript/React
/**
 * Calcula el total de una lista de items
 * @param items - Array de items con precio
 * @returns Total calculado
 */
function calculateTotal(items: Item[]): number {
    // Inicializar total
    let total = 0;
    return total;
}
```

#### ❌ NO ACEPTADO
```python
# Python
def calculate_total(items):
    # Sin docstring ni tipos
    total = 0.0  # Comentario obvio innecesario
    return total
```

```typescript
// TypeScript/React
function calculateTotal(items) {  // Sin tipos
    let total = 0;  // Comentario obvio innecesario
    return total;
}
```

### Indentación y Estilo

#### ✅ ACEPTADO
```python
# Python
class DatabaseManager:
    
    def __init__(self, connection_string: str):
        self.connection = connection_string
        
    def connect(self) -> bool:
        if self.connection:
            print("Conectando...")
            return True
        return False
```

```typescript
// TypeScript/React
interface UserProps {
    name: string;
    age: number;
}

const UserComponent: React.FC<UserProps> = ({ name, age }) => {
    const handleClick = () => {
        console.log(`Usuario: ${name}, Edad: ${age}`);
    };
    
    return (
        <div className="p-4 bg-blue-500 rounded-lg">
            <h1 className="text-xl font-bold">{name}</h1>
            <button 
                onClick={handleClick}
                className="mt-2 px-4 py-2 bg-white rounded"
            >
                Click me
            </button>
        </div>
    );
};
```

#### ❌ NO ACEPTADO
```python
# Python
class DatabaseManager:
  def __init__(self,connection_string):# Indentación incorrecta, sin espacios
      self.connection=connection_string
  def connect(self):
    if self.connection:print("Conectando...");return True# Todo en una línea
    return False
```

```typescript
// TypeScript/React
const UserComponent = ({name,age}) => {
  const handleClick=()=>{console.log(`Usuario: ${name}, Edad: ${age}`);}// Sin espacios
  
  return <div className="p-4 bg-blue-500 rounded-lg"><h1 className="text-xl font-bold">{name}</h1><button onClick={handleClick} className="mt-2 px-4 py-2 bg-white rounded">Click me</button></div>; // Todo en una línea
};
```

### TailwindCSS

#### ✅ ACEPTADO
```typescript
// Clases ordenadas: layout -> spacing -> colors -> typography -> effects
<div className="flex flex-col p-4 bg-blue-500 text-white font-bold rounded-lg shadow-md">
    <h1 className="text-xl mb-2">Título</h1>
</div>
```

#### ❌ NO ACEPTADO
```typescript
// Clases desordenadas y redundantes
<div className="text-white bg-blue-500 font-bold p-4 flex rounded-lg flex-col shadow-md">
    <h1 className="mb-2 text-xl">Título</h1>
</div>
```

## 5. Herramientas Recomendadas

### Linters y Formatters
- **Python**: `black`, `flake8`, `isort`
- **TypeScript/React**: `eslint`, `prettier`
- **TailwindCSS**: `prettier-plugin-tailwindcss`

### Configuración de IDE
- Configuramos el IDE para mostrar espacios en blanco
- Habilitamos auto-formateo al guardar
- Configuramos rulers a 88/100 caracteres

## 6. Control de Versiones

### Commits
- Usamos mensajes descriptivos en inglés
- Formato: `tipo(scope): descripción`
- Ejemplo: `feat(auth): add user login validation`

### Branches
- `main`: rama principal
- `develop`: rama de desarrollo
- `feature/nombre-caracteristica`: nuevas características
- `fix/nombre-bug`: corrección de errores

---

**Nota**: Esta guía debe ser revisada y actualizada regularmente conforme evolucionen las mejores prácticas del equipo.
# 🧪 Tests de Gamificación

## Estructura

```
tests/gamification/
├── conftest.py                 # Fixtures compartidos
├── run_tests.py               # Test runner
├── test_puntos_api.py         # Tests de Puntos (25+ tests)
├── test_etiquetas_api.py      # Tests de Etiquetas (14+ tests)
├── test_tienda_api.py         # Tests de Tienda (12+ tests)
└── test_rachas_api.py         # Tests de Rachas (15+ tests)
```

## Fixtures Disponibles (conftest.py)

### Database
- `db_engine`: SQLite in-memory engine
- `db_session`: Session con auto-rollback
- `client`: TestClient con dependency override

### Usuarios
- `admin_user`: Usuario administrador
- `estudiante_user`: Usuario estudiante (principal)
- `multiple_users`: 10 usuarios para ranking tests

### Autenticación
- `admin_token`: JWT token de admin
- `estudiante_token`: JWT token de estudiante
- `auth_headers`: Headers con Bearer token (admin)
- `estudiante_headers`: Headers con Bearer token (estudiante)

### Puntos
- `usuario_puntos`: Record con 1000 puntos
- `historial_puntos`: 5 entradas de historial
- `insignia_sample`: Insignia de muestra

### Etiquetas
- `etiqueta_sample`: Etiqueta Python Master
- `etiquetas_catalogo`: 3 etiquetas variadas
- `usuario_etiqueta`: Relación usuario-etiqueta

### Tienda
- `item_tienda_sample`: Item de avatar
- `items_catalogo`: 3 items variados
- `inventario_item`: Item en inventario

### Rachas
- `racha_usuario`: Racha de 15 días
- `milestones_racha`: 5 milestones
- `historial_racha_data`: 5 eventos de racha

## Ejecutar Tests

### Todos los tests
```bash
python run_tests.py
```

### Tests específicos
```bash
# Solo módulo de puntos
python run_tests.py --module puntos

# Solo módulo de etiquetas
python run_tests.py --module etiquetas

# Solo módulo de tienda
python run_tests.py --module tienda

# Solo módulo de rachas
python run_tests.py --module rachas
```

### Con cobertura
```bash
python run_tests.py --coverage
# Genera htmlcov/index.html
```

### Modo rápido (sin tests lentos)
```bash
python run_tests.py --fast
```

### Modo detallado
```bash
python run_tests.py --verbose
```

## Cobertura Esperada

| Módulo     | Tests | Cobertura |
|------------|-------|-----------|
| Puntos     | 25+   | ~90%      |
| Etiquetas  | 14+   | ~80%      |
| Tienda     | 12+   | ~80%      |
| Rachas     | 15+   | ~85%      |
| **TOTAL**  | **66+** | **>83%** |

## Patrones de Testing

### Estructura de Test
```python
class TestEndpointName:
    """Tests para específico endpoint."""
    
    def test_success_case(self, client, headers, fixtures):
        """Test caso exitoso."""
        # Arrange
        data = {...}
        
        # Act
        response = client.post("/endpoint", json=data, headers=headers)
        
        # Assert
        assert response.status_code == 200
        assert "field" in response.json()
```

### Test de Autenticación
```python
def test_sin_autenticacion(self, client):
    """Debe fallar sin autenticación."""
    response = client.get("/endpoint")
    assert response.status_code == 401
```

### Test de Validación
```python
def test_validacion_campo(self, client, headers):
    """Debe validar campo requerido."""
    response = client.post("/endpoint", json={}, headers=headers)
    assert response.status_code == 422
```

### Test de Integración
```python
def test_flujo_completo(self, client, headers, fixtures):
    """Test de flujo completo."""
    # Paso 1
    resp1 = client.post("/step1", ...)
    assert resp1.status_code == 200
    
    # Paso 2 usa resultado de paso 1
    id = resp1.json()["id"]
    resp2 = client.get(f"/step2/{id}", ...)
    assert resp2.status_code == 200
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Tests Gamificación

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: cd backend/tests/gamification && python run_tests.py --coverage
      - uses: codecov/codecov-action@v3
```

## Troubleshooting

### Tests fallan con errores de DB
```bash
# Limpiar base de datos
rm -f test_db.sqlite

# Verificar dependencias
pip install pytest pytest-asyncio sqlalchemy faker
```

### Tests lentos
```bash
# Ejecutar sin tests de performance
python run_tests.py --fast

# O marcar tests específicos
@pytest.mark.slow
def test_performance():
    ...
```

### Coverage bajo
```bash
# Ver líneas no cubiertas
python run_tests.py --coverage
# Abrir htmlcov/index.html en navegador
```

## Próximos Pasos

- [ ] Tests de servicios (40+ tests)
- [ ] Tests de integración completa (20+ tests)
- [ ] Tests de performance avanzados
- [ ] Mutation testing
- [ ] Contract testing con frontend

## Recursos

- Documentación pytest: https://docs.pytest.org/
- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/
- SQLAlchemy Testing: https://docs.sqlalchemy.org/en/20/orm/session_transaction.html

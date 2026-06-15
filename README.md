# DX1_Template

Plantilla base para el desarrollo de componentes personalizados para **SpeeDBee Synapse / DX1**.

Contiene la estructura mínima obligatoria con comentarios detallados en castellano para que puedas empezar a desarrollar tu propio componente sin partir de cero.

---

## Estructura del proyecto

```
DX1_Template/
├── scc-info.json                              # Metadatos del paquete (nombre, versión, UUID)
├── source/python/
│   └── template_component.py                  # Código Python del componente (plantilla)
├── parameter_ui/template_component/
│   └── custom_ui.json                         # Definición de la interfaz de parámetros (JSON)
└── template-component-package.sccpkg          # Paquete listo para importar en Synapse
```

---

## Cómo usar esta plantilla

### 1. Copia el proyecto

Clona este repositorio o copia la carpeta. Renombra los archivos y carpetas según tu componente:

- `source/python/template_component.py` → `source/python/mi_componente.py`
- `parameter_ui/template_component/` → `parameter_ui/mi_componente/`

### 2. Edita `scc-info.json`

Actualiza el nombre del paquete, la versión y genera nuevos UUIDs para el paquete y el componente:

```bash
python3 -c "import uuid; print(uuid.uuid4())"
```

### 3. Desarrolla tu componente

Edita `source/python/mi_componente.py`. La plantilla incluye los tres métodos principales con ejemplos comentados:

| Método | Cuándo se ejecuta | Para qué sirve |
|---|---|---|
| `premain(param)` | Una sola vez al arrancar | Abrir conexiones, crear columnas de datos |
| `main(param)` | Bucle hasta que se para | Leer datos, escribir en columnas |
| `postmain(param)` | Una sola vez al parar | Cerrar conexiones, liberar recursos |

### 4. Adapta la interfaz de parámetros

Edita `parameter_ui/mi_componente/custom_ui.json` para añadir los campos que el usuario configurará desde la UI de Synapse.

Tipos de campo disponibles: `string`, `number`, `bool`, `select`, `text`, `array`.

### 5. Genera el paquete

```bash
source ~/sccde/bin/activate
sccde make-package
```

Genera el archivo `.sccpkg` listo para importar en Synapse.

### 6. Importa en Synapse

1. Abre la UI de Synapse → modo edición
2. Menú Settings (engranaje) → **Custom Components**
3. Botón **Add** → selecciona el `.sccpkg`
4. Confirma el reinicio

---

## Tipos de componente

El campo `tag` del decorador `@HiveComponentInfo` define el tipo:

| Tag | Descripción | inports | outports |
|---|---|---|---|
| `collector` | Lee datos de una fuente externa y los escribe en Synapse | 0 | ≥ 1 |
| `emitter` | Recibe datos de Synapse y los envía a un sistema externo | ≥ 1 | 0 |
| `logic` | Transforma o filtra datos entre puertos | ≥ 1 | ≥ 1 |
| `action` | Ejecuta una acción puntual | 0 | 0 |
| `serializer` | Serializa datos a un formato concreto (CSV, JSON…) | ≥ 1 | 0 |

---

## Tipos de dato para columnas

```python
DataType.BOOLEAN
DataType.INT8 / INT16 / INT32 / INT64
DataType.UINT8 / UINT16 / UINT32 / UINT64
DataType.FLOAT / DOUBLE
DataType.STRING
DataType.BINARY
```

---

## Errores personalizados

Define un `ErrorType` por cada causa de error diferente. Todos se agrupan en `ERROR_TYPES` y se pasan al decorador. Dentro de `main()`, usa `return MI_ERROR('detalle')` para parar el componente con un mensaje estructurado en la UI.

```python
MI_ERROR_CONEXION = ErrorType('CONNECTION_ERROR', 'detail')
MI_ERROR_LECTURA  = ErrorType('READ_ERROR',       'detail')
ERROR_TYPES       = [MI_ERROR_CONEXION, MI_ERROR_LECTURA]

# Dentro de main():
return MI_ERROR_CONEXION(f'No se puede conectar a {host}:{port}')
```

---

## Requisitos

- **SpeeDBee Synapse** instalado en el sistema (para `sccde serve`)
- **SCCDE** instalado en un entorno virtual:

```bash
python3 -m venv ~/sccde
source ~/sccde/bin/activate
pip install speedbeesynapse-sccde
```

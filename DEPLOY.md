# Guía de Despliegue en Render

## Causa del error "No open ports detected"

El mensaje **"No open ports detected"** y **"Exited with status 3"** ocurre porque la aplicación **se cierra antes** de que uvicorn pueda vincular el puerto. La causa más habitual es que faltan los **archivos de modelos (.pkl)** que la API necesita al iniciar.

## Pasos para arreglar el deploy

### 1. Generar los artefactos de modelos (obligatorio)

Los modelos econométricos se guardan en `src/models/artifacts/v1/`. Deben existir estos archivos:

- `econ_growth_model.pkl`
- `td_model.pkl`
- `emp_model.pkl`

**Para generarlos**, ejecuta el notebook localmente:

```bash
cd notebooks
# Si usas Jupyter/VS Code: abre y ejecuta todas las celdas de 02_base_model.ipynb
# O con nbconvert:
pip install nbconvert
jupyter nbconvert --to notebook --execute 02_base_model.ipynb --output 02_base_model_executed.ipynb
```

Los archivos se crearán en `src/models/artifacts/v1/`. Luego **commitea y pushea** estos archivos al repositorio:

```bash
git add src/models/artifacts/
git commit -m "Add model artifacts for deployment"
git push
```

### 2. Variables de entorno en Render

En el Dashboard de Render → tu servicio → **Environment**:

| Variable | Descripción |
|----------|-------------|
| `JWT_SECRET_KEY` | Clave secreta para tokens JWT (usa una clave segura en producción) |
| `PORT` | No es necesario configurarla; Render la define automáticamente |

### 3. Comando de inicio

Render debe usar:

```
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

El binding a `0.0.0.0` y al `$PORT` de Render es necesario para que el servicio sea accesible.

### 4. Comando de build (Poetry)

Si usas Poetry:

```
poetry install --no-dev
```

O el equivalente que tengas configurado para instalar dependencias de producción.

## Verificación rápida

Antes de hacer deploy, verifica localmente que los artefactos existen:

```bash
ls src/models/artifacts/v1/
# Deberías ver: econ_growth_model.pkl  td_model.pkl  emp_model.pkl
```

Si faltan, la API no arrancará en Render.

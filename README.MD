# 🧠 Pulso de Memoria

> Dashboard interactivo de patrones temporales de enrutamiento de memoria en agentes conversacionales de IA

[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-4.4.1-informational)](https://dash.plotly.com)
[![Plotly](https://img.shields.io/badge/Plotly-6.9.0-informational)](https://plotly.com)
[![Dataset](https://img.shields.io/badge/Dataset-WildChat--1M-green)](https://huggingface.co/datasets/allenai/WildChat-1M)

---

## Contexto

Este proyecto es el entregable de visualización de datos de la materia, conectado directamente con la tesis:

> *"Arquitectura de Memoria Jerárquica para Agentes de IA: Mejoramiento del Proceso de Inferencia sin Dependencia del Historial Completo"*

El clasificador de texto entrenado en el proyecto de Machine Learning del mismo curso (Sentence Embeddings + Logistic Regression, 97% accuracy) se aplica sobre **56,617 turnos** de conversaciones reales del corpus WildChat-1M en español para generar el dataset de análisis. El dashboard visualiza los patrones temporales que emergen de esas predicciones.

**La Big Idea:** Un agente de IA no necesita recordar todo — necesita saber qué tipo de memoria activar. Este dashboard demuestra que ese patrón es predecible, estructurado y consistente a lo largo del tiempo.

---

## Visualizaciones

El dashboard contiene cuatro visualizaciones interactivas que responden una pregunta analítica cada una:

| Visualización | Pregunta que responde |
|---|---|
| Línea temporal por turno | ¿Cómo evoluciona el tipo de memoria a lo largo de una conversación? |
| Heatmap hora × día | ¿Existen patrones cíclicos según la hora del día o el día de la semana? |
| Barras de confianza | ¿En qué capa el clasificador muestra mayor y menor confianza? |
| Área mensual (12 meses) | ¿La distribución de capas cambia a lo largo del tiempo? |

Los filtros globales (capa de memoria, duración de sesión, rango de fechas) actualizan todas las visualizaciones simultáneamente.

---

## Hallazgo principal

```
Distribución en WildChat (sistema sin memoria jerárquica):
  Semántica  71.7%  ← solo puede responder preguntas factuales
  Trabajo    27.4%  ← y manejar el contexto inmediato
  Episódica   0.9%  ← casi inexistente: nadie puede referenciar
                       sesiones pasadas porque el sistema no las soporta

Distribución ideal con arquitectura jerárquica (hipótesis de la tesis):
  Semántica  ~33%
  Trabajo    ~33%
  Episódica  ~33%  ← esto es lo que la arquitectura propuesta habilita
```

La distribución de 0.9% de episódica se mantiene **estable durante 12 meses** de conversaciones reales — no es un mes atípico, es el comportamiento estructural de un sistema sin memoria persistente.

---

## Stack tecnológico

- **Dashboard:** Dash 4.4.1 + Plotly 6.9.0
- **UI:** Dash Bootstrap Components 2.0.4 (tema FLATLY)
- **Procesamiento de datos:** Pandas 3.0.5 + NumPy + statsmodels 0.14.6
- **Clasificador:** sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`) + Logistic Regression (sklearn)
- **Dataset fuente:** WildChat-1M (Allen Institute for AI, HuggingFace)
- **Formato de datos:** Parquet (PyArrow 25.0.0)
- **Deploy:** Render (Web Service) + Gunicorn 26.0.0

---

## Estructura del proyecto

```
pulso-memoria/
├── app.py                                  ← aplicación Dash completa
├── requirements.txt                        ← dependencias
├── dataset_wildchat_etiquetado.parquet     ← dataset generado (18 MB)
└── README.md
```

---

## Instalación y ejecución local

**Requisitos:** Python 3.14+

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/pulso-memoria.git
cd pulso-memoria

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# requirements.txt:
# dash==4.4.1
# dash-bootstrap-components==2.0.4
# pandas==3.0.5
# plotly==6.9.0
# pyarrow==25.0.0
# gunicorn==26.0.0
# statsmodels==0.14.6

# 4. Ejecutar
python app.py
```

El dashboard queda disponible en `http://localhost:8050`.

---

## Cómo se generó el dataset

El archivo `dataset_wildchat_etiquetado.parquet` no existe previamente — se generó aplicando el clasificador de la tesis sobre conversaciones reales:

```
WildChat-1M (HuggingFace)
        ↓
   Filtrar: conversaciones en español (~80K sesiones)
        ↓
   Muestreo estratificado: 20K sesiones (~56K turnos de usuario)
        ↓
   Clasificador ML (Pipeline B: Sentence Embeddings + LR)
        ↓
   Etiquetar cada turno: memory_layer + confidence_score
        ↓
   Derivar variables temporales: hour_of_day, day_of_week, month
        ↓
   dataset_wildchat_etiquetado.parquet  ✅
```

### Atributos del dataset

| Columna | Tipo | Descripción |
|---|---|---|
| `session_id` | string | Identificador único de sesión |
| `turn_number` | int | Número de turno dentro de la sesión |
| `timestamp` | datetime (UTC) | Fecha y hora del turno |
| `texto` | string | Input del usuario |
| `memory_layer` | categorical | Capa predicha: trabajo / episódica / semántica |
| `confidence_score` | float [0,1] | Probabilidad asignada a la clase predicha |
| `hour_of_day` | int [0-23] | Hora del día |
| `day_of_week` | string | Día de la semana |
| `month` | string | Mes en formato YYYY-MM |
| `session_length` | int | Total de turnos en la sesión |
| `duracion_cat` | categorical | Corta (1-3) / Media (4-10) / Larga (11+) |

---

## Deploy en Render

El dashboard está deployado en Render (free tier). El servicio puede tardar ~30 segundos en responder si estuvo inactivo.

```bash
# Start command usado en Render:
gunicorn app:server
```

### Pasos para re-deployar

1. Hacer push al repositorio de GitHub
2. Render detecta el cambio y redeploya automáticamente
3. Verificar en el log de Render que Gunicorn arranca sin errores

---

## Conexión con el Modelo Anidado de Munzner

| Nivel | Pregunta | Implementación |
|---|---|---|
| Domain Problem | ¿Cuál es el problema y quién es el usuario? | Investigadores de IA y agentes conversacionales |
| Data Abstraction (What?) | ¿Qué datos son relevantes? | 56,617 turnos con timestamps, capa de memoria y confianza |
| Task Abstraction (Why?) | ¿Qué tareas debe soportar? | Identificar tendencia, explorar ciclos, comparar grupos, detectar anomalías |
| Visual Encoding (How?) | ¿Cómo se representan los datos? | Línea temporal, heatmap, barras, área apilada |
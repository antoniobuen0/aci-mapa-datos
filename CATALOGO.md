# Catálogo de datasets — identificación AACC (EDUCAbase)

> Todos los datos provienen de fuentes oficiales del Ministerio de Educación, FP y
> Deportes (EDUCAbase), descargados en CSV-BDSC y transformados a JSON/CSV.

**Portal oficial:**
<https://www.educacionfpydeportes.gob.es/servicios-al-ciudadano/estadisticas/no-universitaria/alumnado/apoyo.html>
→ elige curso → icono verde de EDUCAbase «Otro alumnado con n.e.a.e.».

## 1. Identificación de AACC — `otros_03`

Alumnado con necesidad específica de apoyo educativo (NEAE) **identificado o atendido**
por **altas capacidades intelectuales** en enseñanza no universitaria, por CCAA,
provincia, etapa y sexo.

| Campo | Detalle |
|-------|---------|
| Tabla EDUCAbase | `otros_03` (`otros_03.csv_bdsc`) |
| Cursos | 2011-12 → 2024-25 (sin 2019-20 por COVID) |
| Niveles | España, CCAA y provincias |
| Desagregación | Etapa (Infantil, Primaria, ESO, Bachillerato, FP) y sexo (total/hombre/mujer) |
| Nota | Mide alumnado **registrado oficialmente**, no prevalencia. Desde 2022-23 incluye Infantil, Bachillerato y FP. |
| Ficheros | `data/educabase-identification.json`, `data/csv/identificacion.csv` |

Descarga directa (ej. 2024-25):
```
https://estadisticas.educacion.gob.es/EducaJaxiPx/files/_px/es/csv_bdsc/no-universitaria/alumnado/apoyo/2024-2025/otros/l0/otros_03.csv_bdsc
```

## 2. Identificación por CCAA (histórico) — `otros_05`

Desglose por CCAA de cursos anteriores a 2022-23, cuando `otros_03` no incluía la
dimensión territorial. Incorporado a `data/educabase-identification.json`.

> El sumatorio de CCAA de `otros_05` **no coincide** con el total nacional de `otros_03`
> porque cubren etapas distintas.

## 3. Matrícula no universitaria — `general_1_01` / `todas_01`

Denominador para las tasas de identificación.

| Campo | Detalle |
|-------|---------|
| Tabla EDUCAbase | `general_1_01` (2023-24, 2024-25), `todas_01` (2022-23) |
| Cursos | 2022-23 → 2024-25 |
| Niveles | España, CCAA y provincias |
| Ficheros | `data/educabase-enrollment.json`, `data/csv/matricula.csv` |

Descarga directa (ej. 2024-25):
```
https://estadisticas.educacion.gob.es/EducaJaxiPx/files/_px/es/csv_bdsc/no-universitaria/alumnado/matriculado/2024-2025-da/comunidad/reg_general/l0/general_1_01.csv_bdsc
```

## 4. Tasas derivadas

`data/csv/tasas_identificacion_ccaa.csv` y `data/csv/tasas_identificacion_provincia.csv`
cruzan identificación y matrícula (`sex=total`, `stage=TOTAL`) para dar la tasa real
`identificados / matriculados`. Las tasas **provinciales** solo existen para 2023-24 y
2024-25 (cuando hay denominador provincial).

## Nota: cribado del País Vasco vs EDUCAbase

El cribado del Gobierno Vasco (1.º y 6.º de Primaria) detectó 1.252 alumnos potenciales
en 2022-23 (Naiz, 2023), mientras EDUCAbase registra 681 *identificados/atendidos* en
Primaria. No es contradictorio: el cribado detecta candidatos; EDUCAbase cuenta a quien
completa el proceso oficial y recibe medidas.

## Atribución

Datos EDUCAbase: Ministerio de Educación, FP y Deportes. Elaboración y CSV derivados:
[νοῦς · nous.es](https://nous.es) — mapa interactivo en [mapa.nous.es](https://mapa.nous.es).

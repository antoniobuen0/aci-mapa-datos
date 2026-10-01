# Catálogo de datasets — identificación AACC (EDUCAbase)

> Todos los datos provienen de fuentes oficiales del Ministerio de Educación, FP y
> Deportes (EDUCAbase), descargados en CSV-BDSC y transformados a JSON/CSV.

**Portal oficial:**
<https://www.educacionfpydeportes.gob.es/servicios-al-ciudadano/estadisticas/no-universitaria/alumnado/apoyo.html>
→ elige curso → icono verde de EDUCAbase «Otro alumnado con n.e.a.e.».

## 1. Identificación de AACC — serie oficial

Alumnado con necesidad específica de apoyo educativo (NEAE) **identificado o atendido**
por **altas capacidades intelectuales** en enseñanza no universitaria, por CCAA,
provincia, etapa y sexo.

| Campo | Detalle |
|-------|---------|
| Tablas EDUCAbase | `altascap_01` (2011-12→2019-20), `otros_02` (2020-21→2021-22), `otros_03` (2022-23→2024-25) |
| Cursos | 2011-12 → 2024-25, incluido 2019-20 |
| Niveles | España, CCAA y provincias |
| Desagregación | Etapa (Infantil, Primaria, ESO, Bachillerato, FP) y sexo (total/hombre/mujer) |
| Nota | Mide alumnado **atendido con una medida educativa específica**, no prevalencia ni identificación clínica. |
| Ficheros | `data/educabase-identification.json`, `data/csv/identificacion.csv` |

Descarga directa (ej. 2024-25):
```
https://estadisticas.educacion.gob.es/EducaJaxiPx/files/_px/es/csv_bdsc/no-universitaria/alumnado/apoyo/2024-2025/otros/l0/otros_03.csv_bdsc
```

## 2. Selección de tabla por periodo

El importador selecciona la familia de tabla correspondiente a cada curso y filtra
`Altas capacidades intelectuales` en las tablas `otros`. En todos los cursos valida
que hombres + mujeres y la suma de CCAA coincidan con el total estatal.

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
cruzan identificación y matrícula (`sex=total`, `stage=TOTAL`) para dar la tasa oficial
`identificados / matriculados`. Las tasas **provinciales** solo existen para 2023-24 y
2024-25 (cuando hay denominador provincial).

## 5. Serie histórica «Todos los Centros» (2009-10 → 2013-14)

`data/identification-provinces-historical.json`: serie del Ministerio de Educación
«Alumnado con altas capacidades intelectuales, por enseñanza. Todos los Centros», por
España, CCAA y provincia, recopilada por José Luis (REDACI,
<https://incansableaspersor.wordpress.com/>). Cuadre interno verificado (provincias →
CCAA → España en los 5 cursos).

> Alcance distinto y más amplio que la serie principal (España 2013-14: 15.876 frente a
> 7.277), así que **no es comparable ni fusionable** con `educabase-identification.json`.

## Nota: cribado del País Vasco vs EDUCAbase

El cribado del Gobierno Vasco (1.º y 6.º de Primaria) detectó 1.252 alumnos potenciales
en 2022-23 (Naiz, 2023), mientras EDUCAbase registra 681 *identificados/atendidos* en
Primaria. No es contradictorio: el cribado detecta candidatos; EDUCAbase cuenta a quien
completa el proceso oficial y recibe medidas.

## Atribución

Datos EDUCAbase: Ministerio de Educación, FP y Deportes. Elaboración y CSV derivados:
[νοῦς · nous.es](https://nous.es) — mapa interactivo en [aci.nous.es](https://aci.nous.es).

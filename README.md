# aci-mapa-datos

[![Ko-fi · apoya el proyecto](https://img.shields.io/badge/Ko--fi-apoya_el_proyecto-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/nous_)

**Datos abiertos de identificación de altas capacidades (AACC) en España**, a partir
de las estadísticas oficiales del Ministerio de Educación, Formación Profesional y
Deportes (**EDUCAbase**). Cobertura por **comunidad autónoma** y **provincia**,
cursos **2011-12 → 2024-25**.

> Estos datos alimentan el mapa interactivo **[aci.nous.es](https://aci.nous.es)**.
> Espíritu *open data*: las cifras provienen de tablas públicas, descargables y reproducibles.

## Qué hay aquí

```
data/
  educabase-identification.json   # Alumnado identificado/atendido por AACC (registros completos)
  educabase-enrollment.json       # Matrícula no universitaria (denominador para tasas)
  identification-provinces-historical.json  # Serie «Todos los Centros» 2009-10→2013-14 (no comparable)
  csv/
    identificacion.csv            # Volcado plano: course, geoLevel, geoName, sex, stage, value
    matricula.csv                 # Volcado plano de matrícula
    tasas_identificacion_ccaa.csv         # course, ccaa, identificados, matriculados, tasa
    tasas_identificacion_provincia.csv    # course, provincia, ccaa, identificados, matriculados, tasa
CATALOGO.md                       # Catálogo de datasets, tablas EDUCAbase y URLs de descarga
LICENSE                           # Licencia y atribución
```

## Definiciones clave

- **`value` en identificación** = alumnado **atendido con una medida educativa
  específica** por altas capacidades intelectuales (NEAE). **No** es una estimación
  de prevalencia ni un censo clínico.
- **`tasa`** = `identificados / matriculados` (mismo curso, ámbito y `sex=total`,
  `stage=TOTAL`). Es una **tasa oficial de atención**, no de prevalencia esperada.
- **Niveles** (`geoLevel`): `country`, `ccaa`, `province`.
- **Provincias**: las CCAA uniprovinciales (Asturias, Cantabria, Madrid, Murcia,
  Navarra, La Rioja, Illes Balears) y las ciudades autónomas (Ceuta, Melilla) figuran
  como `ccaa`, no como `province`.

## Avisos metodológicos

1. La serie incluye todos los cursos de **2011-12 a 2024-25**, incluido 2019-20.
2. EDUCAbase reorganiza la estadística en tres familias de tablas, sin cambiar el
   concepto del total nacional: `altascap_01`, `otros_02` y `otros_03`.
3. **Tasas provinciales** solo disponibles para **2023-24 y 2024-25** (es cuando existe
   denominador de matrícula a nivel provincial). Antes, las tasas solo se calculan a
   nivel CCAA/estatal.
4. El dato cuenta alumnado atendido; no debe presentarse como el total de diagnósticos,
   valoraciones psicopedagógicas o prevalencia.
5. `identification-provinces-historical.json` es otra serie del Ministerio («Todos los
   Centros, por enseñanza», 2009-10→2013-14), de alcance más amplio: **no se suma ni se
   compara** con la serie principal (ver `CATALOGO.md`).
6. Algunas tablas de EDUCAbase añaden llamadas de nota a los nombres (p. ej.
   «Barcelona (2)» en la matrícula 2023-24). Los JSON y los volcados planos las
   conservan tal cual; las tablas de tasas usan el nombre limpio.

## Regenerar

Este repositorio se genera desde ACI-MAPA con `scripts/publish_dataset_repo.py`: los
JSON son exactamente los que usa la web y los CSV se derivan de ellos.

## Reproducibilidad

Portal oficial de estadística no universitaria del Ministerio:
<https://www.educacionfpydeportes.gob.es/servicios-al-ciudadano/estadisticas/no-universitaria.html>

Sección de Necesidades de Apoyo Educativo (donde están las AACC):
<https://www.educacionfpydeportes.gob.es/servicios-al-ciudadano/estadisticas/no-universitaria/alumnado/apoyo.html>

Ruta: elige el curso y abre la tabla de altas capacidades o de otro alumnado con
n.e.a.e., según el año. Identificación: `altascap_01` (2011-12→2019-20), `otros_02`
(2020-21→2021-22) y `otros_03` (2022-23→2024-25); matrícula: `general_1_01`. En
`CATALOGO.md` están las URLs de descarga directa (`.csv_bdsc`) verificadas.

## Licencia

- **Datos EDUCAbase**: estadística pública del Ministerio de Educación, FP y Deportes
  (uso libre con atribución a la fuente).
- **CSV derivados y catálogo**: CC BY 4.0 — atribución a [νοῦς · nous.es](https://nous.es).

Ver `LICENSE`.

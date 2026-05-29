# aci-mapa-datos

**Datos abiertos de identificación de altas capacidades (AACC) en España**, a partir
de las estadísticas oficiales del Ministerio de Educación, Formación Profesional y
Deportes (**EDUCAbase**). Cobertura por **comunidad autónoma** y **provincia**,
cursos **2011-12 → 2024-25**.

> Estos datos alimentan el mapa interactivo **[mapa.nous.es](https://mapa.nous.es)**.
> Espíritu *open data*: las cifras provienen de tablas públicas, descargables y reproducibles.

## Qué hay aquí

```
data/
  educabase-identification.json   # Alumnado identificado/atendido por AACC (registros completos)
  educabase-enrollment.json       # Matrícula no universitaria (denominador para tasas)
  csv/
    identificacion.csv            # Volcado plano: course, geoLevel, geoName, sex, stage, value
    matricula.csv                 # Volcado plano de matrícula
    tasas_identificacion_ccaa.csv         # course, ccaa, identificados, matriculados, tasa
    tasas_identificacion_provincia.csv    # course, provincia, ccaa, identificados, matriculados, tasa
CATALOGO.md                       # Catálogo de datasets, tablas EDUCAbase y URLs de descarga
LICENSE                           # Licencia y atribución
```

## Definiciones clave

- **`value` en identificación** = alumnado **oficialmente identificado o atendido** por
  altas capacidades intelectuales (NEAE). **No** es una estimación de prevalencia.
- **`tasa`** = `identificados / matriculados` (mismo curso, ámbito y `sex=total`,
  `stage=TOTAL`). Es una **tasa de identificación real**, no de prevalencia esperada.
- **Niveles** (`geoLevel`): `country`, `ccaa`, `province`.
- **Provincias**: las CCAA uniprovinciales (Asturias, Cantabria, Madrid, Murcia,
  Navarra, La Rioja, Illes Balears) y las ciudades autónomas (Ceuta, Melilla) figuran
  como `ccaa`, no como `province`.

## Avisos metodológicos

1. **Sin dato 2019-20** (interrupción COVID).
2. **Ruptura de serie en 2022-23**: EDUCAbase amplió la cobertura a Infantil 2.º ciclo,
   Bachillerato y FP (antes solo Primaria + ESO). Los saltos de ese curso reflejan ese
   cambio metodológico, no necesariamente más identificación real.
3. **Tasas provinciales** solo disponibles para **2023-24 y 2024-25** (es cuando existe
   denominador de matrícula a nivel provincial). Antes, las tasas solo se calculan a
   nivel CCAA/estatal.
4. El dato **subestima** la identificación: cuenta a quien recibe alguna medida
   educativa (adaptación, flexibilización o enriquecimiento), no diagnósticos privados
   ni informes sin medida activa.

## Reproducibilidad

Portal oficial de estadística no universitaria del Ministerio:
<https://www.educacionfpydeportes.gob.es/servicios-al-ciudadano/estadisticas/no-universitaria.html>

Sección de Necesidades de Apoyo Educativo (donde están las AACC):
<https://www.educacionfpydeportes.gob.es/servicios-al-ciudadano/estadisticas/no-universitaria/alumnado/apoyo.html>

Ruta: elige el curso → icono verde de EDUCAbase **«Otro alumnado con n.e.a.e.»**.
Tabla principal de identificación: `otros_03`; matrícula: `general_1_01`. En
`CATALOGO.md` están las URLs de descarga directa (`.csv_bdsc`) verificadas.

## Licencia

- **Datos EDUCAbase**: estadística pública del Ministerio de Educación, FP y Deportes
  (uso libre con atribución a la fuente).
- **CSV derivados y catálogo**: CC BY 4.0 — atribución a [νοῦς · nous.es](https://nous.es).

Ver `LICENSE`.

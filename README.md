# Aprovechamiento Académico · UPMH

Dashboard estático para visualizar los reportes de aprovechamiento académico
(promedios por corte, alumnos, bajas y % de reprobación) de la Universidad
Politécnica Metropolitana de Hidalgo.

**Sitio publicado:** se activa vía GitHub Pages sobre la rama `main` — la URL
queda en la sección "About" del repositorio una vez habilitado.

## Contenido

- `index.html` — el dashboard (KPIs, gráficas y tabla filtrable). No requiere build ni backend.
- `data.json` — datos ya procesados que consume el dashboard.
- `data/reportes/` — reportes originales en `.xlsx`, tal como los exporta el sistema administrativo.
- `scripts/generar_datos.py` — convierte los `.xlsx` de `data/reportes/` en `data.json`.

## Actualizar con un nuevo periodo o corte

1. Coloca el/los nuevo(s) archivo(s) `.xlsx` dentro de `data/reportes/` (respetando el formato original del reporte).
2. Regenera los datos:

   ```bash
   python3 scripts/generar_datos.py
   ```

3. Revisa `data.json` y confirma los números en el dashboard abriendo `index.html` con un servidor local, por ejemplo:

   ```bash
   python3 -m http.server 8000
   ```

4. Sube los cambios (`git add`, `git commit`, `git push`) — GitHub Pages se actualiza automáticamente.

## Notas sobre los datos

- El "% de Reprobación" institucional agrega las reprobaciones **por materia**, no alumnos únicos: un mismo alumno reprobado en dos materias cuenta dos veces, igual que en el reporte original de cada grupo.
- Los nombres de grupo (ej. "5 - A") pueden repetirse entre programas educativos distintos; el dashboard los distingue internamente por programa + grupo.

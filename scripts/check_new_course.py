#!/usr/bin/env python3
"""Detecta si EDUCAbase ya publica el curso siguiente al último cargado.

Sin dependencias. Imprime un resumen y, bajo GitHub Actions, escribe
`new_course` / `report` en $GITHUB_OUTPUT. Salida 0 siempre (el aviso es el output).
"""
import json, os, sys, urllib.request, urllib.error

BASE = "https://estadisticas.educacion.gob.es/EducaJaxiPx/files/_px/es/csv_bdsc/no-universitaria/alumnado"
DATA = os.path.join(os.path.dirname(__file__), "..", "data", "educabase-identification.json")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None  # un curso inexistente responde 302 -> /404.html


OPENER = urllib.request.build_opener(NoRedirect)


def next_course(course):
    a = int(course[:4]) + 1
    return f"{a}-{a + 1}"


def probe(url):
    """Devuelve (existe, detalle). Existe = 200 y cabecera CSV-BDSC válida."""
    try:
        with OPENER.open(urllib.request.Request(url, headers={"User-Agent": "aci-mapa-datos-watch"}), timeout=60) as r:
            head = r.read(600).decode("latin-1")
            ok = r.status == 200 and ";" in head and "TOTAL" in head.upper()
            return ok, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:  # red caída: no es "no hay curso nuevo"
        return None, f"error: {e}"


def main():
    last = json.load(open(DATA, encoding="utf-8"))["courses"][0]
    nxt = next_course(last)
    ident = [f"{BASE}/apoyo/{nxt}/otros/l0/otros_{n}.csv_bdsc" for n in ("03", "04", "05")]
    matr = [f"{BASE}/matriculado/{nxt}-{s}/comunidad/reg_general/l0/general_1_01.csv_bdsc" for s in ("da", "rd", "avance")]

    found_i = [(u, probe(u)) for u in ident]
    found_m = [(u, probe(u)) for u in matr]
    ident_ok = [u for u, (ok, _) in found_i if ok]
    matr_ok = [u for u, (ok, _) in found_m if ok]
    errors = [u for u, (ok, _) in found_i + found_m if ok is None]

    lines = [f"Último curso cargado: {last}. Curso vigilado: {nxt}.", ""]
    for u, (ok, d) in found_i + found_m:
        lines.append(f"- {'✅' if ok else '·'} {d} — {u}")
    report = "\n".join(lines)
    print(report)

    if errors and not ident_ok:
        print("Errores de red: no se concluye nada.", file=sys.stderr)
        new = ""
    else:
        new = nxt if ident_ok else ""

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"new_course={new}\n")
            f.write(f"matricula_ready={'true' if matr_ok else 'false'}\n")
            f.write("report<<EOF\n" + report + "\nEOF\n")


if __name__ == "__main__":
    main()

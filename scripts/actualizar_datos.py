#!/usr/bin/env python3
"""Actualiza solo los datos de EDUCAbase cuando el Ministerio publica un curso nuevo.

Sin dependencias. Idempotente: si no hay nada nuevo no toca ningún fichero.

  1. Identificación AACC del curso siguiente al último cargado (tablas altascap/otros).
  2. Matrícula (denominador) de cada curso >= 2023-24: usa «rd» (resultados detallados)
     y, si no existe, «da» (datos avance); si el Ministerio revisa las cifras, las sustituye.
  3. Regenera CSV y tasas de los cursos afectados.

Todo se valida antes de escribir (cuadres H+M, CCAA→España, provincias→CCAA, saltos
anómalos). Si algo no cuadra no se escribe nada y se sale con código 2.

Códigos de salida: 0 = sin error (haya o no cambios), 2 = tabla publicada pero no válida.
Con GITHUB_OUTPUT escribe: changed, summary, failed.
"""
import csv, io, json, os, re, sys, time, unicodedata, urllib.error, urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import CCAA, PROVINCIAS  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
D = os.path.join(ROOT, "data")
BASE = "https://estadisticas.educacion.gob.es/EducaJaxiPx/files/_px/es/csv_bdsc/no-universitaria/alumnado"
NOTE_I = "Dato oficial de alumnado atendido por altas capacidades con una medida educativa especifica; no es prevalencia ni identificacion clinica."
NOTE_M = "Dato oficial de alumnado matriculado en enseñanzas no universitarias de régimen general; se usa como denominador para estimar cobertura de identificación."
SEX = {"ambos sexos": "total", "hombres": "hombre", "mujeres": "mujer"}
FIRST_ENROLL_FAMILY = "2023-2024"  # antes (2022-23) la tabla es otra (todas_01) y no se toca
HEARTBEAT_DAYS = 25  # commit periódico: evita que GitHub desactive el cron por inactividad


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None  # un curso inexistente responde 302 -> /404.html


OPENER = urllib.request.build_opener(NoRedirect)


class Invalid(Exception):
    pass


class Unreachable(Exception):
    pass


def fetch(url):
    """Texto del CSV, None si no existe. Reintenta cortes de red; Unreachable si no hay forma."""
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "aci-mapa-datos-actualizador"})
            with OPENER.open(req, timeout=90) as r:
                if r.status != 200:
                    return None
                raw = r.read()
            try:
                return raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                return raw.decode("iso-8859-15")
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308, 404, 403):
                return None
            last = e
        except Exception as e:
            last = e
        time.sleep(3 * (i + 1))
    raise Unreachable(f"{url}: {last}")


# ---------- normalización ----------
def fold(s):
    s = unicodedata.normalize("NFKD", s.replace("º", "").replace("ª", ""))
    return "".join(c for c in s if not unicodedata.combining(c))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", fold(s).lower()).strip("-")


def clean(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def prov_key(s):
    s = re.sub(r"\s*\(\d+\)\s*$", "", clean(s))  # llamadas de nota: «Barcelona (2)»
    return frozenset(fold(p).lower().strip() for p in s.split("/"))


PROV_BY_KEY = {prov_key(p): p for p in PROVINCIAS}


def parse_geo(label, indented):
    """-> (geoLevel, geoName, parent_ccaa|None)"""
    t = clean(label)
    if t.upper() in ("TOTAL", "00 TOTAL"):
        return "country", "España", None
    m = re.match(r"^(\d\d) ", t)
    if m and not indented:
        i = int(m.group(1))
        if not 1 <= i <= len(CCAA):
            raise Invalid(f"código de CCAA desconocido: {label!r}")
        return "ccaa", CCAA[i - 1], None
    k = prov_key(t)
    if k not in PROV_BY_KEY:
        raise Invalid(f"provincia desconocida: {label!r}")
    p = PROV_BY_KEY[k]
    return "province", p, PROVINCIAS[p]


def num(v):
    v = v.strip()
    if re.fullmatch(r"\d{1,3}(\.\d{3})*|\d+", v):
        return int(v.replace(".", ""))
    return None  # «-», «..», vacío: dato suprimido


def rows(text, ncols):
    rd = csv.reader(io.StringIO(text), delimiter=";")
    head = next(rd)
    if len(head) != ncols:
        raise Invalid(f"se esperaban {ncols} columnas y hay {len(head)}: {head}")
    for r in rd:
        if len(r) == ncols and any(r):
            yield r


def parse_table(text, course, source_id, kind):
    """kind 'i' (identificación, 4 cols) o 'm' (matrícula, 5 cols, solo TODOS LOS CENTROS)."""
    out, seen = [], set()
    ccaa = None
    ncols = 4 if kind == "i" else 5
    for r in rows(text, ncols):
        if kind == "m":
            if clean(r[0]).upper() != "TODOS LOS CENTROS":
                continue
            r = r[1:]
        geo, sex, stage, val = r
        if clean(sex).lower() not in SEX:
            raise Invalid(f"sexo desconocido: {sex!r}")
        indented = geo[:1] in (" ", "\xa0")
        level, name, parent = parse_geo(geo, indented)
        if level == "ccaa":
            ccaa = name
        if level == "province" and parent != ccaa:
            raise Invalid(f"provincia {name} fuera de su CCAA ({ccaa})")
        v = num(val)
        if v is None:
            continue
        stage = clean(stage)
        stage = "TOTAL" if stage.upper() == "TOTAL" else re.sub(r"\s*\(\d+\)$", "", stage) if kind == "i" else stage
        s = SEX[clean(sex).lower()]
        key = (name, s, stage)
        if key in seen:
            raise Invalid(f"fila duplicada {key}")
        seen.add(key)
        pre = "educabase-aacc" if kind == "i" else "educabase-enrollment"
        rec = {"id": f"{pre}-{course}-{slug(name)}-{s}-{slug(stage)}", "course": course,
               "geoLevel": level, "geoName": name}
        if kind == "m" and level == "ccaa":  # la matrícula publicada lleva el código oficial 01..19
            rec["geoId"] = "%02d" % (CCAA.index(name) + 1)
        rec.update({"sex": s, "stage": stage, "value": v, "sourceId": source_id,
                    "methodologyNote": NOTE_I if kind == "i" else NOTE_M})
        out.append(rec)
    if not out:
        raise Invalid("tabla vacía")
    return out


# ---------- validación ----------
def validate(recs, label, prev_total=None, prev_count=None):
    idx = {(r["geoName"], r["sex"], r["stage"]): r["value"] for r in recs}
    lvl = {r["geoName"]: r["geoLevel"] for r in recs}
    probs = []
    es = idx.get(("España", "total", "TOTAL"))
    if es is None:
        raise Invalid(f"{label}: falta el total de España")
    for (g, s, st), v in idx.items():
        if s == "total" and ("%s" % g, "hombre", st) in idx and (g, "mujer", st) in idx:
            if idx[(g, "hombre", st)] + idx[(g, "mujer", st)] != v:
                probs.append(f"H+M≠total en {g} / {st}")
    cc = [g for g, l in lvl.items() if l == "ccaa"]
    if len(cc) != len(CCAA):
        probs.append(f"{len(cc)} CCAA en vez de {len(CCAA)}")
    if sum(idx.get((g, "total", "TOTAL"), 0) for g in cc) != es:
        probs.append("suma de CCAA ≠ España")
    by_cc = {}
    for p, c in PROVINCIAS.items():
        if p in lvl:
            by_cc.setdefault(c, []).append(p)
    for c, ps in by_cc.items():
        tot = idx.get((c, "total", "TOTAL"))
        if tot is not None and sum(idx.get((p, "total", "TOTAL"), 0) for p in ps) != tot:
            probs.append(f"provincias ≠ {c}")
    if prev_total and not 0.5 <= es / prev_total <= 2.5:
        probs.append(f"salto anómalo del total nacional: {prev_total} → {es}")
    if prev_count and not 0.8 <= len(recs) / prev_count <= 1.2:
        probs.append(f"nº de registros anómalo: {prev_count} → {len(recs)}")
    if probs:
        raise Invalid(f"{label}: " + "; ".join(probs[:8]))


# ---------- E/S ----------
def load_json(name):
    return json.load(open(os.path.join(D, name), encoding="utf-8"))


def dump_json(name, d, pretty):
    p = os.path.join(D, name)
    s = json.dumps(d, ensure_ascii=False, indent=2) + "\n" if pretty else json.dumps(d, ensure_ascii=False, separators=(",", ":"))
    open(p, "w", encoding="utf-8", newline="\n").write(s)


def read_csv(name):
    with open(os.path.join(D, "csv", name), encoding="utf-8", newline="") as f:
        r = list(csv.reader(f))
    return r[0], r[1:]


def write_csv(name, head, body):
    with open(os.path.join(D, "csv", name), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(head)
        w.writerows(body)


def put_block(body, course, new):
    """Sustituye en su sitio el bloque de un curso (o lo añade al final)."""
    pos = [i for i, r in enumerate(body) if r[0] == course]
    if not pos:
        return body + new
    return body[:pos[0]] + new + [r for r in body[pos[0]:] if r[0] != course]


def next_course(c):
    a = int(c[:4]) + 1
    return f"{a}-{a + 1}"


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (datetime.now().microsecond // 1000)


def ident_candidates(course):
    n = ("03", "04", "05", "02", "06")
    return [(f"educabase-otros-{x}-{course}", f"{BASE}/apoyo/{course}/otros/l0/otros_{x}.csv_bdsc") for x in n] + \
           [(f"educabase-altascap-01-{course}", f"{BASE}/apoyo/{course}/altascap/l0/altascap_01.csv_bdsc")]


def enroll_candidates(course):
    return [f"{BASE}/matriculado/{course}-{s}/comunidad/reg_general/l0/general_1_01.csv_bdsc" for s in ("rd", "da")]


def tasas(ident, enr, course):
    def tot(recs):
        return {(r["geoLevel"], r["geoName"]): r["value"] for r in recs
                if r["course"] == course and r["sex"] == "total" and r["stage"] == "TOTAL"}
    i, m = tot(ident), tot(enr)
    cc, pr = [], []
    for (lv, g), v in i.items():
        if (lv, g) in m and m[(lv, g)]:
            t = round(v / m[(lv, g)], 6)
            if lv == "ccaa":
                cc.append([course, g, str(v), str(m[(lv, g)]), repr(t)])
            elif lv == "province":
                pr.append([course, g, PROVINCIAS[g], str(v), str(m[(lv, g)]), repr(t)])
    key = lambda r: -float(r[-1])
    return sorted(cc, key=key), sorted(pr, key=key)


def csv_rows(recs):
    return [[r["course"], r["geoLevel"], r["geoName"], r["sex"], r["stage"], str(r["value"]), r["sourceId"]] for r in recs]


def main(dry=False):
    log, touched = [], set()
    ident = load_json("educabase-identification.json")
    enr = load_json("educabase-enrollment.json")
    last = ident["courses"][0]
    prev = [r for r in ident["records"] if r["course"] == last]
    prev_total = next(r["value"] for r in prev if r["geoLevel"] == "country" and r["sex"] == "total" and r["stage"] == "TOTAL")

    # 1) identificación del curso siguiente
    nxt = next_course(last)
    for sid, url in ident_candidates(nxt):
        text = fetch(url)
        if text is None:
            continue
        recs = parse_table(text, nxt, sid, "i")
        validate(recs, f"identificación {nxt}", prev_total, len(prev))
        ident["records"] += recs
        ident["courses"].insert(0, nxt)
        ident["sourceIds"].append(sid)
        ident["sourceUrls"][sid] = url
        ident["generatedAt"] = now_iso()
        touched.add(nxt)
        es = next(r["value"] for r in recs if r["geoLevel"] == "country" and r["sex"] == "total" and r["stage"] == "TOTAL")
        log.append(f"Identificación AACC {nxt}: {len(recs)} registros, {es:,} alumnos en España".replace(",", "."))
        break

    # 2) matrícula (nueva o revisada) de cada curso con identificación >= 2023-24
    changed_m = False
    for c in sorted(ident["courses"]):
        if c < FIRST_ENROLL_FAMILY:
            continue
        sid = f"educabase-general-1-01-{c}"
        old = [r for r in enr["records"] if r["course"] == c]
        for url in enroll_candidates(c):
            text = fetch(url)
            if text is None:
                continue
            recs = parse_table(text, c, sid, "m")
            validate(recs, f"matrícula {c}")
            vals = lambda rs: {(r["geoName"], r["sex"], r["stage"]): r["value"] for r in rs}
            if old and vals(old) == vals(recs):  # mismas cifras: no se reescribe el histórico
                if enr["sourceUrls"].get(c) != url:  # solo cambió de «da» a «rd»
                    enr["sourceUrls"][c] = url
                    touched.add(c)
                    changed_m = True
                    log.append(f"Matrícula {c}: ahora desde {url.split('/matriculado/')[1].split('/')[0]} (cifras iguales)")
                break
            enr["records"] = [r for r in enr["records"] if r["course"] != c] + recs
            if c not in enr["courses"]:
                enr["courses"].append(c)
            if sid not in enr["sourceIds"]:
                enr["sourceIds"].append(sid)
            enr["sourceUrls"][c] = url
            touched.add(c)
            changed_m = True
            log.append(f"Matrícula {c}: {'revisada' if old else 'nueva'} ({url.split('/matriculado/')[1].split('/')[0]})")
            break
    if changed_m:
        enr["courses"] = sorted(set(enr["courses"]), reverse=True)
        enr["generatedAt"] = now_iso()

    # 3) escritura
    st_path = os.path.join(D, "estado.json")
    estado = json.load(open(st_path, encoding="utf-8")) if os.path.exists(st_path) else {}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stale = not estado.get("ultimaComprobacion") or \
        (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(estado["ultimaComprobacion"], "%Y-%m-%d")).days >= HEARTBEAT_DAYS
    if touched and not dry:
        dump_json("educabase-identification.json", ident, True)
        dump_json("educabase-enrollment.json", enr, False)
        h, b = read_csv("identificacion.csv")
        for c in touched:
            b = put_block(b, c, csv_rows([r for r in ident["records"] if r["course"] == c]))
        write_csv("identificacion.csv", h, b)
        h, b = read_csv("matricula.csv")
        for c in touched:
            if any(r["course"] == c for r in enr["records"]):
                b = put_block(b, c, csv_rows([r for r in enr["records"] if r["course"] == c]))
        write_csv("matricula.csv", h, b)
        hc, bc = read_csv("tasas_identificacion_ccaa.csv")
        hp, bp = read_csv("tasas_identificacion_provincia.csv")
        for c in sorted(touched):
            tc, tp = tasas(ident["records"], enr["records"], c)
            if tc:
                bc = put_block(bc, c, tc)
            if tp:
                bp = put_block(bp, c, tp)
            if tc or tp:
                log.append(f"Tasas {c}: {len(tc)} CCAA, {len(tp)} provincias")
        write_csv("tasas_identificacion_ccaa.csv", hc, bc)
        write_csv("tasas_identificacion_provincia.csv", hp, bp)
    if (touched or stale) and not dry:
        estado.update({"ultimaComprobacion": today, "ultimoCursoIdentificacion": ident["courses"][0]})
        if touched:
            estado["ultimaCarga"] = today
        json.dump(estado, open(st_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        open(st_path, "a").write("\n")
    return bool(touched), log


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    out = os.environ.get("GITHUB_OUTPUT")
    try:
        changed, log = main(dry)
        msg = "\n".join(log) or "Sin novedades."
        failed = ""
    except Invalid as e:
        changed, msg, failed = False, str(e), "1"
        print("TABLA NO VÁLIDA:", e, file=sys.stderr)
    except Unreachable as e:
        changed, msg, failed = False, f"Sin red, se reintenta mañana: {e}", ""
    print(msg)
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\nfailed={failed}\nsummary<<EOF\n{msg}\nEOF\n")
    sys.exit(2 if failed else 0)

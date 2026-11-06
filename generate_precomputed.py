"""Erzeugt sei_precomputed.json: das Messraster (4 Teilegrößen x 4 Paketzahlen x 200 feste Instanzen), als ganze Zahlen.

    python generate_precomputed.py            # schreibt sei_precomputed.json neu
    python generate_precomputed.py --check    # rechnet neu und vergleicht mit der Datei (Exit 1 bei Abweichung)

Die App rechnet das Raster nicht selbst (es würde jedes Mal Sekunden dauern); tests/test_claims.py rechnet ausgewählte Zellen frisch nach und
vergleicht sie mit der Datei."""

import json
import sys
import time

import sei_constants as C
import sei_evaluation as ev


def erzeugen() -> dict:
    daten = {"seeds": C.SEEDS_PER_CELL, "cap": C.MESS_CAP, "zellen": {}}
    for d in range(len(C.VERTEILUNGEN)):
        for ni in range(len(C.MESS_N)):
            t = time.perf_counter()
            daten["zellen"][ev.zelle_schluessel(d, ni)] = ev.messzelle(d, ni)
            print(f"{ev.zelle_schluessel(d, ni)}: {time.perf_counter() - t:.1f} s", flush=True)
    return daten


def main() -> int:
    daten = erzeugen()
    text = json.dumps(daten, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        gleich = ev.PRECOMPUTED.read_text(encoding="utf-8") == text
        print("gleich" if gleich else "ABWEICHUNG")
        return 0 if gleich else 1
    ev.PRECOMPUTED.write_text(text, encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED)
    return 0


if __name__ == "__main__":
    sys.exit(main())

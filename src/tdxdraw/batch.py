"""CSV / JSON 画线清单与 .eld 文件互转。"""

from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import List

from .eld import Drawing, read_eld

FIELDS = ["market", "code", "line_type", "start_price", "end_price",
          "start_date", "end_date", "start_time", "end_time",
          "period", "line_id", "line_width", "color_bgr"]


def _parse_row(row: dict) -> Drawing:
    d = dict(row)
    for k in ("start_date", "end_date"):
        d[k] = datetime.strptime(str(d[k]), "%Y-%m-%d").date()
    for k in ("start_time", "end_time", "line_id", "line_width", "color_bgr"):
        if k in d:
            d[k] = int(d[k])
    for k in ("start_price", "end_price"):
        d[k] = float(d[k])
    return Drawing(**{k: v for k, v in d.items() if k in FIELDS})


def read_csv(path: str | Path) -> List[Drawing]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [_parse_row(r) for r in csv.DictReader(f)]


def write_csv(path: str | Path, drawings: List[Drawing]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for d in drawings:
            w.writerow({k: getattr(d, k) for k in FIELDS})


def read_json(path: str | Path) -> List[Drawing]:
    items = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(items, dict):
        items = items.get("drawings", [])
    return [_parse_row({k: str(v) for k, v in it.items()}) for it in items]


def write_json(path: str | Path, drawings: List[Drawing]) -> None:
    items = [{k: getattr(d, k) for k in FIELDS} for d in drawings]
    Path(path).write_text(json.dumps({"drawings": items}, ensure_ascii=False, indent=2),
                          encoding="utf-8")


def eld_to_csv(eld_path: str | Path, csv_path: str | Path) -> int:
    ds = read_eld(eld_path)
    write_csv(csv_path, ds)
    return len(ds)


def csv_to_eld(csv_path: str | Path, eld_path: str | Path) -> int:
    ds = read_csv(csv_path)
    from .eld import write_eld
    return write_eld(eld_path, ds)

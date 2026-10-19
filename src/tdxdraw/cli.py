"""tdxdraw 命令行。

用法:
  tdxdraw build  in.csv  out.eld      # CSV/JSON 画线清单 -> 通达信 .eld
  tdxdump 等价: tdxdraw export in.eld out.csv   # .eld -> CSV
"""

from __future__ import annotations

import sys
from pathlib import Path

from .batch import csv_to_eld, eld_to_csv, read_json


def main(argv: list[str] | None = None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) != 3 or a[0] not in ("build", "export"):
        print(__doc__)
        return 1
    cmd, src, dst = a
    if cmd == "build":
        n = csv_to_eld(src, dst) if src.lower().endswith(".csv") else _json_to_eld(src, dst)
        print(f"[tdxdraw] {n} 条画线 -> {dst}（通达信: 画线工具 -> 导入画线）")
    else:
        n = eld_to_csv(src, dst)
        print(f"[tdxdraw] {n} 条画线 -> {dst}")
    return 0


def _json_to_eld(src: str, dst: str) -> int:
    from .eld import write_eld
    ds = read_json(src)
    return write_eld(dst, ds)


if __name__ == "__main__":
    raise SystemExit(main())

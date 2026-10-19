"""tdxdraw — 通达信画线文件（.eld）读写与批量转换。

两条落盘路径：
    1. write_eld    生成 .eld，经通达信"画线导入"功能加载；
    2. write_tdxline 通达信关闭期间直写 tdxline.dat，免导入（实测有效）。

    from tdxdraw import Drawing, write_eld

    d = Drawing("sh", "600519", "hline", 1250.0, 1250.0,
                date(2026, 1, 5), date(2026, 10, 19), line_id=1)
    write_eld("out.eld", [d])
"""

from .batch import csv_to_eld, eld_to_csv, read_csv, read_json, write_csv, write_json
from .eld import (LINE_TYPES, PERIODS, RECORD_SIZE, Drawing,
                  decode, encode, read_eld, write_eld)
from .tdxline import write_tdxline

__version__ = "0.2.0"

__all__ = [
    "Drawing", "encode", "decode", "read_eld", "write_eld", "write_tdxline",
    "read_csv", "write_csv", "read_json", "write_json",
    "csv_to_eld", "eld_to_csv",
    "LINE_TYPES", "PERIODS", "RECORD_SIZE",
    "__version__",
]

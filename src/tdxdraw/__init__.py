"""tdxdraw — 通达信画线文件（.eld）读写与批量转换。

典型流程：把任意来源的坐标清单（CSV / JSON / 你的分析程序输出）
转成通达信官方"画线导入"功能可识别的 .eld 文件。

    from tdxdraw import Drawing, write_eld

    d = Drawing("sh", "600519", "hline", 1250.0, 1250.0,
                date(2026, 1, 5), date(2026, 10, 19), line_id=1)
    write_eld("out.eld", [d])   # 通达信 K 线界面 -> 画线工具 -> 导入画线
"""

from .batch import csv_to_eld, eld_to_csv, read_csv, read_json, write_csv, write_json
from .eld import (LINE_TYPES, PERIODS, RECORD_SIZE, Drawing,
                  decode, encode, read_eld, write_eld)

__version__ = "0.1.0"

__all__ = [
    "Drawing", "encode", "decode", "read_eld", "write_eld",
    "read_csv", "write_csv", "read_json", "write_json",
    "csv_to_eld", "eld_to_csv",
    "LINE_TYPES", "PERIODS", "RECORD_SIZE",
    "__version__",
]

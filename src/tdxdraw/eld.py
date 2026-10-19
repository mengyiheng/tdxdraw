"""tdxdraw.eld — 通达信画线文件（.eld）记录编解码。

每条画线为固定 378 字节记录，格式经通达信官方"画线导入"功能实测验证。
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List

RECORD_SIZE = 0x17A  # 378

MARKETS = {"sz": 0, "sh": 1, "bj": 2}

PERIODS = {
    "1m": 0x07, "5m": 0x00, "15m": 0x01, "30m": 0x02, "60m": 0x03,
    "day": 0x04, "week": 0x05, "month": 0x06, "quarter": 0x0A, "year": 0x0B,
}
PERIOD_DECODE = {v: k for k, v in PERIODS.items()}

LINE_TYPES = {
    "segment": 0x0A, "ray": 0x0B, "arrow": 0x21, "ray2": 0x22,
    "hline": 0x26, "hray": 0x2D, "hsegment": 0x2E,
    "vline": 0x27, "price_tag": 0x2A, "channel": 0x1C,
    "parallel": 0x1D, "gann_percent": 0x0D, "wave": 0x0E,
    "gann_price": 0x1F, "regression": 0x11,
    "circle": 0x23, "rectangle": 0x17, "text": 0x16,
    "gann_fan": 0x0C,
}
LINE_TYPE_DECODE = {v: k for k, v in LINE_TYPES.items()}

# 偏移量表（实测验证）
OFF = {
    "market": 0x00, "code": 0x01, "indicator": 0x18,
    "start_price": 0x56, "end_price": 0x5A, "period": 0x63,
    "line_type": 0x65, "fixed12": 0x66, "start_date": 0x69,
    "start_time": 0x6B, "start_price2": 0x6D, "line_id": 0x71,
    "end_date": 0x75, "end_time": 0x77, "end_price2": 0x79,
    "line_start": 0xCD, "line_width": 0xD1, "line_style": 0xD5,
    "color": 0xD9, "draw_date": 0xE5,
}

# 年份 zone 编码表（zone: 0=1-4月, 1=5-10月, 2=11-12月）
_YEAR_ZONE_YO = {
    (2024, 0): 83, (2024, 1): 81, (2024, 2): 82,
    (2025, 0): 84, (2025, 1): 85, (2025, 2): 86,
    (2026, 0): 88, (2026, 1): 89,
}
_YO_YEAR_ZONE = {v: k for k, v in _YEAR_ZONE_YO.items()}


def _encode_eld_date(d: date) -> int:
    md = d.month * 100 + d.day
    zone = 0 if md <= 511 else (1 if md <= 1023 else 2)
    yo = _YEAR_ZONE_YO.get((d.year, zone))
    if yo is None:
        yo = 80 + (d.year - 2024) * 4 + zone   # 扩展规则（2027+）
    return (yo << 9) | (md - zone * 512)


def _decode_eld_date(v: int) -> date:
    yo, stored_md = v >> 9, v & 0x1FF
    year, zone = _YO_YEAR_ZONE.get(yo, (1941 + yo, 0))
    md = stored_md + zone * 512
    return date(year, md // 100, md % 100)


@dataclass
class Drawing:
    """一条画线。time 字段为当天分钟数（0-1439），日线一般填 900（=15:00）。"""

    market: str          # "sh" / "sz" / "bj"
    code: str            # 6 位代码
    line_type: str       # LINE_TYPES 的键
    start_price: float
    end_price: float
    start_date: date
    end_date: date
    start_time: int = 900
    end_time: int = 900
    period: str = "day"
    line_id: int = 1     # 个股内唯一序号（从 1 开始）
    line_width: int = 1
    color_bgr: int = 0x00FFFFFF          # BGRA
    indicator: bytes = b"\x02STANDK"     # 画线所属指标页

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.market not in MARKETS:
            raise ValueError(f"市场必须是 {list(MARKETS)}: {self.market}")
        if not (self.code.isdigit() and len(self.code) == 6):
            raise ValueError(f"代码必须是 6 位数字: {self.code}")
        if self.line_type not in LINE_TYPES:
            raise ValueError(f"未知画线类型: {self.line_type}")
        if self.period not in PERIODS:
            raise ValueError(f"未知周期: {self.period}")


def encode(d: Drawing) -> bytes:
    """Drawing -> 378 字节记录（通达信画线导入功能可直接识别）。"""
    d.validate()
    r = bytearray(RECORD_SIZE)
    r[OFF["market"]] = MARKETS[d.market]
    r[OFF["code"]:OFF["code"] + 6] = d.code.encode("ascii").ljust(6, b"\x00")
    r[OFF["indicator"]:OFF["indicator"] + 7] = d.indicator[:7].ljust(7, b"\x00")

    struct.pack_into("<f", r, OFF["start_price"], d.start_price)
    struct.pack_into("<f", r, OFF["end_price"], d.end_price)
    r[OFF["period"]] = PERIODS[d.period]
    r[OFF["line_type"]] = LINE_TYPES[d.line_type]
    r[OFF["fixed12"]] = 0x10

    struct.pack_into("<H", r, OFF["start_date"], _encode_eld_date(d.start_date))
    struct.pack_into("<H", r, OFF["start_time"], d.start_time)
    struct.pack_into("<f", r, OFF["start_price2"], d.start_price)

    lid = max(0, d.line_id - 1)
    r[OFF["line_id"]:OFF["line_id"] + 3] = lid.to_bytes(3, "little")

    struct.pack_into("<H", r, OFF["end_date"], _encode_eld_date(d.end_date))
    struct.pack_into("<H", r, OFF["end_time"], d.end_time)
    struct.pack_into("<f", r, OFF["end_price2"], d.end_price)

    r[OFF["line_start"]] = 0x01
    r[OFF["line_width"]] = d.line_width
    r[OFF["line_style"]] = LINE_TYPES[d.line_type]
    struct.pack_into("<I", r, OFF["color"], d.color_bgr)

    now = datetime.now()
    r[OFF["draw_date"]] = (now.day + 204) & 0xFF
    r[OFF["draw_date"] + 1] = (now.month + 34) & 0xFF
    r[OFF["draw_date"] + 2] = (now.year - 1973) & 0xFF
    r[OFF["draw_date"] + 3] = 0x01
    r[OFF["draw_date"] + 4] = 0x01
    return bytes(r)


def decode(rec: bytes) -> Drawing:
    """378 字节记录 -> Drawing。"""
    if len(rec) != RECORD_SIZE:
        raise ValueError(f"记录长度必须为 {RECORD_SIZE} 字节: {len(rec)}")
    return Drawing(
        market={0: "sz", 1: "sh", 2: "bj"}.get(rec[OFF["market"]], "sh"),
        code=rec[OFF["code"]:OFF["code"] + 6].rstrip(b"\x00").decode("ascii", "replace"),
        line_type=LINE_TYPE_DECODE.get(rec[OFF["line_type"]], f"unknown_{rec[OFF['line_type']]:#04x}"),
        start_price=struct.unpack_from("<f", rec, OFF["start_price"])[0],
        end_price=struct.unpack_from("<f", rec, OFF["end_price"])[0],
        start_date=_decode_eld_date(struct.unpack_from("<H", rec, OFF["start_date"])[0]),
        end_date=_decode_eld_date(struct.unpack_from("<H", rec, OFF["end_date"])[0]),
        start_time=struct.unpack_from("<H", rec, OFF["start_time"])[0],
        end_time=struct.unpack_from("<H", rec, OFF["end_time"])[0],
        period=PERIOD_DECODE.get(rec[OFF["period"]], f"p{rec[OFF['period']]:#04x}"),
        line_id=int.from_bytes(rec[OFF["line_id"]:OFF["line_id"] + 3], "little") + 1,
        line_width=rec[OFF["line_width"]],
        color_bgr=struct.unpack_from("<I", rec, OFF["color"])[0],
        indicator=rec[OFF["indicator"]:OFF["indicator"] + 7],
    )


def read_eld(path: str | Path) -> List[Drawing]:
    """读取 .eld 画线文件为 Drawing 列表。"""
    data = Path(path).read_bytes()
    n = len(data) // RECORD_SIZE
    return [decode(data[i * RECORD_SIZE:(i + 1) * RECORD_SIZE]) for i in range(n)]


def write_eld(path: str | Path, drawings: Iterable[Drawing]) -> int:
    """Drawing 列表 -> .eld 文件（通达信画线导入功能可直接加载）。"""
    payload = b"".join(encode(d) for d in drawings)
    Path(path).write_bytes(payload)
    return len(payload) // RECORD_SIZE

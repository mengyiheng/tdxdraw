"""通达信画线存储文件（T0002/tdxline.dat）结构探测。

已确认的观察（基于真实文件逆向）：
- 文件由固定 378 字节的记录串联而成，每条记录对应一条画线；
- 记录头：0x01 + 8 字节证券代码（如 "600809"）+ 0x02 + 8 字节线组名（如 "STANDK"）；
- 价格坐标为小端 float32（如 0x430D451F = 141.33）；
- 日期/时间为紧凑整型，具体编码待对照实验确认。
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

REC_SIZE = 378


@dataclass
class RawRecord:
    offset: int
    kind: int          # 记录头首字节（观察值为 0x01）
    code: str          # 证券代码
    group: str         # 线组名（如 STANDK）
    body: bytes        # 记录剩余原始字节


def iter_records(path: str | Path):
    data = Path(path).read_bytes()
    for off in range(0, len(data) - REC_SIZE + 1, REC_SIZE):
        rec = data[off:off + REC_SIZE]
        if rec[0] != 0x01:
            yield RawRecord(off, rec[0], "", "", rec)   # 非标准记录，原样保留
            continue
        code = rec[1:9].split(b"\x00")[0].decode("ascii", "replace")
        group = rec[9:17].split(b"\x00")[0].decode("ascii", "replace") if rec[9] == 0x02 else ""
        yield RawRecord(off, 0x01, code, group, rec)


if __name__ == "__main__":
    import sys
    from collections import Counter

    path = sys.argv[1] if len(sys.argv) > 1 else r"D:\new_tdx64\T0002\tdxline.dat"
    codes, groups, kinds = Counter(), Counter(), Counter()
    for r in iter_records(path):
        kinds[r.kind] += 1
        if r.code:
            codes[r.code] += 1
        if r.group:
            groups[r.group] += 1
    print(f"记录类型分布: {dict(kinds)}")
    print(f"涉及股票数: {len(codes)}，前 10: {codes.most_common(10)}")
    print(f"线组名分布: {groups.most_common(10)}")

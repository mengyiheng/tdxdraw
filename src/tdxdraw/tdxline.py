"""tdxdraw.tdxline — 通达信客户端画线存储（tdxline.dat）直写。

实测结论（2026-10，通达信 v2023+）：tdxline.dat 记录与 .eld 同构（378 字节），
且客户端启动时会加载追加的正确编码记录——因此**无需手动导入**，
TDX 关闭期间直写文件即可让画线出现在 K 线图上。

⚠️ 使用前提：
    - 通达信必须**完全关闭**（退出时客户端会以内存态重写整个文件，
      运行中注入或运行中追加都会被丢弃）；
    - 操作前请自行备份 tdxline.dat；
    - line_id 需在同股票范围内唯一。
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .eld import Drawing, encode

REC_SIZE = 378


def write_tdxline(tdxline_path: str | Path, drawings: Iterable[Drawing],
                  *, append: bool = True) -> int:
    """把画线直写进通达信的 tdxline.dat。

    drawings 用 tdxdraw.encode 编码（与导入功能逐字节同源）。
    append=True 追加到文件末尾（推荐）；False 覆盖整个文件（慎用）。
    返回写入条数。**调用前请确保通达信已完全退出。**
    """
    payload = b"".join(encode(d) for d in drawings)
    mode = "ab" if append else "wb"
    with open(tdxline_path, mode) as f:
        f.write(payload)
    return len(payload) // REC_SIZE

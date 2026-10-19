# -*- coding: utf-8 -*-
"""tdxline.dat 直写功能测试（字节级；对客户端行为的验证见 FORMAT.md 实测记录）。"""
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from tdxdraw import Drawing, encode, write_tdxline  # noqa: E402


def test_write_tdxline_appends(tmp_path):
    p = tmp_path / "tdxline.dat"
    p.write_bytes(b"\x00" * 378)                      # 模拟已有 1 块
    ds = [Drawing("sh", "600519", "hline", 1250.0, 1250.0,
                  date(2026, 1, 5), date(2026, 10, 19), line_id=88)]
    assert write_tdxline(p, ds, append=True) == 1
    data = p.read_bytes()
    assert len(data) == 2 * 378
    # 追加块与 encode 输出逐字节一致
    assert data[378:] == encode(ds[0])


def test_write_tdxline_overwrite_mode(tmp_path):
    p = tmp_path / "tdxline.dat"
    p.write_bytes(b"\xff" * 100)
    ds = [Drawing("sz", "000001", "segment", 10.0, 11.0,
                  date(2026, 3, 2), date(2026, 3, 5), line_id=1)]
    assert write_tdxline(p, ds, append=False) == 1
    assert p.stat().st_size == 378


def test_write_tdxline_batch(tmp_path):
    p = tmp_path / "tdxline.dat"
    ds = [Drawing("sh", "600519", "hline", 1250.0, 1250.0,
                  date(2026, 1, 5), date(2026, 10, 19), line_id=i)
          for i in (1, 2, 3)]
    assert write_tdxline(p, ds, append=True) == 3
    assert p.stat().st_size == 3 * 378

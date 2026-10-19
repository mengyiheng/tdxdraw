from datetime import date
from pathlib import Path

import pytest

from tdxdraw import Drawing, decode, encode, read_eld, write_eld

FIXTURE = Path(__file__).parent / "fixtures" / "tdx_accepted_001.eld"


def test_decode_real_tdx_accepted_file():
    """通达信官方画线导入功能实测认得的样本，必须能正确解码。"""
    (d,) = read_eld(FIXTURE)
    assert d.market == "sz"
    assert d.code == "002805"
    assert d.line_type == "segment"
    assert d.start_price == pytest.approx(22.20, abs=0.01)
    assert d.end_price == pytest.approx(21.19, abs=0.01)
    assert d.start_date == date(2026, 6, 12)
    assert d.line_id == 3


def test_reencode_matches_tdx_accepted_bytes():
    """重编码应与通达信可接受的原始字节逐字节一致（画线创建日期除外）。"""
    raw = FIXTURE.read_bytes()
    mine = bytearray(encode(decode(raw)))
    mine[0xE5:0xEA] = raw[0xE5:0xEA]      # draw_date 按写入时刻生成
    assert bytes(mine) == raw


def test_encode_decode_roundtrip():
    d = Drawing("sh", "600519", "hline", 1250.0, 1250.0,
                date(2026, 1, 5), date(2026, 10, 19), line_id=7)
    back = decode(encode(d))
    assert back.market == "sh" and back.code == "600519"
    assert back.line_type == "hline"
    assert back.start_price == pytest.approx(1250.0)
    assert back.start_date == date(2026, 1, 5)
    assert back.end_date == date(2026, 10, 19)
    assert back.line_id == 7


def test_eld_file_roundtrip(tmp_path):
    ds = [
        Drawing("sz", "000001", "segment", 10.0, 11.5,
                date(2026, 3, 2), date(2026, 4, 8), line_id=1),
        Drawing("sh", "600519", "rectangle", 1391.6, 1321.62,
                date(2026, 8, 27), date(2026, 9, 30), line_id=2),
    ]
    p = tmp_path / "out.eld"
    assert write_eld(p, ds) == 2
    assert p.stat().st_size == 2 * 378
    back = read_eld(p)
    assert len(back) == 2
    for a, b in zip(back, ds):
        assert a.market == b.market and a.code == b.code
        assert a.line_type == b.line_type
        assert a.start_price == pytest.approx(b.start_price, abs=0.01)
        assert a.end_price == pytest.approx(b.end_price, abs=0.01)
        assert (a.start_date, a.end_date, a.line_id) == (b.start_date, b.end_date, b.line_id)


def test_validation():
    with pytest.raises(ValueError):
        Drawing("xx", "600519", "hline", 1, 1, date(2026, 1, 1), date(2026, 1, 1))
    with pytest.raises(ValueError):
        Drawing("sh", "60051", "hline", 1, 1, date(2026, 1, 1), date(2026, 1, 1))
    with pytest.raises(ValueError):
        Drawing("sh", "600519", "noline", 1, 1, date(2026, 1, 1), date(2026, 1, 1))

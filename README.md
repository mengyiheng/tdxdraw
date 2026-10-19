<p align="center"><img src="assets/cover.png" alt="tdxdraw" width="720"/></p>

# tdxdraw — 通达信画线批量生成与转换工具

把**任意来源的画线坐标清单**（CSV / JSON / 你的分析程序输出）批量转成通达信官方
「画线导入」功能可直接识别的 `.eld` 文件；也可把通达信导出的画线文件反向解析成
CSV / JSON，做二次处理。

- 📤 **生成**：程序化批量画线 → `.eld` → 通达信一键导入
- 📥 **解析**：通达信导出的 `.eld` → CSV / JSON，供回测、复盘、二次分析
- 🪶 **零第三方依赖**，Python 3.9+
- ✅ **逐字节校验**：编码结果与通达信实测可导入的样本文件逐字节一致
- 🧭 **格式完全开源**：378 字节记录结构文档化于 [docs/FORMAT.md](docs/FORMAT.md)

## 安装

```bash
pip install tdxdraw
```

## 快速开始

### 1. 写一个画线清单（CSV）

```csv
market,code,line_type,start_price,end_price,start_date,end_date,period,line_id
sh,600519,hline,1250.00,1250.00,2026-01-05,2026-10-19,day,1
sh,600519,segment,1181.64,1367.85,2026-06-12,2026-09-30,day,2
sz,002805,rectangle,1391.60,1321.62,2026-08-27,2026-09-15,day,1
```

### 2. 转成 .eld 并导入通达信

```bash
tdxdraw build drawings.csv mylines.eld
```

通达信 K 线界面 → 画线工具 → **画线管理（或导入画线）** → 选择 `mylines.eld`，
所有画线立即出现在对应个股的 K 线图上。

### 3. 也可以只用 Python API

```python
from datetime import date
from tdxdraw import Drawing, write_eld, read_eld

d = Drawing("sh", "600519", "hline", 1250.0, 1250.0,
            date(2026, 1, 5), date(2026, 10, 19), line_id=1)
write_eld("mylines.eld", [d])

bars = read_eld("通达信导出.eld")   # 反向解析
```

### 4. 反向导出为 CSV

```bash
tdxdraw export 通达信导出.eld lines.csv
```

## 支持的画线类型

`segment`(线段) `hline`(水平直线) `ray`(直线) `arrow`(箭头) `rectangle`(矩形)
`text`(文字注释) `circle`(圆) `parallel`(平行直线) `channel`(价格通道线)
`gann_fan`(江恩角度线) `gann_percent`(百分比线) `wave`(波段线) 等 40 种，
完整映射见 [docs/FORMAT.md](docs/FORMAT.md)。

支持的周期：`1m 5m 15m 30m 60m day week month quarter year`。

## .eld 文件格式

每条画线 = 378 字节定长记录（小端），核心字段：

| 偏移 | 含义 |
|---|---|
| 0x00 | 市场（0=深 1=沪 2=京） |
| 0x01 | 6 位证券代码 |
| 0x18 | 指标页（如 `\x02STANDK`） |
| 0x56 / 0x5A | 起点 / 终点价格（float32） |
| 0x63 | 周期编码 |
| 0x65 | 画线类型 |
| 0x69 / 0x75 | 起点 / 终点日期（年 zone + 月日 9 位紧凑编码） |
| 0x6B / 0x77 | 起点 / 终点分钟数 |
| 0x71 | 个股内画线序号 |
| 0xD1 / 0xD5 / 0xD9 | 线宽 / 线型 / BGRA 颜色 |

完整字段表见 [docs/FORMAT.md](docs/FORMAT.md)。

## 运行测试

```bash
pip install -e . pytest
pytest
```

测试基准包含一个**经通达信实测可导入**的真实样本文件（逐字节比对）。

## 免责声明

本项目仅做画线坐标数据与通达信画线文件格式之间的转换，不提供任何行情数据，
不构成任何投资建议。使用前请[阅读完整免责声明](DISCLAIMER.md)。

## 量化相关定制需求

承接画线自动化、分析系统 → 通达信画线管道、数据格式转换等定制开发，
联系方式见 [README 联系方式](#量化相关定制需求) 或 [Gitee Issues](https://gitee.com/mengyiheng/tdxdraw/issues)。

## License

MIT

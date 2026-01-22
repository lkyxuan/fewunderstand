"""
单元测试 - 计算逻辑
测试纯计算函数，不依赖数据库
"""
import pytest


# ==================== 涨跌幅计算 ====================

def calculate_change_pct(old_price: float, new_price: float) -> float:
    """计算涨跌幅百分比"""
    if old_price == 0:
        raise ValueError("old_price cannot be zero")
    return ((new_price - old_price) / old_price) * 100


class TestChangePctCalculation:
    """测试涨跌幅计算"""

    def test_positive_change(self):
        """上涨 5%"""
        result = calculate_change_pct(100.0, 105.0)
        assert result == 5.0

    def test_negative_change(self):
        """下跌 10%"""
        result = calculate_change_pct(100.0, 90.0)
        assert result == -10.0

    def test_no_change(self):
        """无变化"""
        result = calculate_change_pct(100.0, 100.0)
        assert result == 0.0

    def test_small_change(self):
        """小幅变化精度"""
        result = calculate_change_pct(100.0, 100.01)
        assert abs(result - 0.01) < 0.0001

    def test_large_change(self):
        """大幅变化 (翻倍)"""
        result = calculate_change_pct(100.0, 200.0)
        assert result == 100.0

    def test_zero_old_price_raises(self):
        """旧价格为0应抛出异常"""
        with pytest.raises(ValueError):
            calculate_change_pct(0.0, 100.0)


# ==================== 信号检测逻辑 ====================

def detect_signal(change_pct: float, threshold: float) -> str | None:
    """
    检测信号类型
    返回: 'pump_5min' | 'dump_5min' | None
    """
    if change_pct >= threshold:
        return "pump_5min"
    elif change_pct <= -threshold:
        return "dump_5min"
    return None


class TestSignalDetection:
    """测试信号检测逻辑"""

    def test_pump_signal(self):
        """涨幅超过阈值触发 pump"""
        result = detect_signal(5.5, 5.0)
        assert result == "pump_5min"

    def test_dump_signal(self):
        """跌幅超过阈值触发 dump"""
        result = detect_signal(-5.5, 5.0)
        assert result == "dump_5min"

    def test_no_signal_within_threshold(self):
        """在阈值范围内不触发信号"""
        result = detect_signal(3.0, 5.0)
        assert result is None

    def test_exact_threshold_triggers_pump(self):
        """恰好等于阈值触发 pump"""
        result = detect_signal(5.0, 5.0)
        assert result == "pump_5min"

    def test_exact_negative_threshold_triggers_dump(self):
        """恰好等于负阈值触发 dump"""
        result = detect_signal(-5.0, 5.0)
        assert result == "dump_5min"

    def test_zero_change_no_signal(self):
        """无变化不触发信号"""
        result = detect_signal(0.0, 5.0)
        assert result is None


# ==================== 价格过滤逻辑 ====================

def should_include_symbol(symbol: str, quote_asset: str, exclude_patterns: list[str]) -> bool:
    """
    判断是否应该包含该交易对
    """
    if not symbol.endswith(quote_asset):
        return False
    for pattern in exclude_patterns:
        if pattern in symbol:
            return False
    return True


class TestSymbolFilter:
    """测试交易对过滤逻辑"""

    def test_valid_usdt_pair(self):
        """有效的 USDT 交易对"""
        result = should_include_symbol("BTCUSDT", "USDT", ["UP", "DOWN", "BEAR", "BULL"])
        assert result is True

    def test_non_usdt_pair(self):
        """非 USDT 交易对被排除"""
        result = should_include_symbol("BTCETH", "USDT", [])
        assert result is False

    def test_leveraged_token_excluded(self):
        """杠杆代币被排除"""
        result = should_include_symbol("BTCUPUSDT", "USDT", ["UP", "DOWN"])
        assert result is False

    def test_bear_token_excluded(self):
        """熊市代币被排除"""
        result = should_include_symbol("ETHBEARUSDT", "USDT", ["BEAR", "BULL"])
        assert result is False

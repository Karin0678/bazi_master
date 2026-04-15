"""
规则引擎测试
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bazi_master.core.bazi_calc import calculate_bazi
from bazi_master.core.wuxing import analyze_wuxing_strength
from bazi_master.core.dayun import calculate_dayun
from bazi_master.services.rules_engine import generate_rules_analysis


class TestRulesEngine:

    def setup_method(self):
        """初始化测试数据"""
        self.bazi = calculate_bazi(1990, 1, 27, 15, 0, "男")
        self.wuxing = analyze_wuxing_strength(self.bazi)
        self.dayun = calculate_dayun(self.bazi)

    def test_wuxing_analysis(self):
        """测试五行旺衰分析"""
        wuxing = self.wuxing

        assert "strength" in wuxing
        assert wuxing["strength"] in ["身强", "身弱", "中和"]
        assert "scores" in wuxing
        assert "xiyong" in wuxing
        assert "xiyong" in wuxing["xiyong"]
        assert "jishen" in wuxing["xiyong"]

        print(f"✓ 五行分析：{wuxing['strength']}，喜{wuxing['xiyong']['xiyong']}，忌{wuxing['xiyong']['jishen']}")

    def test_dayun_calculation(self):
        """测试大运计算"""
        dayun = self.dayun

        assert "dayuns" in dayun
        assert len(dayun["dayuns"]) == 10
        assert "liunian" in dayun
        assert "direction" in dayun
        assert dayun["direction"] in ["顺行", "逆行"]

        print(f"✓ 大运{dayun['direction']}，起运{dayun['start_age']}")
        for d in dayun["dayuns"][:3]:
            print(f"  {d['gz']}大运（{d['year_start']}-{d['year_end']}）")

    def test_overview_analysis(self):
        """测试命格总论生成"""
        text = generate_rules_analysis(self.bazi, self.wuxing, self.dayun, "overview")

        assert len(text) > 100
        assert "命格" in text or "日主" in text
        print(f"✓ 命格总论生成：{len(text)}字")
        print(text[:200] + "...")

    def test_personality_analysis(self):
        """测试性格分析生成"""
        text = generate_rules_analysis(self.bazi, self.wuxing, self.dayun, "personality")
        assert len(text) > 50
        print(f"✓ 性格分析生成：{len(text)}字")

    def test_career_analysis(self):
        """测试事业分析生成"""
        text = generate_rules_analysis(self.bazi, self.wuxing, self.dayun, "career")
        assert len(text) > 50
        print(f"✓ 事业分析生成：{len(text)}字")

    def test_dayun_analysis(self):
        """测试大运分析生成"""
        text = generate_rules_analysis(self.bazi, self.wuxing, self.dayun, "dayun")
        assert len(text) > 50
        print(f"✓ 大运分析生成：{len(text)}字")

    def test_shishen_calculation(self):
        """测试十神计算"""
        from bazi_master.core.constants import get_shishen

        # 庚日主（金阳）
        # 庚（金阳）克甲（木阳）：庚克甲，同阴阳，甲为偏财
        result = get_shishen("庚", "甲")
        assert result == "偏财", f"庚日干，甲应为偏财，实际为{result}"

        # 壬（水阳）庚生壬：壬为食神
        result = get_shishen("庚", "壬")
        assert result == "食神", f"庚日干，壬应为食神，实际为{result}"

        # 戊（土阳）生庚：戊为偏印
        result = get_shishen("庚", "戊")
        assert result == "偏印", f"庚日干，戊应为偏印，实际为{result}"

        print("✓ 十神计算正确")


if __name__ == "__main__":
    import traceback

    tests = TestRulesEngine()
    tests.setup_method()

    methods = [
        tests.test_wuxing_analysis,
        tests.test_dayun_calculation,
        tests.test_overview_analysis,
        tests.test_personality_analysis,
        tests.test_career_analysis,
        tests.test_dayun_analysis,
        tests.test_shishen_calculation,
    ]

    passed = 0
    failed = 0
    for method in methods:
        try:
            method()
            passed += 1
        except Exception as e:
            print(f"✗ {method.__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*40}")
    print(f"测试完成：{passed} 通过，{failed} 失败")

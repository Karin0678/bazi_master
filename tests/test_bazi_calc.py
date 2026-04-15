"""
八字计算准确性测试
验证已知生日的八字结果
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bazi_master.core.bazi_calc import calculate_bazi


class TestBaziCalculation:
    """八字计算测试"""

    def test_known_bazi_1990_01_27_shen(self):
        """
        测试：1990年1月27日申时（15:00）男
        预期四柱：己巳·丁丑·壬辰·戊申
        （1990-01-27在立春前，故年柱用1989年己巳；在小寒后，月支丑）
        （日柱壬辰：以2000-01-07=甲子为基准日，向前推3632天得index=28=壬辰）
        """
        result = calculate_bazi(1990, 1, 27, 15, 0, "男")
        pillars = result["pillars"]

        # 年柱：己巳（1990-01-27在立春前，按1989年己巳算）
        assert pillars["year"]["tg"] == "己", f"年干应为己，实际为{pillars['year']['tg']}"
        assert pillars["year"]["dz"] == "巳", f"年支应为巳，实际为{pillars['year']['dz']}"

        # 月柱：丁丑（1990年小寒1月6日后，立春2月4日前，月支丑）
        assert pillars["month"]["tg"] == "丁", f"月干应为丁，实际为{pillars['month']['tg']}"
        assert pillars["month"]["dz"] == "丑", f"月支应为丑，实际为{pillars['month']['dz']}"

        # 日柱：壬辰
        assert pillars["day"]["tg"] == "壬", f"日干应为壬，实际为{pillars['day']['tg']}"
        assert pillars["day"]["dz"] == "辰", f"日支应为辰，实际为{pillars['day']['dz']}"

        # 时柱：戊申（壬日申时）
        assert pillars["hour"]["tg"] == "戊", f"时干应为戊，实际为{pillars['hour']['tg']}"
        assert pillars["hour"]["dz"] == "申", f"时支应为申，实际为{pillars['hour']['dz']}"

        print(f"✓ 1990-01-27 申时：{pillars['year']['gz']}·{pillars['month']['gz']}·{pillars['day']['gz']}·{pillars['hour']['gz']}")

    def test_day_master_wuxing(self):
        """测试日主五行判断"""
        result = calculate_bazi(1990, 1, 27, 15, 0, "男")
        dm = result["day_master"]

        assert dm["tg"] == "壬"
        assert dm["wuxing"] == "水"
        assert dm["yinyang"] == "阳"
        print(f"✓ 日主：{dm['tg']}（{dm['yinyang']}{dm['wuxing']}）")

    def test_wuxing_count_structure(self):
        """测试五行统计结构"""
        result = calculate_bazi(1990, 1, 27, 15, 0, "男")
        wuxing = result["wuxing"]

        assert "木" in wuxing
        assert "火" in wuxing
        assert "土" in wuxing
        assert "金" in wuxing
        assert "水" in wuxing
        print(f"✓ 五行分布：木{wuxing['木']:.1f} 火{wuxing['火']:.1f} 土{wuxing['土']:.1f} 金{wuxing['金']:.1f} 水{wuxing['水']:.1f}")

    def test_2000_birth(self):
        """测试2000年后出生的八字计算"""
        result = calculate_bazi(2000, 6, 15, 9, 0, "女")
        pillars = result["pillars"]

        # 验证结构完整
        for col in ["year", "month", "day", "hour"]:
            assert "tg" in pillars[col]
            assert "dz" in pillars[col]
            assert "gz" in pillars[col]
            assert len(pillars[col]["gz"]) == 2

        print(f"✓ 2000-06-15 巳时：{pillars['year']['gz']}·{pillars['month']['gz']}·{pillars['day']['gz']}·{pillars['hour']['gz']}")

    def test_hour_to_dizhi(self):
        """测试时辰转地支"""
        from bazi_master.core.constants import hour_to_dizhi

        assert hour_to_dizhi(0) == "子"
        assert hour_to_dizhi(23) == "子"
        assert hour_to_dizhi(1) == "丑"
        assert hour_to_dizhi(3) == "寅"
        assert hour_to_dizhi(15) == "申"
        print("✓ 时辰转地支正确")

    def test_gender_bazi(self):
        """测试男女命盘均可正常计算"""
        for gender in ["男", "女"]:
            result = calculate_bazi(1985, 3, 15, 10, 30, gender)
            assert result["gender"] == gender
        print("✓ 男女命盘均正常")


class TestSolarTerms:
    """节气时间表测试"""

    def test_get_month_jieqi(self):
        """测试节气月令获取"""
        from bazi_master.core.solar_terms import get_month_jieqi

        # 1990年1月27日：应在小寒之后，立春之前，月令为丑月
        _, month_zhi = get_month_jieqi(1990, 1, 27, 15, 0)
        assert month_zhi == "丑", f"1990-01-27月支应为丑，实际为{month_zhi}"

        # 验证立春后为寅月
        _, month_zhi_feb = get_month_jieqi(1990, 3, 15, 12, 0)
        assert month_zhi_feb == "卯", f"1990-03-15月支应为卯，实际为{month_zhi_feb}"

        print("✓ 节气月令获取正确")

    def test_solar_terms_table_coverage(self):
        """测试节气表覆盖范围"""
        from bazi_master.core.solar_terms import SOLAR_TERMS_TABLE

        assert 2000 in SOLAR_TERMS_TABLE
        assert 2025 in SOLAR_TERMS_TABLE
        assert 2030 in SOLAR_TERMS_TABLE

        # 每年应有12个节气
        for year in [2000, 2010, 2020, 2025]:
            terms = SOLAR_TERMS_TABLE[year]
            assert "立春" in terms
            assert "小寒" in terms
            assert len(terms) == 12

        print(f"✓ 节气表覆盖{min(SOLAR_TERMS_TABLE)}-{max(SOLAR_TERMS_TABLE)}年")


if __name__ == "__main__":
    # 直接运行时执行所有测试
    import traceback

    tests = TestBaziCalculation()
    solar_tests = TestSolarTerms()

    all_methods = [
        tests.test_known_bazi_1990_01_27_shen,
        tests.test_day_master_wuxing,
        tests.test_wuxing_count_structure,
        tests.test_2000_birth,
        tests.test_hour_to_dizhi,
        tests.test_gender_bazi,
        solar_tests.test_get_month_jieqi,
        solar_tests.test_solar_terms_table_coverage,
    ]

    passed = 0
    failed = 0
    for method in all_methods:
        try:
            method()
            passed += 1
        except Exception as e:
            print(f"✗ {method.__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*40}")
    print(f"测试完成：{passed} 通过，{failed} 失败")

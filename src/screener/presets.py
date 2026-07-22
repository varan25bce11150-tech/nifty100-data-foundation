"""
Sprint 3 - Day 16
Preset Screeners
"""

from .engine import ScreenerEngine


class PresetScreeners:
    """
    Wrapper around ScreenerEngine for all predefined screeners.
    """

    def __init__(self):
        self.engine = ScreenerEngine()

    def quality_compounder(self):
        return self.engine.run_preset("quality_compounder")

    def value_pick(self):
        return self.engine.run_preset("value_pick")

    def growth_accelerator(self):
        return self.engine.run_preset("growth_accelerator")

    def dividend_champion(self):
        return self.engine.run_preset("dividend_champion")

    def debt_free_bluechip(self):
        return self.engine.run_preset("debt_free_bluechip")

    def turnaround_watch(self):
        return self.engine.run_preset("turnaround_watch")

    def all_presets(self):
        """
        Run every preset and return a dictionary of DataFrames.
        """

        return {
            "Quality Compounder": self.quality_compounder(),
            "Value Pick": self.value_pick(),
            "Growth Accelerator": self.growth_accelerator(),
            "Dividend Champion": self.dividend_champion(),
            "Debt Free Bluechip": self.debt_free_bluechip(),
            "Turnaround Watch": self.turnaround_watch(),
        }

    def summary(self):
        """
        Print summary of preset results.
        """

        results = self.all_presets()

        print("=" * 60)
        print("SPRINT 3 - DAY 16")
        print("=" * 60)

        for name, df in results.items():
            print(f"{name:<25} : {len(df):>3} companies")

        print("=" * 60)

    def close(self):
        self.engine.conn.close()


if __name__ == "__main__":

    screener = PresetScreeners()

    screener.summary()

    screener.close()
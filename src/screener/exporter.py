"""
Sprint 3 - Day 16
Excel Exporter
"""

from pathlib import Path

import pandas as pd

from src.screener.engine import ScreenerEngine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


class ScreenerExporter:

    def __init__(self):
        self.engine = ScreenerEngine()

    def format_sheet(self, writer, sheet_name, df):

        worksheet = writer.sheets[sheet_name]

    # Freeze first row
        worksheet.freeze_panes(1, 0)

    # Auto filter
        worksheet.autofilter(
            0,
            0,
            max(len(df), 1),
            len(df.columns) - 1,
        )

    # Auto-fit columns
        for idx, column in enumerate(df.columns):

            values = [str(column)]
            values.extend(
                df[column].fillna("").astype(str).tolist()
            )

            width = max(len(v) for v in values) + 2

            worksheet.set_column(idx, idx, min(width, 35))

    def export_preset(self, preset):

        df = self.engine.run_preset(preset)

        filename = OUTPUT_DIR / f"{preset}.xlsx"

        with pd.ExcelWriter(
            filename,
            engine="xlsxwriter"
        ) as writer:

            df.to_excel(
                writer,
                sheet_name="Results",
                index=False
            )

            self.format_sheet(
                writer,
                "Results",
                df
            )

        print(f"✓ {preset} exported ({len(df)} companies)")

    def export_all(self):

        presets = self.engine.load_config().keys()

        for preset in presets:
            self.export_preset(preset)

        print("\nAll preset exports completed.")

    def export_peer_data(self):

        query = """
        SELECT *
        FROM peer_percentiles
        """

        df = pd.read_sql(query, self.engine.conn)

        filename = OUTPUT_DIR / "peer_comparison.xlsx"

        with pd.ExcelWriter(
            filename,
            engine="xlsxwriter"
        ) as writer:

            df.to_excel(
                writer,
                sheet_name="Peer Comparison",
                index=False
            )

            self.format_sheet(
                writer,
                "Peer Comparison",
                df
            )

        print("✓ Peer comparison exported")

    def run(self):

        self.export_all()

        self.export_peer_data()

        print("\nSprint 3 Export Complete.")


if __name__ == "__main__":

    ScreenerExporter().run()
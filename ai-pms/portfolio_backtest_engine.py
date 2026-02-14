"""
                r = returns_slice.loc[returns_slice["symbol"] == symbol, "ret_1d"]
                if not r.empty:
                    port_ret += w * float(r.iloc[0])

            nav *= 1 + port_ret

            nav_series.append({"date": next_date, "nav": nav})

        if not nav_series:
            raise ValueError("Backtest produced no NAV series.")

        return pd.DataFrame(nav_series)

    # ---------------- METRICS ----------------

    def _save_summary(self, nav_df: pd.DataFrame) -> None:
        nav_df = nav_df.sort_values("date")

        total_return = nav_df["nav"].iloc[-1] - 1
        days = (nav_df["date"].iloc[-1] - nav_df["date"].iloc[0]).days
        cagr = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0

        daily_ret = nav_df["nav"].pct_change().dropna()
        sharpe = np.sqrt(252) * daily_ret.mean() / daily_ret.std() if len(daily_ret) > 1 else 0

        drawdown = (nav_df["nav"] / nav_df["nav"].cummax() - 1).min()

        summary = {
            "total_return": float(total_return),
            "cagr": float(cagr),
            "sharpe": float(sharpe),
            "max_drawdown": float(drawdown),
        }

        SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SUMMARY_PATH, "w") as f:
            json.dump(summary, f, indent=2)

        print("✓ Backtest summary saved →", SUMMARY_PATH)
        print(summary)

    # ---------------- SAVE ----------------

    def _save(self, nav_df: pd.DataFrame) -> None:
        RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        nav_df.to_parquet(RESULT_PATH, index=False)
        print(f"✓ backtest_results.parquet created → {RESULT_PATH}")


# --------------------------------------------------
# CLI ENTRY
# --------------------------------------------------


def main():
    engine = PortfolioBacktestEngine()
    nav = engine.run()

    print("NAV start:", nav["nav"].iloc[0])
    print("NAV end:", nav["nav"].iloc[-1])
    print("Rows:", len(nav))


if __name__ == "__main__":
    main()

import pandas as pd
class AlphaModel:
    """
    LightGBM-based weekly retrained alpha prediction model.

    Predicts 1-week forward return for each stock.
    """

    def __init__(self):
        self.model = None
        self.feature_cols = None

    def _prepare_target(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["fwd_ret_5d"] = (
            df.groupby("symbol")["ret_1d"]
            .shift(-5)
            .rolling(5)
            .sum()
        )
        return df

    def _select_features(self, df: pd.DataFrame):
        ignore_cols = {"date", "symbol", "fwd_ret_5d"}
        self.feature_cols = [c for c in df.columns if c not in ignore_cols]

    def fit(self, df: pd.DataFrame):
        df = self._prepare_target(df)
        df = df.dropna()

        self._select_features(df)

        X = df[self.feature_cols]
        y = df["fwd_ret_5d"]

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        self.model = lgb.LGBMRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )

        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_val)
        rmse = mean_squared_error(y_val, preds, squared=False)

        print(f"Validation RMSE: {rmse:.6f}")

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        X = df[self.feature_cols]
        df["alpha_score"] = self.model.predict(X)
        return df[["date", "symbol", "alpha_score"]]

    def save(self, path):
        joblib.dump((self.model, self.feature_cols), path)

    def load(self, path):
        self.model, self.feature_cols = joblib.load(path)

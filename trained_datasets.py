from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "trained_models"
RANDOM_STATE = 42


DATASETS: List[Dict[str, object]] = [
    {
        "name": "crop_recommendation",
        "path": "Crop_recommendation.csv",
        "target": "label",
        "task": "classification",
    },
    {
        "name": "india_rainfall",
        "path": "India_rainfall_act_dep_1901_2016_1.csv",
        "target": "Actual Rainfall: JUN-SEPT",
        "task": "regression",
    },
    {
        "name": "smart_city_index",
        "path": "Smart_City_index_headers.csv",
        "target": "SmartCity_Index",
        "task": "regression",
        "drop": ["Id", "SmartCity_Index_relative_Edmonton"],
    },
    {
        "name": "cities_literacy",
        "path": "cities_r2.csv",
        "target": "effective_literacy_rate_total",
        "task": "regression",
    },
    {
        "name": "water_leak_status",
        "path": "water_leak_detection_1000_rows.csv",
        "target": "Leak Status",
        "task": "classification",
    },
    {
        "name": "water_burst_status",
        "path": "water_leak_detection_1000_rows.csv",
        "target": "Burst Status",
        "task": "classification",
    },
    {
        "name": "water_potability",
        "path": "water_potability.csv",
        "target": "Potability",
        "task": "classification",
    },
    {
        "name": "weather_condition",
        "path": "weather_data_extended.csv",
        "target": "Weather Condition",
        "task": "classification",
    },
    {
        "name": "flood_small",
        "path": "archive-5/flood.csv",
        "target": "FloodProbability",
        "task": "regression",
    },
    {
        "name": "flood_train",
        "path": "archive-5/train.csv",
        "target": "FloodProbability",
        "task": "regression",
        "drop": ["id"],
        "prediction_path": "archive-5/test.csv",
        "prediction_id": "id",
    },
]


def make_one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def clean_frame(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]

    for column in df.select_dtypes(include=["object"]).columns:
        converted = pd.to_datetime(df[column], errors="coerce")
        if converted.notna().mean() >= 0.8:
            df[f"{column}_year"] = converted.dt.year
            df[f"{column}_month"] = converted.dt.month
            df[f"{column}_day"] = converted.dt.day
            df[f"{column}_hour"] = converted.dt.hour
            df[f"{column}_minute"] = converted.dt.minute
            df = df.drop(columns=[column])

    return df


def split_location_column(df: pd.DataFrame) -> pd.DataFrame:
    if "location" not in df.columns:
        return df

    location = df["location"].astype(str).str.split(",", n=1, expand=True)
    if location.shape[1] == 2:
        df = df.copy()
        df["latitude"] = pd.to_numeric(location[0], errors="coerce")
        df["longitude"] = pd.to_numeric(location[1], errors="coerce")
        df = df.drop(columns=["location"])
    return df


def build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    numeric_features = features.select_dtypes(include=[np.number, "bool"]).columns.tolist()
    categorical_features = [
        column for column in features.columns if column not in numeric_features
    ]

    transformers = []
    if numeric_features:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            )
        )
    if categorical_features:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", make_one_hot_encoder()),
                    ]
                ),
                categorical_features,
            )
        )

    return ColumnTransformer(transformers=transformers, remainder="drop")


def build_model(task: str):
    if task == "classification":
        return HistGradientBoostingClassifier(
            max_iter=120,
            learning_rate=0.08,
            random_state=RANDOM_STATE,
            early_stopping=True,
        )

    return HistGradientBoostingRegressor(
        max_iter=160,
        learning_rate=0.08,
        random_state=RANDOM_STATE,
        early_stopping=True,
    )


def regression_metrics(y_true: Iterable[float], y_pred: Iterable[float]) -> Dict[str, float]:
    mse = mean_squared_error(y_true, y_pred)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def classification_metrics(y_true: Iterable[int], y_pred: Iterable[int]) -> Dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }


def train_dataset(config: Dict[str, object]) -> Dict[str, object]:
    name = str(config["name"])
    path = ROOT / str(config["path"])
    target = str(config["target"]).strip()
    task = str(config["task"])
    drop = [str(column).strip() for column in config.get("drop", [])]

    print(f"\nTraining {name} from {path.relative_to(ROOT)}")
    df = clean_frame(pd.read_csv(path))
    df = split_location_column(df)

    if target not in df.columns:
        raise ValueError(f"{name}: target column {target!r} not found")

    df = df.dropna(subset=[target])
    y = df[target]
    X = df.drop(columns=[target] + [column for column in drop if column in df.columns])

    label_encoder = None
    stratify = None
    if task == "classification":
        label_encoder = LabelEncoder()
        y = pd.Series(label_encoder.fit_transform(y.astype(str)), index=y.index)
        class_counts = y.value_counts()
        if len(class_counts) > 1 and class_counts.min() >= 2:
            stratify = y

    test_size = 0.2 if len(df) >= 50 else 0.3
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(X_train)),
            ("model", build_model(task)),
        ]
    )
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    metrics = (
        classification_metrics(y_test, predictions)
        if task == "classification"
        else regression_metrics(y_test, predictions)
    )

    artifact = {
        "pipeline": pipeline,
        "label_encoder": label_encoder,
        "target": target,
        "task": task,
        "features": X.columns.tolist(),
    }
    model_path = OUTPUT_DIR / f"{name}.joblib"
    joblib.dump(artifact, model_path)

    result = {
        "name": name,
        "path": str(path.relative_to(ROOT)),
        "target": target,
        "task": task,
        "rows": int(len(df)),
        "features": int(X.shape[1]),
        "model_path": str(model_path.relative_to(ROOT)),
        "metrics": metrics,
    }

    prediction_path = config.get("prediction_path")
    if prediction_path:
        predict_holdout(config, artifact)

    print(json.dumps(result, indent=2))
    return result


def predict_holdout(config: Dict[str, object], artifact: Dict[str, object]) -> None:
    path = ROOT / str(config["prediction_path"])
    prediction_id = config.get("prediction_id")
    target = str(config["target"]).strip()

    df = clean_frame(pd.read_csv(path))
    df = split_location_column(df)
    ids = df[prediction_id] if prediction_id and prediction_id in df.columns else df.index

    drop_columns = [target]
    drop_columns.extend(str(column).strip() for column in config.get("drop", []))
    X = df.drop(columns=[column for column in drop_columns if column in df.columns])
    X = X.reindex(columns=artifact["features"])

    predictions = artifact["pipeline"].predict(X)
    output = pd.DataFrame({prediction_id or "row": ids, target: predictions})
    output_path = OUTPUT_DIR / f"{config['name']}_predictions.csv"
    output.to_csv(output_path, index=False)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    results = []
    failures = []
    for config in DATASETS:
        try:
            results.append(train_dataset(config))
        except Exception as exc:
            failures.append({"name": config.get("name"), "error": str(exc)})
            print(f"Failed {config.get('name')}: {exc}")

    report = {"results": results, "failures": failures}
    report_path = OUTPUT_DIR / "training_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\nSaved report to {report_path.relative_to(ROOT)}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

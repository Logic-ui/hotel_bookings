"""
Model Training & Evaluation Module for Hotel Booking Cancellation Prediction.
Benchmarks Logistic Regression, Random Forest, and HistGradientBoosting classifiers.
Saves the best-performing pipeline and performance metrics.
"""

import os
import json
import time
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

from src.data_pipeline import load_raw_data, prepare_ml_data


def build_preprocessor(numerical_cols: list, categorical_cols: list) -> ColumnTransformer:
    """Constructs sklearn ColumnTransformer for numeric scaling and one-hot encoding."""
    num_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    
    cat_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_transformer, numerical_cols),
            ('cat', cat_transformer, categorical_cols)
        ],
        remainder='drop'
    )
    return preprocessor


def evaluate_model(name: str, pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
    """Computes comprehensive evaluation metrics for a trained model pipeline."""
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else None
    
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_proba)) if y_proba is not None else 0.0
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    return {
        'model_name': name,
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'roc_auc': round(roc_auc, 4),
        'confusion_matrix': cm,
        'classification_report': classification_report(y_test, y_pred, output_dict=True)
    }


def train_and_evaluate_all(
    data_path: str = "hotel_bookings.csv",
    output_dir: str = "models",
    sample_size: int = None
) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Loads data, trains Logistic Regression, Random Forest, and HistGradientBoosting,
    evaluates them, and saves the top-performing pipeline.
    """
    os.makedirs(output_dir, exist_ok=True)
    print("Preparing dataset for ML modeling...")
    raw_df = load_raw_data(data_path)
    X, y, num_cols, cat_cols = prepare_ml_data(raw_df)
    
    if sample_size and sample_size < len(X):
        print(f"Sampling {sample_size} records for rapid training...")
        X = X.sample(n=sample_size, random_state=42)
        y = y.loc[X.index]
        
    print(f"Dataset shape: {X.shape}, Target cancellation rate: {y.mean():.2%}")
    
    # 80/20 Stratified Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    preprocessor = build_preprocessor(num_cols, cat_cols)
    
    # Define models
    models = {
        'Logistic Regression': Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', LogisticRegression(max_iter=1000, random_state=42, C=1.0))
        ]),
        'Random Forest': Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=100, max_depth=16, random_state=42, n_jobs=-1))
        ]),
        'Gradient Boosting (Hist)': Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', HistGradientBoostingClassifier(max_iter=150, max_depth=12, random_state=42))
        ])
    }
    
    benchmark_results = {}
    fitted_pipelines = {}
    
    for name, pipe in models.items():
        print(f"\n--- Training {name} ---")
        t0 = time.time()
        pipe.fit(X_train, y_train)
        train_time = round(time.time() - t0, 2)
        print(f"Training completed in {train_time}s")
        
        metrics = evaluate_model(name, pipe, X_test, y_test)
        metrics['train_time_seconds'] = train_time
        benchmark_results[name] = metrics
        fitted_pipelines[name] = pipe
        print(f"Accuracy: {metrics['accuracy']:.4f} | ROC-AUC: {metrics['roc_auc']:.4f} | F1: {metrics['f1_score']:.4f}")

    # Determine best model based on ROC-AUC
    best_model_name = max(benchmark_results.keys(), key=lambda k: benchmark_results[k]['roc_auc'])
    best_pipeline = fitted_pipelines[best_model_name]
    print(f"\n>> Best performing model: {best_model_name} (ROC-AUC: {benchmark_results[best_model_name]['roc_auc']:.4f})")
    
    # Extract Feature Importances if available
    feature_importances = []
    try:
        classifier = best_pipeline.named_steps['classifier']
        ohe = best_pipeline.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot']
        ohe_cols = list(ohe.get_feature_names_out(cat_cols))
        all_feature_names = num_cols + ohe_cols
        
        if hasattr(classifier, 'feature_importances_'):
            importances = classifier.feature_importances_
            feat_imp = sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True)
            feature_importances = [{'feature': f, 'importance': round(float(imp), 4)} for f, imp in feat_imp[:20]]
        elif hasattr(classifier, 'coef_'):
            importances = np.abs(classifier.coef_[0])
            feat_imp = sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True)
            feature_importances = [{'feature': f, 'importance': round(float(imp), 4)} for f, imp in feat_imp[:20]]
    except Exception as e:
        print(f"Feature importance extraction notice: {e}")

    # Save best model artifact
    model_path = os.path.join(output_dir, "best_cancellation_model.joblib")
    joblib.dump(best_pipeline, model_path)
    print(f"Saved model pipeline to {model_path}")
    
    # Save benchmark metadata
    metadata = {
        'best_model': best_model_name,
        'trained_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'dataset_total_samples': len(X),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'numerical_features': num_cols,
        'categorical_features': cat_cols,
        'models_benchmark': benchmark_results,
        'top_feature_importances': feature_importances
    }
    
    metadata_path = os.path.join(output_dir, "model_metrics.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata and benchmark to {metadata_path}")
    
    return best_pipeline, metadata


if __name__ == "__main__":
    csv_file = os.path.join(os.path.dirname(__file__), "..", "hotel_bookings.csv")
    models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    train_and_evaluate_all(csv_file, models_dir)

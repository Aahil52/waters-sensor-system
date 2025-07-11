import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import argparse

def main():
    
    # argument parsing logic
    parser = argparse.ArgumentParser(description = "Train all ML models and save with TDS/noTDS variants.")
    parser.add_argument('--data', type = str, required = True, help = "Path to input csv")
    args = parser.parse_args()

    # load and sort
    df = pd.read_csv(args.data)

    # parse quarter column (M/D/YYYY)
    df['Date'] = pd.to_datetime(df['Quarter_DDMMYYYY'], format='%m/%d/%Y')

    # sort by date to split into train/test
    df = df.sort_values('Date').reset_index(drop=True)

    # create numeric date feature
    df['DateOrdinal'] = df['Date'].map(pd.Timestamp.toordinal)

    # define feature sets
    features_with_tds = ['DateOrdinal', 'Temp', 'pH', 'Turbidity', 'TDS']
    features_no_tds = ['DateOrdinal', 'Temp', 'pH', 'Turbidity']
    target_column = 'DO'

    X_full = df[features_with_tds]
    X_notds = df[features_no_tds]
    y = df[target_column]

    # split into 80/20 train/test
    n_rows = len(df)
    split_idx = int(n_rows * 0.8)

    X_full_train = X_full.iloc[:split_idx].copy()
    X_full_test = X_full.iloc[split_idx:].copy()
    X_notds_train = X_notds.iloc[:split_idx].copy()
    X_notds_test = X_notds.iloc[split_idx:].copy()
    y_train = y.iloc[:split_idx].copy()
    y_test = y.iloc[split_idx:].copy()

    # four models to test
    models = {
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'MLP': MLPRegressor(hidden_layer_sizes=(50,), max_iter=500, random_state=42)
    }

    # train each model twice (with and without TDS)
    for model_name, base_model in models.items():
        print(f'\n=== {model_name} (no TDS) ===')
        
        # fresh instance for no TDS version
        if model_name == 'LinearRegression':
            model_no_tds = LinearRegression()
        elif model_name == 'RandomForest':
            model_no_tds = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_name == 'GradientBoosting':
            model_no_tds = GradientBoostingRegressor(n_estimators=100, random_state=42)
        else: # MLP
            model_no_tds = MLPRegressor(hidden_layer_sizes=(50,), max_iter=500, random_state=42)
        
        # train on X_notds_train
        model_no_tds.fit(X_notds_train, y_train)
        
        # predict on X_notds_test
        y_pred_nt = model_no_tds.predict(X_notds_test)
        mse_nt = mean_squared_error(y_test, y_pred_nt)
        r2_nt = r2_score(y_test, y_pred_nt)
        print(f'MSE: {mse_nt:.4f}   R^2: {r2_nt:.4f}')
        
        # save model without TDS
        joblib.dump(model_no_tds, f'{model_name}_noTDS_model.joblib')
        
        print(f'\n=== {model_name} (with TDS) ===')
        
        # fresh instance for TDS version
        if model_name == 'LinearRegression':
            model_w_tds = LinearRegression()
        elif model_name == 'RandomForest':
            model_w_tds = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_name == 'GradientBoosting':
            model_w_tds = GradientBoostingRegressor(n_estimators=100, random_state=42)
        else: # MLP
            model_w_tds = MLPRegressor(hidden_layer_sizes=(50,), max_iter=500, random_state=42)
        
        # train on X_full_train (includes TDS)
        model_w_tds.fit(X_full_train, y_train)
        
        # predict on X_full_test
        y_pred_wt = model_w_tds.predict(X_full_test)
        mse_wt = mean_squared_error(y_test, y_pred_wt)
        r2_wt = r2_score(y_test, y_pred_wt)
        print(f'MSE: {mse_wt:.4f}   R^2: {r2_wt:.4f}')
        
        # save model with TDS
        joblib.dump(model_w_tds, f'{model_name}_withTDS_model.joblib')

if __name__ == "__main__":
    main()
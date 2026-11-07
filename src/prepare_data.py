import json
import pandas as pd
import os
from config import DATA_RAW, DATA_PROCESSED, DATA_PREPARED

def prepare_features():
    print("1. Загрузка данных наставника (processed/model_data.json)...")
    file_path = os.path.join(DATA_PROCESSED, 'model_data.json')
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        model_data = json.load(f)
        
    df_resorts = pd.json_normalize(model_data['resorts'])
    df_regions = pd.json_normalize(model_data['regions'])
    
    print("2. Соединение курортов и регионов (JOIN)...")
    df_features = pd.merge(
        df_resorts, 
        df_regions, 
        on='region', 
        how='left',
        suffixes=('', '_region')
    )
    
    assert len(df_features) == 32, f"Ошибка: должно быть 32 курорта, а получено {len(df_features)}"
    assert df_features['trips_2025'].isna().sum() == 0, "Ошибка: есть пропуски в trips_2025"
    
    out_path = os.path.join(DATA_PREPARED, 'resort_features.csv')
    df_features.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"✅ Данные сохранены: {out_path} (Строк: {len(df_features)})")
    
    return df_features

if __name__ == "__main__":
    prepare_features()
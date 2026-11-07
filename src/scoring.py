import pandas as pd
import numpy as np
import os
from config import DATA_PREPARED, WEIGHTS

def min_max(series):
    if series.max() == series.min():
        return pd.Series(50, index=series.index)
    return 100 * (series - series.min()) / (series.max() - series.min())

def log_min_max(series):
    if series.max() == series.min():
        return pd.Series(50, index=series.index)
    return 100 * (np.log1p(series) - np.log1p(series.min())) / (np.log1p(series.max()) - np.log1p(series.min()))

def inverse_log_min_max(series):
    return 100 - log_min_max(series)

def calculate_scores():
    print("1. Загрузка подготовленных данных...")
    file_path = os.path.join(DATA_PREPARED, 'resort_features.csv')
    df = pd.read_csv(file_path)
    
    print("2. Нормализация показателей...")
    df['region_trips_score'] = log_min_max(df['trips_2025'])
    df['region_growth_score'] = (50 + 200 * df['trips_growth_2025']).clip(0, 100)
    df['avg_stay_score'] = ((df['avg_stay_nights_2025'] - 1) / 6 * 100).clip(0, 100)
    
    df['pistes_score'] = log_min_max(df['piste_segments_6km'])
    df['lifts_score'] = log_min_max(df['lift_lines_6km'])
    df['lodging_score'] = log_min_max(df['lodging_objects_6km'])
    df['amenities_sum'] = df['food_objects_6km'] + df['attraction_objects_6km']
    df['amenities_score'] = log_min_max(df['amenities_sum'])
    
    df['snow_days_score'] = min_max(df['avg_snow_days_per_season'])
    df['freezing_days_score'] = min_max(df['avg_freezing_days_per_season'])
    df['snowfall_score'] = log_min_max(df['avg_snowfall_cm_per_season'])
    
    df['airport_score'] = inverse_log_min_max(df['nearest_airport_distance_km'])
    df['transport_score'] = log_min_max(df['transport_objects_6km'])
    
    price_s = df['adult_skipass_avg_rub']
    min_p, max_p = price_s.min(), price_s.max()
    df['price_score'] = price_s.apply(lambda x: 50.0 if pd.isna(x) else 100 - 100*(np.log1p(x)-np.log1p(min_p))/(np.log1p(max_p)-np.log1p(min_p)))
    
    print("3. Расчет итогового индекса...")
    assert sum(WEIGHTS.values()) == 100, "Сумма весов должна быть 100!"
    df['popularity_score'] = sum(df[col] * w for col, w in WEIGHTS.items()) / 100
    
    df['demand_component'] = (df['region_trips_score']*25 + df['region_growth_score']*10 + df['avg_stay_score']*5) / 40
    df['infra_component'] = (df['pistes_score']*10 + df['lifts_score']*7 + df['lodging_score']*5 + df['amenities_score']*3) / 25
    df['climate_component'] = (df['snow_days_score']*8 + df['freezing_days_score']*6 + df['snowfall_score']*6) / 20
    df['access_component'] = (df['airport_score']*8 + df['transport_score']*2) / 10
    df['price_component'] = df['price_score']
    
    print("4. Расчет мест и уверенности...")
    df['rank'] = df['popularity_score'].rank(method='min', ascending=False).astype(int)
    
    df['has_price'] = df['adult_skipass_avg_rub'].notna().astype(int)
    df['has_exact_coord'] = (df['coordinate_quality'] == 'resort_or_complex_page').astype(int)
    df['confidence_score'] = (50 * df['completeness_pct'] + 25 * df['has_price'] + 25 * df['has_exact_coord']).clip(upper=100)
    
    out_path = os.path.join(DATA_PREPARED, 'resort_scores.csv')
    df.to_csv(out_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ Итоговый рейтинг сохранен: {out_path}")
    print("\nТоп-5 курортов:")
    print(df.sort_values('rank')[['rank', 'name_ru', 'popularity_score']].head(5).to_string(index=False))
    
    return df

if __name__ == "__main__":
    calculate_scores()
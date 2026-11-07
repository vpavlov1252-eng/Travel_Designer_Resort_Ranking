import pandas as pd
import numpy as np
import os
from config import DATA_PREPARED, WEIGHTS

# --- НОВЫЕ ЭКСПЕРТНЫЕ ФУНКЦИИ (Модель v2) ---

def client_temperature_score(temp):
    """Оценка температуры по шкале комфорта клиента."""
    if pd.isna(temp): 
        return 50.0
    if -8 <= temp <= -2: 
        return 100.0  # Идеал (вельвет)
    elif -15 <= temp < -8: 
        return 75.0   # Прохладно, но отлично
    elif -2 < temp <= 0: 
        return 60.0   # На грани, снег влажноват
    elif 0 < temp <= 3: 
        return 40.0   # Весенняя каша
    elif -20 <= temp < -15: 
        return 20.0   # Экстрим (сильный мороз)
    else: 
        return 0.0    # Слишком холодно или слишком тепло

def client_snowfall_score(snow):
    """Оценка снегопада за сезон."""
    if pd.isna(snow): 
        return 50.0
    if snow > 400: 
        return 100.0
    elif snow >= 250: 
        return 80.0
    elif snow >= 150: 
        return 50.0
    else: 
        return 20.0

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
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

# --- ОСНОВНАЯ ФУНКЦИЯ ---
def calculate_scores_v2():
    print("1. Загрузка подготовленных данных...")
    file_path = os.path.join(DATA_PREPARED, 'resort_features.csv')
    df = pd.read_csv(file_path)
    
    print("2. Нормализация показателей (Экспертная модель v2)...")
    # Региональный спрос
    df['region_trips_score'] = log_min_max(df['trips_2025'])
    df['region_growth_score'] = (50 + 200 * df['trips_growth_2025']).clip(0, 100)
    df['avg_stay_score'] = ((df['avg_stay_nights_2025'] - 1) / 6 * 100).clip(0, 100)
    
    # Инфраструктура
    df['pistes_score'] = log_min_max(df['piste_segments_6km'])
    df['lifts_score'] = log_min_max(df['lift_lines_6km'])
    df['lodging_score'] = log_min_max(df['lodging_objects_6km'])
    df['amenities_score'] = log_min_max(df['food_objects_6km'] + df['attraction_objects_6km'])
    
    # Климат — НОВАЯ ЛОГИКА
    df['snow_days_score'] = min_max(df['avg_snow_days_per_season'])
    df['freezing_days_score'] = min_max(df['avg_freezing_days_per_season'])
    df['temp_score_v2'] = df['winter_mean_temperature_c'].apply(client_temperature_score)
    df['snowfall_score_v2'] = df['avg_snowfall_cm_per_season'].apply(client_snowfall_score)
    
    # Доступность
    df['airport_score'] = inverse_log_min_max(df['nearest_airport_distance_km'])
    df['transport_score'] = log_min_max(df['transport_objects_6km'])
    
    # Цена
    price_s = df['adult_skipass_avg_rub']
    min_p, max_p = price_s.min(), price_s.max()
    df['price_score'] = price_s.apply(
        lambda x: 50.0 if pd.isna(x) 
        else 100 - 100*(np.log1p(x)-np.log1p(min_p))/(np.log1p(max_p)-np.log1p(min_p))
    )
    
    print("3. Расчет итогового индекса v2...")
    weights_v2 = WEIGHTS.copy()
    # Подменяем ключи на новые экспертные колонки
    weights_v2['temp_score_v2'] = weights_v2.pop('freezing_days_score')
    weights_v2['snowfall_score_v2'] = weights_v2.pop('snowfall_score')
    
    assert sum(weights_v2.values()) == 100, "Сумма весов должна быть 100!"
    df['popularity_score_v2'] = sum(df[col] * w for col, w in weights_v2.items()) / 100
    df['rank_v2'] = df['popularity_score_v2'].rank(method='min', ascending=False).astype(int)
    
    # --- ДОБАВЛЯЕМ РАСЧЕТ КОМПОНЕНТОВ ДЛЯ ДАШБОРДА ---
    df['demand_component'] = (df['region_trips_score']*25 + df['region_growth_score']*10 + df['avg_stay_score']*5) / 40
    df['infra_component'] = (df['pistes_score']*10 + df['lifts_score']*7 + df['lodging_score']*5 + df['amenities_score']*3) / 25
    df['climate_component'] = (df['snow_days_score']*8 + df['temp_score_v2']*6 + df['snowfall_score_v2']*6) / 20
    df['access_component'] = (df['airport_score']*8 + df['transport_score']*2) / 10
    df['price_component'] = df['price_score']
    # --------------------------------------------------

    # Сохраняем
    out_path = os.path.join(DATA_PREPARED, 'resort_scores_v2.csv')
    df.to_csv(out_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ Экспертный рейтинг v2 сохранен: {out_path}")
    
    return df

if __name__ == "__main__":
    calculate_scores_v2()
import pandas as pd
import numpy as np
import os
from config import DATA_PREPARED, WEIGHTS

def recalc_with_weights(df, weights):
    """Пересчитывает popularity_score и rank с новыми весами."""
    assert abs(sum(weights.values()) - 100) < 0.001, "Сумма весов должна быть 100!"
    df = df.copy()
    df['popularity_score_scenario'] = sum(df[col] * w for col, w in weights.items()) / 100
    df['rank_scenario'] = df['popularity_score_scenario'].rank(method='min', ascending=False).astype(int)
    return df

def make_scenario_weights(base_weights, group_keys, boost=1.2):
    new_weights = base_weights.copy()
    group_weight_old = sum(base_weights[k] for k in group_keys)
    group_weight_new = group_weight_old * boost
    other_weight_old = 100 - group_weight_old
    other_weight_new = 100 - group_weight_new
    coef = other_weight_new / other_weight_old if other_weight_old > 0 else 1.0
    for k in new_weights:
        if k in group_keys:
            new_weights[k] = base_weights[k] * boost
        else:
            new_weights[k] = base_weights[k] * coef
    return new_weights

def run_scenarios():
    print("1. Загрузка resort_scores.csv...")
    file_path = os.path.join(DATA_PREPARED, 'resort_scores.csv')
    df = pd.read_csv(file_path)
    
    df['popularity_base'] = df['popularity_score']
    df['rank_base'] = df['rank']
    
    climate_keys = ['snow_days_score', 'freezing_days_score', 'snowfall_score']
    weights_climate = make_scenario_weights(WEIGHTS, climate_keys, boost=1.2)
    df_climate = recalc_with_weights(df, weights_climate)
    df['popularity_climate'] = df_climate['popularity_score_scenario']
    df['rank_climate'] = df_climate['rank_scenario']
    
    access_keys = ['airport_score', 'transport_score']
    weights_access = make_scenario_weights(WEIGHTS, access_keys, boost=1.2)
    df_access = recalc_with_weights(df, weights_access)
    df['popularity_access'] = df_access['popularity_score_scenario']
    df['rank_access'] = df_access['rank_scenario']
    
    df['delta_rank_climate'] = df['rank_climate'] - df['rank_base']
    df['delta_rank_access'] = df['rank_access'] - df['rank_base']
    
    cols = ['resort_id', 'name_ru', 'region',
            'rank_base', 'rank_climate', 'delta_rank_climate', 'rank_access', 'delta_rank_access',
            'popularity_base', 'popularity_climate', 'popularity_access']
    result = df[cols].sort_values('rank_base')
    
    out_path = os.path.join(DATA_PREPARED, 'resort_scores_scenarios.csv')
    result.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"✅ Сценарии сохранены: {out_path}")
    
    print("\n📊 Топ-5 изменений при климате +20% (по модулю):")
    top_climate = df.reindex(df['delta_rank_climate'].abs().sort_values(ascending=False).index).head(5)
    print(top_climate[['name_ru', 'rank_base', 'rank_climate', 'delta_rank_climate']].to_string(index=False))
    
    print("\n📊 Топ-5 изменений при доступности +20% (по модулю):")
    top_access = df.reindex(df['delta_rank_access'].abs().sort_values(ascending=False).index).head(5)
    print(top_access[['name_ru', 'rank_base', 'rank_access', 'delta_rank_access']].to_string(index=False))
    
    print("\n📊 Новые веса (климат +20%):")
    for k, v in weights_climate.items():
        print(f"  {k}: {v:.2f}")
    print(f"  Сумма: {sum(weights_climate.values()):.2f}")
    
    return result

if __name__ == "__main__":
    run_scenarios()
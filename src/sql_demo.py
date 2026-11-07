import sqlite3
import pandas as pd
import os
from config import DATA_PREPARED

def run_sql_analysis():
    print("1. Загрузка данных...")
    df_features = pd.read_csv(os.path.join(DATA_PREPARED, 'resort_features.csv'))
    df_scores = pd.read_csv(os.path.join(DATA_PREPARED, 'resort_scores_v2.csv'))
    
    # Создаем базу данных в оперативной памяти
    conn = sqlite3.connect(':memory:')
    
    print("2. Загрузка таблиц в SQL...")
    # Записываем датафреймы в SQL-таблицы
    df_features.to_sql('resorts', conn, index=False, if_exists='replace')
    df_scores.to_sql('scores', conn, index=False, if_exists='replace')
    
    print("\n3. Выполняем SQL-запрос (Топ-10 по регионам):")
    # Пишем запрос: JOIN двух таблиц, фильтрация, сортировка и агрегация
    query = """
    SELECT 
        s.rank_v2,
        s.name_ru,
        s.region,
        s.popularity_score_v2,
        r.trips_2025,
        r.avg_stay_nights_2025
    FROM scores s
    JOIN resorts r ON s.resort_id = r.resort_id
    WHERE s.region IN ('Краснодарский край', 'Московская область', 'Карачаево-Черкесская Республика')
    ORDER BY s.popularity_score_v2 DESC
    LIMIT 10;
    """
    
    # Выполняем запрос и выводим результат
    result = pd.read_sql_query(query, conn)
    print(result.to_string(index=False))
    
    print("\n4. Выполняем SQL-запрос (Средний балл по регионам):")
    query_avg = """
    SELECT 
        region, 
        COUNT(resort_id) as count_resorts,
        ROUND(AVG(popularity_score_v2), 2) as avg_score,
        SUM(CASE WHEN adult_skipass_avg_rub IS NOT NULL THEN 1 ELSE 0 END) as count_with_price
    FROM scores
    GROUP BY region
    ORDER BY avg_score DESC
    LIMIT 5;
    """
    result_avg = pd.read_sql_query(query_avg, conn)
    print(result_avg.to_string(index=False))
    
    conn.close()
    print("\n✅ SQL-анализ завершен!")

if __name__ == "__main__":
    run_sql_analysis()
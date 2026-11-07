import os

# Корень проекта (на 2 уровня выше файла config.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW = os.path.join(BASE_DIR, 'data', 'raw')
DATA_PROCESSED = os.path.join(BASE_DIR, 'data', 'processed')
DATA_PREPARED = os.path.join(BASE_DIR, 'data', 'prepared')

# Создаем папку prepared, если ее нет
os.makedirs(DATA_PREPARED, exist_ok=True)

# Веса показателей (сумма = 100)
WEIGHTS = {
    'region_trips_score': 25,
    'region_growth_score': 10,
    'avg_stay_score': 5,
    'pistes_score': 10,
    'lifts_score': 7,
    'lodging_score': 5,
    'amenities_score': 3,
    'snow_days_score': 8,
    'freezing_days_score': 6,
    'snowfall_score': 6,
    'airport_score': 8,
    'transport_score': 2,
    'price_score': 5
}
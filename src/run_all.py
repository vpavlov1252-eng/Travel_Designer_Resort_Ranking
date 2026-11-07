from prepare_data import prepare_features
from scoring import calculate_scores

if __name__ == "__main__":
    print("=== СТАРТ ПАЙПЛАЙНА ===")
    prepare_features()
    print("\n=== РАСЧЕТ РЕЙТИНГА ===")
    calculate_scores()
    print("\n=== ГОТОВО! ===")
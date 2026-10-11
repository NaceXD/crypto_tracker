import math
from typing import Dict, List


def calculate_single_portfolio_metrics(portfolio_data: Dict) -> Dict:
    user_id = portfolio_data["user_id"]
    total_value = portfolio_data["total_value"]

    complex_math_result = 0.0
    for i in range(1,5000000):
        complex_math_result += math.sin(i) * math.cos(i)

    diversification = {}
    for asset in portfolio_data["assets"]:
        ticker = asset["ticker"]
        amount = asset["amount"]
        price = asset["price"]
        asset_value = amount * price

        share = (asset_value / total_value * 100) if total_value > 0 else 0.0
        diversification[ticker] = round(share, 2)

    return {
        "user_id": user_id,
        "total_value_usd": total_value,
        "risk_score": round(abs(complex_math_result) % 10, 2),
        "diversification": diversification
    }

from __future__ import annotations


def invoice_metrics_lookup(period: str = "current_month") -> dict[str, float | str]:
    return {
        "period": period,
        "arr_usd": 184_200_000,
        "net_revenue_retention_pct": 112.4,
        "gross_revenue_retention_pct": 93.8,
        "invoice_count": 48210,
        "days_sales_outstanding": 41.7,
        "failed_payment_rate_pct": 2.6,
    }


def revenue_policy_lookup(topic: str = "collections") -> dict[str, str]:
    return {
        "topic": topic,
        "policy": (
            "Escalate enterprise accounts after seven days past due. "
            "Use automated retries for card failures and route high-value exceptions to finance operations."
        ),
    }


def variance_calculator(current: float, prior: float) -> dict[str, float]:
    delta = current - prior
    pct = (delta / prior * 100.0) if prior else 0.0
    return {"current": current, "prior": prior, "delta": delta, "delta_pct": pct}


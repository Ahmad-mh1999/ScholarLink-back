from decimal import Decimal

from apps.articles.models import Journal


def seed_journals():
    samples = [
        {
            "name": "Nature Astronomy",
            "field_of_study": "Astronomy",
            "impact_factor": Decimal("15.20"),
            "publication_type": "subscription",
            "publication_fee": Decimal("2500.00"),
            "font_guidelines": "",
            "margin_guidelines": "",
            "figure_guidelines": "",
        },
        {
            "name": "Cell Reports",
            "field_of_study": "Biology",
            "impact_factor": Decimal("10.85"),
            "publication_type": "open_access",
            "publication_fee": Decimal("1800.00"),
            "font_guidelines": "",
            "margin_guidelines": "",
            "figure_guidelines": "",
        },
        {
            "name": "The Lancet Global Health",
            "field_of_study": "Medicine",
            "impact_factor": Decimal("12.40"),
            "publication_type": "subscription",
            "publication_fee": Decimal("2200.00"),
            "font_guidelines": "",
            "margin_guidelines": "",
            "figure_guidelines": "",
        },
        {
            "name": "arXiv Machine Learning",
            "field_of_study": "Computer Science",
            "impact_factor": Decimal("7.30"),
            "publication_type": "open_access",
            "publication_fee": Decimal("0.00"),
            "font_guidelines": "",
            "margin_guidelines": "",
            "figure_guidelines": "",
        },
        {
            "name": "IEEE Transactions on Software Engineering",
            "field_of_study": "Engineering",
            "impact_factor": Decimal("9.10"),
            "publication_type": "subscription",
            "publication_fee": Decimal("2000.00"),
            "font_guidelines": "",
            "margin_guidelines": "",
            "figure_guidelines": "",
        },
    ]

    created = 0
    for s in samples:
        # Use name as unique key (per model)
        obj, was_created = Journal.objects.get_or_create(
            name=s["name"],
            defaults={
                "field_of_study": s["field_of_study"],
                "impact_factor": s["impact_factor"],
                "publication_type": s["publication_type"],
                "publication_fee": s["publication_fee"],
                "font_guidelines": s.get("font_guidelines", ""),
                "margin_guidelines": s.get("margin_guidelines", ""),
                "figure_guidelines": s.get("figure_guidelines", ""),
            },
        )
        if was_created:
            created += 1

    return created


if __name__ == "__main__":
    c = seed_journals()
    print(f"Seeded journals: {c}")


import random

from .models import PimPam, StudentPimPam


RARITY_LIMITS = [
    (90, 5),
    (75, 4),
    (50, 3),
    (25, 2),
    (0, 1),
]

RARITY_WEIGHTS = {
    1: 45,
    2: 28,
    3: 16,
    4: 8,
    5: 3,
}


def award_pimpam_for_attempt(attempt):
    if not attempt.student or hasattr(attempt, "pimpam_award"):
        return None
    if attempt.score <= 0:
        return None

    max_rarity = 1
    for minimum_score, rarity in RARITY_LIMITS:
        if attempt.score >= minimum_score:
            max_rarity = rarity
            break

    candidates = list(PimPam.objects.filter(rarity__lte=max_rarity))
    if not candidates:
        return None

    owned_ids = set(StudentPimPam.objects.filter(student=attempt.student).values_list("pimpam_id", flat=True))
    unowned = [pimpam for pimpam in candidates if pimpam.pk not in owned_ids]
    pool = unowned or candidates

    rng = random.Random(f"{attempt.pk}:{attempt.student_id}:{attempt.score}")
    weights = [RARITY_WEIGHTS[pimpam.rarity] for pimpam in pool]
    pimpam = rng.choices(pool, weights=weights, k=1)[0]
    return StudentPimPam.objects.create(student=attempt.student, pimpam=pimpam, attempt=attempt)

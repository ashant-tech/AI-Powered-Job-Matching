from datetime import datetime, timezone
from types import SimpleNamespace

from app.ai.ranking import rank_matches


def test_rank_matches_accepts_timezone_aware_created_at():
    match = SimpleNamespace(
        created_at=datetime.now(timezone.utc),
        match_score=50.0,
    )

    assert rank_matches([match]) == [match]
    assert match.match_score == 51.0
import pytest
from etl.transformer import MarvelRivalsTransformer

@pytest.fixture
def transformer():
    return MarvelRivalsTransformer()

@pytest.fixture
def sample_match_data():
    return [{
        "id": "1",
        "timestamp": "2024-03-20T12:00:00Z",
        "duration": 300,
        "winner_team": 1,
        "map": "test_map",
        "players": [
            {
                "hero_id": 1,
                "player_id": "p1",
                "team": 1,
                "stats": {
                    "kills": 5,
                    "deaths": 2,
                    "assists": 3,
                    "damage_dealt": 1000
                }
            }
        ]
    }]

def test_transform_match_data(transformer, sample_match_data):
    result = transformer.transform_match_data(sample_match_data)
    assert len(result) == 1
    assert result[0]["match_id"] == "1"
    assert result[0]["winner_team"] == 1
    assert len(result[0]["heroes"]) == 1
    assert result[0]["heroes"][0]["hero_id"] == 1

def test_calculate_hero_stats(transformer, sample_match_data):
    transformed_data = transformer.transform_match_data(sample_match_data)
    stats = transformer.calculate_hero_stats(transformed_data)
    assert 1 in stats
    assert stats[1]["games_played"] == 1
    assert stats[1]["wins"] == 1
    assert stats[1]["kills"] == 5 
from bot.feeds.base import LiveEvent
from bot.monitor import same_match


def _ev(label):
    return LiveEvent("1", "x", label, True)


def test_cross_source_titles_join():
    assert same_match(_ev("Toronto Raptors vs Miami Heat"),
                      _ev("Raptors vs Heat - Winner?")) is True


def test_same_city_teams_do_not_join():
    assert same_match(_ev("Toronto Maple Leafs vs Montreal Canadiens"),
                      _ev("Toronto Raptors vs Miami Heat")) is False


def test_unrelated_do_not_join():
    assert same_match(_ev("Buffalo Bills vs Detroit Lions"),
                      _ev("Real Betis vs Getafe")) is False


def test_identical_joins():
    assert same_match(_ev("Arsenal vs Chelsea"), _ev("Arsenal vs Chelsea")) is True

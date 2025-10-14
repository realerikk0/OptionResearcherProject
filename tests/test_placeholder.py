from src.greeks_calculator import Greeks, compute_greeks


class DummyModel:
    def delta(self, *args, **kwargs):
        return 0.5

    def gamma(self, *args, **kwargs):
        return 0.1

    def vega(self, *args, **kwargs):
        return 0.2

    def theta(self, *args, **kwargs):
        return -0.05


def test_compute_greeks_returns_expected_values():
    result = compute_greeks(DummyModel())
    assert result == Greeks(delta=0.5, gamma=0.1, vega=0.2, theta=-0.05)

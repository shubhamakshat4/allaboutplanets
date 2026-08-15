import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.astrology import pyjhora_adapter as adapter  # noqa: E402
from app.astrology.chart_calculator import build_chart_context  # noqa: E402
from app.astrology import yoga_engine  # noqa: E402


def make_context(year=1990, month=5, day=15, hour=10, minute=30, second=0,
                 lat=13.0827, lon=80.2707, tz=5.5, ayanamsha="LAHIRI"):
    place = adapter.BirthPlace("Test Place", lat, lon, tz)
    jd = adapter.julian_day(year, month, day, hour, minute, second)
    return build_chart_context(jd, place, ayanamsha)


@pytest.fixture(scope="session")
def ctx():
    """Reference chart: 15 May 1990, 10:30:00, Chennai, Lahiri."""
    return make_context()


@pytest.fixture(scope="session")
def yogas(ctx):
    return yoga_engine.evaluate_all_yogas(ctx)

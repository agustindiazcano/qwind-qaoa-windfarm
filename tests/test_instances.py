import json

import numpy as np
import pytest

from qwind.instances import (SYNTHETIC_ROSES, build_instance, load_wind_rose,
                             meteorological_to_toward, rose_from_sectors, synthetic_instance_specs)


def test_meteorological_to_toward_convention():
    """Wind FROM north blows TOWARD south; wake.py angles are math degrees (0 = east, 90 = north)."""
    assert meteorological_to_toward(0) == 270    # from N -> toward S
    assert meteorological_to_toward(90) == 180   # from E -> toward W
    assert meteorological_to_toward(180) == 90   # from S -> toward N
    assert meteorological_to_toward(270) == 0    # from W -> toward E
    assert meteorological_to_toward(350) == pytest.approx(280)


def test_rose_from_sectors_normalizes_and_converts():
    sectors = [{"direction_deg": 270, "frequency": 3.0, "mean_speed": 9.0},
               {"direction_deg": 0, "frequency": 1.0, "mean_speed": 6.0}]
    rose = rose_from_sectors(sectors)
    assert rose == [(0.0, 0.75), (270.0, 0.25)]
    assert sum(p for _, p in rose) == pytest.approx(1.0)


def test_load_wind_rose(tmp_path):
    path = tmp_path / "windrose.json"
    path.write_text(json.dumps({"sites": {"chubut": {"sectors": [
        {"direction_deg": 270, "frequency": 0.6, "mean_speed": 9.5},
        {"direction_deg": 90, "frequency": 0.4, "mean_speed": 7.0}]}}}))
    assert load_wind_rose(str(path), "chubut") == [(0.0, 0.6), (180.0, 0.4)]
    with pytest.raises(KeyError):
        load_wind_rose(str(path), "nowhere")


def test_load_wind_rose_empty_file_is_an_error(tmp_path):
    path = tmp_path / "windrose.json"
    path.write_text("")
    with pytest.raises(ValueError):
        load_wind_rose(str(path), "chubut")


def test_build_instance_is_deterministic_and_heterogeneous():
    a = build_instance(8, SYNTHETIC_ROSES["A"], seed=3)
    b = build_instance(8, SYNTHETIC_ROSES["A"], seed=3)
    c = build_instance(8, SYNTHETIC_ROSES["A"], seed=4)
    np.testing.assert_array_equal(a.h, b.h)
    np.testing.assert_array_equal(a.J, b.J)
    assert not np.allclose(a.h, c.h)
    assert a.grid_shape == (4, 2)
    assert np.all((a.P0 >= 1.0) & (a.P0 <= 1.2))
    np.testing.assert_array_equal(a.h, -a.P0)


def test_synthetic_instance_specs():
    specs = synthetic_instance_specs()
    assert len(specs) >= 20
    assert [s.instance_id for s in specs] == list(range(len(specs)))
    assert all(s.dataset == "synthetic" and 6 <= s.N <= 12 and 0 < s.K < s.N for s in specs)
    assert {s.wind_rose for s in specs} == set(SYNTHETIC_ROSES)
    assert len({(s.N, s.K, s.wind_rose) for s in specs}) == len(specs)

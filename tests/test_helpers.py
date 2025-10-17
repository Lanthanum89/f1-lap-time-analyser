import pandas as pd
import datetime

from lap_analyser import best_laps_dataframe


def make_fake_session():
    class S:
        pass

    s = S()
    # create a laps DataFrame similar to fastf1's
    data = {
        'Driver': ['HAM', 'VER', 'HAM', 'VER'],
        'Team': ['Mercedes', 'Red Bull', 'Mercedes', 'Red Bull'],
        'LapTime': [pd.to_timedelta('1s'), pd.to_timedelta('1.1s'), pd.to_timedelta('0.95s'), pd.to_timedelta('1.05s')],
        'LapNumber': [1, 1, 2, 2],
        'Compound': ['C5', 'C5', 'C5', 'C5'],
        'IsAccurate': [True, True, True, True],
        'IsPersonalBest': [False, False, True, True]
    }
    s.laps = pd.DataFrame(data)
    return s


def test_best_laps_dataframe():
    s = make_fake_session()
    df = best_laps_dataframe(s)
    # fastest should be HAM (0.95s) then VER (1.05s)
    assert df.iloc[0]['Driver'] == 'HAM'
    assert df.iloc[1]['Driver'] == 'VER'

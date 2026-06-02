from nba_api.stats.endpoints import leagueleaders
import pandas as pd

# Quick test — pull 2023-24 league leaders
leaders = leagueleaders.LeagueLeaders(season='2023-24')
df = leaders.get_data_frames()[0]
print(df.shape)
print(df.head())
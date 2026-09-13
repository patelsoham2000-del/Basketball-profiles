"""
One-time script to download NBA player per-game stats for a season
using the nba_api package, and save them as a local CSV.

We run this ONCE. After this, the notebook only reads the CSV file --
it does not call the internet every time we open the notebook.
This keeps the analysis reproducible even if the API changes later.
"""

import time

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats, commonteamroster
from nba_api.stats.static import teams

SEASON = "2024-25"  # most recently completed full NBA season


def fetch_positions(season):
    """
    leaguedashplayerstats (the main stats endpoint) doesn't include each
    player's position. Position lives on each team's roster instead, so we
    loop over all 30 teams and build a PLAYER_ID -> POSITION lookup table.
    """
    print("Fetching player positions from team rosters...")
    all_teams = teams.get_teams()
    rosters = []

    for team in all_teams:
        roster = commonteamroster.CommonTeamRoster(
            team_id=team["id"], season=season
        ).get_data_frames()[0]
        rosters.append(roster[["PLAYER_ID", "POSITION"]])
        time.sleep(0.6)  # be polite to the API, avoid rate-limiting

    positions = pd.concat(rosters, ignore_index=True)
    # a player traded mid-season can appear on more than one roster;
    # keep just one position per player to avoid duplicate rows later
    positions = positions.drop_duplicates(subset="PLAYER_ID", keep="last")
    return positions


def main():
    print(f"Requesting {SEASON} per-game player stats from stats.nba.com ...")

    response = leaguedashplayerstats.LeagueDashPlayerStats(
        season=SEASON,
        season_type_all_star="Regular Season",
        per_mode_detailed="PerGame",  # ask the API for per-game numbers directly
    )

    df = response.get_data_frames()[0]
    print(f"Received {len(df)} rows and {len(df.columns)} columns.")

    positions = fetch_positions(SEASON)
    df = df.merge(positions, on="PLAYER_ID", how="left")
    print(f"Merged in positions. Missing position for {df['POSITION'].isna().sum()} players.")

    out_path = f"data/nba_player_stats_{SEASON.replace('-', '_')}.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()

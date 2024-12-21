import requests
from bs4 import BeautifulSoup
from app.models.playerInfo import PlayerAverageLastFiveGameStats, PlayerSeasonalStats, PlayerOpposingTeamStats

class PlayerService:
    @staticmethod
    def get_nbaplayer_url(player_name: str) -> requests.Response:
        name_parts = player_name.lower().split()
    
        if len(name_parts) < 2:
            return "Please enter both first and last name"
        
        # [-1] grabs last item in list, [0] grabs first item in list
        last_name, first_name = name_parts[-1], name_parts[0]
        
        # [:1] grabs first letter of last name, [:5] grabs first 5 letters of last name, [:2] grabs first 2 letters of first name
        player_url = f"https://www.basketball-reference.com/players/{last_name[:1]}/{last_name[:5]}{first_name[:2]}01.html"
        player_response = requests.get(player_url)
        
        return player_response
        
    @staticmethod
    def get_nbaplayer_opposingteam_url(player_response: requests.Response) -> str:
        try:
            soup = BeautifulSoup(player_response.content, 'html.parser')
            next_game = soup.find('div', {'id': 'tfooter_last5'})
            
            if next_game:
                next_game_url_ender = next_game.find('a')['href']
                team_code = next_game_url_ender.split('/')[2]
                opposing_team_url = f"https://www.basketball-reference.com/teams/{team_code}/stats_per_game_totals.html"
                
                return opposing_team_url
            
            else:
                return "Could not find next game"
        
        except Exception as e:
            return f"Error: {str(e)}"
        
    @staticmethod
    def get_nbaplayer_5game_stats(player_response: requests.Response) -> PlayerAverageLastFiveGameStats:
        try:
            soup = BeautifulSoup(player_response.content, 'html.parser')
            table = soup.find('table', {'id': 'last5'})
            
            
            name_div = soup.find('div', {'id': 'info'})
            player_name = name_div.find('h1').text.strip()
                
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                
                # Initialize stats
                total_mp = 0
                total_fg = total_fga = total_fg_pct = 0
                total_ft = total_fta = total_ft_pct = 0
                total_3p = total_3pa = total_3p_pct = 0
                total_rebounds = total_assists = total_steals = total_turnovers = 0
                games = len(rows)
                
                # Sum up the stats
                for row in rows:
                    cells = row.find_all('td')
                    total_mp += float(cells[5].text.strip())  # Minutes Played
                    total_fg += float(cells[6].text.strip())  # Field Goals
                    total_fga += float(cells[7].text.strip())  # Field Goals Attempted
                    total_fg_pct += float(cells[8].text.strip())  # Field Goal Percentage
                    total_ft += float(cells[12].text.strip())  # Free Throws
                    total_fta += float(cells[13].text.strip())  # Free Throws Attempted
                    total_ft_pct += float(cells[14].text.strip())  # Free Throw Percentage
                    total_3p += float(cells[9].text.strip())  # 3-Point Field Goals
                    total_3pa += float(cells[10].text.strip())  # 3-Point Field Goals Attempted
                    total_3p_pct += float(cells[11].text.strip())  # 3-Point Field Goal Percentage
                    total_rebounds += float(cells[17].text.strip())  # Total Rebounds
                    total_assists += float(cells[18].text.strip())  # Total Assists
                    total_steals += float(cells[19].text.strip())  # Total Steals
                    total_turnovers += float(cells[21].text.strip())  # Total Turnovers
                    
                avg_mp = total_mp / games
                avg_fg = total_fg / games
                avg_fga = total_fga / games
                avg_fg_pct = round(total_fg_pct / games * 100, 2)
                avg_ft = total_ft / games
                avg_fta = total_fta / games
                avg_ft_pct = round(total_ft_pct / games * 100, 2)
                avg_3p = total_3p / games
                avg_3pa = total_3pa / games
                avg_3p_pct = round(total_3p_pct / games * 100, 2)
                avg_rebounds = total_rebounds / games
                avg_assists = total_assists / games
                avg_steals = total_steals / games
                avg_turnovers = total_turnovers / games
                
                return PlayerAverageLastFiveGameStats(
                    name=player_name,
                    minutes_played=avg_mp,
                    field_goals=avg_fg,
                    field_goals_attempted=avg_fga,
                    field_goal_percentage=avg_fg_pct,
                    free_throws=avg_ft,
                    free_throws_attempted=avg_fta,
                    free_throw_percentage=avg_ft_pct,
                    three_points=avg_3p,
                    three_points_attempted=avg_3pa,
                    three_point_percentage=avg_3p_pct,
                    rebounds=avg_rebounds,
                    assists=avg_assists,
                    steals=avg_steals,
                    turnovers=avg_turnovers
                )
            else:
                raise ValueError("Could not find last 5 games table")
            
        except Exception as e:
            raise Exception(f"Error processing player stats: {str(e)}")
        
    @staticmethod
    def get_nbaplayer_seasonal_stats(player_response: requests.Response) -> PlayerSeasonalStats:
        try:
        
            soup = BeautifulSoup(player_response.content, 'html.parser')
            table = soup.find('table', {'id': 'per_game_stats'})
            
            if table:
                rows = table.find('tbody').find_all('tr')
                latest_season = rows[-1]
                row_cells = latest_season.find_all('td')
                
                return PlayerSeasonalStats(
                    season=latest_season.find('th', {'data-stat': 'year_id'}).text.strip(),
                    age=row_cells[0].text.strip(),
                    team=row_cells[2].text.strip(),
                    position=row_cells[3].text.strip(),
                    games=int(row_cells[4].text.strip()),
                    games_started=int(row_cells[5].text.strip()),
                    games_started_percentage=float(int(row_cells[5].text.strip()) / int(row_cells[4].text.strip())) * 100,
                    minutes_played=row_cells[6].text.strip(),
                    field_goals=row_cells[7].text.strip(),
                    field_goals_attempted=row_cells[8].text.strip(),
                    field_goal_percentage=(round(float(row_cells[9].text.strip()) * 100, 2)),
                    three_points=row_cells[10].text.strip(),
                    three_points_attempted=row_cells[11].text.strip(),
                    three_point_percentage=(round(float(row_cells[12].text.strip()) * 100, 2)),
                    two_points=row_cells[13].text.strip(),
                    two_points_attempted=row_cells[14].text.strip(),
                    two_point_percentage=(round(float(row_cells[15].text.strip()) * 100, 2)),
                    free_throws=row_cells[17].text.strip(),
                    free_throws_attempted=row_cells[18].text.strip(),
                    free_throw_percentage=(round(float(row_cells[19].text.strip()) * 100, 2)),
                    effective_field_goal_percentage=(round(float(row_cells[16].text.strip()) * 100, 2)),
                    total_rebounds=row_cells[22].text.strip(),
                    total_assists=row_cells[23].text.strip(),
                    total_steals=row_cells[24].text.strip()
                )
            else:
                raise ValueError("Could not find seasonal stats table")
            
        except Exception as e:
            raise Exception(f"Error processing seasonal stats: {str(e)}")

        
    @staticmethod
    def get_opposing_team_stats(opposing_team_url: str) -> PlayerOpposingTeamStats:
        try:
            # Dictionary of known team code mappings
            team_code_mappings = {
                'NOP': 'NOH',
                'BRK': 'BKN',
                'CHO': 'CHA',
            }

            def try_team_url(url):
                response = requests.get(url)
                if response.status_code == 200:
                    return response
                return None

            # Try the original URL first
            team_response = try_team_url(opposing_team_url)
            
            # If original URL fails, try alternative team codes
            if not team_response:
                team_code = opposing_team_url.split('/')[4]
                if team_code in team_code_mappings:
                    alternative_url = opposing_team_url.replace(team_code, team_code_mappings[team_code])
                    team_response = try_team_url(alternative_url)

            if team_response:
                soup = BeautifulSoup(team_response.content, 'html.parser')
                
                # Check for redirect
                meta_refresh = soup.find('meta', {'http-equiv': 'refresh'})
                if meta_refresh:
                    redirect_url = meta_refresh['content'].split('URL=')[1]
                    full_redirect_url = f"https://www.basketball-reference.com{redirect_url}"
                    team_response = requests.get(full_redirect_url)
                    soup = BeautifulSoup(team_response.content, 'html.parser')

                table = soup.find('table', {'id': 'stats'})
                if table:
                    team_stats = table.find('tbody').find('tr')

                    # Create and return PlayerOpposingTeamStats object
                    return PlayerOpposingTeamStats(
                        team_name=team_stats.find('td', {'data-stat': 'team_id'}).text,
                        wins=int(team_stats.find('td', {'data-stat': 'wins'}).text),
                        losses=int(team_stats.find('td', {'data-stat': 'losses'}).text),
                        games_played=int(team_stats.find('td', {'data-stat': 'g'}).text),
                        points_per_game=float(team_stats.find('td', {'data-stat': 'pts_per_g'}).text),
                        field_goal_percentage=(round(float(team_stats.find('td', {'data-stat': 'fg_pct'}).text) * 100, 2)),
                        three_point_percentage=(round(float(team_stats.find('td', {'data-stat': 'fg3_pct'}).text) * 100, 2)),
                        rebounds=float(team_stats.find('td', {'data-stat': 'trb_per_g'}).text),
                        assists=float(team_stats.find('td', {'data-stat': 'ast_per_g'}).text),
                        steals=float(team_stats.find('td', {'data-stat': 'stl_per_g'}).text),
                        blocks=float(team_stats.find('td', {'data-stat': 'blk_per_g'}).text),
                        turnovers=float(team_stats.find('td', {'data-stat': 'tov_per_g'}).text)
                    )
            else:
                raise ValueError("Could not find team stats table")
                
        except Exception as e:
            raise Exception(f"Error processing team stats: {str(e)}")
import requests
from bs4 import BeautifulSoup

def get_nbaplayer_url(player_name):                                                             
    name_parts = player_name.lower().split()
    
    if len(name_parts) < 2:
        return "Please enter both first and last name"
    
    last_name, first_name = name_parts[-1], name_parts[0],
    
    player_url = f"https://www.basketball-reference.com/players/{last_name[:1]}/{last_name[:5]}{first_name[:2]}01.html"
    player_response = requests.get(player_url)
    return player_response

def get_nbaplayer_opposingteam_url(player_response):
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
    
def get_nbaplayer_5game_stats(player_response):
    try:
        soup = BeautifulSoup(player_response.content, 'html.parser')
        
        table = soup.find('table', {'id': 'last5'})
        
        if table:
            rows = table.find_all('tr')[1:]  # Skip header row
            # Initialize stats
            total_mp = 0
            total_fg = 0
            total_fga = 0
            total_fg_pct = 0
            total_ft = 0
            total_fta = 0
            total_ft_pct = 0
            total_3p = 0
            total_3pa = 0
            total_3p_pct = 0
            total_rebounds = 0
            total_assists = 0
            total_steals = 0
            total_turnovers = 0
      
            games = len(rows)
            # Get team from first game
            team = rows[1].find('td', {'data-stat': 'team_name_abbr'}).text.strip()
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
          

            # Calculate averages
            avg_mp = total_mp / games
            avg_fg = total_fg / games
            avg_fga = total_fga / games
            avg_fg_pct = total_fg_pct / games * 100
            avg_ft = total_ft / games
            avg_fta = total_fta / games
            avg_ft_pct = total_ft_pct / games * 100
            avg_3p = total_3p / games
            avg_3pa = total_3pa / games
            avg_3p_pct = total_3p_pct / games * 100
           
            
            return f"{player_name.title()} in their last 5 games| Team: {team} | MP: {avg_mp:.1f} | FG: {avg_fg:.1f} | FGA: {avg_fga:.1f} | FG%: {avg_fg_pct:.1f}% | FT: {avg_ft:.1f} | FTA: {avg_fta:.1f} | FT%: {avg_ft_pct:.1f}% | 3P: {avg_3p:.1f} | 3PA: {avg_3pa:.1f} | 3P%: {avg_3p_pct:.1f}%"
            
        else:
            return "Could not find last 5 games table"
            
    except Exception as e:
        return f"Error: {str(e)}"

def get_nbaplayer_seasonal_stats(player_response):
    try:
        
        soup = BeautifulSoup(player_response.content, 'html.parser')
        table = soup.find('table', {'id': 'per_game_stats'})
        
        if table:
            rows = table.find('tbody').find_all('tr')
            latest_season = rows[-1]
            row_cells = latest_season.find_all('td')
            
            season = latest_season.find('th', {'data-stat': 'year_id'}).text.strip()
            age = row_cells[0].text.strip()
            team = row_cells[2].text.strip()
            position = row_cells[3].text.strip()
            games = int(row_cells[4].text.strip())
            games_started = int(row_cells[5].text.strip())
            games_started_pct = (games_started / games * 100) if games > 0 else 0
            minutes_played = row_cells[6].text.strip()
            field_goals = row_cells[7].text.strip()
            field_goals_attempted = row_cells[8].text.strip()
            field_goal_percentage = row_cells[9].text.strip()
            three_points = row_cells[10].text.strip()
            three_points_attempted = row_cells[11].text.strip()
            three_points_percentage = row_cells[12].text.strip()
            two_points = row_cells[13].text.strip()
            two_points_attempted = row_cells[14].text.strip()
            two_points_percentage = row_cells[15].text.strip()
            free_throws = row_cells[17].text.strip()
            free_throws_attempted = row_cells[18].text.strip()
            free_throw_percentage = row_cells[19].text.strip()
            effective_field_goal_percentage = row_cells[16].text.strip()
            total_rebounds = row_cells[22].text.strip()
            total_assists = row_cells[23].text.strip()
            total_steals = row_cells[24].text.strip()
            return f"{player_name.title()} | Season: {season} | Age: {age} | Team: {team} | Position: {position} | Games: {games} | Games Started: {games_started} | Games Started %: {games_started_pct:.1f}% | MP: {minutes_played} | FG: {field_goals} | FGA: {field_goals_attempted} | FG%: {field_goal_percentage} | 3P: {three_points} | 3PA: {three_points_attempted} | 3P%: {three_points_percentage} |2P: {two_points} | 2PA: {two_points_attempted} | 2P%: {two_points_percentage} | FT: {free_throws} | FTA: {free_throws_attempted} | FT%: {free_throw_percentage} | eFG%: {effective_field_goal_percentage} | TRB: {total_rebounds} | AST: {total_assists} | STL: {total_steals}"
    
        else:
            return "Could not find seasonal stats table"
    
    except Exception as e:
        return f"Error: {str(e)}"
    
def get_opposing_team_stats(opposing_team_url):
    try:
        # Dictionary of known team code mappings
        team_code_mappings = {
            'NOP': 'NOH',  # New Orleans Pelicans (formerly Hornets)
            'BRK': 'BKN',  # Brooklyn Nets alternative code
            'CHO': 'CHA',  # Charlotte Hornets alternative code
            # Add more mappings as needed
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
            team_code = opposing_team_url.split('/')[4]  # Extract team code from URL
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

            # Rest of the function remains the same
            table = soup.find('table', {'id': 'stats'})
            if table:
                team_stats = table.find('tbody').find('tr')

                team_name = team_stats.find('td', {'data-stat': 'team_id'}).text
                wins = team_stats.find('td', {'data-stat': 'wins'}).text
                losses = team_stats.find('td', {'data-stat': 'losses'}).text
                games_played = team_stats.find('td', {'data-stat': 'g'}).text
                points = team_stats.find('td', {'data-stat': 'pts_per_g'}).text
                fg_pct = team_stats.find('td', {'data-stat': 'fg_pct'}).text
                fg3_pct = team_stats.find('td', {'data-stat': 'fg3_pct'}).text
                rebounds = team_stats.find('td', {'data-stat': 'trb_per_g'}).text
                assists = team_stats.find('td', {'data-stat': 'ast_per_g'}).text
                steals = team_stats.find('td', {'data-stat': 'stl_per_g'}).text
                blocks = team_stats.find('td', {'data-stat': 'blk_per_g'}).text
                turnovers = team_stats.find('td', {'data-stat': 'tov_per_g'}).text
                

                return f"Team Stats | {team_name} | W: {wins} | L: {losses} | G: {games_played} | PPG: {points} | FG%: {fg_pct} | 3P%: {fg3_pct} | REB: {rebounds} | AST: {assists} | STL: {steals} | BLK: {blocks} | TOV: {turnovers}"
        return "Could not find team stats"
                
    except Exception as e:
        return f"Error: {str(e)}"











player_name = input("Enter NBA player name (First Last): ")
player_url = get_nbaplayer_url(player_name)
opposing_team_url = get_nbaplayer_opposingteam_url(player_url)

print("\nPlayer's Last 5 Games:")
print(get_nbaplayer_5game_stats(player_url))
print("\nPlayer's Season Stats:")
print(get_nbaplayer_seasonal_stats(player_url))
print("\nOpposing Team Stats:")
print(get_opposing_team_stats(opposing_team_url))


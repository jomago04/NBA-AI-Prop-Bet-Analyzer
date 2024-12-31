from datetime import datetime

def calculateDaysSinceLastGame(last_game_date_str):
    # Convert the string date to a datetime object
    last_game_date = datetime.strptime(last_game_date_str, "%Y-%m-%d")
    
    # Get the current date
    current_date = datetime.now()
    
    # Calculate the difference in days
    difference = current_date - last_game_date
    
    return difference.days  # Return the difference in days
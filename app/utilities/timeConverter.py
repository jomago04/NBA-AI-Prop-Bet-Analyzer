class TimeConverter:
    @staticmethod
    def convert_time_string_to_float(minutes_played: str) -> float:
        try:
            # Splits string into minutes and seconds
            minutes, seconds = map(int, minutes_played.split(':'))
            # Returns float of minutes (decimal) seconds
            return minutes + (seconds / 60.0)
        except:
            return 0.0
    
    @staticmethod
    def convert_time_float_to_string(minutes_played: float) -> str:
        try:
            # Converts float to total seconds
            total_seconds = int(minutes_played * 60)
            # Converts total seconds to minutes and seconds
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            # Returns string of minutes and seconds
            return f"{minutes}:{seconds:02d}"
        except:
            return "0:00"
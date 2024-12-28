class TimeConverter:
    @staticmethod
    def convertTimeStringToFloat(minutes_played: str) -> float:
        try:
            # Splits string into minutes and seconds
            minutes, seconds = map(int, minutes_played.split(':'))
            # Returns float of minutes (decimal) seconds
            return minutes + (seconds / 60.0)
        except:
            return 0.0
    
    @staticmethod
    def convertTimeFloatToString(minutes_played: float) -> str:
        try:
            # Converts float to total seconds
            totalSeconds = int(minutes_played * 60)
            # Converts total seconds to minutes and seconds
            minutes = totalSeconds // 60
            seconds = totalSeconds % 60
            # Returns string of minutes and seconds
            return f"{minutes}:{seconds:02d}"
        except:
            return "0:00"
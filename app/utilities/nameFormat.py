class NameFormat:
    def getNameParts(playerName: str):
        nameParts = playerName.lower().split()
        
        return nameParts
    
    def formatName(nameParts: list[str]):
        formattedPlayerName = ' '.join(word.capitalize() for word in nameParts)
        
        return formattedPlayerName

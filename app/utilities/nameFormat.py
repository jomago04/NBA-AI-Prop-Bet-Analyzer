class NameFormat:
    def get_name_parts(player_name: str):
        name_parts = player_name.lower().split()
        
        return name_parts
    
    def format_name(name_parts: list[str]):
        formatted_player_name = ' '.join(word.capitalize() for word in name_parts)
        
        return formatted_player_name

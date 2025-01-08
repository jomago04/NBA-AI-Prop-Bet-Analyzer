import discord
from discord.ext import commands
from app.services.runScraper import GetNBAPlayerStats
from app.services.aiAnalysis import NBAAiAnalysis

class NBABetBot:
    def __init__(self, token: str):
        self.token = token
        self.player_stats = GetNBAPlayerStats()
        self.ai_analysis = NBAAiAnalysis()
        
        # Bot setup
        intents = discord.Intents.all()
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.setup_commands()
        
    def setup_commands(self):
        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user} is ready!')
            
        @self.bot.command(name='analyze')
        async def analyze(ctx, player_name: str, bet_type: str, line: float):
            try:
                await ctx.send(f"Analyzing {bet_type} line of {line} for {player_name}...")
                
                stats_tuple = self.player_stats.getAllPlayerStats(player_name)
                if not all(stats_tuple):
                    await ctx.send("❌ Failed to retrieve player stats")
                    return
                    
                player_info, season_averages, season_totals, last_five_game_averages, opposing_team, individual_last_five_games = stats_tuple
                
                analysis = await self.ai_analysis.analyze_bet(
                    player_name=player_name,
                    bet_type=bet_type,
                    line=line,
                    stats={
                        'player_info': player_info,
                        'season_averages': season_averages,
                        'season_totals': season_totals,
                        'last_five_game_averages': last_five_game_averages,
                        'opposing_team': opposing_team,
                        'individual_last_five_games': individual_last_five_games
                    }
                )
                
                # Create embedded message
                embed = discord.Embed(
                    title=f"Bet Analysis: {player_name}",
                    color=0x00ff00
                )
                
                # Split analysis into prediction and detailed sections
                parts = analysis.split('ANALYSIS:')
                prediction = parts[0].strip()
                detailed_analysis = parts[1].strip() if len(parts) > 1 else "No detailed analysis provided."
                
                # Add prediction to embed
                embed.add_field(name="Prediction", value=prediction, inline=False)
                
                # Split detailed analysis if it's too long
                if len(detailed_analysis) > 1024:
                    # Split into multiple parts
                    part1 = detailed_analysis[:1024]
                    part2 = detailed_analysis[1024:]
                    embed.add_field(name="Detailed Analysis (Part 1)", value=part1, inline=False)
                    embed.add_field(name="Detailed Analysis (Part 2)", value=part2[:1024], inline=False)
                else:
                    embed.add_field(name="Detailed Analysis", value=detailed_analysis, inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)}")
    
    def run(self):
        self.bot.run(self.token)
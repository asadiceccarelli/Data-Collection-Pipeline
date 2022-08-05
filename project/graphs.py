from valid_inputs import valid_clubs
from RDS import rds_connect
import matplotlib.pyplot as plt
import numpy as np
from dateutil.relativedelta import relativedelta
from matplotlib.gridspec import GridSpec


class CreateGraph:
    '''
    This class is used to create a figure of 10 subplots used to graphically show a teams statistics over the course of the season.

    Attributes
    ----------
    club (str): The Premier League club to be inspected.
    year (str): The year to be inspected.
    '''
    def __init__(self, club, year):
        self.club = club
        self.year = year
        self.connection = rds_connect().connect()
        self.query = f'SELECT * FROM public."{self.club}-{self.year[-5:-3]}{self.year[-2:]}" ORDER BY "Date"'
        self.query_result = self.connection.execute(self.query)
        self.values = self.query_result.fetchall()
        self.home_stadium = max(set(self._get_stats_list()[1]), key = self._get_stats_list()[1].count)  # Finds home stadium from the most common element in list

    def _get_stats_list(self):
        '''
        Return [dates, locations, homes_or_away, results, goals_scored, goals_against,
            possession, shots_on_target, shots, touches, passes, tackles, clearances,
            corners, offsides, fouls_conceeded, yellow_cards, red_cards]
        '''
        stats_list = []
        for i in range(2, 20):
            stats_list.append([j[i] for j in self.values])
        return stats_list

    def _home_vs_away(self, location):
        '''
        Splits the match list into home and away games.

        Args:
            location (str): 'Home' or 'Away'
        Returns:
            list: A list of either the home games or away games, of length 19.
        '''
        query = f'SELECT * FROM public."{self.club}-{self.year[-5:-3]}{self.year[-2:]}" WHERE "Location" = \'{self.home_stadium}\' ORDER BY "Date"'
        query_result = self.connection.execute(query)
        home_games = query_result.fetchall()
        query = f'SELECT * FROM public."{self.club}-{self.year[-5:-3]}{self.year[-2:]}" WHERE "Location" != \'{self.home_stadium}\' ORDER BY "Date"'
        query_result = self.connection.execute(query)
        away_games = query_result.fetchall()
        if location == 'home':
            return home_games
        else:
            return away_games
        
    def _figure_setup(self):
        '''Splits the figure into 10 subplots using GridSpec, and adds a title.'''
        self.fig = plt.figure(constrained_layout=True, figsize=(15,8))
        self.gs = GridSpec(4, 6, figure=self.fig)
        self.ax1 = self.fig.add_subplot(self.gs[0, :3])
        self.ax2 = self.fig.add_subplot(self.gs[0, 3:])
        self.ax3 = self.fig.add_subplot(self.gs[1, 0])
        self.ax4 = self.fig.add_subplot(self.gs[1, 1])
        self.ax5 = self.fig.add_subplot(self.gs[1, 2])
        self.ax6 = self.fig.add_subplot(self.gs[1, 3])
        self.ax7 = self.fig.add_subplot(self.gs[1, 4])
        self.ax8 = self.fig.add_subplot(self.gs[1, 5])
        self.ax9 = self.fig.add_subplot(self.gs[2, :])
        self.ax10 = self.fig.add_subplot(self.gs[3, :])
        self.fig.suptitle(f'{self.club} {self.year} season statistics', fontsize=24, fontweight='bold')

    def _results_pie(self):
        '''Creates a pie chart showing the percentage of each win, loss and draw.'''
        wins = self._get_stats_list()[3].count('Win')
        draws = self._get_stats_list()[3].count('Draw')
        sizes = [wins, draws, len(self._get_stats_list()[3]) - wins - draws]
        mylabels = ['Wins', 'Draws', 'Losses']
        mycolors = ['g', 'y', 'r']
        myexplode = [0.2, 0, 0]
        self.ax1.set_title('Results')
        self.ax1.pie(sizes, labels=mylabels, colors=mycolors, explode=myexplode, autopct='%1.1f%%', textprops={'fontsize': 8}, shadow=True)
    
    def _wins_possession_pie(self):
        '''Creates a pie chart showing the percentage of each win, loss and draw, when possession > 50%.'''
        query = f'SELECT * FROM public."{self.club}-{self.year[-5:-3]}{self.year[-2:]}" WHERE "Possession %%" > 50 ORDER BY "Date"'
        query_result = self.connection.execute(query)
        possession = query_result.fetchall()
        possession_wins = [i[5] for i in possession].count('Win')
        possession_draws = [i[5] for i in possession].count('Draw')
        sizes = [possession_wins, possession_draws, len(possession) - possession_wins - possession_draws]
        mylabels = ['Wins', 'Draws', 'Losses']
        mycolors = ['g', 'y', 'r']
        myexplode = [0.2, 0, 0]
        self.ax2.set_title('Results when more possession')
        self.ax2.pie(sizes, labels=mylabels, colors=mycolors, explode=myexplode, autopct='%1.1f%%', textprops={'fontsize': 8}, shadow=True)

    def _results_bar(self):
        '''Creates a bar chart showing the number of home vs. away wins.'''
        home_results = [i[5] for i in self._home_vs_away('home')].count('Win')
        away_results = [i[5] for i in self._home_vs_away('away')].count('Win')
        results = [home_results, away_results]
        xlabels = ['(H)', '(A)']
        xpos = [-0.2, 0.2]
        mywidth = 0.4
        mycolors = ['royalblue', 'darkorange']
        self.ax3.bar(xpos, results, width=mywidth, color=mycolors)
        self.ax3.set_xlim([-0.8, 0.8])
        self.ax3.set_title('Number of wins')
        self.ax3.set_xticks(xpos, xlabels)

    def _goals_bar(self):
        '''Creates a bar chart showing the average number of home vs. away goals scored and goals conceeded per game.'''
        home_gs = sum([i[6] for i in self._home_vs_away('home')]) / len(self._home_vs_away('home'))
        away_gs = sum([i[6] for i in self._home_vs_away('away')]) / len(self._home_vs_away('away'))
        home_ga = sum([i[7] for i in self._home_vs_away('home')]) / len(self._home_vs_away('home'))
        away_ga = sum([i[7] for i in self._home_vs_away('away')]) / len(self._home_vs_away('away'))
        home = [home_gs, home_ga]
        away = [away_gs, away_ga]
        xlabels = ['GS', 'GA']
        x = np.arange(len(xlabels))
        mywidth = 0.4
        self.ax4.bar(x - mywidth/2, home, width=mywidth, label='(H)', color=['royalblue'])
        self.ax4.bar(x + mywidth/2, away, width=mywidth, label='(A)', color=['darkorange'])
        self.ax4.set_title('Goals scored/against per game')
        self.ax4.set_xticks(x, xlabels)
        self.ax4.legend()

    def _shots_bar(self):
        '''Creates a bar chart showing the average number of home vs. away shots and shots on target per game.'''
        home_shots = sum([i[10] for i in self._home_vs_away('home')]) / len(self._home_vs_away('home'))
        away_shots = sum([i[10] for i in self._home_vs_away('away')]) / len(self._home_vs_away('away'))
        home_shots_ot = sum([i[9] for i in self._home_vs_away('home')]) / len(self._home_vs_away('home'))
        away_shots_ot = sum([i[9] for i in self._home_vs_away('away')]) / len(self._home_vs_away('away'))
        home = [home_shots, home_shots_ot]
        away = [away_shots, away_shots_ot]
        xlabels = ['Shots', 'On target']
        x = np.arange(len(xlabels))
        mywidth = 0.4
        self.ax5.bar(x - mywidth/2, home, width=mywidth, label='(H)', color=['royalblue'])
        self.ax5.bar(x + mywidth/2, away, width=mywidth, label='(A)', color=['darkorange'])
        self.ax5.set_title('Shots per game')
        self.ax5.set_xticks(x, xlabels)
        self.ax5.legend()

    def _passes_bar(self):
        '''Creates a bar chart showing the average number of home vs. away passes per game.'''
        home_passes = sum([i[11] for i in self._home_vs_away('home')]) / len(self._home_vs_away('home'))
        away_passes = sum([i[11] for i in self._home_vs_away('away')]) / len(self._home_vs_away('away'))
        passes = [home_passes, away_passes]
        xlabels = ['(H)', '(A)']
        xpos = [-0.2, 0.2]
        mywidth = 0.4
        mycolors = ['royalblue', 'darkorange']
        self.ax6.bar(xpos, passes, width=mywidth, color=mycolors)
        self.ax6.set_xlim([-0.8, 0.8])
        self.ax6.set_title('passes')
        self.ax6.set_xticks(xpos, xlabels)

    def _fouls_bar(self):
        '''Creates a bar chart showing the average number of home vs. away fouls per game.'''
        home_fouls = sum([i[17] for i in self._home_vs_away('home')]) / len(self._home_vs_away('home'))
        away_fouls = sum([i[17] for i in self._home_vs_away('away')]) / len(self._home_vs_away('away'))
        fouls = [home_fouls, away_fouls]
        xlabels = ['(H)', '(A)']
        xpos = [-0.2, 0.2]
        mywidth = 0.4
        mycolors = ['royalblue', 'darkorange']
        self.ax7.bar(xpos, fouls, width=mywidth, color=mycolors)
        self.ax7.set_xlim([-0.8, 0.8])
        self.ax7.set_title('Fouls conceeded per game')
        self.ax7.set_xticks(xpos, xlabels)

    def _offsides_bar(self):
        '''Creates a bar chart showing the average number of home vs. away offsides per game.'''
        home_offsides = sum([i[14] for i in self._home_vs_away('home')]) / len(self._home_vs_away('home'))
        away_offsides = sum([i[14] for i in self._home_vs_away('away')]) / len(self._home_vs_away('away'))
        offsides = [home_offsides, away_offsides]
        xlabels = ['(H)', '(A)']
        xpos = [-0.2, 0.2]
        mywidth = 0.4
        mycolors = ['royalblue', 'darkorange']
        self.ax8.bar(xpos, offsides, width=mywidth, color=mycolors)
        self.ax8.set_xlim([-0.8, 0.8])
        self.ax8.set_title('Offsides per game')
        self.ax8.set_xticks(xpos, xlabels)

    def _shots_line(self):
        '''Creates a line graph showing the shots and shots on target in comparison with a bar chart of goals scored, combines using the twinx() method.'''
        self.ax9.bar(self._get_stats_list()[0], self._get_stats_list()[4], width=3, color='green')
        ax11 = self.ax9.twinx()  # Shares x axis
        ax11.plot(self._get_stats_list()[0], self._get_stats_list()[8])
        ax11.plot(self._get_stats_list()[0], self._get_stats_list()[7])
        self.ax9.set_title('Shots, shots on target and goals scored')
        self.ax9.set_xlim([self._get_stats_list()[0][0], self._get_stats_list()[0][-1] + relativedelta(days=+50)])  # Leaves space for legend
        self.ax9.legend(['Goals scored'])
        ax11.legend(['Shots', 'Shots on target'], loc='lower right')

    def _fouls_cards_twin(self):
        '''Creates a line graph showing the fouls conceeded in comparison with a bar chart of yellow and red cards, combines using the twinx() method.'''
        self.ax10.bar(self._get_stats_list()[0], self._get_stats_list()[-2], width=3, color='gold')
        self.ax10.bar(self._get_stats_list()[0], self._get_stats_list()[-1], width=3, color='red')
        ax12 = self.ax10.twinx()  # Shares x axis
        ax12.plot(self._get_stats_list()[0], self._get_stats_list()[-3])
        ax12.set_title('Fouls and carded offences')
        self.ax10.set_ylabel('No. cards')
        ax12.set_ylabel('No. fouls')
        ax12.set_xlim([self._get_stats_list()[0][0], self._get_stats_list()[0][-1] + relativedelta(days=+50)])  # Leaves space for legend
        self.ax10.legend(['Yellow cards', 'Red cards'])
        ax12.legend(['Fouls conceeded'], loc='lower right')


    def show_graphs(self):
        '''Displays all the graphs on the same figure.'''
        self._figure_setup()
        self._results_pie()
        self._wins_possession_pie()
        self._results_bar()
        self._goals_bar()
        self._shots_bar()
        self._passes_bar()
        self._fouls_bar()
        self._offsides_bar()
        self._shots_line()
        self._fouls_cards_twin()
        plt.show()
        self.fig.savefig(f'graphical-data/{valid_clubs()[self.club]}-{self.year[-2:]}.png')

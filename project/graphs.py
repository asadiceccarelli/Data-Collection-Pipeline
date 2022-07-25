from RDS import rds_connect
import matplotlib.pyplot as plt
import numpy as np
from dateutil.relativedelta import relativedelta
from matplotlib.gridspec import GridSpec


class CreateGraph:
    def __init__(self, club, year):
        self.club = club
        self.year = year
        self.connection = rds_connect().connect()
        self.query = f'SELECT * FROM public."{self.club}-{self.year[-5:-3]}{self.year[-2:]}" ORDER BY "Date"'
        self.query_result = self.connection.execute(self.query)
        self.values = self.query_result.fetchall()

    def stats_list(self):
        '''
        Return [dates, locations, homes_or_away, results, goals_scored, goals_against,
            possession, shots_on_target, shots, touches, passes, tackles, clearances,
            corners, offsides, fouls_conceeded, yellow_cards, red_cards]
        '''
        stats_list = []
        for i in range(2, 20):
            stats_list.append([j[i] for j in self.values])
        return stats_list

    def home_vs_away(self, location):
        query = f'SELECT * FROM public."{self.club}-{self.year[-5:-3]}{self.year[-2:]}" WHERE "Location" = \'Stamford Bridge, London\' ORDER BY "Date"'
        query_result = self.connection.execute(query)
        home_games = query_result.fetchall()
        query = f'SELECT * FROM public."{self.club}-{self.year[-5:-3]}{self.year[-2:]}" WHERE "Location" != \'Stamford Bridge, London\' ORDER BY "Date"'
        query_result = self.connection.execute(query)
        away_games = query_result.fetchall()
        if location == 'home':
            return home_games
        else:
            return away_games
        
    def figure_setup(self):
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

    def results_pie(self):
        wins = self.stats_list()[3].count('Win')
        draws = self.stats_list()[3].count('Draw')
        sizes = [wins, draws, len(self.stats_list()[3]) - wins - draws]
        mylabels = ['Wins', 'Draws', 'Losses']
        mycolors = ['g', 'y', 'r']
        myexplode = [0.2, 0, 0]
        self.ax1.set_title('Results')
        self.ax1.pie(sizes, labels=mylabels, colors=mycolors, explode=myexplode, autopct='%1.1f%%', textprops={'fontsize': 8}, shadow=True)
    
    def wins_possession_pie(self):
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

    def results_bar(self):
        home_results = [i[5] for i in self.home_vs_away('home')].count('Win')
        away_results = [i[5] for i in self.home_vs_away('away')].count('Win')
        results = [home_results, away_results]
        xlabels = ['(H)', '(A)']
        xpos = [-0.2, 0.2]
        mywidth = 0.4
        mycolors = ['royalblue', 'darkorange']
        self.ax3.bar(xpos, results, width=mywidth, color=mycolors)
        self.ax3.set_xlim([-0.8, 0.8])
        self.ax3.set_title('Number of wins')
        self.ax3.set_xticks(xpos, xlabels)

    def goals_bar(self):
        home_gs = sum([i[6] for i in self.home_vs_away('home')]) / len(self.home_vs_away('home'))
        away_gs = sum([i[6] for i in self.home_vs_away('away')]) / len(self.home_vs_away('away'))
        home_ga = sum([i[7] for i in self.home_vs_away('home')]) / len(self.home_vs_away('home'))
        away_ga = sum([i[7] for i in self.home_vs_away('away')]) / len(self.home_vs_away('away'))
        home = [home_gs, home_ga]
        away = [away_gs, away_ga]
        xlabels = ['GS', 'GA']
        x = np.arange(len(xlabels))
        mywidth = 0.4
        self.ax4.bar(x - mywidth/2, home, width=mywidth, label='(H)', color=['royalblue'])
        self.ax4.bar(x + mywidth/2, away, width=mywidth, label='(A)', color=['darkorange'])
        self.ax4.set_title('Ave no. goals scored/against')
        self.ax4.set_xticks(x, xlabels)
        self.ax4.legend()

    def shots_bar(self):
        home_shots = sum([i[10] for i in self.home_vs_away('home')]) / len(self.home_vs_away('home'))
        away_shots = sum([i[10] for i in self.home_vs_away('away')]) / len(self.home_vs_away('away'))
        home_shots_ot = sum([i[9] for i in self.home_vs_away('home')]) / len(self.home_vs_away('home'))
        away_shots_ot = sum([i[9] for i in self.home_vs_away('away')]) / len(self.home_vs_away('away'))
        home = [home_shots, home_shots_ot]
        away = [away_shots, away_shots_ot]
        xlabels = ['Shots', 'On target']
        x = np.arange(len(xlabels))
        mywidth = 0.4
        self.ax5.bar(x - mywidth/2, home, width=mywidth, label='(H)', color=['royalblue'])
        self.ax5.bar(x + mywidth/2, away, width=mywidth, label='(A)', color=['darkorange'])
        self.ax5.set_title('Ave no. shots')
        self.ax5.set_xticks(x, xlabels)
        self.ax5.legend()

    def passes_bar(self):
        home_passes = sum([i[11] for i in self.home_vs_away('home')]) / len(self.home_vs_away('home'))
        away_passes = sum([i[11] for i in self.home_vs_away('away')]) / len(self.home_vs_away('away'))
        passes = [home_passes, away_passes]
        xlabels = ['(H)', '(A)']
        xpos = [-0.2, 0.2]
        mywidth = 0.4
        mycolors = ['royalblue', 'darkorange']
        self.ax6.bar(xpos, passes, width=mywidth, color=mycolors)
        self.ax6.set_xlim([-0.8, 0.8])
        self.ax6.set_title('Ave no. passes')
        self.ax6.set_xticks(xpos, xlabels)

    def fouls_bar(self):
        home_fouls = sum([i[17] for i in self.home_vs_away('home')]) / len(self.home_vs_away('home'))
        away_fouls = sum([i[17] for i in self.home_vs_away('away')]) / len(self.home_vs_away('away'))
        fouls = [home_fouls, away_fouls]
        xlabels = ['(H)', '(A)']
        xpos = [-0.2, 0.2]
        mywidth = 0.4
        mycolors = ['royalblue', 'darkorange']
        self.ax7.bar(xpos, fouls, width=mywidth, color=mycolors)
        self.ax7.set_xlim([-0.8, 0.8])
        self.ax7.set_title('Ave no. fouls conceeded')
        self.ax7.set_xticks(xpos, xlabels)

    def offsides_bar(self):
        home_offsides = sum([i[14] for i in self.home_vs_away('home')]) / len(self.home_vs_away('home'))
        away_offsides = sum([i[14] for i in self.home_vs_away('away')]) / len(self.home_vs_away('away'))
        offsides = [home_offsides, away_offsides]
        xlabels = ['(H)', '(A)']
        xpos = [-0.2, 0.2]
        mywidth = 0.4
        mycolors = ['royalblue', 'darkorange']
        self.ax8.bar(xpos, offsides, width=mywidth, color=mycolors)
        self.ax8.set_xlim([-0.8, 0.8])
        self.ax8.set_title('Ave no. offsides')
        self.ax8.set_xticks(xpos, xlabels)

    def shots_line(self):
        self.ax9.bar(self.stats_list()[0], self.stats_list()[4], width=3, color='green')
        ax11 = self.ax9.twinx()  # Shares x axis
        ax11.plot(self.stats_list()[0], self.stats_list()[8])
        ax11.plot(self.stats_list()[0], self.stats_list()[7])
        self.ax9.set_title('Shots, shots on target and goals scored')
        self.ax9.set_xlim([self.stats_list()[0][0], self.stats_list()[0][-1] + relativedelta(days=+50)])  # Leaves space for legend
        self.ax9.legend(['Goals scored'])
        ax11.legend(['Shots', 'Shots on target'], loc='lower right')

    def fouls_cards_twin(self):
        self.ax10.bar(self.stats_list()[0], self.stats_list()[-2], width=3, color='gold')
        self.ax10.bar(self.stats_list()[0], self.stats_list()[-1], width=3, color='red')
        ax12 = self.ax10.twinx()  # Shares x axis
        ax12.plot(self.stats_list()[0], self.stats_list()[-3])
        ax12.set_title('Fouls and carded offences')
        self.ax10.set_ylabel('No. cards')
        ax12.set_ylabel('No. fouls')
        ax12.set_xlim([self.stats_list()[0][0], self.stats_list()[0][-1] + relativedelta(days=+50)])  # Leaves space for legend
        self.ax10.legend(['Yellow cards', 'Red cards'])
        ax12.legend(['Fouls conceeded'], loc='lower right')


    def show_graphs(self):
        self.figure_setup()
        self.results_pie()
        self.wins_possession_pie()
        self.results_bar()
        self.goals_bar()
        self.shots_bar()
        self.passes_bar()
        self.fouls_bar()
        self.offsides_bar()
        self.shots_line()
        self.fouls_cards_twin()
        plt.show()


if __name__ == '__main__':
    PL = CreateGraph('Chelsea', '2021/22')
    PL.show_graphs()

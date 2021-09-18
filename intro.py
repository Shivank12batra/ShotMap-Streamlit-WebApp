import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer.pitch import Pitch, VerticalPitch
import seaborn as sns
import streamlit as st


st.markdown("<h1 style='text-align: center'>Customisable Shot Maps</h1>", unsafe_allow_html=True)
st.markdown('By Shivank Batra')
st.markdown('Data Collected from Understat: https://understat.com/')
st.markdown('A web app to visualise and analyse shot tendecies of various teams and players in the top five European leagues with availability of different filter options.')
st.markdown('To read more about Expected Goals(xG): https://theanalyst.com/na/2021/06/what-are-expected-goals-xg/')
team_df = pd.DataFrame()
player_df = pd.DataFrame()
leagues = ['EPL', 'LaLiga', 'Bundesliga', 'SerieA', 'Ligue1']
league_option = st.sidebar.selectbox(
    'Select League',
     leagues)
df = pd.read_csv('2020.21.{}.Shot.csv'.format(league_option))

teams = df['h_team'].unique()
option = st.sidebar.selectbox(
    'Select Team',
     teams)
team_h = df[(df['h_team'] == option) & (df['h_a'] == 'h')]
team_a = df[(df['a_team'] == option) & (df['h_a'] == 'a')]
team_df = pd.concat([team_h, team_a])

players = team_df['player'].unique()
players = np.insert(players, 0, 'N/A')
option2 = st.sidebar.selectbox(
'Select Player',
players)

if option2 != 'N/A':
    player_df = team_df[team_df['player'] == option2]

result = st.sidebar.radio('Filter Out For', ('None', 'Goal', 'Non-Goal Shots'))
xG = st.sidebar.slider('Select The xG Range', 0.0, 1.0,step=0.1, value=(0.0, 1.0))
min_val, max_val = xG
shot = df['shotType'].unique()
shot = np.delete(shot, -1)
shot_type = st.sidebar.multiselect('Select Shot Types(Can Select Multiple)', tuple(shot))
viz = st.sidebar.radio('Visualization Options', ('Shotmap', 'Shotmap + Median Shot Distance Line', 'Heatmap', 'Hexbins'))

def filters(data, *args):
    if result != 'None':
        if result == 'Goal':
            data = data[data['result'] == result]
        else:
            data = data[data['result'] != 'Goal']
    data = data[(data['xG'] >= min_val) & (data['xG'] <= max_val)]
    if len(shot_type) == 1:
        data = data[data['shotType'] == shot_type[0]]
    elif len(shot_type) == 2:
        data = data[(data['shotType'] == shot_type[0]) | (data['shotType'] == shot_type[1])]
    return data


if not player_df.empty:
    inside = player_df.copy()
else:
    inside = team_df.copy()

final_df = filters(inside, result, min_val, max_val, shot_type)

final_df['X'] = final_df['X']*100
final_df['Y'] = final_df['Y']*100
fig, ax = plt.subplots(figsize=(12, 8))
pitch = VerticalPitch(pitch_type='opta', half=True, pad_bottom=0.5,
goal_type='box', goal_alpha=0.8, pitch_color='#fef1e7', tight_layout=False)
fig, ax = pitch.draw()
fig.set_facecolor('#fef1e7')
mycolormap = LinearSegmentedColormap.from_list('my colormap', ['#80ffdb', '#7400b8'], N=100)
mSize = [0.2, 0.2, 0.2, 0.2]
mSizeS = [10000*i for i in mSize]
mx = [i for i in range(27, 87, 15)]
my = list([66]*4)
mSize2 = [i for i in np.arange(0.1, 1.1, 0.2)]
mSizeS2 = [700*i for i in mSize2]
mx2 = [65, 60, 54, 47, 39]
my2 = list([55]*5)
outside_text = ['xG/shot', 'shots', 'xG', 'goals']
xG_text = round(final_df['xG'].sum(), 2)
xG_shot = round(final_df['xG'].mean(), 2)
s_text = final_df.shape[0]
goal_df = final_df[final_df['result'] == 'Goal']
if not goal_df.empty:
    g_text = goal_df['result'].value_counts()[0]
else:
    g_text = 0
inside_text = [g_text, xG_text, s_text, xG_shot]
rev_inside_text = inside_text[::-1]
if 'Shotmap' in viz:
    try:
        ax.set_position([1, 1, 1, 1])
        if option2 != 'N/A':
            plt.title('{} Shot Map'.format(option2), fontsize=20, fontfamily='serif', fontweight='bold')
        else:
            plt.title('{} Shot Map'.format(option), fontsize=20, fontfamily='serif', fontweight='bold')
        final_df = final_df.reset_index()
        for x in range(len(final_df['xG'])):
            if final_df['result'].iloc[x] == 'Goal':
                c, alpha, ec = '#18E7E1', 0.4, '#18E7E1'
            else:
                c, alpha, ec = '#F9F7FC', 0.6, '#FF008E'
            if final_df['xG'].iloc[x] > 0.5:
                s = 300
            elif 0.3 <= final_df['xG'].iloc[x] >= 0.5:
                s = 225
            elif 0.1 <= final_df['xG'].iloc[x] >= 0.3:
                s = 150
            else:
                s = 75
            ax.scatter(final_df['Y'][x], final_df['X'][x], c=c, alpha=alpha, s=s, ec=ec, zorder=3)
        ax.scatter(mx, my, s=mSizeS, marker='h', color='#fef1e7', ec='grey', lw=2, alpha=1)
        ax.scatter(mx2, my2, s=mSizeS2, color='#fef1e7', ec='black', lw=1, alpha=1)
        ax.text(mx2[0]+4, my2[0], 'low\nquality\nchance', ha='center', va='center', c='black', weight='bold', fontfamily='serif', fontsize=5)
        ax.text(mx2[-1]-6, my2[-1], 'high\nquality\nchance', ha='center', va='center', c='black', weight='bold', fontfamily='serif', fontsize=5)
        for i in range(len(rev_inside_text)):
            if i == 3:
                c = '#18E7E1'
            else:
                c = 'black'
            ax.text(mx[i], my[i], rev_inside_text[i], ha='center', va='center', c=c, fontfamily='serif', weight='bold')
            ax.text(mx[i], my[i]-5, outside_text[i], ha='center', va='center', c=c, fontfamily='serif', weight='bold')
    except:
        pass

if 'Median Shot Distance Line' in viz:
    median_x_coord = final_df['X'].median()
    median_y_coord = final_df['Y'].median()
    median_dist = round(np.sqrt(np.square(50-median_y_coord) + np.square(100-median_x_coord)), 2)
    ax.plot((100, 0), (median_x_coord, median_x_coord), ls='--', zorder=4,c='black')
    ax.text(23, median_x_coord+0.6, 'Median Shot Distance', fontsize=7, fontfamily='serif', fontweight='bold', c='black')
    ax.text(100, median_x_coord+0.6, '{} metres'.format(median_dist), fontsize=7, fontfamily='serif', fontweight='bold', c='black')
if 'Hexbins' == viz:
    try:
        hexbins = pitch.hexbin(final_df['X'], final_df['Y'], ax=ax, edgecolors='#f4f4f4',
                      gridsize=(16, 16), cmap=mycolormap)
    except:
        pass
if 'Heatmap' == viz:
    try:
        sns.kdeplot(final_df['Y'], final_df['X'], shade=True, shade_lowest=False, alpha=0.7, cmap=mycolormap, n_levels=10, zorder=2)
        plt.ylim(50, 100)
    except:
        pass

st.pyplot(fig)

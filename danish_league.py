# -*- coding: utf-8 -*-

import streamlit as st
import numpy as np
import pandas as pd
import pickle
import time
from matplotlib import pyplot as plt
from  matplotlib.ticker import FuncFormatter
import seaborn as sns
import folium


st.set_page_config(layout="wide")

### Data Import ###
df_database = pd.read_csv("./data/data8.csv")
#geo = pd.read_csv("./data/geo.csv") 
types = ["Mean","Total","Median","Maximum","Minimum"]
label_attr_dict = {"Goals":"goals", "Points":"points","Halftime Goals":"ht_goals","Shots on target":"shots_on", "Shots off target":"shots_off","Ball Possession":"possession", "Fouls Committed":"fouls", "Yellow Cards":"yellow", "Red Cards":"red", "Corners":"corners","Pre Match Expected Goals":"pre_xg", "Post Match Expected Goals":"xg", "Winning odds":"odds"}
label_attr_dict_teams = {"Goals Scored":"goals","Goals Received":"goals_received","Points received":"points","Halftime Goals Scored":"ht_goals","Halftime Goals Received":"halftime_goals_received", "Ball Possession":"possession", "Fouls Committed":"fouls", "Red Cards":"red", "Yellow Cards":"yellow", "Corners":"corners", "Pre Match Expected Goals":"pre_xg", "Post Match Expected Goals":"xg", "Winning odds":"odds"}
label_attr_dict_correlation = {"Goals":"delta_goals","Points received":"delta_points","Halftime Goals":"delta_ht_goals","Shots on target":"delta_shots_on","Shots off target":"delta_shots_off","Possession":"delta_possession","Fouls":"delta_fouls","Yellow Cards":"delta_yellow","Red Cards":"delta_red","Corners":"delta_corners", "Pre Match Expected Goals":"delta_pre_xg", "Post Match Expected Goals":"delta_xg", "Winning odds":"delta_odds"}
label_fact_dict = {"goals scored":'goals',"halftime goals scored":'ht_goals',"shots on target":'shots_on','shots off target':'shots_off',"possession ratio":'possession',"fouls":'fouls',"yellow Cards":'yellow',"Red Cards":'red',"corners":'corners', "pre match expected goals":"pre_xg", "post match expected goals":"xg", "winning odds":"odds"}
color_dict = {'AGF': '#0088CC', 'AaB':'#CC3311', 'Brondby':'#0088CC', 'Esbjerg':'#EE7733', 'FC Helsingor':'#0088CC', 'Hobro':'#CC3311', 'Horsens':'#00A99D', 'Kobenhavn':'#0088CC', 'Lyngby':'#0088CC', 'Midtjylland':'#00A99D', 'Nordsjaelland':'#0088CC', 'OB':'#EE7733','Randers':'#00A99D', 'Silkeborg':'#00A99D', 'Sonderjyske':'#EE7733', 'Vejle':'#EE7733', 'Vendsyssel':'#CC3311', 'Vestsjaelland':'#0088CC', 'Viborg':'#00A99D'}
def get_unique_seasons_modified(df_data):
    #returns unique season list in the form "Season 13/14" for labels
    unique_seasons = np.unique(df_data.season).tolist()
    seasons_modified = []
    for s,season in enumerate(unique_seasons):
        if s==0:
            season = "‏‏‎ ‎‏‏‎ ‎" + season
        if s==len(unique_seasons)-1:
            season = season + "‏‏‎ ‎‏‏‎ ‎"
        seasons_modified.append(season.replace("-","/"))
    return seasons_modified

def get_unique_matchdays(df_data):
    #returns minimum and maximum
    return np.unique(df_data.matchday).tolist()

def get_unique_teams(df_data):
    unique_teams = np.unique(df_data.team).tolist()
    return unique_teams

def filter_season(df_data):
    df_filtered_season = pd.DataFrame()
    seasons = np.unique(df_data.season).tolist() #season list "13-14"
    start_raw = start_season.replace("/","-").replace("‏‏‎ ‎‏‏‎ ‎","") #get raw start season "13-14"
    end_raw = end_season.replace("/","-").replace("‏‏‎ ‎‏‏‎ ‎","") #get raw end season "19-20"
    start_index = seasons.index(start_raw)
    end_index = seasons.index(end_raw)+1
    seasons_selected = seasons[start_index:end_index]
    df_filtered_season = df_data[df_data['season'].isin(seasons_selected)]
    return df_filtered_season

def filter_matchday(df_data):
    df_filtered_matchday = pd.DataFrame()
    matchdays_list = list(range(selected_matchdays[0], selected_matchdays[1]+1))
    df_filtered_matchday = df_data[df_data['matchday'].isin(matchdays_list)]
    return df_filtered_matchday

def filter_teams(df_data):
    df_filtered_team = pd.DataFrame()
    if all_teams_selected == 'Select teams manually (choose below)':
        df_filtered_team = df_data[df_data['team'].isin(selected_teams)]
        return df_filtered_team
    return df_data

def filter_region(df_data):
    df_filtered_region = pd.DataFrame()
    if all_regions_selected == 'Select regions manually (choose below)':
        df_filtered_region = df_data[df_data['reg'].isin(selected_regions)]
        return df_filtered_region
    return df_data

def stack_home_away_dataframe(df_data):
    df_data["game_id"] = df_data.index + 1
    delta_names = ['goals','ht_goals','shots_on','shots_off','possession','fouls','yellow','red','corners','points','pre_xg','xg','odds']
    for column in delta_names:
        h_delta_column = 'h_delta_'+ column
        a_delta_column = 'a_delta_'+ column
        h_column = 'h_'+ column
        a_column = 'a_'+ column
        df_data[h_delta_column] = df_data[h_column]-df_data[a_column]
        df_data[a_delta_column] = df_data[a_column]-df_data[h_column]
    #st.dataframe(data=df_data)
    column_names = ['possession','yellow','red','corners','points','pre_xg','xg','odds','delta_goals','delta_ht_goals','delta_shots_on','delta_shots_off','delta_possession','delta_fouls','delta_yellow','delta_red','delta_corners','delta_points','delta_pre_xg','delta_xg','delta_odds']
    h_column_names = ['game_id','season','matchday','reg','h_team','h_goals','a_goals','h_ht_goals','a_ht_goals','h_shots_on','a_shots_on','h_shots_off','a_shots_off','h_fouls','a_fouls']
    a_column_names = ['game_id','season','matchday','reg','a_team','a_goals','h_goals','a_ht_goals','h_ht_goals','a_shots_on','h_shots_on','a_shots_off','h_shots_off','a_fouls','h_fouls']
    column_names_new = ['game_id','season','matchday','reg','location','team','goals','goals_received','ht_goals','ht_goals_received','shots_on','shots_on_test','shots_off','shots_off_test','fouls','got_fouled','possession','yellow','red','corners', 'points', 'pre_xg','xg', 'odds', 'delta_goals','delta_ht_goals','delta_shots_on','delta_shots_off','delta_possession','delta_fouls','delta_yellow','delta_red','delta_corners','delta_points','delta_pre_xg','delta_xg','delta_odds']
    for column in column_names: 
        h_column_names.append("h_" + column)
        a_column_names.append("a_" + column)
    df_home = df_data.filter(h_column_names)
    df_away = df_data.filter(a_column_names)
    df_home.insert(3,'location','h')
    df_away.insert(3,'location','a')
    df_home.columns = column_names_new
    df_away.columns = column_names_new
    df_total = df_home.append(df_away, ignore_index=True).sort_values(['game_id','season', 'matchday'], ascending=[True,True, True])
    df_total_sorted = df_total[['game_id','season','matchday','reg','location','team','goals','goals_received','delta_goals','ht_goals','ht_goals_received','delta_ht_goals','shots_on','shots_on_test','delta_shots_on','shots_off','shots_off_test','delta_shots_off','possession','delta_possession','fouls','got_fouled','delta_fouls','yellow','delta_yellow','red','delta_red','corners','delta_corners','points','delta_points','pre_xg','delta_pre_xg','xg','delta_xg','odds','delta_odds']]
    return df_total_sorted

def group_measure_by_attribute(aspect,attribute,measure):
    df_data = df_data_filtered
    df_return = pd.DataFrame()
    if(measure == "Total"):
        if(attribute == "possession"):
            measure = "Mean"
        else:
            df_return = df_data.groupby([aspect]).sum()            
    
    if(measure == "Mean"):
        df_return = df_data.groupby([aspect]).mean()
        
    if(measure == "Median"):
        df_return = df_data.groupby([aspect]).median()
    
    if(measure == "Minimum"):
        df_return = df_data.groupby([aspect]).min()
    
    if(measure == "Maximum"):
        df_return = df_data.groupby([aspect]).max()
    
    df_return["aspect"] = df_return.index
    if aspect == "team":
        df_return = df_return.sort_values(by=[attribute], ascending = False)
    return df_return
    
########################
### ANALYSIS METHODS ###
########################

def plot_x_per_season(attr,measure):
    rc = {'figure.figsize':(8,4.5),
          'axes.facecolor':'white',
          'axes.edgecolor': 'white',
          'axes.labelcolor': 'white',
          'figure.facecolor': 'white',
          'patch.edgecolor': 'white',
          'text.color': '#004570',
          'xtick.color': '#004570',
          'ytick.color': '#004570',
          'grid.color': 'grey',
          'font.size' : 12,
          'axes.labelsize': 12,
          'xtick.labelsize': 12,
          'ytick.labelsize': 12}
    plt.rcParams.update(rc)
    fig, ax = plt.subplots()
    ### Goals
    attribute = label_attr_dict[attr]
    df_plot = pd.DataFrame()
    df_plot = group_measure_by_attribute("season",attribute,measure)
    ax = sns.barplot(x="aspect", y=attribute, data=df_plot, color = "#004570")
    y_str = measure + " " + attr + " " + " per Team"
    if measure == "Total":
        y_str = measure + " " + attr
    if measure == "Minimum" or measure == "Maximum":
        y_str = measure + " " + attr + " by a Team"
        
    ax.set(xlabel = "Season", ylabel = y_str)
    if measure == "Mean" or attribute in ["possession"]:
        for p in ax.patches:
            ax.annotate(format(p.get_height(), '.2f'), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 15),
                   textcoords = 'offset points')
    else:
        for p in ax.patches:
            ax.annotate(format(str(int(p.get_height()))), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 15),
                   textcoords = 'offset points')
    st.pyplot(fig)

def plot_x_per_matchday(attr,measure):
    rc = {'figure.figsize':(8,4.5),
          'axes.facecolor':'white',
          'axes.edgecolor': 'white',
          'axes.labelcolor': 'white',
          'figure.facecolor': 'white',
          'patch.edgecolor': 'white',
          'text.color': '#004570',
          'xtick.color': '#004570',
          'ytick.color': '#004570',
          'grid.color': 'grey',
          'font.size' : 8,
          'axes.labelsize': 12,
          'xtick.labelsize': 8,
          'ytick.labelsize': 12}
    plt.rcParams.update(rc)
    fig, ax = plt.subplots()
    ### Goals
    attribute = label_attr_dict[attr]
    df_plot = pd.DataFrame()
    df_plot = group_measure_by_attribute("matchday",attribute,measure)
    ax = sns.barplot(x="aspect", y=attribute, data=df_plot.reset_index(), color = "#004570")
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)+1))
    y_str = measure + " " + attr + " per Team"
    if measure == "Total":
        y_str = measure + " " + attr
    if measure == "Minimum" or measure == "Maximum":
        y_str = measure + " " + attr + " by a Team"
        
    ax.set(xlabel = "Matchday", ylabel = y_str)
    if measure == "Mean" or attribute in ["possession"]:
        for p in ax.patches:
            ax.annotate(format(p.get_height(), '.2f'), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 18),
                   rotation = 90,
                   textcoords = 'offset points')
    else:
        for p in ax.patches:
            ax.annotate(format(str(int(p.get_height()))), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 18),
                   rotation = 90,
                   textcoords = 'offset points')
    st.pyplot(fig)

def plot_x_per_team(attr,measure): #total #against, #conceived
    rc = {'figure.figsize':(8,4.5),
          'axes.facecolor': 'white',
          'axes.edgecolor': 'white',
          'axes.labelcolor': 'white',
          'figure.facecolor': 'white',
          'patch.edgecolor': 'white',
          'text.color': '#004570',
          'xtick.color': '#004570',
          'ytick.color': '#004570',
          'grid.color': 'grey',
          'font.size' : 8,
          'axes.labelsize': 12,
          'xtick.labelsize': 8,
          'ytick.labelsize': 12}
    
    plt.rcParams.update(rc)
    fig, ax = plt.subplots()
    ### Goals
    attribute = label_attr_dict_teams[attr]
    df_plot = pd.DataFrame()
    df_plot = group_measure_by_attribute("team",attribute,measure)
    if specific_team_colors:
        ax = sns.barplot(x="aspect", y=attribute, data=df_plot.reset_index(), palette = color_dict)
    else:
        ax = sns.barplot(x="aspect", y=attribute, data=df_plot.reset_index(), color = "#004570")
    y_str = measure + " " + attr + " " + "per Game"
    if measure == "Total":
        y_str = measure + " " + attr
    if measure == "Minimum" or measure == "Maximum":
        y_str = measure + " " + attr + "in a Game"
    ax.set(xlabel = "Team", ylabel = y_str)
    plt.xticks(rotation=66,horizontalalignment="right")
    if measure == "Mean" or attribute in ["possession"]:
        for p in ax.patches:
            ax.annotate(format(p.get_height(), '.2f'), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 18),
                   rotation = 90,
                   textcoords = 'offset points')
    else:
        for p in ax.patches:
            ax.annotate(format(str(int(p.get_height()))), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 18),
                   rotation = 90,
                   textcoords = 'offset points')
    st.pyplot(fig)

def plt_attribute_correlation(aspect1, aspect2):
    df_plot = df_data_filtered
    rc = {'figure.figsize':(5,5),
          'axes.facecolor':'white',
          'axes.edgecolor': 'white',
          'axes.labelcolor': 'white',
          'figure.facecolor': 'white',
          'patch.edgecolor': 'white',
          'text.color': '#004570',
          'xtick.color': '#004570',
          'ytick.color': '#004570',
          'grid.color': 'grey',
          'font.size' : 8,
          'axes.labelsize': 12,
          'xtick.labelsize': 12,
          'ytick.labelsize': 12}
    plt.rcParams.update(rc)
    fig, ax = plt.subplots()
    asp1 = label_attr_dict_correlation[aspect1]
    asp2 = label_attr_dict_correlation[aspect2]
    if(corr_type=="Regression Plot (Recommended)"):
        ax = sns.regplot(x=asp1, y=asp2, x_jitter=.1, data=df_plot, color = '#004570',scatter_kws={"color": "#004570"},line_kws={"color": "#c2dbfc"})
    if(corr_type=="Standard Scatter Plot"):
        ax = sns.scatterplot(x=asp1, y=asp2, data=df_plot, color = '#004570')
    #if(corr_type=="Violin Plot (High Computation)"):
    #    ax = sns.violinplot(x=asp1, y=asp2, data=df_plot, color = '#f21111')
    ax.set(xlabel = aspect1, ylabel = aspect2)
    st.pyplot(fig, ax)

def find_match_game_id(min_max,attribute,what):
    df_find = df_data_filtered
    search_attribute = label_fact_dict[attribute]
    if(what == "difference between teams"):
        search_attribute = "delta_" + label_fact_dict[attribute]
        df_find[search_attribute] = df_find[search_attribute].abs()
    if(what == "by both teams"):
        df_find = df_data_filtered.groupby(['game_id'], as_index=False).sum()
    column = df_find[search_attribute]
    index = 0
    if(min_max == "Minimum"):
        index = column.idxmin()
    if(min_max == "Maximum"):
        index = column.idxmax()
    #st.dataframe(data=df_find)
    game_id = df_find.at[index, 'game_id']
    value = df_find.at[index,search_attribute]
    team = ""
    if(what != "by both teams"):
        team = df_find.at[index, 'team']
    return_game_id_value_team = [game_id,value,team]
    return return_game_id_value_team

def build_matchfacts_return_string(return_game_id_value_team,min_max,attribute,what):
    game_id = return_game_id_value_team[0]
    df_match_result = df_data_filtered.loc[df_data_filtered['game_id'] == game_id]
    season = df_match_result.iloc[0]['season'].replace("-","/")
    matchday = str(df_match_result.iloc[0]['matchday'])
    home_team = df_match_result.iloc[0]['team']
    away_team = df_match_result.iloc[1]['team']
    goals_home = str(df_match_result.iloc[0]['goals'])
    goals_away = str(df_match_result.iloc[1]['goals'])
    goals_home = str(df_match_result.iloc[0]['goals'])    
    string1 =  "On matchday " + matchday + " of season " + season + " " + home_team + " played against " + away_team + ". "
    string2 = ""
    if(goals_home>goals_away):
        string2 = "The match resulted in a " + goals_home + ":" + goals_away + " (" + "HT " + str(df_match_result.iloc[0]['ht_goals']) + ":" + str(df_match_result.iloc[1]['ht_goals']) +") win for " + home_team + "."
    if(goals_home<goals_away):
        string2 = "The match resulted in a " + goals_home + ":" + goals_away + " (" + "HT " + str(df_match_result.iloc[0]['ht_goals']) + ":" + str(df_match_result.iloc[1]['ht_goals']) +") loss for " + home_team + "."
    if(goals_home==goals_away):
        string2 = "The match resulted in a " + goals_home + ":" + goals_away + " (" + "HT " + str(df_match_result.iloc[0]['ht_goals']) + ":" + str(df_match_result.iloc[1]['ht_goals']) +") draw. "
    string3 = ""
    string4 = ""
    value = str(abs(round(return_game_id_value_team[1],2)))
    team = str(return_game_id_value_team[2])
    if(what == "difference between teams"):
        string3 = " Over the course of the match, a difference of " + value + " " + attribute + " was recorded between the teams."
        string4 = " This is the " + min_max.lower() + " difference for two teams in the currently selected data."
    if(what == "by both teams"):
        string3 = " Over the course of the match, both teams recorded " + value + " " + attribute + " together."
        string4 = " This is the " + min_max.lower() +" value for two teams in the currently selected data."
    if(what == "by a team"):
        string3 = " Over the course of the match, " + team + " recorded " + value + " " + attribute + "."
        string4 = " This is the " + min_max.lower() +" value for a team in the currently selected data."
    answer = string1 + string2 + string3 + string4
    st.markdown(answer)
    return df_match_result
    
####################
### INTRODUCTION ###
####################

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.1, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('Superliga Streamlit App')
with row0_2:
    st.image('danish_super_league.png')
row3_spacer1, row3_1, row3_spacer2 = st.columns((.1, 3.2, .1))
with row3_1:
    st.markdown("Welcome to the Danish Superliga visualisation!")
    st.markdown("Here you can find data visualisation for numerous parameters for football matches that occured between 2013 - 2022.")

#################
### SELECTION ###
#################
df_stacked = stack_home_away_dataframe(df_database)

st.sidebar.text('')
st.sidebar.text('')
st.sidebar.text('')
### SEASON RANGE ###
st.sidebar.markdown("**First select the data range you want to analyze:** 👇")
unique_seasons = get_unique_seasons_modified(df_database)
start_season, end_season = st.sidebar.select_slider('Select the season range you want to include', unique_seasons, value = ["‏‏‎ ‎‏‏‎ ‎13/14","22/23‏‏‎ ‎‏‏‎ ‎"])
df_data_filtered_season = filter_season(df_stacked)


### MATCHDAY RANGE ###
unique_matchdays = get_unique_matchdays(df_data_filtered_season) #min and max matchday
selected_matchdays = st.sidebar.select_slider('Select the matchday range you want to include', unique_matchdays, value=[min(unique_matchdays),max(unique_matchdays)])
df_data_filtered_matchday = filter_matchday(df_data_filtered_season)


### TEAM SELECTION ###
unique_teams = get_unique_teams(df_data_filtered_matchday)
all_teams_selected = st.sidebar.selectbox('Do you want to only include specific teams? If the answer is yes, please check the box below and then select the team(s) in the new field.', ['Include all available teams','Select teams manually (choose below)'])
if all_teams_selected == 'Select teams manually (choose below)':
    selected_teams = st.sidebar.multiselect("Select and deselect the teams you would like to include in the analysis. You can clear the current selection by clicking the corresponding x-button on the right", unique_teams, default = unique_teams)
df_data_filtered_team = filter_teams(df_data_filtered_matchday)  

### REGION RANGE ###
unique_regions = [str(r) for r in np.unique(df_database.reg).tolist()]

all_regions_selected = st.sidebar.selectbox('Do you want to only include specific regions? If the answer is yes, please check the box below and then select the region(s) in the new field.', ['Include all regions','Select regions manually (choose below)'])
if all_regions_selected == 'Select regions manually (choose below)':
    selected_regions = st.sidebar.multiselect("Select and deselect regions you would like to include in the analysis. You can clear the current selection by clicking the corresponding x-button on the right", unique_regions, default = unique_regions)

df_data_filtered = filter_region(df_data_filtered_team)  


### SEE DATA ###
row6_spacer1, row6_1, row6_spacer2 = st.columns((.2, 7.1, .2))
with row6_1:
    st.subheader("Currently selected data:")

row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3, row2_3, row2_spacer4, row2_4, row2_spacer5   = st.columns((.2, 1.6, .2, 1.6, .2, 1.6, .2, 1.6, .2))
with row2_1:
    unique_games_in_df = df_data_filtered.game_id.nunique()
    str_games = "🏟️ " + str(unique_games_in_df) + " Matches"
    st.markdown(str_games)
with row2_2:
    unique_teams_in_df = len(np.unique(df_data_filtered.team).tolist())
    t = " Teams"
    if(unique_teams_in_df==1):
        t = " Team"
    str_teams = "🏃‍♂️ " + str(unique_teams_in_df) + t
    st.markdown(str_teams)
with row2_3:
    total_goals_in_df = df_data_filtered['goals'].sum()
    str_goals = "🥅 " + str(total_goals_in_df) + " Goals"
    st.markdown(str_goals)
with row2_4:
    total_shots_in_df = df_data_filtered['shots_on'].sum()
    str_shots = "👟⚽ " + str(total_shots_in_df) + " Shots"
    st.markdown(str_shots)

row3_spacer1, row3_1, row3_spacer2 = st.columns((.2, 7.1, .2))
with row3_1:
    st.markdown("")
    see_data = st.expander('You can click here to see the raw data first 👉')
    with see_data:
         st.dataframe(data=df_database.reset_index(drop=True))
        #st.dataframe(data=df_data_filtered.reset_index(drop=True))
st.text('')

#st.dataframe(data=df_stacked.reset_index(drop=True))
#st.dataframe(data=df_data_filtered)



################
### ANALYSIS ###
################

### DATA EXPLORER ###
row12_spacer1, row12_1, row12_spacer2 = st.columns((.2, 7.1, .2))
with row12_1:
    st.subheader('Match Finder')
    st.markdown('Show the (or a) match with the...')  
if (all_teams_selected == 'Include all available teams') and (all_regions_selected == 'Include all regions'):
    row13_spacer1, row13_1, row13_spacer2, row13_2, row13_spacer3, row13_3, row13_spacer4   = st.columns((.2, 2.3, .2, 2.3, .2, 2.3, .2))
    with row13_1:
        show_me_hi_lo = st.selectbox ("", ["Maximum","Minimum"],key = 'hi_lo') 
    with row13_2:
        show_me_aspect = st.selectbox ("", list(label_fact_dict.keys()),key = 'what')
    with row13_3:
        show_me_what = st.selectbox ("", ["by a team", "by both teams", "difference between teams"],key = 'one_both_diff')
    row14_spacer1, row14_1, row14_spacer2 = st.columns((.2, 7.1, .2))
    with row14_1:
        return_game_id_value_team = find_match_game_id(show_me_hi_lo,show_me_aspect,show_me_what)
        df_match_result = build_matchfacts_return_string(return_game_id_value_team,show_me_hi_lo,show_me_aspect,show_me_what)     
    row15_spacer1, row15_1, row15_2, row15_3, row15_4, row15_spacer2  = st.columns((0.5, 1.5, 1.5, 1, 2, 0.5))
    with row15_1:
        st.subheader(" ‎")
    with row15_2:
        st.subheader(str(df_match_result.iloc[0]['team']))
    with row15_3:
        end_result = str(df_match_result.iloc[0]['goals']) + " : " +str(df_match_result.iloc[1]['goals'])
        ht_result = " ‎ ‎( " + str(df_match_result.iloc[0]['ht_goals']) + " : " +str(df_match_result.iloc[1]['ht_goals']) + " )"
        st.subheader(end_result)  
    with row15_4:
        st.subheader(str(df_match_result.iloc[1]['team']))
else:
    row17_spacer1, row17_1, row17_spacer2 = st.columns((.2, 7.1, .2))
    with row17_1:
        st.warning('Unfortunately this analysis is only available if all teams and regions are included')

if (all_teams_selected == 'Include all available teams') and (all_regions_selected == 'Include all regions'):
    row16_spacer1, row16_1, row16_2, row16_3, row16_4, row16_5, row16_spacer2  = st.columns((0.5, 1.5, 1, 1.5, 1, 1, 0.5))
    with row16_1:
        st.markdown("🧮 Winning odds")
        st.markdown("👟👍 Shots on target")
        st.markdown("👟👎 Shots off target")        
        st.markdown("📔 Pre Match EG")
        st.markdown("📖 Post Match EG")            
        st.markdown("🏆 Points")
        st.markdown("⛹🏻 Possession")
        st.markdown("🤕 Fouls")
        st.markdown("🟨 Yellow Cards")
        st.markdown("🟥 Red Cards")
        st.markdown("📐 Corners")
    with row16_2:
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[0]['odds']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[0]['shots_on']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[0]['shots_off']))        
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[0]['pre_xg']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[0]['xg']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[0]['points']))        
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[0]['possession']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(int(df_match_result.iloc[0]['fouls'])))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[0]['yellow']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[0]['red']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[0]['corners']))
    with row16_4:
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[1]['odds']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[1]['shots_on']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[1]['shots_off']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[1]['pre_xg']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[1]['xg']))        
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[1]['points']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[1]['possession']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(int(df_match_result.iloc[1]['fouls'])))    
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[1]['yellow']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[1]['red']))
        st.markdown(" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎"+str(df_match_result.iloc[1]['corners']))

    row19_spacer1  = st.columns((7))

    row18_spacer1, row18_1, row18_spacer2  = st.columns((0.5, 6, 0.5))
    with row18_1:

#    with row16_5:

        geo_sub = df_database[df_database.index == (return_game_id_value_team[0]-1)]

        attendance = list(geo_sub.attendance)
        city = list(geo_sub.city)
        reg = list(geo_sub.reg)

        if attendance[0] == 1:
            attendance1 = 'unknown number of'
        else:
            attendance1 = format(attendance[0], ",")
        longitude = float(geo_sub.lon)
        latitude = float(geo_sub.lat)
        stadium_name = list(geo_sub.stadium_name)[0]
        coordinates = pd.DataFrame(np.column_stack([longitude, latitude]), columns=['lat', 'lon'])

        st.markdown(f'🇩🇰 **Match** with index {return_game_id_value_team[0]} was played at **{stadium_name}, {city[0]}, {reg[0]}** and **{attendance1} fans** watched the game on the stadium')
        
        zoom_level = st.selectbox(
            "Zoom Level",
            ["Stadium View", "City View", "Region View", "Country View"], index=0
        )
        if zoom_level == "Stadium View":
            st.map(coordinates, zoom=14)
        elif zoom_level == "City View":
            st.map(coordinates, zoom=12)
        elif zoom_level == "Region View":
            st.map(coordinates, zoom=8)
        elif zoom_level == "Country View":
            st.map(coordinates, zoom=6)
        
### TEAM ###
row4_spacer1, row4_1, row4_spacer2 = st.columns((.2, 7.1, .2))
with row4_1:
    st.subheader('Analysis per Team')
row5_spacer1, row5_1, row5_spacer2, row5_2, row5_spacer3  = st.columns((.2, 2.3, .4, 4.4, .2))
with row5_1:
    st.markdown('Investigate a variety of stats for each team. Which team scores the most goals per game?')    
    plot_x_per_team_selected = st.selectbox ("Which attribute do you want to analyze?", list(label_attr_dict_teams.keys()), key = 'attribute_team')
    plot_x_per_team_type = st.selectbox ("Which measure do you want to analyze?", types, key = 'measure_team')
    specific_team_colors = st.checkbox("Use color scheme based on regions in Denmark")
with row5_2:
    if (all_teams_selected != 'Select teams manually (choose below)' or selected_teams) and (all_regions_selected != 'Select regions manually (choose below)' or selected_regions):
        plot_x_per_team(plot_x_per_team_selected, plot_x_per_team_type)
    else:
        st.warning('Please select at least one team and region')

### SEASON ###
row6_spacer1, row6_1, row6_spacer2 = st.columns((.2, 7.1, .2))
with row6_1:
    st.subheader('Analysis per Season')
row7_spacer1, row7_1, row7_spacer2, row7_2, row7_spacer3  = st.columns((.2, 2.3, .4, 4.4, .2))
with row7_1:
    st.markdown('Investigate developments and trends. Which season had teams score the most goals?')    
    plot_x_per_season_selected = st.selectbox ("Which attribute do you want to analyze?", list(label_attr_dict.keys()), key = 'attribute_season')
    plot_x_per_season_type = st.selectbox ("Which measure do you want to analyze?", types, key = 'measure_season')
with row7_2:
    if (all_teams_selected != 'Select teams manually (choose below)' or selected_teams) and (all_regions_selected != 'Select regions manually (choose below)' or selected_regions):
        plot_x_per_season(plot_x_per_season_selected,plot_x_per_season_type)
    else:
        st.warning('Please select at least one team and region')

### MATCHDAY ###
row8_spacer1, row8_1, row8_spacer2 = st.columns((.2, 7.1, .2))
with row8_1:
    st.subheader('Analysis per Matchday')
row9_spacer1, row9_1, row9_spacer2, row9_2, row9_spacer3  = st.columns((.2, 2.3, .4, 4.4, .2))
with row9_1:
    st.markdown('Investigate stats over the course of a season. At what point in the season do teams score the most goals? Do teams run less towards the end of the season?')    
    plot_x_per_matchday_selected = st.selectbox ("Which aspect do you want to analyze?", list(label_attr_dict.keys()), key = 'attribute_matchday')
    plot_x_per_matchday_type = st.selectbox ("Which measure do you want to analyze?", types, key = 'measure_matchday')
with row9_2:
    if (all_teams_selected != 'Select teams manually (choose below)' or selected_teams) and (all_regions_selected != 'Select regions manually (choose below)' or selected_regions):
        plot_x_per_matchday(plot_x_per_matchday_selected, plot_x_per_matchday_type)
    else:
        st.warning('Please select at least one team and region')



### CORRELATION ###
corr_plot_types = ["Regression Plot (Recommended)","Standard Scatter Plot"] #removed "Violin Plot (High Computation)"

row10_spacer1, row10_1, row10_spacer2 = st.columns((.2, 7.1, .2))
with row10_1:
    st.subheader('Correlation of Game Stats')
row11_spacer1, row11_1, row11_spacer2, row11_2, row11_spacer3  = st.columns((.2, 2.3, .4, 4.4, .2))
with row11_1:
    st.markdown('Investigate the correlation of attributes, but keep in mind correlation does not imply causation. Do teams that run more than their opponents also score more goals? Do teams that have more shots than their opponents have more corners?')    
    corr_type = st.selectbox ("What type of correlation plot do you want to see?", corr_plot_types)
    y_axis_aspect2 = st.selectbox ("Which attribute do you want on the y-axis?", list(label_attr_dict_correlation.keys()))
    x_axis_aspect1 = st.selectbox ("Which attribute do you want on the x-axis?", list(label_attr_dict_correlation.keys()))
with row11_2:
    if (all_teams_selected != 'Select teams manually (choose below)' or selected_teams) and (all_regions_selected != 'Select regions manually (choose below)' or selected_regions):
        plt_attribute_correlation(x_axis_aspect1, y_axis_aspect2)
    else:
        st.warning('Please select at least one team and region')

for variable in dir():
    if variable[0:2] != "__":
        del globals()[variable]
del variable

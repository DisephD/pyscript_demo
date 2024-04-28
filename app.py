from io import StringIO
import js
import json
import plotly
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pyodide.http import open_url
from pyscript import display
import warnings
warnings.filterwarnings("ignore")

url = "https://raw.githubusercontent.com/DisephD/pyscript_tutorial/main/drink_water_data.csv"

data = pd.read_csv(open_url(url), parse_dates=["Date"])
water_data = data.query("year == 2024")


def format_week_num(week_num):
  return f"Week {week_num}"


def plot (selected_month):

    js.document.getElementById('stats').innerHTML = ''
    filtered_df = water_data[water_data["month"]==selected_month]

    total_water = filtered_df["Water(ml)"].sum()
    avg_water = total_water/len(filtered_df)
    highest_water = filtered_df["Water(ml)"].max()
    target_ml = 62_000
    target_reach = target_ml - total_water
    toprows = [
        int(total_water),
        int(round(avg_water, -1)),
        int(highest_water),
        int(target_reach)
    ]
    
    json_string = json.dumps (toprows)
    display(json_string, target="stats")

    
    #--------------------line chart-------------------------------
    daily_total = filtered_df.groupby("day")["Water(ml)"].sum().reset_index()
    fig = px.line(daily_total, x="day", y="Water(ml)", height=300, width= 670, markers=True,
                color_discrete_sequence=["blue"])
    fig.update_traces (marker_size = 6, texttemplate='%{text:.2s}')

    fig.update_layout(plot_bgcolor="rgb(254,254,254)", margin=dict(t=50,l=10,b=5,r=10), 
    title= "Daily Trend", title_font_family ="Times New Roman Black", title_font_size = 17, title_x = 0.01, 
    xaxis_tickfont_size=11,
    yaxis=dict( title=None, titlefont_size=14, tickfont_size=11, tickfont_color= "#A9A9AB", ),
    xaxis = dict(title=None, tickfont_size =11,  tickfont_color= "#A9A9AB"),
    )
    graphJSON = fig.to_json()
    js.Plotly.newPlot("line_chart", js.JSON.parse(graphJSON))


    #========this is the bar graph============
    bar_daily_total = filtered_df.groupby("week")["Water(ml)"].sum().reset_index()
    bar_fig = px.bar (bar_daily_total, x ="week", y = "Water(ml)", title= "", labels ="")
    bar_fig.update_xaxes(tickvals= bar_daily_total["week"].unique(), ticktext=[format_week_num(week)for week in bar_daily_total['week'].unique()])

    bar_fig.update_layout(
    plot_bgcolor="rgb(254,254,254,0.7)", margin=dict(t=50,l=10,b=10,r=10), width=270, height = 300,
    xaxis_tickfont_size=14,yaxis=dict( title='', titlefont_size=14, tickfont_size=13),
    xaxis = dict(title="", tickfont_size =13), bargap=0.3, 
    )

    bar_fig.update_traces(width=0.5)
    graphJSON = bar_fig.to_json()
    js.Plotly.newPlot("bar_chart", js.JSON.parse(graphJSON))\
    

    #=======this is the table===============
    table_daily_total = filtered_df.groupby("Date")["Water(ml)"].sum().reset_index()
    table_daily_total["Daily_Change"] = np.round(table_daily_total["Water(ml)"].pct_change()*100,1).fillna(0).apply(lambda x: f"+{x}" if x > 0 else str(x)) + "%"

    table_fig= go.Figure(data=[go.Table (columnwidth = [12, 10, 10],
                                    header=dict(values=list(table_daily_total.columns), fill_color='white', align=['left', "right", "right"], height= 37,font=dict(size=14, color= "#141414"),line_color= "rgb(231, 239, 250)",), cells=dict(values=[table_daily_total["Date"], table_daily_total["Water(ml)"], table_daily_total["Daily_Change"]], fill_color='white', line_color= "rgb(231, 239, 250)", align=['left',"right","right"], height=36))
                                    ])
    table_fig.layout.width= 570
    table_fig.update_layout(plot_bgcolor="rgb(254,254,254)",height= 300, margin=dict(t=5,l=10,b=10,r=10),)
    graphJSON = table_fig.to_json()
    js.Plotly.newPlot("table", js.JSON.parse(graphJSON))


    #--------------this is the heatmap---------------
    filtered_df['time'] = pd.to_datetime(filtered_df['hour'], format='%H: %M')
    time_bins = [0, 11, 18, 21, 24]
    time_labels = ['Morning', 'Afternoon', 'Evening', 'Night']
    filtered_df['time_of_day'] = pd.cut(filtered_df['time'].dt.hour, bins=time_bins, labels=time_labels, right=False)
    filtered_df.drop("time", axis=1, inplace=True)

    heatmap_data = filtered_df.groupby(['day_of_the_week', 'time_of_day'])["Water(ml)"].sum().reset_index()
    custom_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat','Sun', ]
    heatmap_data['day_of_the_week'] = pd.Categorical(heatmap_data['day_of_the_week'], categories=custom_order, ordered=True)
    heatmap_data = heatmap_data.sort_values(by='day_of_the_week')

    heatmap_pivot= heatmap_data.pivot_table(index="time_of_day", columns= "day_of_the_week", values= "Water(ml)", aggfunc="sum", fill_value= 0)


    heat_fig= px.imshow(heatmap_pivot, color_continuous_scale='Blues', height=300, width = 250)
    heat_fig.update_traces(showscale=False, coloraxis=None,colorscale= "Blues")

    heat_fig.update_layout(plot_bgcolor="rgb(254,254,254)", title='heatmap',margin=dict(t=50,l=10,b=5,r=10), 
        xaxis_tickfont_size=14,
        yaxis=dict( title=None, titlefont_size=14, tickfont_size=13),
        xaxis = dict(title=None, tickfont_size =13),
    )
    heat_fig.update_xaxes(side="top")

    graphJSON = heat_fig.to_json()
    js.Plotly.newPlot("heatmap", js.JSON.parse(graphJSON))




def selectChange():
    selected_month = js.document.getElementById("selected_month").value
    plot(selected_month)
    # choice = js.document.getElementById("select").value
    # plot(choice)

plot("February")
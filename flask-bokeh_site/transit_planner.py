import numpy as np
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import widgetbox, column, row
from bokeh.models import Band, BoxAnnotation, ColumnDataSource, Range1d
from bokeh.models.widgets import Select, Slider, Paragraph, Button
from bokeh.plotting import figure
import glob
import os
from collections import OrderedDict
import json

# Captures form selection passed as request parameter
# This ensures the data for the correct bus route is loaded
args = curdoc().session_context.request.arguments
args_route = "55"
try:
    args_route = args.get('route')[0]
except TypeError:
    pass

# Load the Data Set
names = ["tripid", "start", "stop", "day_of_week", "decimal_time", "travel_time", "wait_time"]
all_files = glob.glob(os.path.join("../processed_data/trips_and_waits/" + args_route + "/", "*.csv"))   
df_each = (pd.read_csv(f, skiprows=1, names=names) for f in all_files)
df = pd.concat(df_each, ignore_index=True)

# Load the list of bus stops
def load_bus_stops(rt):
    with open("../processed_data/stop_lists/" + rt + ".json", 'r') as f:
        bus_stops = json.load(f, object_pairs_hook=OrderedDict)
    return bus_stops

bus_stops = load_bus_stops(args_route)['negative'].keys()

# Create initial graphs
day_of_week = ["All days", "Weekdays", "Saturdays", "Sundays"]
default = {
    'start': "MidwayOrange", 'stop': "Ashland", 
    'day': "All days",
    'hour': 17, 'minute': 30
}

# "q" as in query
q = df[(df.start == default['start']) & (df.stop == default['stop'])]
bins = np.arange(0,24.25,0.25)
x_scale = np.arange(0,24,0.25)
grouped = q.groupby([pd.cut(q.decimal_time,bins,labels=x_scale,right=False)])

travel_ninetieth = grouped.travel_time.quantile(0.9)
wait_ninetieth = grouped.wait_time.quantile(0.9)

# Defines travel time plots and sets defaults
title = "{} -> {} ({})".format(default['start'], default['stop'], default['day'])
plot_travel = figure(
    title=title,
    x_range=Range1d(0, 24, bounds="auto"), y_range=(0,travel_ninetieth.max()+10),
    x_axis_label='Time (Decimal Hours)', y_axis_label='Travel Time (Minutes)',
    width=600, height=300,
    responsive=True
)
line_travel = plot_travel.line(x_scale, grouped.travel_time.median(), color="red")
scatter_travel = plot_travel.circle(q.decimal_time, q.travel_time, color="navy", radius=0.01)

# Defines wait time plots and sets defaults
plot_wait = figure(
    x_range=Range1d(0, 24, bounds="auto"), y_range=(0,wait_ninetieth.max()+10),
    x_axis_label='Time (Decimal Hours)', y_axis_label='Wait Time (Minutes)',
    width=600, height=300,
    responsive=True
)
line_wait = plot_wait.line(x_scale, grouped.wait_time.median(), color="red")
scatter_wait = plot_wait.circle(q.decimal_time, q.wait_time, color="navy", radius=0.01)

# Creates paragraph summary of typical travel and wait times at given time of day
time_index = (default['hour'] * 4) + (default['minute'] / 15)
line1 = "At {}:{:02d} the {} bus leaves around every {} minutes from {} going to {}.\n".format(
    default['hour'], default['minute'],
    args_route,
    round(grouped.wait_time.median()[time_index], 1),
    default['start'], default['stop']
)
line2 = "The trips take around {} minutes.".format(
    round(grouped.travel_time.median()[time_index], 1)
)
paragraph = Paragraph(text=line1+line2, width=800)

# Creates box around selected time band
slider_time = default['hour'] + (default['minute'] / 15) / 4.0
box_travel = BoxAnnotation(
    left=slider_time, right=slider_time+0.25,
    fill_color='green', fill_alpha=0.1
)
box_wait = BoxAnnotation(
    left=slider_time, right=slider_time+0.25,
    fill_color='green', fill_alpha=0.1
)
plot_travel.add_layout(box_travel)
plot_wait.add_layout(box_wait)

# Create widgets
select_start = Select(title="Start", value=default['start'], options=bus_stops)
select_stop = Select(title="Stop", value=default['stop'], options=bus_stops)
select_day = Select(title="Days", value=default['day'], options=day_of_week)
slider_hour = Slider(start=0, end=23, value=default['hour'], step=1, title="Hour")
slider_minute = Slider(start=0, end=59, value=default['minute'], step=1, title="Minute")
button = Button(label="Submit", button_type="success")

# Callback functions
def update_start(attr, new, old):
    default['start'] = old

def update_stop(attr, new, old):
    default['stop'] = old

def update_day(attr, new, old):
    default['day'] = old

def update_hour(attr, new, old):
    default['hour'] = old

def update_minute(attr, new, old):
    default['minute'] = old

def update():
    if (default['day'] == "All days"):                        
        a = 0
        b = 6
    elif (default['day'] == "Weekdays"):
        a = 0
        b = 4
    elif (default['day'] == "Saturdays"):
        a = 5
        b = 5
    else:
        a = 6
        b = 6

    plot_travel.title.text = "{} -> {} ({})".format(
        default['start'], default['stop'], default['day']
    )
    
    q = df[(df.start == default['start']) & (df.stop == default['stop']) & (df.day_of_week.between(a,b))]
    grouped = q.groupby([pd.cut(q.decimal_time, bins, labels=x_scale, right=False)])
    
    travel_ninetieth = grouped.travel_time.quantile(0.9)
    wait_ninetieth = grouped.wait_time.quantile(0.9)

    slider_time = default['hour'] + (default['minute'] / 15) / 4.0

    # Updates travel time plots
    plot_travel.y_range.end = travel_ninetieth.max() + 10
    scatter_travel.data_source.data = dict(x=q.decimal_time, y=q.travel_time)
    line_travel.data_source.data = dict(x=x_scale, y=grouped.travel_time.median())
    box_travel.left = slider_time
    box_travel.right = slider_time + 0.25
    
    # Updates wait time plots
    plot_wait.y_range.end = wait_ninetieth.max() + 10
    scatter_wait.data_source.data = dict(x=q.decimal_time, y=q.wait_time)
    line_wait.data_source.data = dict(x=x_scale, y=grouped.wait_time.median())
    box_wait.left = slider_time
    box_wait.right = slider_time + 0.25

    # Updates paragraph text
    time_index = (default['hour'] * 4) + (default['minute'] / 15)

    if np.isnan(grouped.wait_time.median()[time_index]):
        paragraph.text = "At {}:{:02d} there are no 55 Garfield buses leaving from {} going to {}. ".format(
            default['hour'], default['minute'],
            default['start'], default['stop']
        )
    else:
        line1 = "At {}:{:02d} the 55 Garfield bus leaves around every {} minutes from {} going to {}.\n".format(
            default['hour'], default['minute'],
            round(grouped.wait_time.median()[time_index], 1),
            default['start'], default['stop']
        )
        line2 = "The trips take around {} minutes.".format(
            round(grouped.travel_time.median()[time_index], 1)
        )
        paragraph.text = line1 + line2

# Calls update when widget values are changed
widgets = [select_start, select_stop, select_day, slider_hour, slider_minute, button]

select_start.on_change('value', update_start)
select_stop.on_change('value', update_stop)
select_day.on_change('value', update_day)
slider_hour.on_change('value', update_hour)
slider_minute.on_change('value', update_minute)
button.on_click(update)

inputs = widgetbox(widgets)
text_widget = widgetbox(paragraph)
curdoc().add_root(
    column([row([inputs, column([plot_travel, plot_wait])]), row(text_widget)],
    sizing_mode='scale_width')
)
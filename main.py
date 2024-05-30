# Import libraries and modules
import pandas_datareader as pdr
import numpy as np
import pandas as pd
import math
import datetime as dt
import yfinance as yf

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import TextInput, Button, DatePicker, MultiChoice
from bokeh.layouts import column, row

def load_data(symbol, start_date, end_date):
    df = yf.download(symbol, start_date, end_date)
    return df

def plot_data(df, indicator, sync_axis=None):
    gain = df['Close'] > df['Open']
    loss = df['Open'] > df['Close']
    width = 12 * 60 * 60 * 1000  # half day in ms
    
    if sync_axis is not None:
        p = figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", width=1000, x_range=sync_axis)
    else:
        p = figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", width=1000)

    p.xaxis.major_label_orientation = math.pi / 4
    p.grid.grid_line_alpha = 0.25
    
    p.segment(df.index, df['High'], df.index, df['Low'], color="black")
    p.vbar(df.index[gain], width, df['Open'][gain], df['Close'][gain], fill_color="#00ff00", line_color="#00ff00")
    p.vbar(df.index[loss], width, df['Open'][loss], df['Close'][loss], fill_color="#ff0000", line_color="#ff0000")
    
    
    
    for indicator in indicator:
        if indicator == '30 Day SMA':
            df['SMA30'] = df['Close'].rolling(window=30).mean()
            p.line(df.index, df['SMA30'], color='purple', legend_label='30 Day SMA', line_width=2)
        elif indicator == '100 Day SMA':
            df['SMA100'] = df['Close'].rolling(window=30).mean()
            p.line(df.index, df['SMA100'], color='purple', legend_label='100 Day SMA', line_width=2)
        elif indicator == 'Linear Regression':
            par = np.polyfit(range(len(df.index.values)), df['Close'].values, 1, full=True)
            slope = par[0][0]
            intercept = par[0][1]
            y_pred = [slope * i + intercept for i in range(len(df.index.values))]
            p.segment(df.index[0], y_pred[0], df.index[-1], y_pred[-1], color='red', legend_label='Linear Regression', line_width=2)  
            
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"
    return p
    
def on_button_clicked():
    ticker1 = stock1_text.value
    ticker2 = stock2_text.value
    start = date_picker_from.value
    end = date_picker_to.value
    indicators = indicator_choice.value

    df1 = load_data(ticker1, start, end)
    df2 = load_data(ticker2, start, end)
    p1 = plot_data(df1, indicators)
    p2 = plot_data(df2, indicators, sync_axis=p1.x_range)
    curdoc().clear()
    curdoc().add_root(layout)
    curdoc().add_root(row(p1, p2))

stock1_text = TextInput(title="Stock 1")
stock2_text = TextInput(title="Stock 2")
date_picker_from = DatePicker(title="Start Date", value="2020-01-01", min_date="2000-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))
date_picker_to = DatePicker(title="End Date", value="2020-02-01", min_date="2000-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))

indicator_choice = MultiChoice(options=["100 Day SMA", "30 Day SMA", "Linear Regression"])

load_button = Button(label="Load Data", button_type="success")
load_button.on_click(on_button_clicked)

layout = column(stock1_text, stock2_text, date_picker_from, date_picker_to, indicator_choice, load_button)

curdoc().clear()
curdoc().add_root(layout)
#Indicators are not showin
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure
from datetime import datetime

from math import pi

import pandas as pd

from bokeh.plotting import figure, show, output_file

from bokeh.sampledata.stocks import MSFT
from bokeh.document import Document
import json, re
from bokeh.embed import components
from bokeh.models import CrosshairTool, BoxZoomTool, WheelZoomTool, DataRange1d, CustomJS, Span


df = pd.DataFrame(MSFT)[:50]
df["date"] = pd.to_datetime(df["date"])
df["mid"] = (df["open"] + df["close"])/2
df["spans"] = abs(df['open']-df['close'])

#source = ColumnDataSource(df, name='data')

structure = dict(
    date=[], open=[], high=[], low=[], close=[], volume=[],
    color=[], mid=[], spans=[]
)

source = ColumnDataSource(structure, name='ohlc')



#차트 구조 설정
TOOLS = "xpan,reset,save"
p = figure(x_axis_type="datetime", y_axis_location="right",
             tools=TOOLS, plot_width=1000, toolbar_location="left", webgl=True)

p.y_range = DataRange1d()


p.xaxis.major_label_orientation = pi/4
p.x_range.follow = "end"
p.x_range.range_padding = 0


p.grid.grid_line_alpha=0.3
p.min_border_left = 10
p.min_border_top = 10
p.add_tools(CrosshairTool(line_color='green', line_alpha=0.4))
p.add_tools(BoxZoomTool(dimensions=["width"]))
p.add_tools(WheelZoomTool(dimensions=["width"]))




#차트 데이터 모양 설정
width = 12*60*60*1000 # half day in ms
p.segment(x0='date', y0='low',  x1='date', y1='high', color="color", source=source)

#p.segment(x0='date', y0='open',  x1='date', y1='close',line_width=15, color="color", source=source)
p.rect('date', 'mid', width, 'spans', fill_color="color", line_color="color", source=source)
#p.rect(df.date[dec], mids[dec], w, spans[dec], fill_color="#F2583E", line_color="black")



#파일로 저장
script, div = components(p)
docs_json = json.loads(re.search(r'var docs_json = (.*)', script).group(1)[:-1])
render_items = json.loads(re.search(r'var render_items = (.*)', script).group(1)[:-1])
chart_doc = {
    "docs_json" : docs_json,
    "render_items" : render_items
}

with open('./view_source/src/app/chart.component.json', mode='w') as f:
    json.dump(chart_doc, f)

with open('./view_source/src/app/chart.component.html', mode='w') as f:
    f.write(div)

print(div)

#show(p)

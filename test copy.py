import time
from nicegui import ui
import plotly.graph_objects as go
from random import random
import polars as pl

# ui.label('page with custom title')

costs_timeline_df = pl.read_csv('costs_timeline.csv')
input_variables_timeline_df = pl.read_csv('input_variables_timeline.csv')

# ui.graph('my graph', [1, 2, 3, 4, 5])
fig1 = go.Figure()
fig1.update_layout(margin=dict(l=0, r=0, t=0, b=0), yaxis_range = [0, 100])
fig2 = go.Figure()
fig2.update_layout(margin=dict(l=0, r=0, t=0, b=0), yaxis_range = [0, costs_timeline_df['value'].max()], title='Costs')

fig3 = go.Figure()
fig3.update_layout(margin=dict(l=0, r=0, t=0, b=0), yaxis_range = [0, 100])

#make horizontal group that is centered with space in betweem
with ui.row().classes('h-90 w-full justify-center space-x-20'):
    # fill 80% of the width but 20% of the height
    with ui.column().classes('w-3/5 h-95'):
        ui.markdown('##### Inventory Allocations')
        plot1 = ui.plotly(fig1).classes('w-full h-40').style('margin: 0; padding: 0;')
        ui.markdown('##### Reorder Points')
        plot3 = ui.plotly(fig3).classes('w-full h-40')
    with ui.column().classes('w-1/5 h-80, justify-center'):
        ui.markdown('##### Costs')
        plot2 = ui.plotly(fig2).classes('w-full h-full')
class obj:
    def __init__(self):
        self.value = 0
        # self.active = False
times = costs_timeline_df['time'].unique()
def add_trace(e):
    time = times[e.value]
    # remove previous traces
    fig1.data = []
    filtered_df=input_variables_timeline_df.filter((pl.col('time')==time) & (pl.col('variable_type')=='inventory_allocations'))
    fig1.add_trace(go.Bar(
        x=filtered_df['component'], 
        y=filtered_df['value'], 
        marker=dict(color=filtered_df['subcomponent'].str.slice(2,1).cast(pl.Int32))
    ))

    fig2.data = []
    filtered_df=costs_timeline_df.filter(pl.col('time')==time)
    # print(filtered_df)
    fig2.add_trace(go.Bar(
        x=filtered_df['variable_type'], 
        y=filtered_df['value'], 
        marker=dict(color="blue")
    ))

    fig3.data = []
    filtered_df=input_variables_timeline_df.filter((pl.col('time')==time) & (pl.col('variable_type')=='reorder_points'))
    fig3.add_trace(go.Bar(
        x=filtered_df['component'], 
        y=filtered_df['value'], 
        marker=dict(color=filtered_df['subcomponent'].str.slice(2,1).cast(pl.Int32))
    ))


    # fig.range_y = [0, 50_000]
    plot1.update()
    plot2.update()
    plot3.update()



def timer_call(obj1):
    # for i in range(len(times)):
    obj1.value += 1
    # print(slider)
    # print(obj1.value)
    if obj1.value >= len(times):
        obj1.value = 0
        add_trace(obj1)
            # break
    else:
        add_trace(obj1)
            
obj1 = obj()
timer = ui.timer(0.25, lambda: timer_call(obj1), active=False)


slider = ui.slider(min=0, max=len(times)-1, value=0, step=1, on_change=add_trace)
slider.bind_value(obj1, 'value')

add_trace(obj())
def run_slider(e, button):
    # obj1 = obj()
    button.text = 'pause' if not timer.active else 'play'
    if timer.active:
        timer.deactivate()
    else: 
        timer.activate()
    
        
        # time.sleep(0.5)
        # ui.step(1)
    # slider.on_value_change(add_trace)

# slider.on_value_change(add_trace)
with ui.row():
    # ui.label()
    label = ui.label('0')
    label.bind_text_from(obj1, 'value', backward=lambda v: f"Time: {times[v]:.2f}")
    
    button = ui.button('play')
    button.on_click(lambda e: run_slider(e, button))


ui.run(title='My App')

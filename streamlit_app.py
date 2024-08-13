import pandas as pd
import numpy as np
import streamlit as st


import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


bookings = pd.read_parquet('data/processed_bookings.parquet')

plot_data = bookings.copy()
min_report_date = plot_data.report_date.min()
max_report_date = plot_data.report_date.max()
new_max_report_date = max_report_date + pd.DateOffset(months=4)
zmin = plot_data.total_reservations.min()
zmax = plot_data.total_reservations.max()
zmax = 30

    
custom_colorscale = [

    [0, 'white'],         
    [0.2, 'lightblue'],   
    [0.4, 'blue'],        
    [0.6, 'lightgreen'],  
    [0.8, 'yellow'],      
    [1, 'red']            
]


groups = ['RMA', 'RMB', 'RMC', 'RMD', 'RME', 'RMF', 'RMG', 'RMH', 'RMI', 'RMJ', 'RMK', 'RML', 'RMQ', 'RMT', 'RMZ', 'others']
RESERVATION_THRESHOLDS = list(range(5, 31))

# Create the figure
fig = make_subplots(rows=1, cols=1)

# Create traces for each group and the total
traces = []
for group in groups + ['total']:
    trace = go.Scatter(
        x=[],
        y=[],
        mode='markers',
        marker=dict(
            colorscale=custom_colorscale,
            size=8, 
            colorbar=dict(title='Reservations'),
            showscale=True
        ),
        name=group,
        visible=False,
        hovertemplate='Stay Date: %{x}<br>Report Date: %{y}<br>Reservations: %{marker.color}<extra></extra>'
    )
    traces.append(trace)

traces[0].visible = True
# Add traces to the figure
for trace in traces:
    fig.add_trace(trace)

# Make the first trace (RMA) visible by default
traces[0]['visible'] = True

# Create frames for the slider
frames = []
for threshold in RESERVATION_THRESHOLDS:
    frame_data = []
    for group in groups + ['total']:
        if group == 'total':
            plot_data = bookings[bookings['total_reservations'] > threshold]
            x = plot_data['stay_date']
            y = plot_data['report_date']
            color = plot_data['total_reservations']
        else:
            plot_data = bookings[bookings[f'{group}_reservation'] > threshold]
            x = plot_data['stay_date']
            y = plot_data['report_date']
            color = plot_data[f'{group}_reservation']
        
        frame_data.append(go.Scatter(
            x=x, 
            y=y, 
            marker=dict(color=color, colorscale=custom_colorscale),
            hovertemplate='Stay Date: %{x}<br>Report Date: %{y}<br>Reservations: %{marker.color}<extra></extra>'
        ))
    
    frames.append(go.Frame(data=frame_data, name=str(threshold)))

fig.frames = frames

# Create buttons for group selection
buttons = []
for i, group in enumerate(groups + ['total']):
    button = dict(
        label=group,
        method="update",
        args=[{"visible": [i == j for j in range(len(groups) + 1)]},
              {"title": f"{group} Reservations"}],
    )
    buttons.append(button)

# Update layout
fig.update_layout(
    title="Reservation Analysis",
    title_x=0.45,
    title_y=0.95,
    updatemenus=[{
        'type': 'dropdown',
        'x': 0.85,
        'y': 1.1,
        'buttons': buttons
    }],
    sliders=[{
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'Threshold: ',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': [
            {
                'args': [[f.name], {
                    'frame': {'duration': 300, 'redraw': True},
                    'mode': 'immediate',
                    'transition': {'duration': 300}
                }],
                'label': str(k+5),
                'method': 'animate'
            } for k, f in enumerate(fig.frames)
        ]
    }]
)

# Set x and y axis ranges
all_dates = pd.concat([bookings['stay_date'], bookings['report_date']])
min_date = all_dates.min()
max_date = all_dates.max()

fig.update_xaxes(title_text="Stay Date", range=[min_date, max_date])
fig.update_yaxes(title_text="Report Date", range=[min_date, max_date])

initial_data = fig.frames[0].data
for i, trace in enumerate(fig.data):
    trace.x = initial_data[i].x
    trace.y = initial_data[i].y
    trace.marker.color = initial_data[i].marker.color

st.write("Reservation Analysis by Thresholding ")
# Show figure
st.plotly_chart(fig)



RESERVATION_THRESHOLDS = list(range(5, 31))

max_y_values = []
for threshold in RESERVATION_THRESHOLDS:
    counts = []
    for group in groups:
        count = (bookings[f'{group}_reservation'] > threshold).sum()
        counts.append(count)
    max_y_values.append(max(counts))

# Create the figure
fig = go.Figure()

initial_counts = []
for group in groups:
    count = (bookings[f'{group}_reservation'] > RESERVATION_THRESHOLDS[0]).sum()
    initial_counts.append(count)

# Create initial empty bar trace
fig.add_trace(go.Bar(x=groups, y=initial_counts, name='Reservations'))

# Create frames for the slider
frames = []
for threshold, max_y in zip(RESERVATION_THRESHOLDS, max_y_values):
    counts = []
    for group in groups:
        count = (bookings[f'{group}_reservation'] > threshold).sum()
        counts.append(count)
    
    frame = go.Frame(
        data=[go.Bar(x=groups, y=counts, name='Reservations')],
        name=str(threshold),
        layout=go.Layout(yaxis_range=[0, max_y * 1.1])
    )
    frames.append(frame)

fig.frames = frames

# Update layout
fig.update_layout(
    title="Reservation Counts by Group",
    title_x=0.5,
    xaxis_title="Group",
    yaxis_title="Number of Spike Instances",
    updatemenus=[{
        'type': 'buttons',
        'showactive': False,
        'y': 1.15,
        'x': 1.3,
        'xanchor': 'right',
        'yanchor': 'top',
        'buttons': [{
            'label': 'Play',
            'method': 'animate',
            'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}]
        }, {
            'label': 'Pause',
            'method': 'animate',
            'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}]
        }]
    }],
    sliders=[{
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'Threshold: ',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': [
            {
                'args': [[f.name], {
                    'frame': {'duration': 300, 'redraw': True},
                    'mode': 'immediate',
                    'transition': {'duration': 300}
                }],
                'label': str(k+5),
                'method': 'animate'
            } for k, f in enumerate(fig.frames)
        ]
    }]
)

st.write("Reservation Counts by Group ")
# Show figure
st.plotly_chart(fig)
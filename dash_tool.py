import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np

raw_datas = []

for ii in range(4):
    raw_data = []
    for i in range(6):
        raw_data.append({})

        k = 1000#np.random.randint(10, 20, 1)[0]
        raw_data[i]['event_T'] = []
        raw_data[i]['event_B'] = []
        for jj in range(k):
            n = np.random.randint(100, 160, 1)[0]
            # raw_data[i]['event_T'].append(np.random.randint(0, 4, n).tolist())
            raw_data[i]['event_T'].append(np.random.choice(4, n, p=[0.4, 0.4, 0.1, 0.1]).tolist())
        for jj in range(k):
            n = np.random.randint(100, 160, 1)[0]
            # raw_data[i]['event_B'].append(np.random.randint(0, 4, n).tolist())
            raw_data[i]['event_B'].append(np.random.choice(4, n, p=[0.4, 0.4, 0.1, 0.1]).tolist())


    raw_datas.append(raw_data)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='item_select',
        options=[
            {'label': 'A', 'value': 0},
            {'label': 'B', 'value': 1},
            {'label': 'C', 'value': 2},
            {'label': 'D', 'value': 3},
        ],
        value=0
    ),
    dcc.RadioItems(
        id='dayoff_select',
        options=[
            {'label': '0', 'value': 0},
            {'label': '1', 'value': 1},
            {'label': '2', 'value': 2},
            {'label': '3', 'value': 3},
            {'label': '4', 'value': 4},
            {'label': '5', 'value': 5},
        ],
        value=0
    ),

    dcc.RadioItems(
        id='tb_select',
        options=[
            {'label': 'T', 'value': 'T'},
            {'label': 'B', 'value': 'B'},
        ],
        value='T'
    ),

    html.Div(id='rs',
        children=[
        dcc.RangeSlider(
            id='range_slider',
            # count=1,
            marks={i / 10: '{}'.format(i/10) for i in range(0, 10)},
            min=0,
            max=1,
            step=0.1,
            value=[0, 0.5]
        ),
        html.Div(id='output-container-range-slider-non-linear', style={'margin-top': 20}),
    ]),

    # html.Div(id='dd_item'),
    html.Div(id='heatmap_div',
        children=dcc.Graph(
            id='heatmap',
            figure={
                'data': [{
                    'z': [
                        [1, 2, 3],
                        [4, 5, 6]
                    ],
                    'text': [
                        ['a', 'b', 'c'],
                        ['d', 'e', 'f']
                    ],
                    'customdata': [
                        ['c-a', 'c-b', 'c-c'],
                        ['c-d', 'c-e', 'c-f'],
                    ],
                    'type': 'heatmap',
                }],
            },
            # marker ={
            #     'cmin': 1,
            #     'cmax': 4,
            # },
        ),
    ),
])



def heatmap_draw(index, day_off, tb, clip_range):
    global raw_datas
    raw_data = raw_datas[index]
    max_ = 0
    if tb == 'T':
        TB = 'event_T'
    else:
        TB = 'event_B'
    for i in range(len(raw_data[day_off][TB])):
        if max_ < len(raw_data[day_off][TB][i]):
            max_ = len(raw_data[day_off][TB][i])
    # print(max_, np.mean(std_data))
    hist = np.zeros((4, max_))
    for i in range(len(raw_data[day_off][TB])):
        for j in range(len(raw_data[day_off][TB][i])):
            hist[raw_data[day_off][TB][i][j], j] += 1
    seq_size = 3
    std_data = np.zeros((4, int(max_ / seq_size)))
    for i in range(int(max_ / seq_size)):
        std_data[:, i] = np.std(hist[:, i * seq_size:(i + 1) * seq_size] / np.sum(hist[:, i * seq_size:(i + 1) * seq_size], axis=0), axis=1)
    event = ['a', 'b', 'c', 'd']
    return [dcc.Graph(
            id='heatmap',
            figure={
                'data': [{
                    'z': np.clip(std_data, clip_range[0], clip_range[1]),
                    'type': 'heatmap',
                }],
                'layout':{
                    'yaxis':dict(tickvals=np.arange(len(event)), ticktext=event, title='event'),
                    'xaxis':dict(title='pitch / 3(seq)'),
                }
            },
        ),
        dcc.Graph(
            id='plot',
            figure={
                'data': [{
                    'x': np.arange(np.sum(np.array(hist), axis=0).shape[0]),
                    'y': np.sum(np.array(hist), axis=0),
                    'type': 'plot',
                }],
                'layout': {
                    'yaxis': dict(title='Game Count'),
                    'xaxis': dict(title='pitch count'),
                }
            },
        ),
        ]

@app.callback(
    dash.dependencies.Output('heatmap_div', 'children'),
    [dash.dependencies.Input('item_select', 'value'),
     dash.dependencies.Input('dayoff_select', 'value'),
     dash.dependencies.Input('tb_select', 'value'),
     dash.dependencies.Input('range_slider', 'value')])
def update_output(index, day_off, tb, clip_range):
    print(index, day_off, tb, clip_range)
    return heatmap_draw(index, day_off, tb, clip_range)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=6004)
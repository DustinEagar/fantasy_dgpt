from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
from utils.analysis_utils import (
    plot_player_histogram,
    player_historic_linechart,
    player_scoring_linechart,
    plot_scatterplot,
    player_summary
)

# Initialize the Dash app
app = Dash(__name__)

# Load the data
df = pd.read_csv('data/players_crawled_25_updated2.csv')
player_list = sorted(df['Player'].unique())

# Define the app layout
app.layout = html.Div([
    html.H1("Disc Golf Player Analysis Dashboard"),
    
    # Player selection dropdown
    html.Div([
        html.Label("Select Player:"),
        dcc.Dropdown(
            id='player-dropdown',
            options=[{'label': player, 'value': player} for player in player_list],
            value=player_list[0]
        )
    ], style={'width': '50%', 'margin': '20px'}),
    
    # Player summary section
    html.Div([
        html.H3("Player Summary"),
        html.Div(id='player-summary-stats')
    ]),
    
    # Graphs section
    html.Div([
        html.H3("Player Performance Visualizations"),
        
        # Historic tournament performance
        html.Div([
            html.H4("Tournament History"),
            dcc.Graph(id='historic-performance')
        ]),
        
        # Fantasy scoring history
        html.Div([
            html.H4("Fantasy Scoring History"),
            dcc.Graph(id='fantasy-scoring')
        ]),
        
        # Rating distribution
        html.Div([
            html.H4("Rating Distribution"),
            dcc.Graph(id='rating-distribution')
        ])
    ])
])

@callback(
    Output('player-summary-stats', 'children'),
    Output('historic-performance', 'figure'),
    Output('fantasy-scoring', 'figure'),
    Output('rating-distribution', 'figure'),
    Input('player-dropdown', 'value')
)
def update_player_analysis(selected_player):
    # Generate player summary
    rating_summary = player_summary(df, 'composite_rating', selected_player)
    
    summary_div = html.Div([
        html.P([
            f"Composite Rating: {rating_summary['value']:.1f}",
            html.Br(),
            f"Rank: {rating_summary['rank']}",
            html.Br(),
            f"Percentile: {rating_summary['percentile']}",
            html.Br(),
            f"Percent of Max: {rating_summary['pct_of_max']}%"
        ])
    ])
    
    # Generate visualizations
    historic_fig = player_historic_linechart(df, selected_player)
    scoring_fig = player_scoring_linechart(df, selected_player)
    rating_fig = plot_player_histogram(df, 'composite_rating', selected_player)
    
    return summary_div, historic_fig, scoring_fig, rating_fig

if __name__ == '__main__':
    app.run(debug=True)

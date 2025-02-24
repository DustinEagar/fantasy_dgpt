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
    
    # Player summary sections
    html.Div([
        html.H3("Player Summary"),
        html.Div(id='player-summary-stats'),
        
        html.H3("Scoring Summary"),
        html.Div(id='scoring-summary-stats')
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
        ]),
        
        # Points vs Rating scatter plot
        html.Div([
            html.H4("Fantasy Points vs Rating"),
            dcc.Graph(id='points-rating-scatter')
        ])
    ])
])

@callback(
    Output('player-summary-stats', 'children'),
    Output('historic-performance', 'figure'),
    Output('fantasy-scoring', 'figure'),
    Output('rating-distribution', 'figure'),
    Output('scoring-summary-stats', 'children'),
    Output('points-rating-scatter', 'figure'),
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
    
    # Generate scoring summary
    scoring_summary = player_summary(df, 'fantasy_points_24', selected_player)
    
    scoring_div = html.Div([
        html.P([
            f"2024 Fantasy Points: {scoring_summary['value']:.1f}",
            html.Br(),
            f"Rank: {scoring_summary['rank']}",
            html.Br(),
            f"Percentile: {scoring_summary['percentile']}",
            html.Br(),
            f"Percent of Max: {scoring_summary['pct_of_max']}%"
        ])
    ])
    
    # Generate scatter plot
    scatter_fig = plot_scatterplot(
        df, 
        col_x='fantasy_points_24', 
        col_y='composite_rating',
        player_name=selected_player
    )
    
    return summary_div, historic_fig, scoring_fig, rating_fig, scoring_div, scatter_fig

if __name__ == '__main__':
    app.run(debug=True)

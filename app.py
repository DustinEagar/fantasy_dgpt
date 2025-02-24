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

# Define styles
COLORS = {
    'background': '#f8f9fa',
    'text': '#212529',
    'primary': '#0d6efd',
    'secondary': '#6c757d',
    'border': '#dee2e6'
}

CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '8px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'padding': '20px',
    'marginBottom': '20px'
}

HEADER_STYLE = {
    'color': COLORS['text'],
    'padding': '20px 0',
    'marginBottom': '20px',
    'borderBottom': f'1px solid {COLORS["border"]}'
}

CONTAINER_STYLE = {
    'maxWidth': '1200px',
    'margin': '0 auto',
    'padding': '20px'
}

# Load the data
df = pd.read_csv('data/players_crawled_25_updated2.csv')
player_list = sorted(df['Player'].unique())

# Define the app layout
app.layout = html.Div([
    # Main container
    html.Div([
        # Header
        html.H1("Disc Golf Player Analysis Dashboard", style=HEADER_STYLE),
        
        # Player selection dropdown
        html.Div([
            html.Label("Select Player:", style={'marginBottom': '8px', 'display': 'block'}),
            dcc.Dropdown(
                id='player-dropdown',
                options=[{'label': player, 'value': player} for player in player_list],
                value=player_list[0],
                style={'borderRadius': '4px'}
            )
        ], style={'width': '50%', 'marginBottom': '30px'}),
        
        # Summary cards row
        html.Div([
            # Player Summary Card
            html.Div([
                html.H3("Player Summary", style={'marginTop': '0'}),
                html.Div(id='player-summary-stats')
            ], style={**CARD_STYLE, 'flex': '1', 'marginRight': '20px'}),
            
            # Scoring Summary Card
            html.Div([
                html.H3("Scoring Summary", style={'marginTop': '0'}),
                html.Div(id='scoring-summary-stats')
            ], style={**CARD_STYLE, 'flex': '1'})
        ], style={'display': 'flex', 'marginBottom': '30px'}),
        
        # Graphs section
        html.Div([
            html.H3("Player Performance Visualizations", 
                   style={'marginBottom': '20px', 'color': COLORS['text']}),
            
            # Graphs stack
            html.Div([
                # Historic tournament performance
                html.Div([
                    html.H4("Tournament History", style={'marginTop': '0'}),
                    dcc.Graph(id='historic-performance')
                ], style=CARD_STYLE),
                
                # Fantasy scoring history
                html.Div([
                    html.H4("Fantasy Scoring History", style={'marginTop': '0'}),
                    dcc.Graph(id='fantasy-scoring')
                ], style=CARD_STYLE),
                
                # Rating distribution
                html.Div([
                    html.H4("Rating Distribution", style={'marginTop': '0'}),
                    dcc.Graph(id='rating-distribution')
                ], style=CARD_STYLE),
                
                # Points vs Rating scatter plot
                html.Div([
                    html.H4("Fantasy Points vs Rating", style={'marginTop': '0'}),
                    dcc.Graph(id='points-rating-scatter')
                ], style=CARD_STYLE)
            ])
        ])
    ], style=CONTAINER_STYLE)
], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'})

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
    rating_fig = plot_player_histogram(df, 'composite_rating', selected_player, nbins=45)
    
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
        player_name=selected_player,
        x_reference=50
    )
    
    return summary_div, historic_fig, scoring_fig, rating_fig, scoring_div, scatter_fig

if __name__ == '__main__':
    app.run(debug=True)

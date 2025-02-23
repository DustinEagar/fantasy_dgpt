import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def player_historic_linechart(stats_data, player_name=None):
    """
    Create an interactive line chart showing a player's historical tournament performance.
    
    Args:
        stats_data: Dictionary or JSON string containing tournament stats
        player_name: Optional player name for chart title
        
    Returns:
        Plotly Figure object with the line chart
    """
    # Parse stats data if it's a string
    if isinstance(stats_data, str):
        stats_data = json.loads(stats_data)
    
    # Convert to DataFrame, handling both list and direct dict formats
    try:
        df = pd.DataFrame(stats_data[0])
    except:
        df = pd.DataFrame(stats_data)
        
    # Convert dates and sort chronologically
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Convert places to numeric, handling 'DNF' etc
    df['Place_Numeric'] = pd.to_numeric(df['Place'], errors='coerce')
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add place line (inverted)
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=-df['Place_Numeric'],
            name="Place",
            line=dict(color='blue'),
            hovertemplate="Date: %{x}<br>Place: %{customdata}<extra></extra>",
            customdata=df['Place_Numeric']
        ),
        secondary_y=False
    )
    
    # Add tier markers
    for tier in df['Tier'].unique():
        mask = df['Tier'] == tier
        fig.add_trace(
            go.Scatter(
                x=df[mask]['Date'],
                y=-df[mask]['Place_Numeric'],
                name=f"Tier {tier}",
                mode='markers',
                marker=dict(size=8),
                hovertemplate=(
                    "Date: %{x}<br>" +
                    "Place: %{customdata}<br>" +
                    "Tournament: %{text}<extra></extra>"
                ),
                text=df[mask]['Tournament'],
                customdata=df[mask]['Place_Numeric']
            ),
            secondary_y=False
        )
    
    # Update layout
    title = f"Tournament History - {player_name}" if player_name else "Tournament History"
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Place (inverted)",
        hovermode='x unified',
        showlegend=True
    )
    
    # Invert y-axis so better places are higher
    fig.update_yaxes(autorange="reversed", secondary_y=False)
    
    return fig

import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def player_historic_linechart(df, player_name):
    """
    Create an interactive line chart showing a player's historical tournament performance.
    
    Args:
        df: DataFrame containing player data
        player_name: Player name to filter and use in chart title
        
    Returns:
        Plotly Figure object with the line chart
    """
    # Get player's stats data
    player_row = df[df['Player'] == player_name].iloc[0]
    stats_data = player_row['stats_data']
    
    # Handle JSON decoding
    if isinstance(stats_data, str):
        try:
            # Clean and normalize JSON string
            stats_data = (stats_data.replace("'", '"')
                         .replace('True', 'true')
                         .replace('False', 'false')
                         .replace('None', 'null')
                         .replace('},]', '}]')  # Fix trailing commas
                         .replace(',}', '}')
                         .strip())
            
            # Fix problematic quotes in tournament names
            while '"s ' in stats_data:  # Handle cases like Discraft"s
                stats_data = stats_data.replace('"s ', "'s ")
            stats_data = stats_data.replace('""', '"')  # Fix any double quotes
            
            try:
                stats_data = json.loads(stats_data)
            except json.JSONDecodeError as e:
                # If error, try to show the problematic section
                error_pos = e.pos
                context = stats_data[max(0, error_pos-50):min(len(stats_data), error_pos+50)]
                print(f"Error decoding JSON near position {error_pos}:")
                print(f"Context: ...{context}...")
                print(f"Full error: {e}")
                return None
                
        except Exception as e:
            print(f"Error preprocessing JSON string: {e}")
            return None
            
    # Convert stats to DataFrame
    try:
        if isinstance(stats_data, list):
            stats_df = pd.DataFrame(stats_data[0])
        else:
            stats_df = pd.DataFrame(stats_data)
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        return None
        
    # Convert dates and sort chronologically
    stats_df['Date'] = pd.to_datetime(stats_df['Date'])
    stats_df = stats_df.sort_values('Date')
    
    # Convert places to numeric, handling 'DNF' etc
    stats_df['Place_Numeric'] = pd.to_numeric(stats_df['Place'], errors='coerce')
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add place line (inverted)
    fig.add_trace(
        go.Scatter(
            x=stats_df['Date'],
            y=-stats_df['Place_Numeric'],
            name="Place",
            line=dict(color='blue'),
            hovertemplate="Date: %{x}<br>Place: %{customdata}<extra></extra>",
            customdata=stats_df['Place_Numeric']
        ),
        secondary_y=False
    )
    
    # Add tier markers
    for tier in stats_df['Tier'].unique():
        mask = stats_df['Tier'] == tier
        fig.add_trace(
            go.Scatter(
                x=stats_df[mask]['Date'],
                y=-stats_df[mask]['Place_Numeric'],
                name=f"Tier {tier}",
                mode='markers',
                marker=dict(size=8),
                hovertemplate=(
                    "Date: %{x}<br>" +
                    "Place: %{customdata}<br>" +
                    "Tournament: %{text}<extra></extra>"
                ),
                text=stats_df[mask]['Tournament'],
                customdata=stats_df[mask]['Place_Numeric']
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

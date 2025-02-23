import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime

def ratings_composite(df: pd.DataFrame, player_name: str, decay_rate=0.1, ref_date=None):
    """
    Calculate a composite rating from a player's ratings history using exponential time decay.
    
    Args:
        df: DataFrame containing player data
        player_name: Name of the player to analyze
        decay_rate: Controls how quickly older ratings decay (higher = faster decay)
        ref_date: Reference date for calculating time differences (defaults to most recent tournament)
        
    Returns:
        float: Composite rating weighted by recency
    """
    # Get player's ratings data
    player_row = df[df['Player'] == player_name].iloc[0]
    ratings_data = player_row['ratings_data']
    
    # Handle JSON decoding
    if isinstance(ratings_data, str):
        import json
        try:
            # First try to safely evaluate as a Python literal
            import ast
            try:
                python_obj = ast.literal_eval(ratings_data)
                ratings_data = json.dumps(python_obj)
            except:
                # If literal_eval fails, fall back to manual cleaning
                ratings_data = ratings_data.replace('\\"', '"').replace("\\'", "'")
                ratings_data = ratings_data.replace("'", '"')
                ratings_data = re.sub(r'"([^"]+)"s\s', r'"\1\'s ', ratings_data)
                
                # Fix standard JSON values
                ratings_data = (ratings_data.replace('True', 'true')
                             .replace('False', 'false')
                             .replace('None', 'null')
                             .replace('},]', '}]')
                             .replace(',}', '}')
                             .strip())
            
            ratings_data = json.loads(ratings_data)
        except Exception as e:
            print(f"Error processing ratings data for {player_name}: {e}")
            return None
            
    if isinstance(ratings_data, list):
        ratings_data = ratings_data[0]
        
    # Create DataFrame
    df = pd.DataFrame({
        'Rating': ratings_data['Rating'],
        'Date': ratings_data['Date'],
        'Tier': ratings_data['Tier']
    })
    
    # Convert types
    df['Rating'] = pd.to_numeric(df['Rating'])
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter for relevant tiers
    valid_tiers = ['A', 'ES', 'M', 'XM']
    df = df[df['Tier'].isin(valid_tiers)]
    
    if len(df) == 0:
        return None
        
    # Sort by date
    df = df.sort_values('Date')
    
    # Use most recent date if ref_date not provided
    if ref_date is None:
        ref_date = df['Date'].max()
    elif isinstance(ref_date, str):
        ref_date = pd.to_datetime(ref_date)
    
    # Calculate time differences in years
    df['years_ago'] = (ref_date - df['Date']).dt.total_seconds() / (365.25 * 24 * 60 * 60)
    
    # Calculate weights with exponential decay
    df['weight'] = np.exp(-decay_rate * df['years_ago'])
    
    # Zero out weights for tournaments more than 3 years old
    df.loc[df['years_ago'] > 3, 'weight'] = 0
    
    # Calculate weighted average
    if df['weight'].sum() > 0:
        composite_rating = (df['Rating'] * df['weight']).sum() / df['weight'].sum()
        return round(composite_rating, 1)
    else:
        return None

def plot_histogram(df: pd.DataFrame, column: str, annotate_top_n: dict = None, nbins: int = None):
    """
    Plots a histogram for the given column using Plotly Express.
    
    Optionally, annotates the top n rows (sorted by `column` in descending order)
    for each annotation column specified in annotate_top_n.
    
    Parameters:
      df (pd.DataFrame): The data.
      column (str): The column to plot in the histogram.
      annotate_top_n (dict, optional): Dictionary of {annotation_column: n}.
          For each key, the top n rows (sorted by `column`) will be annotated with 
          the string value from that annotation column.
      nbins (int, optional): Number of bins to use in the histogram.
    """
    # Check if the main column exists in the DataFrame
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in the DataFrame.")
    
    # Create the histogram using Plotly Express with the specified number of bins
    fig = px.histogram(df, x=column, nbins=nbins, title=f"Histogram of {column}")
    
    # If annotation instructions are provided, add them
    if annotate_top_n:
        # Ensure each annotation column exists
        for ann_col in annotate_top_n.keys():
            if ann_col not in df.columns:
                raise ValueError(f"Annotation column '{ann_col}' not found in DataFrame.")
        
        # Determine a baseline y-position for annotations.
        # Here we take the maximum bar height from the histogram data.
        if fig.data and fig.data[0].y:
            max_y = max(fig.data[0].y)
        else:
            max_y = 0
        
        # A small offset to position annotations above the highest bar
        offset = max_y * 0.05 if max_y > 0 else 1
        
        # For each annotation column, select the top n rows (sorted by the main column)
        for ann_col, n in annotate_top_n.items():
            top_rows = df.sort_values(by=column, ascending=False).head(n)
            annotation_y_counter = 0
            for _, row in top_rows.iterrows():
                # Add an annotation at the x value from the row and above the histogram
                fig.add_annotation(
                    x=row[column],
                    y=max_y + annotation_y_counter*offset,
                    text=str(row[ann_col]),
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-20  # Adjust arrow length as needed
                )
                annotation_y_counter+=1
    
    fig.show()
    
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
            import re
            import ast
            
            # First try to safely evaluate as a Python literal
            try:
                # Convert string to Python object
                python_obj = ast.literal_eval(stats_data)
                # Convert Python object to proper JSON
                stats_data = json.dumps(python_obj)
            except:
                # If literal_eval fails, fall back to manual cleaning
                stats_data = stats_data.replace('\\"', '"').replace("\\'", "'")
                stats_data = stats_data.replace("'", '"')
                stats_data = re.sub(r'"([^"]+)"s\s', r'"\1\'s ', stats_data)
                
                # Fix standard JSON values
                stats_data = (stats_data.replace('True', 'true')
                             .replace('False', 'false')
                             .replace('None', 'null')
                             .replace('},]', '}]')
                             .replace(',}', '}')
                             .strip())
            
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
    
    # Add place line
    fig.add_trace(
        go.Scatter(
            x=stats_df['Date'],
            y=stats_df['Place_Numeric'],
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
                y=stats_df[mask]['Place_Numeric'],
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
        yaxis_title="Place",
        hovermode='x unified',
        showlegend=True
    )
    
    # Configure y-axis to show better places (1st) at the top
    fig.update_yaxes(
        autorange="reversed",
        rangemode="tozero",
        secondary_y=False
    )
    
    return fig

def player_summary(df: pd.DataFrame, column: str, player_name: str):
    """
    Get summary statistics for a player's value in the given column.
    
    Parameters:
      df (pd.DataFrame): The data.
      column (str): The column to analyze.
      player_name (str): Name of the player to summarize.
      
    Returns:
      dict: Dictionary containing player's value, percentile, and percent of max
    """
    # Check if the main column exists in the DataFrame
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in the DataFrame.")
        
    # Get player's value
    player_row = df[df['Player'] == player_name]
    if len(player_row) == 0:
        raise ValueError(f"Player '{player_name}' not found in DataFrame.")
    
    player_value = player_row[column].iloc[0]
    
    # Calculate player's percentile
    percentile = np.round(stats.percentileofscore(df[column], player_value), 1)
    
    # Calculate fraction of max
    max_value = df[column].max()
    frac_of_max = np.round(player_value / max_value * 100, 1)
    
    # Calculate rank (1-based)
    rank = (df[column] > player_value).sum() + 1
    total = len(df)
    
    return {
        'value': player_value,
        'percentile': percentile,
        'pct_of_max': frac_of_max,
        'rank': f"{rank}/{total}"
    }

def plot_player_histogram(df: pd.DataFrame, column: str, player_name: str, nbins: int = None):
    """
    Plots a histogram for the given column and annotates the specified player's value.
    
    Parameters:
      df (pd.DataFrame): The data.
      column (str): The column to plot in the histogram.
      player_name (str): Name of the player to annotate.
      nbins (int, optional): Number of bins to use in the histogram.
    """
    # Check if the main column exists in the DataFrame
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in the DataFrame.")
        
    # Get player's value
    player_row = df[df['Player'] == player_name]
    if len(player_row) == 0:
        raise ValueError(f"Player '{player_name}' not found in DataFrame.")
    
    player_value = player_row[column].iloc[0]
    
    # Get player summary stats
    summary = player_summary(df, column, player_name)
    
    # Create the histogram
    fig = px.histogram(df, x=column, nbins=nbins, title=f"Histogram of {column}")
    
    # Determine annotation y-position
    if fig.data and fig.data[0].y:
        max_y = max(fig.data[0].y)
    else:
        max_y = 0
    
    # Add player annotation
    fig.add_annotation(
        x=player_value,
        y=max_y * 1.5,
        text=(f"{player_name}<br>" +
              f"Value: {summary['value']:.1f}<br>" +
              f"Rank: {summary['rank']}<br>" +
              f"Percentile: {summary['percentile']}<br>" +
              f"% of Max: {summary['pct_of_max']}%"),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40
    )
    
    fig.show()
    return fig

import ast
import re

def plot_scatterplot(df: pd.DataFrame, col_x: str, col_y: str, color_col: str = None):
    """
    Create an interactive scatter plot comparing two columns, with optional coloring.
    
    Args:
        df: DataFrame containing player data
        col_x: Column name for x-axis
        col_y: Column name for y-axis
        color_col: Optional column name for point colors
        
    Returns:
        Plotly Figure object with the scatter plot
    """
    # Validate columns exist
    for col in [col_x, col_y]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame")
    if color_col and color_col not in df.columns:
        raise ValueError(f"Color column '{color_col}' not found in DataFrame")
            
    # Create hover text
    hover_data = {'Player': True}
    for col in [col_x, col_y]:
        hover_data[col] = ':.2f'
    if color_col:
        hover_data[color_col] = ':.2f'
        
    # Create scatter plot
    fig = px.scatter(
        df,
        x=col_x,
        y=col_y,
        color=color_col,
        hover_data=hover_data,
        title=f"{col_y} vs {col_x}",
        labels={
            col_x: col_x.replace('_', ' ').title(),
            col_y: col_y.replace('_', ' ').title(),
            color_col: color_col.replace('_', ' ').title() if color_col else None
        }
    )
    
    return fig

def player_scoring_linechart(df, player_name, points_map_file='data/points_map_2025.json'):
    """
    Create an interactive line chart showing a player's fantasy points per tournament.
    
    Args:
        df: DataFrame containing player data
        player_name: Player name to filter and use in chart title
        points_map_file: Path to JSON file containing points mapping
        
    Returns:
        Plotly Figure object with the line chart
    """
    # Get player's stats data
    player_row = df[df['Player'] == player_name].iloc[0]
    stats_data = player_row['stats_data']
    
    # Load points mapping
    with open(points_map_file) as f:
        points_map = json.load(f)
    
    # Handle JSON decoding
    if isinstance(stats_data, str):
        try:
            # First try to safely evaluate as a Python literal
            try:
                python_obj = ast.literal_eval(stats_data)
                stats_data = json.dumps(python_obj)
            except:
                # If literal_eval fails, fall back to manual cleaning
                stats_data = stats_data.replace('\\"', '"').replace("\\'", "'")
                stats_data = stats_data.replace("'", '"')
                stats_data = re.sub(r'"([^"]+)"s\s', r'"\1\'s ', stats_data)
                stats_data = (stats_data.replace('True', 'true')
                             .replace('False', 'false')
                             .replace('None', 'null')
                             .replace('},]', '}]')
                             .replace(',}', '}')
                             .strip())
            
            stats_data = json.loads(stats_data)
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
    
    # Calculate fantasy points for each tournament
    stats_df['Points'] = stats_df.apply(
        lambda row: points_map.get(row['Place'], 0) * (1.5 if row['Tier'] in ['M', 'XM'] else 1.0)
        if row['Tier'] in ['M', 'ES', 'XM'] else 0,
        axis=1
    )
    
    # Create figure
    fig = go.Figure()
    
    # Add points line
    fig.add_trace(
        go.Scatter(
            x=stats_df['Date'],
            y=stats_df['Points'],
            name="Fantasy Points",
            line=dict(color='blue'),
            hovertemplate=(
                "%{customdata[2]}<br>" +
                "Date: %{x}<br>" +
                "Points: %{customdata[0]:.1f}<br>" +
                "Place: %{customdata[1]}<extra></extra>"
            ),
            customdata=list(zip(
                stats_df['Points'].round(1),
                stats_df['Place'],
                stats_df['Tournament']
            ))
        )
    )
    
    # Add tier markers
    for tier in stats_df['Tier'].unique():
        if tier in ['M', 'ES', 'XM']:  # Only show scoring events
            mask = stats_df['Tier'] == tier
            fig.add_trace(
                go.Scatter(
                    x=stats_df[mask]['Date'],
                    y=stats_df[mask]['Points'],
                    name=f"Tier {tier}",
                    mode='markers',
                    marker=dict(size=8),
                    hovertemplate=(
                        "%{customdata[2]}<br>" +
                        "Date: %{x}<br>" +
                        "Points: %{customdata[0]:.1f}<br>" +
                        "Place: %{customdata[1]}<extra></extra>"
                    ),
                    customdata=list(zip(
                        stats_df[mask]['Points'].round(1),
                        stats_df[mask]['Place'],
                        stats_df[mask]['Tournament']
                    ))
                )
            )
    
    # Update layout
    title = f"Fantasy Points History - {player_name}" if player_name else "Fantasy Points History"
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Fantasy Points",
        hovermode='closest',
        showlegend=True
    )
    
    return fig

import pandas as pd
import numpy as np
from scipy import stats

def extract_numbers(s):
    """Extract numbers from strings containing formatted text with numbers."""
    import re
    pattern = r'.*[:$#]\s?((\d{1,5}(?:,\d{3})*|\d+)(\.\d+)?)'
    matches = re.findall(pattern, s)
    if matches:
        return [match[0] for match in matches][0]
    return None

def extract_ratings_vec(input_data, tiers=None, cutoff_date=None):
    """
    Extract filtered vector of round ratings from player's rating history.
    
    Args:
        input_data: Dictionary of ratings scraped from ratings details
        tiers: List of tournament tier strings to include
        cutoff_date: String date 'yyyy-mm-dd' to filter ratings after
    
    Returns:
        numpy array of ratings values
    """
    df = pd.DataFrame(input_data)
    df['Date'] = pd.to_datetime(df['Date']) if isinstance(df['Date'].iloc[0], str) else df['Date']
    
    if cutoff_date:
        cutoff = pd.Timestamp(cutoff_date)
        df = df[df['Date'] > cutoff]

    if tiers:
        df = df[df['Tier'].isin(tiers)]
        
    return df['Rating'].values

import json

def calculate_fantasy_points(stats_data, points_map, year):
    """
    Calculate fantasy points for a player's tournament results.
    
    Args:
        stats_data: Dictionary of tournament stats
        points_map: Dictionary mapping places to point values
        year: Year to calculate points for
        
    Returns:
        Total fantasy points
    """
    if isinstance(stats_data, str):
        stats_data = json.loads(stats_data)
        
    df = pd.DataFrame(stats_data)
    df = df[df['Tier'].isin(['M', 'ES', 'XM'])]
    df = df[df['Date'].dt.year == year]

    df['event_points'] = df['Place'].astype(int).map(points_map)
    df.loc[df['Tier'].isin(['M', 'XM']), 'event_points'] *= 1.5

    return df['event_points'].sum()

def calculate_composite_scores(df, year1_weight=0.65, year2_weight=0.35):
    """
    Calculate composite fantasy scores and percentiles.
    
    Args:
        df: DataFrame with fantasy_points columns
        year1_weight: Weight for most recent year
        year2_weight: Weight for previous year
        
    Returns:
        DataFrame with added composite columns
    """
    df['composite_fp'] = (
        year1_weight * df['fantasy_points_23'] + 
        year2_weight * df['fantasy_points_22']
    )
    
    df['composite_percentile'] = df['composite_fp'].apply(
        lambda x: np.round(stats.percentileofscore(df['composite_fp'], x), 1)
    )
    
    df['frac_calvin'] = df['composite_fp'] / 3464
    
    return df

import pandas as pd
from tqdm import tqdm
import time
import argparse
import json
from .scraping_utils import get_player_career_stats, scrape_player_stats
from .feature_extraction import (
    extract_numbers,
    calculate_fantasy_points,
    calculate_composite_scores
)

def scrape_player_data(input_csv, stats_years):
    """
    Scrape player data from PDGA website.
    
    Args:
        input_csv: Path to CSV containing PDGA player numbers
        stats_years: List of years to scrape stats for
        
    Returns:
        DataFrame with scraped player data
    """
    # Read player list
    players_df = pd.read_csv(input_csv)
    
    # Get career stats
    for index, row in tqdm(players_df.iterrows(), total=players_df.shape[0]):
        stats = get_player_career_stats(player_pdga=row['pdga_number'])
        for key, value in stats.items():
            players_df.at[index, key] = value
        time.sleep(1.5)
        
    # Clean numeric columns
    numeric_cols = ['career_events', 'join_date', 'rating_current', 
                   'career_wins', 'career_earnings', 'world_rank']
    for col in numeric_cols:
        raw_col = f'{col}_raw'
        players_df[col] = players_df[raw_col].apply(extract_numbers)
        players_df = players_df.drop(columns=[raw_col])
        
    # Get detailed stats and ratings
    for index, row in tqdm(players_df.iterrows(), total=players_df.shape[0]):
        stats, ratings = scrape_player_stats(
            pdga_number=row['pdga_number'],
            years_list=stats_years
        )
        players_df.at[index, 'stats_data'] = [stats.to_dict(orient='list')]
        players_df.at[index, 'ratings_data'] = [ratings.to_dict(orient='list')]
        time.sleep(1.5)
        
    return players_df

def calculate_features(df, points_map, stats_years):
    """
    Calculate fantasy features from scraped player data.
    
    Args:
        df: DataFrame with scraped player data
        points_map: Dictionary mapping places to point values
        stats_years: List of years used in scraping
        
    Returns:
        DataFrame with calculated features
    """
    # Calculate fantasy points
    for year in stats_years:
        col = f'fantasy_points_{str(year)[-2:]}'
        df[col] = df['stats_data'].apply(
            lambda x: calculate_fantasy_points(x, points_map, year)
        )
        
    # Calculate composite scores
    df = calculate_composite_scores(df)
    
    # Convert rating to float
    df['rating_current'] = df['rating_current'].astype(float)
    
    # Drop intermediate columns
    drop_cols = ['stats_data', 'ratings_data', 'career_earnings',
                 'world_rank', 'pdga_number']
    df = df.drop(columns=drop_cols)
    
    return df.sort_values('composite_fp', ascending=False)

def generate_player_dataset(input_csv, stats_years, points_map):
    """
    Generate complete player dataset with stats and fantasy points.
    
    Args:
        input_csv: Path to CSV containing PDGA player numbers
        stats_years: List of years to scrape stats for
        points_map: Dictionary mapping places to fantasy points
        
    Returns:
        DataFrame with player stats and fantasy points
    """
    df = scrape_player_data(input_csv, stats_years)
    # Save intermediate scraped data
    df.to_csv('data/scraped_temp.csv', index=False)
    print("Intermediate scraped data saved to data/scraped_temp.csv")
    return calculate_features(df, points_map, stats_years)

def main():
    parser = argparse.ArgumentParser(description='Generate fantasy disc golf player dataset')
    parser.add_argument('input_csv', help='Path to CSV containing PDGA player numbers')
    parser.add_argument('output_csv', help='Path to save the output dataset')
    parser.add_argument('--years', nargs='+', type=int, required=True,
                      help='Years to scrape stats for (e.g. --years 2023 2024)')
    parser.add_argument('--points-map', type=str, required=True,
                      help='Path to JSON file containing place-to-points mapping')
    
    args = parser.parse_args()
    
    # Load points mapping from JSON
    with open(args.points_map) as f:
        points_map = json.load(f)
    
    # Generate dataset
    df = generate_player_dataset(args.input_csv, args.years, points_map)
    
    # Save to CSV
    df.to_csv(args.output_csv, index=False)
    print(f"Dataset saved to {args.output_csv}")

if __name__ == '__main__':
    main()

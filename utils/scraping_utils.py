import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from .feature_extraction import extract_numbers

def ratings_date_parse(s):
    """Parse date from PDGA ratings format."""
    return s.split('to')[-1].strip()

def scrape_pdga_table(url, table_id, event=False):
    """
    Scrape a table from a PDGA webpage.
    
    Args:
        url: URL of the PDGA page
        table_id: HTML id of the table to scrape
        event: Whether this is an event results table (affects header handling)
        
    Returns:
        pandas DataFrame containing the table data
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', id=table_id)
    rows = table.find_all('tr')

    # Extract headers
    headers = []
    counter = 1  # Counter for naming round rating columns
    for header in rows[0].find_all('th'):
        header_text = header.text.strip()
        if event and not header_text:  # If header is empty in event table
            header_text = f'rating_{counter}'  # Assign custom name
            counter += 1
        headers.append(header_text)

    # Extract data
    data = []
    for row in rows[1:]:
        cols = [ele.text.strip() for ele in row.find_all('td')]
        data.append(cols)

    return pd.DataFrame(data, columns=headers)

def get_player_career_stats(player_pdga):
    """
    Get career statistics for a player from their PDGA profile.
    
    Args:
        player_pdga: PDGA number of the player
        
    Returns:
        Dictionary containing career statistics
    """
    css_selectors = {
        'career_events_raw': '.career-events',
        'join_date_raw': '.join-date', 
        'rating_current_raw': '.current-rating',
        'career_wins_raw': '.career-wins',
        'career_earnings_raw': '.career-earnings',
        'world_rank_raw': '.world-rank'
    }
    
    url = f'https://www.pdga.com/player/{str(player_pdga)}/details'
    response = requests.get(url)

    collection_dict = {'pdga_number': player_pdga}
    soup = BeautifulSoup(response.content, 'html.parser')
    
    for key, selector in css_selectors.items():
        elements = soup.select(selector)
        if elements:
            extracted_text = ' '.join([elem.get_text(strip=True) for elem in elements])
        else:
            extracted_text = 'Element not found'
            
        collection_dict[key] = extracted_text

    return collection_dict

def scrape_player_stats(pdga_number, years_list):
    """
    Scrape tournament results and ratings history for a player.
    
    Args:
        pdga_number: PDGA number of the player
        years_list: List of years to scrape data for
        
    Returns:
        Tuple of (tournament stats DataFrame, ratings DataFrame)
    """
    table_id_stats = "player-results-mpo"
    table_id_ratings = "player-results-details"
    
    # Get tournament stats
    stats = pd.DataFrame()
    for year in years_list:
        try:
            url_stats = f'https://www.pdga.com/player/{str(pdga_number)}/stats/{year}'
            stats_year = scrape_pdga_table(url=url_stats, table_id=table_id_stats)
            stats = pd.concat([stats, stats_year])
        except Exception as e:
            print(e)
            pass
        time.sleep(1.5)

    if stats.shape[0] > 0:
        stats = stats[stats['Tier'].isin(['ES', 'M', 'A', 'B', 'XM'])]
        stats['Date'] = pd.to_datetime(stats['Dates'].apply(lambda x: x.split('to')[-1].strip()))
        stats = stats[['Place', 'Tier', 'Date', 'Tournament']]

    # Get ratings history
    url_ratings = f'https://www.pdga.com/player/{str(pdga_number)}/details'
    try:
        ratings = scrape_pdga_table(url=url_ratings, table_id=table_id_ratings)
        ratings = ratings[ratings['Tier'].isin(['ES', 'M', 'A', 'B', 'XM'])]
        ratings['Date'] = pd.to_datetime(ratings['Date'].apply(lambda x: x.split('to')[-1].strip()))
        ratings = ratings[['Rating', 'Date', 'Tournament', 'Tier', 'Round']]
    except Exception as e:
        ratings = pd.DataFrame()
        print(f'{e}, {pdga_number}')

    return stats, ratings

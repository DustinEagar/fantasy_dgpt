# Fantasy Disc Golf Analysis

The objective of this project is to analyze past performance of touring professional disc golfers to inform a draft and trade strategy for fantasy disc golf.

## Basic Outline

The project has three overacrhing components.

- Collect data about past results
    - Last 2 or 3 seasons of results from PDGA and/or UDisc Live
    - Player data - ratings and career history from PDGA

- EDA, analysis of trends
- Model expected fantasy DG performance for players
    - Determine if there is a compelling improvement on using average of past performance as predictor of 2024 performance
    - Inform draft strategy with derivation an auction preference order and value for each player

This project is focused on a draft valuation model that focuses on overall season performance, rather than a player-event forecast, which may be attempted later.

## Outline of Fantasy Format

Players select via draft auction a set of touring pros, with 6 players "starting" at each event. Each player's finishing result yields fantasy points as follows:

Here's a markdown table with the specified columns:


| Place | Points | % of 1st |
|-------|--------|----------|
| 1st   | 300    | 100.00%  |
| 2nd   | 245    | 81.67%   |
| 3rd   | 195    | 65.00%   |
| 4th   | 155    | 51.67%   |
| 5th   | 135    | 45.00%   |
| 6th   | 110    | 36.67%   |
| 7th   | 97     | 32.33%   |
| 8th   | 85     | 28.33%   |
| 9th   | 75     | 25.00%   |
| 10th  | 64     | 21.33%   |
| 11th  | 56     | 18.67%   |
| 12th  | 48     | 16.00%   |
| 13th  | 42     | 14.00%   |
| 14th  | 36     | 12.00%   |
| 15th  | 33     | 11.00%   |
| 16th  | 30     | 10.00%   |
| 17th  | 27     | 9.00%    |
| 18th  | 24     | 8.00%    |
| 19th  | 21     | 7.00%    |
| 20th  | 18     | 6.00%    |
| 21st  | 15     | 5.00%    |
| 22nd  | 12     | 4.00%    |
| 23rd  | 10     | 3.33%    |
| 24th  | 8      | 2.67%    |
| 25th  | 6      | 2.00%    |
| 26th  | 4      | 1.33%    |
| 27th  | 3      | 1.00%    |
| 28th  | 2      | 0.67%    |
| 30th  | 1      | 0.33%    |

$Points = f_{points}(Place)$

## Model Hypotheses
Inform data collection and structure with possible hypotheses to test.

### Dummy Baseline
Model expected fantasy points as the average of past results. Where $t$ is an event or set of events, $X_t$ denotes a random variable corresponding to the performance of player $X$ over event set $t$, and $i$ are past observations:

$$E[X_t] = 1/n\sum_i{x_{it}}$$

For example, to predict Calvin Heimburg's fantasy performance at PDGA Worlds using the dummy baseline model with 3 seasons of past data from 2021, 2022, and 2023, we simply average the points he would have scored. 2023 - 5th place, 135 pts; 2022 - 6th, 110; 2021 - 11th, 56, for an average of 100.3 points.

This approach could also be extended with a weighting function that, for example, assigns greater weight to more recent results.

An advantage of this approach is that it is very straightforward to compute. Disadvantages include blindness to changes in schedule; blindness to new touring pros; blindness to year-over-year and during-season changes.

### Model Expected Performance Based on Current Rating

An alternative approach would be to model a player's expected performance in the event as a function of that player's current rating. We make the simplifying assumption that the distribution of round ratings $R_i$ for player $i$ is normally distributed around $\mu_i$ with variance $\sigma_i$. Then, the expectation of the number of points $X$ for player $i$ is given by

$$X_i = f(R_i) +\epsilon$$
$$E[X_i] = f(E[R_i])$$
$$R_i \sim N(\mu_i,\sigma_i )$$

We could additionally condition on other factors, like player $i$'s age. We could also construct a different weighting for more recent rounds - since the PDGA rating system already adds higher weight to more recent rounds, we'll skip over that for now.

$$X_i = f(R_i \sim N(\mu_i, \sigma_i |Y_i))$$

 What we are looking to capture here is our prior belief that younger touring pros who may be on the "upswing" of their careers may outplay their current rating more often than older players. Since we don't have direct access to players' ages, we can use their number of years as PDGA members as a rough proxy

 ## Data Gathering

 List of 93 MPO DGPT tour card holders for 2024 and their pdga numbers on [discgolfscene.com](https://www.discgolfscene.com/tournaments/2024_DGPT_Tour_Card_and_Tour_Pass_Registration_2023/registration).

 PDGA Ratings and rating history from [www.pdga.com](https://www.discgolfscene.com/tournaments/2024_DGPT_Tour_Card_and_Tour_Pass_Registration_2023/registration) (scraped)

2023 Major (pro) and Elite Series PDGA Events from [pdga](https://www.pdga.com/tour/search?date_filter[min][date]=2023-01-01&date_filter[max][date]=2023-12-31&Tier[]=ES&Tier[]=M&Tier[]=XM&Classification[]=Pro)

```python
#List of event urls
pdga_event_string = 'https://www.pdga.com/tour/event/'

events_list_23 = [65206, 66457, 65288, 65208, 64955, 66458, 65207, 69022, 65289, 67392, 68353, 64036, 67202, 65115, 66174, 65116, 68748, 65291, 64957, 74356]

```


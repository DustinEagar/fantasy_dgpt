# Fantasy Disc Golf Analysis

The objective of this project is to analyze past performance of touring professional disc golfers to inform a draft and trade strategy for fantasy disc golf.

## Basic Outline

The project has three overacrhing components.

- Collect data about past results
    - Last 2 or 3 seasons of results from PDGA and/or UDisc Live
    - Data on courses (type, length, elevation, etc)
    - Weather data - past events and historical averages for events
- EDA, analysis of trends
- Model expected fantasy DG performance for players
    - Determine if there is a compelling improvement on using average of past performance as predictor of 2024 performance
    - Inform draft strategy with derivation an auction preference order and value for each player

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

An alternative approach would be to model a player's expected performance in the event as a function of that player's current rating.
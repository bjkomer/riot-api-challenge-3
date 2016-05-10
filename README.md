# Submission for Riot API Challenge 3.0

Check it out [here](https://platicopter.pythonanywhere.com/)! It was designed to look best with Chrome, other browsers will not be ideal (but hopefully still functional).

## What is it?

Mastery Match is a simple app that lets you find high level players that play similar champions as you. The goal is to show you other players you can learn from to improve your game. This can be through spectating games, trying out their builds, or seeing what team comps they play with your champions.

## How does it work?

It uses the champion mastery API to build profiles for all of the challenger and master tier players in each region (and some diamond players as well). These profiles are created by normalizing the mastery points that each summoner has across all champions they have played. The normalization is done to account for the differences in the number of games played between summoners. When you enter your summoner name, it creates a profile for you and compares it to all summoners of interest in the database. You can choose to filter for only players in your region or only challenger/master players. The top 5 best matches are returned with links to their lolking profiles. From there you can spectate their games if they are online or look through their match history.

## More specific details

The quality of a match is calculated as a weighted combination of three metrics. 

The first metric is a sum of squared differences of the champion points across all champions (130 champions total). If someone has not played a particular champion, their score for that champion is set to zero. This metric is a measure of how closely the entire mastery profile matches. The lower this number is, the better. 

The second metric is a sum of squared differences of the champion points across only the top 10 highest mastered champions for each player. The point of this metric is to bias towards champions that are played more often, and to not hurt the score if lesser played champions don't quite match up. For example, if you've played Teemo only one time and the player you are being matched with hasn't played Teemo at all, this shouldn't really be all that important for your match score. While this effect is small for one champion, it gets compounded quite fast when 80+ champions don't quite line up. This would have an effect on the first metric, but not on this one.

The third metric comes from an element-wise multiplication of the mastery profiles. The length of the resulting 130 dimensional vector is computed and used for this metric. The larger this number is, the better the match. This metric gives preference to champions that have a high mastery score for both players without worrying about the exact number. For example, if one player has a score of 0.5 on a champion, and another player has 0.6 on that champion, the previous two metrics would count that as a mismatch by 0.1, while this metric would just multiply them to get a sense of closeness. This makes both highly played champions and champions that are not played at all have the most influence on the score. 

Data for high level players to compare to is gathered beforehand and stored on the server for quick access and to reduce API calls. The data for master and challenger players is gathered from a single API call for each region. The data for diamond players is more complicated, and comes from getting the match history of a couple random diamond players and then gathering the summoner IDs of all other diamond players that they have played with to come up with a dataset. The size is limited to 1000 diamond players in each region to conserve space.
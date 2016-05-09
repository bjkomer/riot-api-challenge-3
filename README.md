# Submission for Riot API Challenge 3.0

Check it out [here](Platicopter.pythonanywhere.com)

## What is it?

Mastery Match is a simple app that lets you find high level players that play similar champions as you. The goal is to show you other players you can learn from to improve your game. This can be through spectating games, trying out their builds, or seeing what team comps they play with your champions.

## How does it work?

 It uses the champion mastery API to build profiles for all of the challenger and master tier players in each region (and some diamond players as well). These profiles are created by normalizing the mastery points that each summoner has across all champions they have played. The normalization is done to account for the differences in the number of games played between summoners. When you enter your summoner name, it creates a profile for you and compares it to all summoners of interest in the database. You can choose to filter for only players in your region or only challenger/master players. The top 5 best matches are returned with links to their lolking profiles.
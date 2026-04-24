# Everyday Automation Discord Bot

A Python Discord bot that helps users check tech news, weather, reading progress, and study reminders using simple slash commands.

## Features

- Tech news using NewsAPI
- Weather updates using OpenWeatherMap
- Daily reading tracker
- Study reminder timer
- Clean /help command
- Error handling for invalid input and API issues

## Commands

| Command | Description |
|---|---|
| /help | Shows all available commands |
| /news [query] | Gets latest tech news |
| /weather <city> | Gets current weather for a city |
| /reading goal <pages> | Sets daily reading goal |
| /reading log <pages> | Logs pages read |
| /reading progress | Shows reading progress |
| /studyreminder <minutes> | Sends a reminder after a set time |

## APIs Used

- NewsAPI
- OpenWeatherMap

## Setup

Install dependencies:

```bash
pip install -r requirements.txt

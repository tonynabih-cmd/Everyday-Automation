\# Everyday Automation Discord Bot



A single Discord bot that brings together \*\*tech news\*\*, \*\*weather\*\*, \*\*daily reading tracking\*\*, and \*\*study reminders\*\* – all through clean slash commands and embeds.



\---



\## Features



\- \*\*📰 Tech News\*\* – Fetch the latest 5 technology headlines (optionally filter by keyword)

\- \*\*🌤️ Weather\*\* – Get current weather for any city (temperature, feels‑like, humidity)

\- \*\*📖 Reading Tracker\*\* – Set a daily page goal, log your reading, and see a visual progress bar

\- \*\*⏰ Study Reminder\*\* – Set a timer that pings you after X minutes

\- \*\*🆘 Help\*\* – /help command explains every feature

\- \*\*🧯 Solid error handling\*\* – Friendly messages for invalid input, API downtime, or missing data



\---



\## Commands



| Command | Description |

|--------|-------------|

| `/help` | Show all available commands with descriptions |

| `/news \[query]` | Top 5 tech headlines; optional keyword search (e.g., `AI`) |

| `/weather <city>` | Current weather in a city (e.g., `London`) |

| `/reading goal <pages>` | Set your daily reading target |

| `/reading log <pages>` | Log pages you just read |

| `/reading progress` | View today’s progress (progress bar + percentage) |

| `/studyreminder <minutes>` | Get a ping after the specified number of minutes |



\---



\## Prerequisites



\- Python \*\*3.9+\*\*

\- A \*\*Discord bot token\*\* (see \[Discord Developer Portal](https://discord.com/developers/applications))

\- \*\*API keys\*\* (free tiers are fine):

&#x20; - \[NewsAPI](https://newsapi.org/) – for news headlines

&#x20; - \[OpenWeatherMap](https://openweathermap.org/api) – for weather



\---



\## Setup



1\. \*\*Clone or download\*\* this repository.



2\. \*\*Install dependencies:\*\*

&#x20;  ```bash

&#x20;  pip install -r requirements.txt


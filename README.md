# BansheeMissingMods

Lightweight application to monitor daily banshee mods in Destiny2 and notify users if they are missing one of the mods being sold

This application performs a simple API request to the backend of `@cujarrett`'s [daily banshee mods twitter bot](https://github.com/cujarrett/banshee-44-mods-bot), then checks a user's Player Profile to determine if the player has acquired the daily mods or not.

Application is very much sandbox stage at this point but is running daily on a raspberry pi for myself and a friend.

## Getting Started

This app is built with Python 3.8 and managed with [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today). With these tools installed, you can get a virtual environment set up with the required dependencies by running::

```shell
pipenv install
```

Commands can be run in the virtual environment via `pipenv run` or the environment can be "activated" via `pipenv shell`. Currently, everything happens in `main.py`, but you may want to run things interactively with a repl like `ipython`.

### Requirements

This app interacts with the Bungie API. You will first need to [sign up for a project](https://www.bungie.net/en/Application) with Bungie and keep the provided API key in an environment variable called `BUNGIE_API_KEY`

The main script also expects a `member_list.csv` file with the following format:

```text
membership_id,email,name
```

## Architecture Plan

Rough plan of architecture for moving app into AWS for public exposure.

In short, users will be able to sign up for the banshee buddy service with the help of a simple web app. The frontend will consist of a search feature (find profile by membership type (PSN, Xbox, Steam, etc.) and name), and a simple "sign me up" form (need member info and email address). This will integrate with a thin API layer that interacts with the bungie API (to search for profile) and a DynamoDB datastore (to keep track of signed up users and metadata). Once a user is in the database, they will begin receiving daily emails. This is done via a polling function that runs on a daily basis to retrieve daily mods, scan the user database, and dispatch worker functions for each member. The dispatching will be done via a message queue and members may be batched (X users per message). These messages will then be picked up by the worker function (may receive messages in batch size of N). The worker function will simply query the collections data for a user's profile from the bungie API and then find the entry for the day's banshee mods. The user will only be emailed if they are missing one of the available mods. Emails will also include a link to unsubscribe from the service which will call the API to issue a DELETE request to the database.

Costs are almost negligible (and mostly free-tier eligible) for the compute and storage aspects. Costs are expected to be minimal for the hosting of the web application (especially as it is only used during sign-up). The major cost comes from Simple Email Service which charges $0.10 for every 1,000 emails.


![AWS Architecture](./aws-architecture.png)

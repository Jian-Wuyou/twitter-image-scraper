# twitter-image-scraper
## Setup

First, install `tqdm`. Via pip, the command is

```sh
$ pip install tqdm
```

Next, you need to generate your api key and api secret key.
If you don't have them, go to [Twitter Developers](https://dev.twitter.com/)
and create your application.
After you get your api key and api secret key, create a .env file like this:

```
BEARER_TOKEN=YOUR_BEARER_TOKEN
```

## Usage

Run the file by calling

```sh
$ py main.py
```

The program will prompt you for the username of the account you want to download.
It will then proceed to download the images into the directory "./artists/{username}"
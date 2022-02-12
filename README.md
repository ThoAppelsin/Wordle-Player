
# Wordle Player

A program that plays the game [Wordle](https://www.powerlanguage.co.uk/wordle/) on the web. It tries to optimize for the worst case (e.g. to find any word in at most 4 tries), rather than the average case (e.g. to find the words in 2.24 steps on average) or in terms of any other score metric.

## Setup and run

For the setup:
1. Create a python virtual environment: `python -m venv env`
2. Install the required packages: `pip install -r requirements.txt`
3. Install Firefox. *If you'd like to use any other browser, you must change some stuff regarding selenium in the first 10 lines of the script.*

You may then run the script and let it do its thing: `python bot.py`

## How it works?

`wordslist.txt` contains all the 5-letter words considered as valid by the Wordle English.

On the initial run, for each pair of words `wordA` and `wordB` in that list, the script simulates what the outcome (i.e. the 3 colors for each of the 5 letters) would be when we make the guess `wordA` if the secret answer was `wordB`. This takes about 8 minutes to compute, but we store this as a 12972⨯12972 8-bit unsigned integer matrix (takes about 160MB) to reuse on the subsequent runs of the script.

The script then just picks the guess that would leave us with the least amount of candidates, considering the worst possible responses (responses that yield the maximum amount of candidates for a given guess) from Wordle. In other words, the script makes its guess pessimistically, expecting the worst from Wordle.

This is repeated until the secret is found.

## Is it perfect?

Not yet. It only thinks of one step ahead and tries to minimize the number of candidates left. However, it might just be that a set of 100 candidates is actually partitioned much more evenly than another set of 90 candidates, so much so that we would be better off going for the set of 100 candidates.

## What's next?

- [ ] add a switch for Wordle TR
- [ ] make it perfect
- [ ] test it against each of the 12972 words and see how well it does

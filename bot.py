import numpy as np
import numpy.random as npr
import scipy.stats as sps
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

service = Service(GeckoDriverManager().install())
browser = webdriver.Firefox(service=service)

browser.get('https://www.powerlanguage.co.uk/wordle/')

body = browser.find_element('tag name', 'body')

# dismiss the modal box
body.click()

puzzleLen = 5
resultsMap = {
        'absent': 0,
        'present': 1,
        'correct': 2
        }

def resultsToNum(results):
    return sum(x * 3 ** i for i, x in enumerate(results))

def getResults(row):
    results = browser.execute_script(f"return Array.from(document.querySelector('game-app').shadowRoot.querySelectorAll('game-row')[{row}].shadowRoot.querySelectorAll('game-tile'), x => x.attributes.evaluation.value)")
    return resultsToNum(resultsMap[r] for r in results)

def check(row, j):
    return browser.execute_script(f"return document.querySelector('game-app').shadowRoot.querySelectorAll('game-row')[{row}].shadowRoot.querySelectorAll('game-tile')[{j}].attributes.letter.value")

def guess(word, row):
    for j, letter in enumerate(word):
        typed = ''
        while typed != letter:
            body.send_keys(letter)
            sleep(0.1)
            try:
                typed = check(row, j)
            except:
                pass

    # submit the guess
    body.send_keys('\uE007')

    # sleep(0.7)
    results = getResults(row)
    # sleep(0.7)

    return results

def simulateResultsMutual(A, B):
    resA = [0] * puzzleLen
    resB = [0] * puzzleLen

    A = list(A)
    B = list(B)
    for i in range(puzzleLen):
        if A[i] == B[i]:
            resA[i] = resB[i] = 2
            A[i] = B[i] = None
    for i in range(puzzleLen):
        if resA[i] == 0:
            for j in range(puzzleLen):
                if A[i] == B[j]:
                    resA[i] = resB[j] = 1
                    A[i] = B[j] = None
                    break
    return resultsToNum(resA), resultsToNum(resB)

perfectResult = resultsToNum([2] * puzzleLen)

def analyze(candidates, progress=False):
    analysis = np.identity(len(candidates), dtype=np.uint8) * perfectResult
    percIncr = 10
    perc = percIncr
    for i, A in enumerate(candidates):
        for j, B in enumerate(candidates[:i]):
            analysis[i, j], analysis[j, i] = simulateResultsMutual(A, B)
        if progress and i * (i + 1) >= len(candidates) * (len(candidates) - 1) * perc // 100:
            print(f"{perc}% done")
            perc += percIncr
    return analysis

def main():
    with open('wordslist.txt') as f:
        words = [x.strip() for x in f.readlines()]
    candIdxes = np.arange(len(words))

    fraFilename = f'first_round_analysis_{len(words)}.npy'
    try:
        analysis = np.load(fraFilename)
    except OSError:
        print(f"{fraFilename} is not available, making it now...")
        analysis = analyze(words, progress=True)
        np.save(fraFilename, analysis)
    else:
        print(f"Recovered analysis from {fraFilename}.")

    for i in range(6):
        if len(candIdxes) == 1:
            guessIdx = candIdxes[0]
        else:
            worstCaseNumCandidates = sps.mode(analysis, axis=1)[1]
            bestGuessIdxes = [i for i in np.flatnonzero(worstCaseNumCandidates == worstCaseNumCandidates.min())]
            if len(bestGuessIdxes) > 1:
                bestCandGuessIdxes = set(bestGuessIdxes).intersection(candIdxes)
                if len(bestCandGuessIdxes) > 0:
                    bestGuessIdxes = list(bestCandGuessIdxes)
                guessIdx = npr.choice(bestGuessIdxes)
                print(*(words[i] for i in bestGuessIdxes), '=>', words[guessIdx])
            else:
                guessIdx = bestGuessIdxes[0]
                print(words[guessIdx])
        results = guess(words[guessIdx], i)
        if results == perfectResult:
            return i
        columnsToKeep = analysis[guessIdx, :] == results
        candIdxes = candIdxes[columnsToKeep]
        analysis = analysis[:, columnsToKeep]

main()


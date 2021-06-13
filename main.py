import asyncio
from io import BytesIO
from itertools import chain
from os import getenv

from PIL import Image
from PIL.ImageDraw import Draw

import numpy as np
from loguru import logger
from more_itertools import first
from numpy.linalg import norm
from pyppeteer import launch
from pyppeteer_stealth import stealth


HEADLESS = getenv('HEADLESS', True)
BROWSER_DATA_DIR = getenv('BROWSER_DATA_DIR', './tmp')

BRANCH_COLOR = np.array([161, 116, 56, 255])
THRESHOLD = 50
N_LOOK_AHEAD = 5
X_LEFT_BRANCH = 0
X_RIGHT_BRANCH = 59
Y_START = 42
Y_GAP = 50
WIDTH = 60
HEIGHT = Y_START + Y_GAP * (N_LOOK_AHEAD-1) + 3
Y_INDEXES = tuple(reversed(tuple(Y_START + Y_GAP * i for i in range(N_LOOK_AHEAD))))

l_indexes = (Y_INDEXES, [X_LEFT_BRANCH, ] * N_LOOK_AHEAD)
r_indexes = (Y_INDEXES, [X_RIGHT_BRANCH, ] * N_LOOK_AHEAD)

default_args = [
    '--no-sandbox',
]
tmp_img_fp = "screenshots/tmp_{}.png"


def nearest_branch(arr, indexes):
    return first(np.where((norm(arr[indexes] - BRANCH_COLOR, axis=1) > THRESHOLD) == False)[0], N_LOOK_AHEAD)


def draw_detect_point(img, fp):
    draw = Draw(img)
    for xy in chain(zip(*l_indexes), zip(*r_indexes)):
        draw.point(xy[::-1], 'red')
    img.save(fp)


def crop_box(box: dict) -> dict:
    x, _, width, _ = box.values()
    return {
        'x': (width - WIDTH) / 2,
        'y': 0,
        'width': WIDTH,
        'height': HEIGHT,
    }


async def async_play(url: str):
    browser = await launch(headless=HEADLESS, userDataDir=BROWSER_DATA_DIR, ignoreHTTPSErrors=True, args=default_args)
    page = await browser.newPage()
    await stealth(page)
    await page.setViewport({'width': 600, 'height': 600})

    await page.goto(url)
    btn_start = await page.waitForXPath('//div[@class="icon_play"]')
    await btn_start.click()

    content = await page.waitForXPath('//div[@class="page_content"]')
    box = crop_box(await content.boundingBox())

    btn_left = await page.waitForXPath('//div[@id="button_left"]')
    btn_right = await page.waitForXPath('//div[@id="button_right"]')

    await page.waitFor('.in_game')
    logger.info("Playing...")
    # count = 0
    while await page.querySelectorAll('.in_game'):
        # count += 1
        b_data = await page.screenshot(clip=box)
        img = Image.open(BytesIO(b_data))
        arr = np.array(img)
        l_count, r_count = nearest_branch(arr, l_indexes), nearest_branch(arr, r_indexes)
        # draw_detect_point(img, tmp_img_fp.format(count))
        if l_count > r_count:
            for _ in range(l_count - 1):
                await btn_left.click()
        else:
            for _ in range(r_count - 1):
                await btn_right.click()
    score = await (
        await (await page.waitForXPath('//div[@id="score_value"]/text()')).getProperty("textContent")).jsonValue()
    logger.info(f"Your Score This Time: {score}")
    await page.browser.close()


def main(url: str):
    while True:
        asyncio.run(async_play(url))


if __name__ == '__main__':
    url = "https://tbot.xyz/lumber/#eyJ1Ijo3MTgyMjI2NDIsIm4iOiJQYW5kYWFhYSBZaXAiLCJnIjoiTHVtYmVySmFjayIsImNpIjoiNzg1NTYxMTg0NDEzMzgyNzgyOCIsImkiOiJCUUFBQUJnUUV3RGxQRTNCR3oyVkgzRnNGU1EifWFiODNlOTZjMmI2NjAzYWVkNjlkZTBkNDdjMTQyZGI5?tgShareScoreUrl=tgb%3A%2F%2Fshare_game_score%3Fhash%3DxrwtNOUxByeJDXVIyEou"
    # url = input("Input your game link: ")
    main(url)

import asyncio
from io import BytesIO
from itertools import chain

from PIL import Image
from PIL.ImageDraw import Draw

import numpy as np
from loguru import logger
from more_itertools import first
from numpy.linalg import norm

from browser import new_browser_page

branch_color = np.array([161, 116, 56, 255])

tmp_img_fp = "screenshots/tmp_{}.png"

threshold = 50

l_indexes = ([242, 192, 142, 92, 42], [0, ] * 5)
r_indexes = ([242, 192, 142, 92, 42], [59, ] * 5)


def func(arr):
    return first(np.where(arr == False)[0], len(arr))


def draw_detect_point(img, fp):
    draw = Draw(img)
    for xy in chain(zip(*l_indexes), zip(*r_indexes)):
        draw.point(xy[::-1], 'red')
    img.save(fp)


def crop_box(box: dict) -> dict:
    x, y, width, height = box.values()
    mid = width / 2
    x = mid - 30
    width = 60
    result = {
        'x': x,
        'y': y,
        'width': width,
        'height': 245,
    }
    return result


async def _main(url: str):
    page = await new_browser_page(headless=True)

    await page.goto(url)
    btn_start = await page.waitForXPath('//div[@class="icon_play"]')
    await btn_start.click()

    content = await page.waitForXPath('//div[@class="page_content"]')
    box = await content.boundingBox()
    box = crop_box(box)

    btn_left = await page.waitForXPath('//div[@id="button_left"]')
    btn_right = await page.waitForXPath('//div[@id="button_right"]')

    await page.waitFor('.in_game')
    logger.info("Playing...")
    while await page.querySelectorAll('.in_game'):
        b_data = await page.screenshot(clip=box)
        img = Image.open(BytesIO(b_data))

        arr = np.array(img)

        l_count = func(norm(arr[l_indexes] - branch_color, axis=1) - threshold > 0)
        r_count = func(norm(arr[r_indexes] - branch_color, axis=1) - threshold > 0)

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


if __name__ == '__main__':
    url = "https://tbot.xyz/lumber/#eyJ1Ijo3MTgyMjI2NDIsIm4iOiJQYW5kYWFhYSBZaXAiLCJnIjoiTHVtYmVySmFjayIsImNpIjoiNzg1NTYxMTg0NDEzMzgyNzgyOCIsImkiOiJCUUFBQUJnUUV3RGxQRTNCR3oyVkgzRnNGU1EifWFiODNlOTZjMmI2NjAzYWVkNjlkZTBkNDdjMTQyZGI5?tgShareScoreUrl=tgb%3A%2F%2Fshare_game_score%3Fhash%3DxrwtNOUxByeJDXVIyEou"
    # url = input("Input your game link: ")
    while True:
        asyncio.run(_main(url))

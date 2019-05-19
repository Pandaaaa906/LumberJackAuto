import asyncio
from io import BytesIO
from itertools import chain

from PIL import Image
from PIL.ImageDraw import Draw

import numpy as np
from numpy.linalg import norm

from browser import new_browser_page

branch_color = np.array([161, 116, 56, 255])

tmp_img_fp = "screenshots/tmp_{}.png"

threshold = 50

l_indexes = ([242, 192, 142, 92, 42], [270, ] * 5)
r_indexes = ([242, 192, 142, 92, 42], [330, ] * 5)


def func(arr):
    for i, value in enumerate(arr):
        if not value:
            break
    return i


def draw_detect_point(img, fp):
    draw = Draw(img)
    for xy in chain(zip(*l_indexes), zip(*r_indexes)):
        draw.point(xy[::-1], 'red')
    img.save(fp)


async def _main(url):
    page = await new_browser_page(headless=False)

    await page.goto(url)
    btn_start = await page.waitForXPath('//div[@class="icon_play"]')
    await btn_start.click()

    content = await page.waitForXPath('//div[@class="page_content"]')
    box = await content.boundingBox()

    btn_left = await page.waitForXPath('//div[@id="button_left"]')
    btn_right = await page.waitForXPath('//div[@id="button_right"]')

    for count in range(200):
        b_data = await page.screenshot(clip=box)
        img = Image.open(BytesIO(b_data))

        arr = np.array(img)

        l_arr = (norm(arr[l_indexes] - branch_color, axis=1) - threshold > 0)
        r_arr = (norm(arr[r_indexes] - branch_color, axis=1) - threshold > 0)

        l_count = func(l_arr)
        r_count = func(r_arr)

        # draw_detect_point(img, tmp_img_fp.format(count))

        if l_count > r_count:
            for _ in range(l_count-1):
                await btn_left.click()
        else:
            for _ in range(r_count-1):
                await btn_right.click()


if __name__ == '__main__':
    url = input("Input your game link: ")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(url))

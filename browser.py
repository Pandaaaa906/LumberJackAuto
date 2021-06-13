from pyppeteer import launch
from pyppeteer_stealth import stealth

default_args = [
    '--no-sandbox',
]


async def new_browser_page(headless=True, ignoreHTTPSErrors=True, userDataDir='./tmp', args=None, **kwargs):
    if args is None:
        args = default_args
    browser = await launch(ignoreHTTPSErrors=ignoreHTTPSErrors,
                           headless=headless,
                           userDataDir=userDataDir,
                           args=args,
                           **kwargs)
    page = await browser.newPage()
    await stealth(page)
    await page.setViewport({'width': 600, 'height': 600})
    return page

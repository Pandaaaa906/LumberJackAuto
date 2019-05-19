from pyppeteer import launch

with open("preload.js", 'r') as f:
    preload_js = f.read()

default_args = ['--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-position=0,0',
                '--disable-gpu',
                '--ignore-certifcate-errors',
                '--ignore-certifcate-errors-spki-list',
                '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3312.0 Safari/537.36'
                ]


async def new_browser_page(headless=True, ignoreHTTPSErrors=True, userDataDir='./tmp', args=None, **kwargs):
    if args is None:
        args = default_args
    browser = await launch(ignoreHTTPSErrors=ignoreHTTPSErrors,
                           headless=headless,
                           userDataDir=userDataDir,
                           #executablePath="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                           #executablePath="H:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                           args=args,
                           **kwargs)
    page = await browser.newPage()
    await page.setViewport({'width': 600, 'height': 600})
    await page.evaluateOnNewDocument(preload_js)
    return page

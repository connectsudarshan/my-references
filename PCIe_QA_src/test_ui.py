import asyncio, os, sys
from playwright.async_api import async_playwright
URL='file:///home/claude/pcie/out/PCIe_QA_Study_Guide.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':1280,'height':900})
        pg = await ctx.new_page()
        errs=[]
        pg.on('console', lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
        pg.on('pageerror', lambda e: errs.append('pageerror:'+str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(600)
        await pg.screenshot(path='out/shot_home.png')
        # open question via sidebar
        await pg.click('.nav-item[data-id="1.02"]'); await pg.wait_for_timeout(200)
        assert await pg.locator('.reveal-box').count()==1, 'reveal box missing'
        await pg.screenshot(path='out/shot_q_hidden.png')
        await pg.keyboard.press('Space'); await pg.wait_for_timeout(200)
        assert await pg.locator('.short-box').count()==1, 'short not shown'
        assert await pg.locator('figure.fig svg').count()==1, 'figure missing'
        await pg.keyboard.press('2'); await pg.wait_for_timeout(200)
        await pg.screenshot(path='out/shot_q_revealed.png', full_page=True)
        # nav next
        await pg.keyboard.press('ArrowRight'); await pg.wait_for_timeout(200)
        assert '1.03' in await pg.inner_text('.q-id'), 'next failed'
        await pg.keyboard.press('Space'); await pg.keyboard.press('1'); await pg.wait_for_timeout(200)
        # rating persisted?
        st = await pg.evaluate("JSON.parse(localStorage.getItem('pcieqa.v1')).ratings")
        print('ratings:', {k:v['r'] for k,v in st.items()})
        # reference mode
        await pg.click('#modeSeg button[data-mode="ref"]'); await pg.wait_for_timeout(200)
        assert await pg.locator('.short-box').count()==1, 'ref mode should show answer'
        await pg.click('#modeSeg button[data-mode="study"]'); await pg.wait_for_timeout(200)
        # search
        await pg.fill('#searchInput','replay'); await pg.wait_for_timeout(200)
        print('search replay ->', await pg.locator('.nav-item').count(), 'items')
        await pg.fill('#searchInput','')
        # mock
        await pg.click('#sidebar .sidebar-header'); await pg.wait_for_timeout(200)
        await pg.click('[data-act="mock"]'); await pg.wait_for_timeout(200)
        await pg.screenshot(path='out/shot_mock_setup.png')
        await pg.click('#startMock'); await pg.wait_for_timeout(300)
        await pg.screenshot(path='out/shot_mock_run.png')
        for i in range(10):
            await pg.keyboard.press('Space'); await pg.wait_for_timeout(80)
            await pg.keyboard.press(['1','2','3'][i%3]); await pg.wait_for_timeout(120)
        await pg.wait_for_timeout(300)
        await pg.screenshot(path='out/shot_mock_summary.png', full_page=True)
        txt = await pg.inner_text('.hero h2'); print('summary heading:', txt)
        await pg.click('#home'); await pg.wait_for_timeout(300)
        await pg.screenshot(path='out/shot_home2.png', full_page=True)
        # review weak
        print('weak btn disabled?', await pg.locator('[data-act="weak"]').is_disabled())
        # mobile
        m = await b.new_context(viewport={'width':390,'height':800}); mp = await m.new_page()
        mp.on('pageerror', lambda e: errs.append('mobile pageerror:'+str(e)))
        await mp.goto(URL+'#/q/1.09'); await mp.wait_for_timeout(400)
        await mp.click('[data-reveal]'); await mp.wait_for_timeout(200)
        await mp.screenshot(path='out/shot_mobile.png')
        ov = await mp.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        print('mobile horizontal overflow:', ov)
        print('ERRORS:', errs)
        await b.close()
asyncio.run(main())

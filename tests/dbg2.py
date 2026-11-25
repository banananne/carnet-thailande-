from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(timezone_id="Asia/Bangkok", service_workers="block")
    pg = ctx.new_page()
    pg.clock.set_fixed_time(datetime(2026, 11, 21, 12, 0, tzinfo=ZoneInfo("Asia/Bangkok")))
    pg.goto(BASE, wait_until="load")
    print(pg.evaluate("new Date().toString() + ' | ' + new Date().getFullYear() + '-' + (new Date().getMonth()+1) + '-' + new Date().getDate()"))
    pg.clock.set_fixed_time(datetime(2026, 12, 28, 23, 59, 30, tzinfo=ZoneInfo("Asia/Bangkok")))
    print(pg.evaluate("new Date().toString()"))
    b.close()

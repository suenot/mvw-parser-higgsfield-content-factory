"""Source: higgsfield.ai/content-factory (server-rendered preset cards).

Scrolls the page in Camoufox until no new cards appear (56 presets as of
2026-10-31); falls back to static HTML. Prompts are not exposed on the page.
"""
import re

from mvw_core import Item, cli_args, fetch_text

SOURCE = "higgsfield-content-factory"
PAGE = "https://higgsfield.ai/content-factory"
CARD = re.compile(r'<li class="_presetCard.*?</li>', re.S)
VIDEO = re.compile(r'<video[^>]*src="([^"]+)"[^>]*poster="([^"]+)"')
TITLE = re.compile(r'aria-label="Open (?!original on )([^"]+)"')
STAT = re.compile(r'class="sr-only">(\w+): ([^<]+)<')
ORIG = re.compile(r'<a href="([^"]+)"[^>]*aria-label="Open original on ([^"]+)"')


def render_scrolled(max_rounds=60):
    """Load the page in Camoufox and scroll like a visitor until no new cards appear."""
    from camoufox.sync_api import Camoufox

    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.goto(PAGE, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        count, stable = 0, 0
        for _ in range(max_rounds):
            page.mouse.wheel(0, 4000)
            page.evaluate("document.querySelectorAll('*').forEach(e=>{if(e.scrollHeight>e.clientHeight+50&&getComputedStyle(e).overflowY.match(/auto|scroll/))e.scrollTop=e.scrollHeight})")
            page.wait_for_timeout(1500)
            n = page.locator("li[class*=_presetCard]").count()
            stable = stable + 1 if n == count else 0
            count = n
            if stable >= 4:
                break
        return page.content()


def main():
    args = cli_args(__doc__)
    try:
        html = render_scrolled()
    except ImportError:
        print("camoufox not installed, falling back to static HTML (first batch only)")
        html = fetch_text(PAGE)
    cards = CARD.findall(html)
    if args.limit:
        cards = cards[: args.limit]
    new = 0
    for c in cards:
        v = VIDEO.search(c)
        if not v:
            continue
        video, poster = v.groups()
        item_id = video.rsplit("/", 1)[-1][:16]
        it = Item(SOURCE, item_id)
        new += it.is_new
        if not args.no_media:
            it.download("original.mp4", video)
            it.download("poster.jpg", poster)
        title = TITLE.search(c)
        orig = ORIG.search(c)
        stats = {k.lower(): val for k, val in STAT.findall(c)}
        it.save_meta(
            title=title.group(1) if title else item_id,
            source_url=PAGE,
            post_url=orig.group(1) if orig else None,
            platform=orig.group(2) if orig else None,
            stats=stats,
        )
    print(f"{SOURCE}: {len(cards)} items, {new} new")


main()

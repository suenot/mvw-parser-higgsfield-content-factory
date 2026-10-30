"""Source: higgsfield.ai/content-factory (server-rendered preset cards).

Only the SSR page is parsed (first batch of presets). Prompts are not in the
static HTML; TODO: find the paginated API behind the page (needs a browser
network capture, use Camoufox - not Chrome).
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


def main():
    args = cli_args(__doc__)
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

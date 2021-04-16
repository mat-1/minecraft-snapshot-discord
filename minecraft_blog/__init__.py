from typing import Any, List
import aiohttp

s = None

async def fetch_blog() -> List[Any]:
	global s
	if s is None:
		s = aiohttp.ClientSession()

	async with s.get('https://launchercontent.mojang.com/javaPatchNotes.json') as r:
		data = await r.json()

	return data['entries']

async def fetch_latest_blog_title() -> str:
	patch_notes = await fetch_blog()
	latest_title = patch_notes[0]['title']
	latest_id = latest_title\
		.lower()\
		.replace(' ', '-')\
		.replace('.', '-')\
		.replace(':', '')
	return latest_id

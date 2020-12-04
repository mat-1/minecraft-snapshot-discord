import aiohttp
import asyncio
import json
import os
import io

if not os.getenv('summarywebhook'):
	from dotenv import load_dotenv
	load_dotenv()

# s is set by execute_webhook
s = None

summary_webhook = os.getenv('summarywebhook')
textures_webhook = os.getenv('textureswebhook')
sounds_webhook = os.getenv('soundswebhook')
java_webhook = os.getenv('javawebhook')


async def execute_webhook(webhook, content, file=None, filename='image.png', chunked=True):
	global s
	if not s:
		s = aiohttp.ClientSession()

	if chunked and len(content) > 2000:
		remaining_content = content
		while len(remaining_content) > 2000:
			cut_index = remaining_content[:2000].rindex('\n')
			await execute_webhook(webhook, remaining_content[:cut_index])
			remaining_content = content[cut_index:]
		await execute_webhook(webhook, remaining_content, file=file, filename=filename)
		return

	webhook_executed = False
	while not webhook_executed:
		data = {
			'content': content,
		}
		if file:
			f = io.BytesIO(file)
			if '/' in filename:
				filename = filename.split('/')[-1]
			f.name = filename
			data['file'] = f

		r = await s.post(
			webhook,
			data=data,
		)
		r = await r.text()
		print(r)
		if r == '':
			webhook_executed = True
		else:
			r = json.loads(r)
			if 'retry_after' in r:
				await asyncio.sleep(r['retry_after'] / 1000)
			else:
				webhook_executed = True

async def execute_summary_webhook(content):
	await execute_webhook(summary_webhook, content)

async def execute_textures_webhook(content, file=None, filename='image.png'):
	await execute_webhook(textures_webhook, content, file, filename)

async def execute_sounds_webhook(content, file=None, filename='image.png'):
	await execute_webhook(sounds_webhook, content, file, filename)

async def execute_java_webhook(content, file=None, filename='image.png'):
	await execute_webhook(java_webhook, content, file, filename)



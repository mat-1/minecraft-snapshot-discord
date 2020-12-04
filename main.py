import minecraft
# import aiohttp
import asyncio
# import zipfile
# import os
# import io
# import hashlib
# import json
# import database
# import server
# import re

# summary_webhook = os.getenv('summarywebhook')
# textures_webhook = os.getenv('textureswebhook')
# sounds_webhook = os.getenv('soundswebhook')
# java_webhook = os.getenv('javawebhook')

# s = aiohttp.ClientSession()


# def sha1_hash(data):
# 	sha1 = hashlib.sha1()
# 	sha1.update(data)
# 	return sha1.hexdigest()

# async def get_version_data(s, version_id=None):
# 	r = await s.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
# 	data = await r.json()
# 	if not version_id:
# 		return data['versions'][0]
# 	else:
# 		for version in data['versions']:
# 			if version['id'] == version_id:
# 				return version


# async def get_packages_data(data_url, s):
# 	r = await s.get(data_url)
# 	data = await r.json()
# 	return data


# async def get_jar_file(jar_url, s):
# 	r = await s.get(jar_url)
# 	jar_compressed = await r.read()
# 	return jar_compressed

# async def get_assets_json(assets_url, s):
# 	r = await s.get(assets_url)
# 	return await r.json()

# async def execute_webhook(content, s, file=None, filename='image.png', webhook=None):
# 	if webhook is None:
# 		webhook = summary_webhook
# 	posted = False
# 	while not posted:
# 		data = {
# 			'content': content,
# 		}
# 		if file:
# 			f = io.BytesIO(file)
# 			f.name = filename
# 			data['file'] = f

# 		r = await s.post(
# 			webhook,
# 			data=data,
# 		)
# 		r = await r.text()
# 		if r == '':
# 			posted = True
# 		else:
# 			r = json.loads(r)
# 			if 'retry_after' in r:
# 				await asyncio.sleep(r['retry_after'] / 1000)
# 			else:
# 				posted = True

# def get_image_type(path):
# 	if path.startswith('textures/item/'):
# 		return 'item texture'
# 	elif path.startswith('textures/block/'):
# 		return 'block texture'
# 	elif path.startswith('entity/banner/'):
# 		return 'banner design'
# 	elif path.startswith('entity/shield/'):
# 		return 'shield design'
# 	elif path.startswith('textures/entity/'):
# 		return 'entity texture'

# async def get_mappings(mapping_url, s):
# 	r = await s.get(mapping_url)
# 	mappings = await r.text()
# 	return mappings.splitlines()

# def get_classes_from_mappings(mappings):
# 	classes = set()
# 	for line in mappings:
# 		if line.startswith('    '):
# 			pass # methodline
# 		elif line.startswith('#'):
# 			pass # comment
# 		elif line.endswith(':'):
# 			# classline
# 			class_name, obfuscated_name = line[:-1].split(' -> ')
# 			class_name = class_name.split('$')[0]
# 			classes.add(class_name)
# 	return classes

# class MinecraftVersion():
# 	def __init__(self, id, type=None, url=None, time=None, release_time=None):
# 		pass

# async def get_previous_version():
# 	previous_version_id = await database.get_version()
# 	previous_version_data = await get_version_data(s, previous_version_id)
# 	return {
# 		'id': previous_version_id,
# 		'data': previous_version_data
# 	}


# async def run():
# 	print('run')
# 	test = False

# 	version_data = await get_version_data(s)
# 	print(await get_previous_version())

# 	print(version_data)
# 	return

# 	await get_previous_version()

# 	version_id = version_data['id']
# 	if version_id != previous_version_id:
# 		await execute_webhook(f'@everyone New version! **{version_id}**', s)
# 		await execute_webhook(f'New version: **{version_id}**!', s, webhook=java_webhook)
# 		if not test:
# 			await database.update_version(version_id)
# 	else:
# 		if not test:
# 			return


# 	data_url = version_data['url']
# 	previous_data_url = previous_version_data['url']
# 	# {url, size, sha1}
# 	packages_data = await get_packages_data(data_url, s)
# 	previous_packages_data = await get_packages_data(previous_data_url, s)
# 	jar_url = packages_data['downloads']['client']['url']
# 	assets_url = packages_data['assetIndex']['url']
# 	print('jar_url', jar_url)
# 	jar_bytes = await get_jar_file(jar_url, s)
# 	print('assets_url', assets_url)
# 	assets_json = await get_assets_json(assets_url, s)
# 	assets_json = assets_json['objects']

# 	previous_version_id

# 	if 'client_mappings' in packages_data['downloads']:
# 		client_mappings_url = packages_data['downloads']['client_mappings']['url']
# 		old_client_mappings_url = previous_packages_data['downloads']['client_mappings']['url']

# 		client_mappings = await get_mappings(client_mappings_url, s)
# 		old_client_mappings = await get_mappings(old_client_mappings_url, s)

# 		current_classes = get_classes_from_mappings(client_mappings)
# 		old_classes = get_classes_from_mappings(old_client_mappings)

# 		new_classes = set()


# 		for classname in current_classes:
# 			if classname not in old_classes:
# 				new_classes.add(classname)
# 		cleaned_data = []
# 		most_changed = {}
# 		for new_class in new_classes:
# 			if not new_class.startswith('net.minecraft.'): continue
# 			new_class_split = new_class.split('.')[2:]
# 			if len(new_class_split) < 2: continue
# 			class_category = new_class_split[1].title()
# 			class_name = ' '.join(new_class_split[2:])
# 			class_name = re.sub('([A-Z])', r' \1', class_name).strip().replace('  ', ' ').lower()
# 			cleaned_data.append(f'{class_category}: {class_name}')
# 			for class_level in range(2, len(new_class_split)):
# 				# get like world, world.level, world.level.block, world.level.block.piston, etc and add it to a list to count how many relevant classes were added
# 				class_part = '.'.join(new_class_split[:class_level + 1])
# 				if class_part not in most_changed:
# 					most_changed[class_part] = 0
# 				most_changed[class_part] += 1

# 		for class_name in dict(most_changed):
# 			parent_class = '.'.join(class_name.split('.')[:-1])
# 			if parent_class not in most_changed: continue
# 			parent_changes = most_changed[parent_class]
# 			class_changes = most_changed[class_name]
# 			if class_changes / parent_changes >= .5:
# 				del most_changed[parent_class]


# 		most_changed_classes = sorted(most_changed, key=most_changed.get, reverse=True)[:20]
# 		most_changed_classes_data = []
# 		for class_name in most_changed_classes:
# 			change_count = most_changed[class_name]
# 			if change_count > 1:
# 				class_examples = []
# 				for new_class in new_classes:
# 					if new_class.startswith('net.minecraft.' + class_name + '.'):
# 						class_examples.append('.'.join(new_class.split('.')[len(class_name.split('.')) + 2:]))
# 				class_examples_joined = ', '.join(class_examples)
# 				most_changed_classes_data.append(f'{change_count} new classes related to **{class_name}** ({class_examples_joined})')
# 		await execute_webhook('\n'.join(most_changed_classes_data), s, '\n'.join(new_classes).encode(), webhook=java_webhook, filename=f'{version_id} new classes.txt')
# 		# print('new classes:', ('\n'.join(cleaned_data)).encode())

# 	file_hashes = {}

# 	print('Gotten client jar')

# 	jar_zip = zipfile.ZipFile(io.BytesIO(jar_bytes), 'r')

# 	# remove the file after reading

# 	old_hashes = await database.get_file_hashes()

# 	asset_filenames = set()

# 	language_new_data = {}
# 	language_changed_data = {}
# 	language_removed_data = {}

# 	did_textures_webhook = False

	

# 	for file in jar_zip.infolist():
# 		filename = file.filename
# 		if filename.startswith('assets/minecraft/'):
# 			with jar_zip.open(filename, 'r') as f:
# 				data = f.read()
# 				filename = filename[len('assets/minecraft/'):]
# 				hashed = sha1_hash(data)
# 				asset_filenames.add(filename)

# 				if filename in old_hashes:
# 					if old_hashes[filename] != hashed:
# 						if filename.endswith('.png'):
# 							if not did_textures_webhook:
# 								await execute_webhook(f'New version: **{version_id}**', s, webhook=textures_webhook)
# 								did_textures_webhook = True
# 							texture_type = get_image_type(filename)
# 							if not texture_type:
# 								prefix_text = 'Changed image file!'
# 							else:
# 								prefix_text = f'Changed {texture_type}!'
# 							await execute_webhook(f'{prefix_text} `{filename}`', s, data, filename=filename, webhook=textures_webhook)
# 						elif filename == 'lang/en_us.json':
# 							lang_old = await database.get_lang()
# 							lang_new = json.loads(data.decode())

# 							diffed = {}

# 							for i, key in enumerate(lang_new):
# 								value = lang_new[key]
# 								if key not in lang_old or value != lang_old[key]:
# 									string = f'+ {key}: {value}'
# 									diffed[string] = i
# 									if key in lang_old:
# 										language_changed_data[key] = value
# 									else:
# 										language_new_data[key] = value

# 							for i, key in enumerate(lang_old):
# 								value = lang_old[key]
# 								if key not in lang_new or value != lang_new[key]:
# 									string = f'- {key}: {value}'
# 									diffed[string] = i
# 									if key not in lang_new:
# 										language_removed_data[key] = value
									

# 							diffed = '\n'.join(sorted(diffed, key=diffed.get))
# 							# await execute_webhook(f'Language file changed!\n```diff\n{diffed}```')
							
							
# 				else:
# 					if not filename.endswith('.json'):
# 						if filename.endswith('.png'):
# 							texture_type = get_image_type(filename)
# 							if not texture_type:
# 								prefix_text = 'New image file!'
# 							else:
# 								prefix_text = f'New {texture_type}!'
# 							await execute_webhook(f'{prefix_text} `{filename}`', s, data, filename=filename, webhook=textures_webhook)
# 				if not test:
# 					if filename == 'lang/en_us.json':
# 						await database.update_lang(json.loads(data.decode()))
# 				file_hashes[filename] = hashed

# 	for filename in old_hashes:
# 		if filename not in asset_filenames:
# 			if not filename.endswith('.json'):
# 				if filename.endswith('.png'):
# 					if not did_textures_webhook:
# 						await execute_webhook(f'New version: **{version_id}**', s, webhook=textures_webhook)
# 						did_textures_webhook = True
# 					texture_type = get_image_type(filename)
# 					if not texture_type:
# 						prefix_text = 'Changed image file!'
# 					else:
# 						prefix_text = f'Changed {texture_type}!'

# 					await execute_webhook(f'Removed {prefix_text} `{filename}`', s, data, webhook=textures_webhook)

# 	if not test:
# 		await database.update_file_hashes(file_hashes)

# 	print('Done!')

# 	modified_block_suffix = ['wall', 'slab', 'stairs', 'pressure_plate', 'button']


# 	new_blocks = []
# 	new_items = []
# 	new_options = []

# 	for item in language_new_data:
# 		print(item, language_new_data[item])
# 		sections = item.split('.')
# 		if item.startswith('block.minecraft.'):
# 			blockname = '.'.join(sections[2:])
# 			new_blocks.append(blockname)
# 		elif item.startswith('item.minecraft.'):
# 			itemname = '.'.join(sections[2:])
# 			new_items.append(itemname)
# 		elif item.startswith('options.'):
# 			new_options.append('.'.join(sections[1:]))


# 	new_blocks = sorted(new_blocks, key=len)
# 	new_items = sorted(new_items, key=len)

# 	blocks_summary = []
# 	items_summary = []
# 	options_summary = []

# 	# new blocks
# 	while new_blocks:
# 		block_id = new_blocks[0]
# 		block_name = language_new_data['block.minecraft.' + block_id]
# 		block_id_tmp = block_id
# 		extra_blocks = []
# 		if block_id_tmp.endswith('_bricks'):
# 			block_id_tmp = block_id_tmp[:-1]
# 		is_base_block = True
# 		for thing in modified_block_suffix:
# 			if block_id_tmp.endswith('_' + thing):
# 				is_base_block = False
# 		if is_base_block:
# 			for other_block in new_blocks:
# 				if other_block.startswith(block_id_tmp + '_'):
# 					extra_blocks.append(other_block)
# 					new_blocks.remove(other_block)
# 		if extra_blocks:
# 			extra_block_names = [language_new_data['block.minecraft.' + extra_block] for extra_block in extra_blocks]
# 			blocks_summary.append(f'- **{block_name}**, {", ".join(extra_block_names)}')
# 		else:
# 			blocks_summary.append(f'- **{block_name}**')
# 		new_blocks.remove(block_id)


# 	while new_items:
# 		item_id = new_items[0]
# 		item_name = language_new_data['item.minecraft.' + item_id]
# 		item_id_tmp = item_id
# 		if item_id_tmp.endswith('_bricks'):
# 			item_id_tmp = item_id_tmp[:-1]
# 		items_summary.append(f'- **{item_name}**')
# 		new_items.remove(item_id)


# 	# new options
# 	sent_options = set()
# 	for category, option in new_options:
# 		option_name = language_new_data[f'options.{category}.{option}'].split(':')[0]
# 		if option_name in sent_options: continue
# 		sent_options.add(option_name)
# 		options_summary.append(f'- {category}: **{option_name}**')


# 	asset_hashes = []
# 	previous_asset_hashes = await database.get_asset_hashes()

# 	has_new_sounds = False

# 	for asset_dir in assets_json:
# 		asset_data = assets_json[asset_dir]
# 		asset_size = asset_data['size']
# 		asset_hash = asset_data['hash']
# 		asset_hash_start = asset_hash[:2]
# 		asset_url = f'https://resources.download.minecraft.net/{asset_hash_start}/{asset_hash}'
# 		asset_hashes.append(asset_hash)
# 		asset_filename = asset_dir.split('/')[-1]

# 		if asset_filename.endswith('.png'): continue
# 		if asset_filename.endswith('.json'): continue
# 		if asset_hash in previous_asset_hashes: continue
# 		if not has_new_sounds:
# 			await execute_webhook(f'-----------\nNew version: {version_id}\n-----------', s, webhook=sounds_webhook)
# 		has_new_sounds = True
# 		if asset_size > 1000000:
# 			await execute_webhook(f'Asset `{asset_dir}` is too big to send. Here\'s a direct link: {asset_url}', s, webhook=sounds_webhook)
# 		else:
# 			r = await s.get(asset_url)
# 			asset_bytes = await r.read()
# 			await execute_webhook(f'New asset: `{asset_dir}`', s, asset_bytes, filename=asset_filename, webhook=sounds_webhook)
# 	if not test:
# 		print('updating asset hashes')
# 		await database.update_asset_hashes(asset_hashes)

		


# 	print('Summary:')
# 	await execute_webhook('**Summary**', s)
# 	if blocks_summary:
# 		if len(blocks_summary) == 1:
# 			message = 'New block:\n' + blocks_summary[0]
# 		else:
# 			message = 'New blocks:\n' + ('\n'.join(blocks_summary))
# 		print(message)
# 		await execute_webhook(message, s)
		
# 	if items_summary:
# 		if len(items_summary) == 1:
# 			message = 'New item:\n' + items_summary[0]
# 		else:
# 			message = 'New items:\n' + ('\n'.join(items_summary))
# 		print(message)
# 		await execute_webhook(message, s)

# 	if options_summary:
# 		if len(options_summary) == 1:
# 			message = 'New option:\n' + options_summary[0]
# 		else:
# 			message = 'New options:\n' + ('\n'.join(options_summary))
# 		await execute_webhook(message, s)

# 	await execute_webhook('*All new/changed textures in <#698245980377841705>*', s)
# 	if has_new_sounds:
# 		await execute_webhook('*All new sounds in <#698245980377841705>*', s)

# 	print('Finished sending all webhooks')

# 	return


async def main():
	# while True:
	# old_assets = get database
	old_assets = {}
	async for difference in minecraft.diff_versions('1.16.4', '20w49a', old_assets):
		print('DIFFERENCE:', type(difference), difference)
		if isinstance(difference, minecraft.AssetsDiff):
			pass
		elif isinstance(difference, minecraft.DownloadableAssetsDiff):
			print(difference.changed)
		# return
		# await asyncio.sleep(60)

asyncio.get_event_loop().run_until_complete(main())

# # asyncio.ensure_future(main())

# # server.run()

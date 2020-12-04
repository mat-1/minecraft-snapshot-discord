import minecraft
import asyncio
import webhook
import summary
import re

async def make_summary(version_diff, mappings_diff, assets_diff, downloadable_assets_diff):
	pass

async def make_mapping_messages(mappings_diff, new_version_id):
	await webhook.execute_java_webhook(f'New version: **{new_version_id}**')
	displaying_classes = []
	most_changed_classes = {}

	for added_class in mappings_diff.added:
		if not added_class.startswith('net.minecraft.'):
			# if it doesn't start with net.minecraft then we don't care about it
			continue
		added_class_split = added_class.split('.')[2:]
		if len(added_class_split) < 2: continue

		added_class_category_display = added_class_split[1].title()
		added_class_name = ' '.join(added_class_split[2:])

		# add spaces before capitalized words
		added_class_name = re.sub('([A-Z])', r' \1', added_class_name).strip().replace('  ', ' ').lower()

		displaying_classes.append(f'{added_class_category_display}: {added_class_name}')
		for class_level in range(2, len(added_class_split)):
			# get like world, world.level, world.level.block, world.level.block.piston, etc and add it to a list to count how many relevant classes were added
			class_part = '.'.join(added_class_split[:class_level + 1])
			if class_part not in most_changed_classes:
				most_changed_classes[class_part] = 0
			most_changed_classes[class_part] += 1

	for class_name in dict(most_changed_classes):
		# remove classes that dont make up the majority of the c	hanges
		parent_class = '.'.join(class_name.split('.')[:-1])
		if parent_class not in most_changed_classes: continue
		parent_changes = most_changed_classes[parent_class]
		class_changes = most_changed_classes[class_name]
		if class_changes / parent_changes >= .5:
			del most_changed_classes[parent_class]

	most_changed_classes_displaying = sorted(most_changed_classes, key=most_changed_classes.get, reverse=True)[:15]
	most_changed_classes_data = []
	for class_name in most_changed_classes_displaying:
		change_count = most_changed_classes[class_name]
		if change_count > 1:
			class_examples = []
			for new_class in mappings_diff.added:
				if new_class.startswith('net.minecraft.' + class_name + '.'):
					class_examples.append('.'.join(new_class.split('.')[len(class_name.split('.')) + 2:]))
			class_examples_joined = ', '.join(class_examples[:10])
			if len(class_examples) > 10:
				class_examples_joined += f' ...{len(class_examples) - 10} more'
			most_changed_classes_data.append(f'{change_count} new classes related to **{class_name}** ({class_examples_joined})')

	result_content = '\n'.join(most_changed_classes_data)

	file_contents = '\n'.join(mappings_diff.added).encode()
	file_name = f'{new_version_id} new classes.txt'
	await webhook.execute_java_webhook(result_content, file=file_contents, filename=file_name)


async def make_assets_messages(assets_diff, new_version_id):
	await webhook.execute_textures_webhook(f'New version: **{new_version_id}**')
	for removed in assets_diff.removed:
		await webhook.execute_textures_webhook(f'Removed `{removed.filename}`', file=removed.bytes, filename=removed.filename)
	for renamed in assets_diff.renamed:
		await webhook.execute_textures_webhook(f'Renamed `{renamed.old.filename}` to `{renamed.new.filename}`', file=renamed.new.bytes, filename=renamed.new.filename)
	for changed in assets_diff.changed:
		await webhook.execute_textures_webhook(f'Modified `{changed.old.filename}`', file=changed.old.bytes, filename='old ' + changed.old.filename)
		await webhook.execute_textures_webhook(f'->', file=changed.new.bytes, filename=changed.new.filename)
	for added in assets_diff.added:
		await webhook.execute_textures_webhook(f'Added `{added.filename}`', file=added.bytes, filename=added.filename)

async def make_downloadable_assets_messages(downloadable_assets_diff, new_version_id):
	await webhook.execute_sounds_webhook(f'New version: **{new_version_id}**')
	for removed in downloadable_assets_diff.removed:
		await removed.download()
		await webhook.execute_sounds_webhook(f'Removed `{removed.filename}`', file=removed.bytes, filename=removed.filename)
	for renamed in downloadable_assets_diff.renamed:
		await renamed.new.download()
		await webhook.execute_sounds_webhook(f'Renamed `{renamed.old.filename}` to `{renamed.new.filename}`', file=renamed.new.bytes, filename=renamed.new.filename)
	for changed in downloadable_assets_diff.changed:
		await changed.old.download()
		await changed.new.download()
		await webhook.execute_sounds_webhook(f'Modified `{changed.old.filename}`', file=changed.old.bytes, filename='old ' + changed.old.filename)
		await webhook.execute_sounds_webhook(f'->', file=changed.new.bytes, filename=changed.new.filename)
	for added in downloadable_assets_diff.added:
		await added.download()
		await webhook.execute_sounds_webhook(f'Added `{added.filename}`', file=added.bytes, filename=added.filename)





async def main():
	while True:
		# old_assets = get database
		old_assets = {}

		version_diff = None
		mappings_diff = None
		assets_diff = None
		downloadable_assets_diff = None
		lang_diff = None

		old_version_id = '1.16.4'
		new_version_id = '20w49a'
		
		async for difference in minecraft.diff_versions(old_version_id, new_version_id, old_assets):
			if isinstance(difference, minecraft.VersionDiff):
				version_diff = difference
				# await webhook.execute_summary_webhook(f'@everyone New version! **{difference.new.id}**')

			elif isinstance(difference, minecraft.MappingsDiff):
				mappings_diff = difference
				# await make_mapping_messages(difference, new_version_id)

			elif isinstance(difference, minecraft.AssetsDiff):
				assets_diff = difference
				# await make_assets_messages(difference, new_version_id)

			elif isinstance(difference, minecraft.LangDiff):
				lang_diff = difference

			elif isinstance(difference, minecraft.DownloadableAssetsDiff):
				downloadable_assets_diff = difference
				# await make_downloadable_assets_messages(difference, new_version_id)

		await summary.make_summary_messages(
			version_diff=version_diff,
			mappings_diff=mappings_diff,
			assets_diff=assets_diff,
			downloadable_assets_diff=downloadable_assets_diff,
			lang_diff=lang_diff
		)
		
		return # remove this return when its working
		await asyncio.sleep(60)

asyncio.get_event_loop().run_until_complete(main())

# # asyncio.ensure_future(main())

# # server.run()

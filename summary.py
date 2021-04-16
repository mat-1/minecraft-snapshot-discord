import webhook
import difflib

def parse_language(lang_diff):
	category_weights = {
		# how important a category is, from 0 to 1 (default is 0.5)
		'biome': 1,
		'block': .95,
		'item': .9,
		'gamerule': .6,
		'option': .45,
		'death message': .15,
		'sounds': .1,
	}
	categories = {
		'block.': 'block',
		'item.': 'item',
		'options.': 'option',
		'death.': 'death message',
		'subtitles.': 'sounds',
		'biome.': 'biome',
		'gamerule.': 'gamerule',
	}
	category_items = {}

	for lang_item in lang_diff.added:
		lang_key = lang_item.key
		lang_value = lang_item.value
		for category_value in categories:
			category_name = categories[category_value]
			if lang_key.startswith(category_value):
				if category_name not in category_items:
					category_items[category_name] = []
				category_items[category_name].append(lang_value)

	new_features_unsorted = []

	for category_name in category_items:
		category_weight = category_weights.get(category_name, .5)
		items_in_category = category_items.get(category_name, [])
		if len(items_in_category) > 0:
			new_features_unsorted.append({
				'category': category_name,
				'items': items_in_category,
				'weight': category_weight
			})

	new_features_sorted = sorted(new_features_unsorted, key=lambda f: f['weight'], reverse=True)

	return new_features_sorted
		

def group_similar(strings):
	output = []
	added_strings = set()

	for string in strings:
		if string in added_strings: continue
		possibilities = strings
		possibilities.remove(string)
		matches = difflib.get_close_matches(string, possibilities, n=100, cutoff=.6)
		matches = [match for match in matches if match not in added_strings]
		added_strings.update(string)
		added_strings.update(matches)
		output.append([string] + matches)
	return output

async def make_summary_messages(version_diff, mappings_diff, assets_diff, downloadable_assets_diff, lang_diff):
	new_features = parse_language(lang_diff)
	print(new_features)
	for feature in new_features:
		feature_category = feature['category']
		feature_items = feature['items']
		message = []
		if len(feature_items) == 1:
			message.append(f'New {feature_category}:')
		else:
			# if its not 1, make it plural
			message.append(f'New {feature_category}s:')
		items_grouped = group_similar(feature_items)
		for item in items_grouped:
			item_commas = ', '.join(item)
			message.append(f' - **{item_commas}**')

		await webhook.execute_summary_webhook('\n'.join(message))


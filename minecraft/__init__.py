import aiohttp
import asyncio
import zipfile
import hashlib
import json
import os
import io
import re

# s is set by fetch_text or fetch_json
s = None

async def fetch_text(url):
	print('fetching text...', url)
	global s
	if s is None:
		s = aiohttp.ClientSession()

	async with s.get(url) as r:
		data = await r.text()
	print('fetched text')
	return data

async def fetch_json(url):
	print('fetching json...', url)
	global s
	if s is None:
		s = aiohttp.ClientSession()
	async with s.get(url) as r:
		data = await r.json()
	print('fetched json')
	return data

async def fetch_bytes(url):
	print('fetching bytes...', url)
	global s
	if s is None:
		s = aiohttp.ClientSession()
	async with s.get(url) as r:
		data = await r.read()
	print('fetched bytes')
	return data


def sha1_hash(data):
	sha1 = hashlib.sha1()
	sha1.update(data)
	return sha1.hexdigest()

class Diff():
	def __init__(self, new, old):
		self.new = new
		self.old = old

class MappingsDiff(Diff):
	def __init__(self, new, old):
		self.new = new
		self.old = old

		old_mappings = old.get_class_mapping_names()
		new_mappings = new.get_class_mapping_names()

		added_mappings = set()
		removed_mappings = set()

		for new_mapping in new_mappings:
			if new_mapping not in old_mappings:
				added_mappings.add(new_mapping)

		for old_mapping in old_mappings:
			if old_mapping not in new_mappings:
				removed_mappings.add(old_mapping)

		self.added = added_mappings
		self.removed = removed_mappings

	def __str__(self):
		return f'<Added {len(self.added)}, removed {len(self.removed)}>'

class VersionDiff(Diff):
	def __init__(self, new, old):
		self.new = new
		self.old = old

	def __str__(self):
		return f'<{self.old.id} -> {self.new.id}>'


class AssetDiff(Diff):
	def __init__(self, new, old):
		self.new = new
		self.old = old

	def __repr__(self):
		if self.old.filename != self.new.filename:
			return f'<{self.old.filename} -> {self.new.filename}>'
		else:
			return f'<{self.old.filename} modified>'

class LangItem():
	def __init__(self, key, value):
		self.key = key
		self.value = value

	def __repr__(self):
		return f'<{self.key}: {self.value}>'

	def __hash__(self):
		return hash(self.key)

class LangItemDiff(Diff):
	def __init__(self, new, old):
		self.new = new
		self.old = old

	def __repr__(self):
		return f'<{self.old.value} -> {self.new.value}>'

class LangDiff(Diff):
	def __init__(self, new, old):
		self.new = new
		self.old = old

		self.added = []
		self.changed = []
		self.removed = []

		for new_lang_item in new:
			if new_lang_item.key not in old:
				# if it wasn't there before, it's new
				self.added.append(new_lang_item)
			else:
				old_lang_item = old[new_lang_item.key]
				if old_lang_item.value != new_lang_item.value:
					self.changed.append(LangItemDiff(old_lang_item, new_lang_item))

		for old_lang_item in old:
			if old_lang_item.key not in new:
				# it used to be there, but is not there anymore.
				self.removed.append(old_lang_item)

	def __repr__(self):
		return f'<{len(self.added)} added, {len(self.removed)} removed, {len(self.changed)} changed>'


class AssetsDiff(Diff):
	def __init__(self, new, old):
		self.new = new
		self.old = old

		self.added = []
		self.removed = []
		self.changed = []
		self.renamed = []

		for new_asset in new:
			if new_asset in old:
				# either the hash or filename used to be there
				old_asset = old[new_asset]
				if old_asset.hash == new_asset.hash:
					same_hash = True
				else:
					same_hash = False
				if old_asset.filename == new_asset.filename:
					same_name = True
				else:
					same_name = False

				if same_hash and same_name:
					# file is exactly the same
					continue
				elif not same_hash and same_name:
					# the file was modified
					# TODO: make AssetDiff instead of using a plain Diff
					self.changed.append(AssetDiff(new_asset, old_asset))
				elif same_hash and not same_name:
					# the file was renamed
					# TODO: make AssetDiff instead of using a plain Diff
					self.renamed.append(AssetDiff(new_asset, old_asset))
				else:
					# if this happens that means both the file name was hash was changed
					# this should never happen, and if it does it's a bug
					pass
			else:
				# new asset!
				self.added.append(new_asset)

		for old_asset in old:
			if old_asset not in new:
				# file was deleted
				self.removed.append(old_asset)

	def __str__(self):
		return f'<{len(self.added)} added, {len(self.removed)} removed, {len(self.changed)} changed, {len(self.renamed)} renamed>'

class MinecraftDownloadableAsset():
	__slots__ = ('hash', 'bytes', 'filename')

	def __init__(self, filename, hash):
		self.hash = hash
		self.filename = filename
		self.bytes = None

	async def download(self):
		if self.bytes:
			# already downloaded, no need to re-download
			return self.bytes

		asset_hash_start = self.hash[:2]
		asset_url = f'https://resources.download.minecraft.net/{asset_hash_start}/{self.hash}'
		asset_bytes = await fetch_bytes(asset_url)
		self.bytes = asset_bytes
		return asset_bytes

	def __repr__(self):
		return f'<{self.filename}>'
	
	def __hash__(self):
		return hash(self.hash)


class DownloadableAssetsDiff(Diff):
	def __init__(self, new, old):
		self.new = new
		self.old = old

		self.added = []
		self.removed = []
		self.changed = []
		self.renamed = []

		for new_asset in new:
			if new_asset in old:
				# either the hash or filename used to be there
				old_asset = old[new_asset]
				if old_asset.hash == new_asset.hash:
					same_hash = True
				else:
					same_hash = False
				if old_asset.filename == new_asset.filename:
					same_name = True
				else:
					same_name = False

				if same_hash and same_name:
					# file is exactly the same
					continue
				elif not same_hash and same_name:
					# the file was modified
					# TODO: make AssetDiff instead of using a plain Diff
					self.changed.append(AssetDiff(new_asset, old_asset))
				elif same_hash and not same_name:
					# the file was renamed
					# TODO: make AssetDiff instead of using a plain Diff
					self.renamed.append(AssetDiff(new_asset, old_asset))
				else:
					# if this happens that means both the file name was hash was changed
					# this should never happen, and if it does it's a bug
					pass
			else:
				# new asset!
				self.added.append(new_asset)

		for old_asset in old:
			if old_asset not in new:
				# file was deleted
				self.removed.append(old_asset)

	def __str__(self):
		return f'<{len(self.added)} added, {len(self.removed)} removed, {len(self.changed)} changed, {len(self.renamed)} renamed>'

class MinecraftDownloadableAssets():
	__slots__ = ('assets', '_i')


	def __init__(self, assets):
		self.assets = assets
		self._i = -1


	def diff(self, old):
		return DownloadableAssetsDiff(new=self, old=old)


	@staticmethod
	def downloadable_assets_from_objects(data):
		assets = []
		for asset_dir, asset_data in data.items():
			if isinstance(asset_data, dict):
				asset_size = asset_data['size']
				asset_hash = asset_data['hash']
			else:
				# if it's not a dict, it was probably inputted with the format {dir: hash,}
				asset_size = 0
				asset_hash = asset_data

			asset = MinecraftDownloadableAsset(filename=asset_dir, hash=asset_hash)

			if asset.filename.startswith('minecraft/sounds/'):
				assets.append(asset)
			else:
				pass
		return MinecraftDownloadableAssets(assets=assets)

	def get_assets_dict(self):
		data = {}
		for asset in self.assets:
			data[asset.filename] = asset.hash
		return data

	@staticmethod
	async def downloadable_assets_from_url(url):
		sounds = []
		assets_json = await fetch_json(url)
		objects_json = assets_json['objects']
		return MinecraftDownloadableAssets.downloadable_assets_from_objects(objects_json)

	def __iter__(self):
		self._i = -1
		return self

	def __next__(self):
		self._i += 1
		if self._i >= len(self.assets):
			raise StopIteration
		else:
			return self.assets[self._i]

	def __contains__(self, item):
		for asset in self:
			if asset == item:
				return True
			elif hasattr(item, 'filename') and asset.filename == item.filename:
				return True
			elif asset.filename == item:
				return True
		for asset in self:
			# check for the hash last, in case theres duplicate files
			if asset.hash == item:
				return True
			elif hasattr(item, 'hash') and asset.hash == item.hash:
				return True

		return False

	def __getitem__(self, item):
		for asset in self:
			if asset == item:
				return asset
			elif hasattr(item, 'filename') and asset.filename == item.filename:
				return asset
			elif asset.filename == item:
				return asset
		for asset in self:
			# check for the hash last, in case theres duplicate files
			if asset.hash == item:
				return asset
			elif hasattr(item, 'hash') and asset.hash == item.hash:
				return asset

		return None


class MinecraftMappings():
	__slots__ = ('class_mappings',)

	def __init__(self, class_mappings):
		self.class_mappings = class_mappings

	def get_class_mapping_names(self):
		return set(self.class_mappings.values())
	
	@staticmethod
	def mappings_from_text(data):
		class_mappings = {}
		for line in data.splitlines():
			if line.startswith('    '):
				# methodline
				pass
			elif line.startswith('#'):
				# comment
				pass
			elif line.endswith(':'):
				# classline
				class_name, obfuscated_name = line[:-1].split(' -> ')
				class_name = class_name.split('$')[0]
				class_mappings[obfuscated_name] = class_name
		return MinecraftMappings(class_mappings=class_mappings)

	@staticmethod
	async def mappings_from_url(url):
		data = await fetch_text(url)
		return MinecraftMappings.mappings_from_text(data)

	def diff(self, other) -> MappingsDiff:
		return MappingsDiff(new=self, old=other)

class MinecraftAssets():
	__slots__ = ('textures', 'lang', '_i')
	def __init__(self, textures, lang):
		self.textures = list(textures)
		self.lang = lang
		self._i = -1

	def __repr__(self):
		return f'<{len(self.textures)} textures>'

	def diff(self, old):
		return AssetsDiff(new=self, old=old)

	def __iter__(self):
		self._i = -1
		return self

	def __next__(self):
		self._i += 1
		if self._i >= len(self.textures):
			raise StopIteration
		else:
			return self.textures[self._i]

	def __contains__(self, item):
		for texture in self:
			if texture == item:
				return True
			elif hasattr(item, 'filename') and texture.filename == item.filename:
				return True
			elif texture.filename == item:
				return True
		for texture in self:
			# check for the hash last, in case theres duplicate files
			if texture.hash == item:
				return True
			elif hasattr(item, 'hash') and texture.hash == item.hash:
				return True

		return False

	def __getitem__(self, item):
		for texture in self:
			if texture == item:
				return texture
			elif hasattr(item, 'filename') and texture.filename == item.filename:
				return texture
			elif texture.filename == item:
				return texture
		for texture in self:
			# check for the hash last, in case theres duplicate files
			if texture.hash == item:
				return texture
			elif hasattr(item, 'hash') and texture.hash == item.hash:
				return texture

		return None


class MinecraftAsset():
	__slots__ = ('bytes', 'hash', 'filename', 'type')
	def __init__(self, bytes, hash, filename, type):
		self.bytes = bytes
		self.hash = hash
		self.filename = filename
		self.type = type

	@staticmethod
	def type_from_filename(filename):
		filename_split = filename.split('/')
		if filename_split[0] == 'assets' and filename_split[1] == 'minecraft':
			if filename_split[2] == 'textures':
				if filename_split[3] == 'block':
					# block textures
					return 'block texture'
				elif filename_split[3] == 'entity':
					# entity textures
					if filename_split[4] == 'shield':
						return 'shield design'
					elif filename_split[4] == 'banner':
						return 'banner design'
					else:
						return 'entity texture'
				else:
					# unknown, defaults to "texture"
					return 'texture'
			elif filename_split[2] == 'lang':
				return 'language'
		# not a texture? just default to asset
		return 'asset'


	@staticmethod
	def asset_from_file(file):
		filename = file.name
		bytes = file.read()
		hash = sha1_hash(bytes)
		type = MinecraftAsset.type_from_filename(filename)

		if type == 'language':
			return MinecraftLang(bytes=bytes, hash=hash, filename=filename)
		else:
			return MinecraftAsset(bytes=bytes, hash=hash, filename=filename, type=type)

	def __hash__(self):
		return hash(self.hash)

	def __repr__(self):
		return f'<{self.filename}>'

class MinecraftLang(MinecraftAsset):
	__slots__ = ('bytes', 'hash', 'filename', 'type', 'data', 'items', '_i')
	def __init__(self, bytes, hash, filename):
		self.bytes = bytes
		self.hash = hash
		self.filename = filename
		self.type = 'language'

		self.data = json.loads(self.bytes.decode())
		self.items = [LangItem(key, value) for key, value in self.data.items()]

		self._i = -1

	def diff(self, old):
		return LangDiff(new=self, old=old)

	def __iter__(self):
		self._i = -1
		return self

	def __next__(self):
		self._i += 1
		if self._i >= len(self.items):
			raise StopIteration
		else:
			return self.items[self._i]

	def __getitem__(self, key):
		for item in self.items:
			if item.key == key:
				return item
		return None

	def __contains__(self, key):
		for item in self.items:
			if item.key == key:
				return True
		return False

class MinecraftJar():
	__slots__ = ('assets',)
	def __init__(self, assets: MinecraftAssets):
		self.assets = assets

	@staticmethod
	def jar_from_zip(jar):
		assets = set()
		for file in jar.infolist():
			filename = file.filename
			read_file = False
			if filename.startswith('assets/minecraft/') and filename.endswith('.png'):
				read_file = True
			elif filename == 'assets/minecraft/lang/en_us.json':
				read_file = True

			if read_file:
				with jar.open(filename, 'r') as f:
					asset = MinecraftAsset.asset_from_file(f)
					assets.add(asset)

		lang = None
		textures = set()

		for asset in assets:
			if asset.type == 'language':
				lang = asset
			elif asset.filename.startswith('assets/minecraft/textures/'):
				textures.add(asset)
		assets = MinecraftAssets(
			textures=textures,
			lang=lang
		)
		return MinecraftJar(assets=assets)

	@staticmethod
	async def jar_from_url(url):
		jar_compressed = await fetch_bytes(url)
		jar_zip = zipfile.ZipFile(io.BytesIO(jar_compressed), 'r')
		return MinecraftJar.jar_from_zip(jar_zip)

class MinecraftPackages():
	__slots__ = ('jar_url', 'assets_url', 'version', 'client_mappings_url')
	def __init__(self, jar_url, assets_url, version, client_mappings_url):
		self.jar_url = jar_url
		self.assets_url = assets_url
		self.version = version
		self.client_mappings_url = client_mappings_url

	@staticmethod
	def packages_from_data(data):
		assets_url = data['assetIndex']['url']
		version = MinecraftVersion(
			id=data['id'],
			type=data['type'],
			# the package url isn't provided in the package response, but it's not necessary
			packages_url=None,
			time=data['time'],
			release_time=data['releaseTime'],
		)

		downloads = data['downloads']
		jar_url = downloads['client']['url']
		if 'client_mappings' in downloads:
			client_mappings_url = downloads['client_mappings']['url']
		else:
			client_mappings_url = None

		return MinecraftPackages(
			jar_url=jar_url,
			assets_url=assets_url,
			version=version,
			client_mappings_url=client_mappings_url,
		)

	async def get_client_mappings(self) -> MinecraftMappings:
		return await MinecraftMappings.mappings_from_url(self.client_mappings_url)

	async def get_jar_file(self) -> MinecraftJar:
		return await MinecraftJar.jar_from_url(self.jar_url)

	async def get_downloadable_assets(self) -> MinecraftDownloadableAssets:
		return await MinecraftDownloadableAssets.downloadable_assets_from_url(self.assets_url)

	@staticmethod
	async def packages_from_url(url):
		data = await fetch_json(url)
		return MinecraftPackages.packages_from_data(data)



class MinecraftVersion():
	__slots__ = ('id', 'type', 'packages_url', 'time', 'release_time')
	def __init__(self, id, type, packages_url, time, release_time):
		self.id = id
		self.type = type
		self.packages_url = packages_url
		self.time = time
		self.release_time = release_time

	@staticmethod
	def version_from_data(data):
		return MinecraftVersion(
			id=data['id'],
			type=data['type'],
			packages_url=data['url'],
			time=data['time'],
			release_time=data['releaseTime'],
		)

	@staticmethod
	async def version_from_id(version_id=None):
		launcher_manifest_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
		data = await fetch_json(launcher_manifest_url)
		if not version_id:
			return MinecraftVersion.version_from_data(data['versions'][0])
		else:
			for version in data['versions']:
				if version['id'] == version_id:
					return MinecraftVersion.version_from_data(version)

	@staticmethod
	async def get_latest_version():
		return await MinecraftVersion.version_from_id()


	def __str__(self):
		return self.id

	async def get_packages(self) -> MinecraftPackages:
		return await MinecraftPackages.packages_from_url(self.packages_url)

async def get_previous_version() -> MinecraftVersion:
	previous_version_id = '20w48a'

	previous_version_data = await MinecraftVersion.version_from_id(previous_version_id)
	return previous_version_data

async def diff_versions(old_version_id, new_version_id, old_downloadable_assets):
	global s
	new_version = await MinecraftVersion.version_from_id(new_version_id)
	old_version = await MinecraftVersion.version_from_id(old_version_id)

	# VersionDiff
	yield VersionDiff(new_version, old_version)

	new_packages = await new_version.get_packages()
	old_packages = await old_version.get_packages()

	new_mappings = await new_packages.get_client_mappings()
	old_mappings = await old_packages.get_client_mappings()

	# MappingsDiff
	yield new_mappings.diff(old_mappings)

	new_jar = await new_packages.get_jar_file()
	old_jar = await old_packages.get_jar_file()

	# AssetsDiff
	yield new_jar.assets.diff(old_jar.assets)
	# LangDiff
	yield new_jar.assets.lang.diff(old_jar.assets.lang)

	new_downloadable_assets = await new_packages.get_downloadable_assets()
	old_downloadable_assets = await old_packages.get_downloadable_assets()
	# old_downloadable_assets = MinecraftDownloadableAssets.downloadable_assets_from_objects(old_downloadable_assets)

	# DownloadableAssetsDiff
	yield new_downloadable_assets.diff(old_downloadable_assets)

	await s.close()
	s = None

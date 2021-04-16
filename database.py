import motor.motor_asyncio
import os

dburi = os.getenv('dburi')

client = motor.motor_asyncio.AsyncIOMotorClient(dburi)

db = client['minecraft_snapshots']

data_coll = db['data']


async def get_file_hashes():
	data = await data_coll.find_one({
		'_id': 'file hashes'
	})
	return data['data']

async def update_file_hashes(new_data):
	await data_coll.update_one({
		'_id': 'file hashes'
	}, {
		'$set': {
			'data': new_data
		}
	})


async def get_lang():
	data = await data_coll.find_one({
		'_id': 'lang'
	})
	return data['data']

async def update_lang(new_data):
	await data_coll.update_one({
		'_id': 'lang'
	}, {
		'$set': {
			'data': new_data
		}
	})


async def get_version():
	data = await data_coll.find_one({
		'_id': 'version'
	})
	return data['data']


async def update_version(new_data):
	await data_coll.update_one({
		'_id': 'version'
	}, {
		'$set': {
			'data': new_data
		}
	})


async def get_newest_blog_title() -> str:
	data = await data_coll.find_one({
		'_id': 'blog-title'
	})
	return data['data']


async def update_newest_blog_title(new_title: str):
	await data_coll.update_one({
		'_id': 'blog-title'
	}, {
		'$set': {
			'data': new_title
		}
	})


async def get_asset_hashes():
	data = await data_coll.find_one({
		'_id': 'asset hashes'
	})
	return data['data']


async def update_asset_hashes(new_data):
	await data_coll.update_one({
		'_id': 'asset hashes'
	}, {
		'$set': {
			'data': new_data
		}
	})

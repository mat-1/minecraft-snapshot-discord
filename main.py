import minecraft
import asyncio



async def main():
	while True:
		# old_assets = get database
		old_assets = {}
		async for difference in minecraft.diff_versions('1.16.4', '20w49a', old_assets):
			print('DIFFERENCE:', type(difference), difference)
			if isinstance(difference, minecraft.VersionDiff):
				pass
			elif isinstance(difference, minecraft.MappingsDiff):
				pass
			elif isinstance(difference, minecraft.AssetsDiff):
				pass
			elif isinstance(difference, minecraft.DownloadableAssetsDiff):
				print(difference.changed)
		
		return # remove this return when its working
		await asyncio.sleep(60)

asyncio.get_event_loop().run_until_complete(main())

# # asyncio.ensure_future(main())

# # server.run()

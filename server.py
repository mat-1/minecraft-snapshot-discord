from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
	return web.Response(text='Hello, world')

app = web.Application()
app.add_routes(routes)
def run():
	web.run_app(app)
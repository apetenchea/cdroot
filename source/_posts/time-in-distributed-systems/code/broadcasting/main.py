import argparse
from sanic import Sanic, response
from application import Application
from middleware import Middleware
from network import Network


app = Sanic(__name__)


@app.before_server_start
async def setup(app, loop):
    # We have to parse the args again, because Sanic opens a sub-process,
    # and global variables are not preserved on Windows. On Linux, this would
    # work just fine when using a global args variable.
    args = parse_args()
    application = Application()
    middleware = Middleware(args.port, application)
    network = Network([f'http://localhost:{port}' for port in args.ports], middleware)
    app.ctx.application = application
    app.ctx.middleware = middleware
    app.ctx.network = network


@app.route("/", methods=["POST"])
async def broadcast(request):
    data = request.json
    if data is None:
        return response.json({"error": "Invalid JSON"}), 400

    await request.app.ctx.network.process(data)
    return response.empty()


@app.route("/", methods=["GET"])
async def dump(request):
    return response.json(request.app.ctx.application.dump())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int)
    parser.add_argument('--ports', nargs='+', type=int)
    return parser.parse_args()


if __name__ == "__main__":
    app.run(host='localhost', port=parse_args().port)

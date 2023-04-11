import argparse
from flask import Flask, request, jsonify, make_response
from application import Application
from middleware import Middleware
from network import Network

app = Flask(__name__)


@app.route("/", methods=["POST"])
def broadcast():
    global network

    json_data = request.get_json()
    if json_data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    network.process(json_data)
    return make_response()


@app.route("/", methods=["GET"])
def dump():
    return jsonify(application.dump())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int)
    parser.add_argument('--ports', nargs='+', type=int)
    args = parser.parse_args()

    application = Application()
    middleware = Middleware(args.port, application)
    network = Network([f'http://localhost:{port}' for port in args.ports], middleware)

    app.run(host='localhost', port=args.port)

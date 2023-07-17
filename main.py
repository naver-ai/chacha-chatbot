import argparse
from os import path, getcwd

import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    try:
        load_dotenv(path.join(getcwd(), ".env"))
    except:
        raise Exception("Please run setup_admin.py first.")

    parser.add_argument("--production", dest="debug", action="store_false")
    parser.add_argument("--debug", dest="debug", action="store_true")
    parser.add_argument('-p', '--port', dest="port", type=int, help='Port number')

    parser.set_defaults(debug=True, port=8000)

    args = parser.parse_args()

    uvicorn.run("backend.server:app", host="0.0.0.0", port=args.port, reload=args.debug)


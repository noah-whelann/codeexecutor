"""
A sample Hello World server.
"""
import os
import json
from io import StringIO
import sys

from flask import Flask, render_template, request

# pylint: disable=C0103
app = Flask(__name__)


def run_script(script):

    # must parse in here too

    buffer_output = StringIO()
    original_stdout = sys.stdout
    sys.stdout = buffer_output

    exec(script)

    exec_result = buffer_output.getvalue()

    return exec_result


@app.route('/execute', methods=['POST'])
def hello():
    """Return a friendly HTTP greeting."""
    message = "This is it!"

    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    data = request.get_json()
    if data and data.get("script"):
        script = data.get("script")
        result = run_script(script)
        return json.dumps({"result": result,
                          "stdout": "stdout"})
    else:
        return json.dumps({"result": "result"},
                          {"stdout": "stdout"})


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')

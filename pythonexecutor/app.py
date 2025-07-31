"""
A sample Hello World server.
"""
from encodings.punycode import T
from flask import Flask, render_template, request
import os
import json
from io import StringIO
import sys
import tempfile
import subprocess
import


# pylint: disable=C0103
app = Flask(__name__)


def run_script(script):

    main_return_statement = """

if __name__ == '__main__':
    import json
    try:
        result = main()
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
"""

    # must parse in here too

    script_with_main = script + '\n' + main_return_statement


    temp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)

    buffer_output = StringIO()
    original_stdout = sys.stdout
    sys.stdout = buffer_output

    temp.write(script)
    temp_path = temp.name

    try:

        process = subprocess.run(["nsjail", "--quiet", "--chroot", "/", "--",
                   "python3", temp_path], capture_output=True, text=True, timeout=5)
        
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        try:
            result = json.loads(stdout)
        except json.JSONDecodeError:
            result = {"error": "could not parse"}

        return {"result": result, stdout: stderr}
        
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    finally:
        os.remove(temp_path)
        sys.stdout = original_stdout
        buffer_output.close()


@app.route('/execute', methods=['POST'])
def hello():
    """Return a friendly HTTP greeting."""
    message = "This is it!"

    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')
    print("just got executed")
    data = request.get_json()
    if data and data.get("script"):
        script = data.get("script")
        result = run_script(script)
        return json.dumps(result)
    else:
        return json.dumps({"result": "result"},
                          {"stdout": "stdout"})


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')

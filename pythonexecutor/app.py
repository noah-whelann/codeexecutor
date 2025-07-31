from flask import Flask, jsonify, render_template, request
import json
import tempfile
import os
import subprocess
import shutil

app = Flask(__name__)


def run_script(script):

    # Append this to the end of the script that was sent over in order to strictly obtain the result of the "main" function
    main_return_statement = """

if __name__ == '__main__':
    import json
    try:
        result = main()
        print(json.dumps(result))
    except NameError:
        print(json.dumps({"error": "no main()"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
"""

    # must parse in here too

    script_with_main = script.strip() + '\n' + main_return_statement

    # Creates a temporary file for the user's script to be loaded into
    temp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)

    temp.write(script_with_main)
    temp.flush()
    temp.close()
    temp_path = temp.name

    # Ensures that we are working in the correct python directory
    python_path = shutil.which(
        "python3") or shutil.which("python") or "python3"

    try:
        # Runt he users script in a subprocess with nsjail enabled to ensure a safe environment
        process = subprocess.run([
            "nsjail", "--quiet",
            "--disable_clone_newuser",
            "--disable_clone_newns",
            "--disable_proc",
            "--iface_no_lo",
            "--", python_path, temp_path
        ], capture_output=True, text=True, timeout=5)

        stdout = process.stdout
        stderr = process.stderr

        # split the std output into an array of lines
        lines = process.stdout.splitlines()

        if not lines:
            return {"result": {"error": "no output"}}

        # the very last line of the stdout will be the return from main() as we appended this part earlier
        raw_json = lines[-1]
        # Slice the lines up until that last element, all of which will be the return statements
        user_stdout = "\n".join(lines[:-1])
        if user_stdout:
            user_stdout += "\n"

        try:
            result = json.loads(raw_json)
        except json.JSONDecodeError:
            result = {"error": "could not parse", "stdout": stdout}

        return {
            "result": result,
            "stdout": user_stdout,
        }

    except subprocess.TimeoutExpired:
        return {
            "result": {"error": "timeout"},
            "stdout": "",
        }
    finally:
        # clean up the temp file that was created
        os.remove(temp_path)


@app.route('/execute', methods=['POST'])
def execute():
    print("just got executed")
    data = request.get_json()
    if data and data.get("script"):
        script = data.get("script")
        result = run_script(script)
        return jsonify(result)
    else:
        return jsonify({"error": "no script"})


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')

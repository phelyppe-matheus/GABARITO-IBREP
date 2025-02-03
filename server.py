from flask import Flask, request, render_template, jsonify, redirect
from flask_cors import CORS
from cryptography.fernet import Fernet
import os


from strings.tests import strings as test_strings
from strings.capture import strings as capture_strings
from controller import reviewController

key = os.environ.get("ANSWER_KEY")
origin = os.environ.get("ACCEPT_ORIGINS", "*").split(",")
system_url = os.environ.get("SYSTEM_URL", "https://ibrep.alfamaoraculo.com.br/api/set/score")
system_title = os.environ.get("SYSTEM_TITLE", "GABARITO CAMERA")

COLOR_PRIMARY = os.environ.get("COLOR_PRIMARY", "red")
COLOR_SECONDARY = os.environ.get("COLOR_SECONDARY", "blue")
COLOR_AUX = os.environ.get("COLOR_AUX", "white")

app = Flask(__name__, template_folder="templates")
CORS(app, origins=origin)
fernet = Fernet(key)
supported_languages = ["en", "pt"]

@app.route("/", methods=["GET"])
def goto_capture():
    return redirect("/exam/capture")

@app.route("/api/exam/review", methods=["POST"])
def exam_review():
    res = {"err": {}}
    exam = request.json
    try:
        reviewController(exam=exam, response=res)
    except TypeError:
        res['err']["tipo"] = "Check the types of what you've sent."
    except ValueError as e:
        res['err']["wrongValue"] = str(e)
    # except Exception as e:
    #     res['err']["unknown"] = str(e)
    return jsonify(res)


@app.route("/exam/capture", methods=["GET"])
def exam_capture():
    conf = {}
    conf["strings"] = capture_strings
    conf["system_title"] = system_title
    conf["school_url"] = system_url
    conf["colors"] = {
        "primary": COLOR_PRIMARY,
        "secondary": COLOR_SECONDARY,
        "aux": COLOR_AUX
    }
    return render_template('capture.html', conf=conf)


@app.route("/exam/makeqrcode", methods=["GET"])
def make_qr_code():
    lang = request.accept_languages.best_match(supported_languages)
    conf = {
        "strings": test_strings[lang]
    }
    return render_template('makeqrcode.html', conf=conf)


@app.route("/encrypt", methods=["POST"])
def encrypt():
    data = request.json
    if ("msg" not in data): return jsonify({"err": "no message to encrypt"})

    return jsonify({"msg": fernet.encrypt(bytes(data["msg"], "utf-8")).decode("utf-8")})




if __name__ == '__main__':
    app.run()
    app.config['TEMPLATES_AUTO_RELOAD'] = True
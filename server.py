from flask import Flask, request, render_template, jsonify, redirect
from flask_cors import cross_origin
from cryptography.fernet import Fernet
import os


from languages import strings
from controller import reviewController

key = os.environ.get("ANSWER_KEY")
origin = os.environ.get("ACCEPT_ORIGINS", "*").split(",")
ibrep_url = os.environ.get("IBREP_URL", "https://ibrep.alfamaoraculo.com.br/api/set/score")

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
    except Exception as e:
        res['err']["unknown"] = str(e)
    return jsonify(res)


@app.route("/exam/capture", methods=["GET"])
def exam_capture():
    conf = {"ibrep_url": ibrep_url}
    return render_template('capture.html', conf=conf)


@app.route("/exam/makeqrcode", methods=["GET"])
def make_qr_code():
    lang = request.accept_languages.best_match(supported_languages)
    conf = {
        "strings": strings[lang]
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
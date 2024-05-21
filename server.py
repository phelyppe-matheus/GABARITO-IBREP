from flask import Flask, request, render_template, jsonify, redirect
from flask_cors import CORS, cross_origin
import numpy as np
from cryptography.fernet import Fernet
import os
import ast
import json
import utils

from ORMGabarito import AnswerSheetRecognitionModel

app = Flask(__name__, template_folder="templates")
key = os.environ.get("ANSWER_KEY")
fernet = Fernet(key)

@app.route("/", methods=["GET"])
def goto_capture():
    return redirect("/exam/capture")

@app.route("/api/exam/review", methods=["POST"])
@cross_origin(origins="*")
def exam_review():
    res = {"err": {}}
    try:
        exam = request.json
        questionCount = int(exam["questionCount"])
        choiceCount = int(exam["choicesCount"])
        reviewer = AnswerSheetRecognitionModel()
        match exam["examPhotoType"]:
            case 0:
                reviewer.setUp(questionCount, choiceCount, base64=exam["examPhoto"])
            case 1:
                reviewer.setUp(questionCount, choiceCount, buffer=exam["examPhoto"])
            case _:
                res['err']['noSuchPhotoType'] = 'Please provide a valid examPhoto Type'
        qrcodeData = reviewer.getQrCodeData()[0]
        exam.update(utils.qrdata_to_examdata(json.loads(qrcodeData)))
        reviewer.recognise()
        if hasattr(reviewer, "studentsAnswers"):
            reviewer.kernelSize = 1
            res["answers"] = np.char.mod("%c", reviewer.studentsAnswers+65).tolist()
        else:
            res['err']['noSheet'] = "Não pude reconhecer as questões"
        if "correctAnswers" in exam:
            exam["correctAnswers"] = bytes(exam["chosen"], "utf-8")
            exam["correctAnswers"] = fernet.decrypt(exam["correctAnswers"]).decode("utf-8")
            res["correctAnswers"] = exam["correctAnswers"]
            exam["correctAnswers"] = ast.literal_eval(exam["correctAnswers"])
            exam["correctAnswers"] = np.char.mod("%c", np.array(exam["correctAnswers"])+65).tolist()

            if len(exam["correctAnswers"]) == questionCount:
                reviewer.reviewAnswers(exam["correctAnswers"])
                res["score"] = reviewer.score
            elif len(exam["correctAnswers"]) > questionCount:
                res['err']["answers"] = "Respostas demais"
            elif len(exam["correctAnswers"]) < questionCount:
                res['err']["answers"] = "Respostas insuficientes"
        res['err'].update(reviewer.err)
    except TypeError:
        res['err']["tipo"] = "Check the types of what you've sent."
    except ValueError as e:
        res['err']["wrongValue"] = str(e)
    except Exception as e:
        res['err']["unknown"] =str(e)
    return jsonify(res)


@app.route("/exam/capture", methods=["GET"])
def exam_capture():
    return render_template('capture.html')


@app.route("/exam/makeqrcode", methods=["GET"])
def make_qr_code():
    return render_template('makeqrcode.html')


@app.route("/encrypt", methods=["POST"])
def encrypt():
    data = request.json
    if ("msg" not in data): return jsonify({"err": "no message to encrypt"})

    return jsonify({"msg": fernet.encrypt(bytes(data["msg"], "utf-8")).decode("utf-8")})




if __name__ == '__main__':
    app.run()
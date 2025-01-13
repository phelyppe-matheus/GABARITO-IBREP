from flask import Flask, request, render_template, jsonify, redirect
from flask_cors import CORS, cross_origin
import numpy as np
from cryptography.fernet import Fernet
import os
import ast
import json


import utils
from languages import strings
from ORMGabarito import AnswerSheetRecognitionModel

app = Flask(__name__, template_folder="templates")
key = os.environ.get("ANSWER_KEY")
ibrep_url = os.environ.get("IBREP_URL", "https://ibrep.alfamaoraculo.com.br/api/set/score")
fernet = Fernet(key)
supported_languages = ["en", "pt"]

@app.route("/", methods=["GET"])
def goto_capture():
    return redirect("/exam/capture")

@app.route("/api/exam/review", methods=["POST"])
@cross_origin(origins="*")
def exam_review():
    res = {"err": {}}
    try:
        reviewer = AnswerSheetRecognitionModel()
        exam = request.json
        qrcodeData = reviewer.getQrCodeData(base64=exam["examPhoto"])
        if not len(qrcodeData):
            raise ValueError("Não foi possível identificar o qr code")
        else:
            qrcodeData = qrcodeData[0]
        exam.update(utils.qrdata_to_examdata(json.loads(qrcodeData)))
        res.update(utils.qrdata_to_resdata(json.loads(qrcodeData)))

        questionCount = int(exam["questionCount"])
        choiceCount = int(exam["choicesCount"])
        match exam["examPhotoType"]:
            case 0:
                reviewer.setUp(questionCount, choiceCount, base64=exam["examPhoto"])
            case 1:
                reviewer.setUp(questionCount, choiceCount, buffer=exam["examPhoto"])
            case _:
                res['err']['noSuchPhotoType'] = 'Please provide a valid examPhoto Type'
        reviewer.recognise()
        if hasattr(reviewer, "studentsAnswers"):
            reviewer.kernelSize = 1
            res["answers"] = np.char.mod("%c", reviewer.studentsAnswers+65).tolist()
        else:
            res['err']['noSheet'] = "Não pude reconhecer as questões"
        if "correctAnswers" in exam:
            # Decrypt correctAnswers
            exam["correctAnswers"] = bytes(exam["correctAnswers"], "utf-8")
            exam["correctAnswers"] = fernet.decrypt(exam["correctAnswers"]).decode("utf-8")

            print(f"correctAnswers (decriptografado): {exam['correctAnswers']}")  # Para depuração

            # Convertendo a sequência para lista de caracteres
            exam["correctAnswers"] = [*exam["correctAnswers"]]

            # Ajustando as respostas com base no número de alternativas disponíveis
            choices_count = int(exam["choicesCount"])

            # Mapeando as respostas de forma dinâmica
            mapped_answers = [utils.map_answer_to_letter(int(answer), choices_count) for answer in exam["correctAnswers"]]

            print(f"correctAnswers após mapeamento dinâmico: {mapped_answers}")  # Para depuração

            exam["correctAnswers"] = mapped_answers

            if len(exam["correctAnswers"]) == questionCount:
                reviewer.reviewAnswers(exam["correctAnswers"])
                res["score"] = reviewer.score
                res["marked"] = reviewer.ndarrayToJPG(reviewer.markCorrectAnswers(exam["correctAnswers"]))
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
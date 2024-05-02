from flask import Flask, request, render_template, jsonify
from flask_cors import CORS, cross_origin
import numpy as np

from ORMGabarito import AnswerSheetRecognitionModel

app = Flask(__name__, template_folder="templates")

@app.route("/api/exam/review", methods=["POST"])
@cross_origin(origins="*")
def exam_review():
    res = dict()
    exam = request.json
    questionCount = exam["questionCount"]
    choiceCount = exam["choicesCount"]
    reviewer = AnswerSheetRecognitionModel(questionCount, choiceCount)
    reviewer.recognise(base64=exam["examPhoto"])
    if hasattr(reviewer, "studentsAnswers"):
        reviewer.kernelSize = 1
        res["answers"] = np.char.mod("%c", reviewer.studentsAnswers+65).tolist()
    else:
        res['err'] = "Não pude reconhecer a imagem"
    if "correctAnswers" in exam:
        reviewer.reviewAnswers(exam["correctAnswers"])
        res["score"] = reviewer.score,
    return jsonify(res)

@app.route("/exam/review/test", methods=["GET"])
def test_exam_review():
    return render_template('index.html')



if __name__ == '__main__':
    app.run()
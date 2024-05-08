from flask import Flask, request, render_template, jsonify
from flask_cors import CORS, cross_origin
import numpy as np

from ORMGabarito import AnswerSheetRecognitionModel

app = Flask(__name__, template_folder="templates")

@app.route("/api/exam/review", methods=["POST"])
@cross_origin(origins="*")
def exam_review():
    res = dict()
    try:
        exam = request.json
        questionCount = int(exam["questionCount"])
        choiceCount = int(exam["choicesCount"])
        reviewer = AnswerSheetRecognitionModel(questionCount, choiceCount)
        match exam["examPhotoType"]:
            case 0:
                reviewer.recognise(base64=exam["examPhoto"])
            case 1:
                reviewer.recognise(buffer=exam["examPhoto"])
            case _:
                res['err'] = 'please provide the examPhoto Type'
        if hasattr(reviewer, "studentsAnswers"):
            reviewer.kernelSize = 1
            res["answers"] = np.char.mod("%c", reviewer.studentsAnswers+65).tolist()
        else:
            res['err'] = "Não pude reconhecer as questões"
        if "correctAnswers" in exam:
            reviewer.reviewAnswers(exam["correctAnswers"])
            res["score"] = reviewer.score
    except TypeError:
        res['err'] = "Cheque sua tipagem."
    return jsonify(res)


@app.route("/exam/review/test", methods=["GET"])
def test_exam_review():
    return render_template('index.html')



if __name__ == '__main__':
    app.run()
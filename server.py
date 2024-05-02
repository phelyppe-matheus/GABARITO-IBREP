from flask import Flask, request, render_template
import json
import numpy as np

from ORMGabarito import AnswerSheetRecognitionModel

app = Flask(__name__, template_folder="templates")

@app.route("/api/exam/review", methods=["POST"])
def exam_review():
    exam = request.json
    reviewer = AnswerSheetRecognitionModel(exam["correctAnswers"], exam["choicesCount"])
    reviewer.recognise(base64=exam["examPhoto"])
    reviewer.reviewAnswers()
    return json.dumps({
        "score": reviewer.score,
        "answers": np.char.mod("%c", reviewer.studentsAnswers+65).tolist()
    })

@app.route("/exam/review/test", methods=["GET"])
def test_exam_review():
    return render_template('index.html')



if __name__ == '__main__':
    app.run()
from flask import Flask, request
import json
import numpy as np

from ORMGabarito import AnswerSheetRecognitionModel

app = Flask(__name__)

@app.route("/exam/review", methods=["POST"])
def exam_review():
    exam = request.json
    reviewer = AnswerSheetRecognitionModel(exam["correctAnswers"], exam["choicesCount"])
    reviewer.recognise(base64=exam["examPhoto"])
    reviewer.reviewAnswers()
    return json.dumps({
        "score": reviewer.score,
        "answers": np.char.mod("%c", reviewer.studentsAnswers+65).tolist()
    })



if __name__ == '__main__':
    app.run()
import json
import utils

from classes.review import Review

def reviewController(exam, response):
    review = Review()
    examPhotoType = exam["examPhotoType"]
    examPhoto = exam["examPhoto"]
    qrcodeData = review.getQrDataFromImage(examPhoto, examPhotoType)[0];
    choiceCount, questionCount, encryptedAnswers = utils.qrdata_to_examdata(json.loads(qrcodeData))

    exam = review.obfuscateExamPage()
    review.setUpReviewerByPhotoType(examPhoto, examPhotoType, questionCount, choiceCount)
    review.recognizeAnswersFromPhoto()
    review.setRecognizedAnswersToResponse()

    if encryptedAnswers and not hasattr(review.response, "err"):
        correctAnswers = review.decryptAnswers(encryptedAnswers, choiceCount)

        review.reviewStudentAnswers(correctAnswers, questionCount)
    utils.update(response, review.response)
    utils.update(response['err'], review.reviewer.err)


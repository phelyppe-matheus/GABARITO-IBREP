import json
import utils

from classes.review import Review

def reviewController(exam, response):
    review = Review()
    examPhotoType = exam["examPhotoType"]
    examPhoto = exam["examPhoto"]
    qrcodeData = review.getQrDataFromImage(examPhoto, examPhotoType);
    choiceCount, questionCount, encryptedAnswers = utils.qrdata_to_examdata(json.loads(qrcodeData))

    review.setUpReviewerByPhotoType(examPhoto, examPhotoType, questionCount, choiceCount)
    review.recognizeAnswersFromPhoto()
    review.setRecognizedAnswersToResponse()

    if encryptedAnswers and not hasattr(review.response, "err"):
        correctAnswers = review.decryptAnswers(encryptedAnswers, choiceCount)

        review.reviewStudentAnswers(correctAnswers, questionCount)
    utils.update(response, review.response)
    utils.update(response, utils.qrdata_to_resdata(json.loads(qrcodeData)))
    utils.update(response['err'], review.reviewer.err)


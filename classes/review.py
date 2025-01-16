import numpy as np
import json
import utils
import os

from ORMGabarito import AnswerSheetRecognitionModel
from cryptography.fernet import Fernet

key = os.environ.get("ANSWER_KEY")
fernet = Fernet(key)

class Review:
    def __init__(self):
        self.reviewer = AnswerSheetRecognitionModel()
        self.response = {}
        self.response["err"] = {}

    def getQrDataFromImage(self, photo, type):
        match type:
            case 0:
                qrCodeData = self.reviewer.getQrCodeData(base64=photo)
            case 1:
                qrCodeData = self.reviewer.getQrCodeData(buffer=photo)
            case 2:
                raise Exception("Doesn't support link yet")
            case 3:
                qrCodeData = self.reviewer.getQrCodeData(path=photo)
            case _:
                self.response['err']['noSuchPhotoType'] = 'Please provide a valid examPhoto Type'
        return qrCodeData
    
    def blockPageRactFromDetection(self, diffuseY):
        self.reviewer.defuse = [0, 0, self.reviewer.img.shape[1], diffuseY]

    def loadResponse(self):

        if not len(qrcodeData):
            raise ValueError("Não foi possível identificar o qr code")
        else:
            qrcodeData = qrcodeData[0]

        self.response.update(utils.qrdata_to_resdata(json.loads(qrcodeData)))
    
    def setUpReviewerByPhotoType(self, photo, type, questions, choices):
        match type:
            case 0:
                self.reviewer.setUp(questions, choices, base64=photo)
            case 1:
                self.reviewer.setUp(questions, choices, buffer=photo)
            case 2:
                raise Exception("Doesn't support link yet")
            case 3:
                self.reviewer.setUp(questions, choices, path=photo)
            case _:
                self.response['err']['noSuchPhotoType'] = 'Please provide a valid examPhoto Type'
    
        if not hasattr(self.reviewer, "imgWarp"):
            self.response['err']['noWarp'] = "Não pude reconhecer as questões"
    
    def decryptAnswers(self, correctAnswers, choiceCount):
        # Decrypt correctAnswers
        correctAnswersBytes = bytes(correctAnswers, "utf-8")
        correctAnswersDecrypted = fernet.decrypt(correctAnswersBytes).decode("utf-8")

        # Convertendo a sequência para lista de caracteres
        correctAnswers = [*correctAnswersDecrypted]

        # Mapeando as respostas de forma dinâmica
        mappedAnswers = [utils.map_answer_to_letter(int(answer), choiceCount) for answer in correctAnswers]

        return mappedAnswers

    def reviewStudentAnswers(self, answers, count):
        if len(answers) == count:
            self.reviewer.reviewAnswers(answers)
            self.response["score"] = self.reviewer.score
            self.response["marked"] = self.reviewer.ndarrayToJPG(self.reviewer.markCorrectAnswers(answers))
        elif len(answers) > count:
            self.response['err']["answers"] = "Respostas demais"
        elif len(answers) < count:
            self.response['err']["answers"] = "Respostas insuficientes"

    def recognizeAnswersFromPhoto(self):
        self.reviewer.recognise()

    def setRecognizedAnswersToResponse(self):
        if hasattr(self.reviewer, "studentsAnswers"):
            self.reviewer.kernelSize = 1
            self.response["answers"] = self.reviewer.studentsAnswers
        else:
            self.response['err']['noSheet'] = "Não pude reconhecer as questões"
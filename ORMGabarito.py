import cv2
import numpy as np
import base64
import math
from qreader import QReader

qreader = QReader()

class ORMParameters:
    minArea = 1500
    lowThreshold = 0.5
    hitThreshold = 0.7

class AnswerSheetRecognitionModel:
    choiceWidth = 140
    verticalPadding = 0.22
    horizontalPadding = 0.0

    def __init__(self):
        self.contours = []

    def readb64(self, uri):
        encoded_data = uri.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    
    def getQrCodeData(self, path = None, base64=None, buffer=None):
        self.loadimg(path, base64, buffer)
        return qreader.detect_and_decode(self.img)

    def setUp(self, questionCount, choiceCount, path = None, base64=None, buffer=None):
        self.questionCount = questionCount
        self.choiceCount = choiceCount
        self.imgWidth = self.choiceWidth * choiceCount
        self.loadimg(path, base64, buffer)

    def recognise(self):
        self.studentsAnswers = np.int8(np.zeros((self.questionCount))-2)
        self.err = {}

        _, __, ___, imgCanny = self.preProcessing(self.img)
        self.findRectContour(imgCanny)

        if len(self.contours):
            reconAnswers = self.contours[0]
            if reconAnswers.size >= 0:
                self.warpRect(reconAnswers)

                self.getAnswers()
        return 0
    
    def loadimg(self, path = None, base64=None, buffer=None):
        if path:
            self.path = path
            self.img = cv2.imread(self.path)
        elif base64:
            self.img = self.readb64(base64)
        elif buffer:
            nparr = np.frombuffer(buffer, np.uint8)
            self.img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif not hasattr(self, "img"):
            raise Exception("missing image")

    def preProcessing(self, img, imgShape=(0,0)):
        if imgShape == (0,0):
            imgShape = (self.imgWidth, self.imgWidth)
        imgResized = cv2.resize(img, (imgShape[0], imgShape[1]))
        if imgResized.shape[-1] == 3: imgGray = cv2.cvtColor(imgResized, cv2.COLOR_BGR2GRAY)
        else: imgGray = imgResized
        if self.choiceCount >= self.questionCount :imgBlur = cv2.GaussianBlur(imgGray, (5,5), 1)
        else: imgBlur = cv2.GaussianBlur(imgGray, (3,3), 1)
        imgCanny = cv2.Canny(imgBlur,10,50)

        return imgResized, imgGray, imgBlur, imgCanny

    def findContour(self, imgCanny):
        contours, _ = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contours

    def findRectContour(self, imgCanny):
        contours = self.findContour(imgCanny)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > ORMParameters.minArea:
                self.addContourIfRect(contour)
    
    def addContourIfRect(self, contour):
        approx = self.findCornerPoints(contour)
        if 20 > len(approx) > 3:
            self.contours.append(approx)
        self.contours = sorted(self.contours, key=cv2.contourArea, reverse=True)

    def findCornerPoints(self, contour):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.002*peri, True)
        return approx
    
    def reorder(self, points):
        points = points.reshape(-1,2)
        newPoints = np.zeros((4,1,2))
        add = points.sum(1)
        diff = np.diff(points, axis=1)
        newPoints[0] = points[np.argmin(add)]
        newPoints[1] = points[np.argmin(diff)]
        newPoints[2] = points[np.argmax(diff)]
        newPoints[3] = points[np.argmax(add)]

        return newPoints

    def scalePoints(self, points, fx, fy):
        return points*[fx,fy]

    def warpRect(self, answers):
        answers = self.reorder(answers)
        answersSized = self.scalePoints(answers,self.img.shape[1]/self.imgWidth,self.img.shape[0]/self.imgWidth)
        imgGraySized = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.imgHeight = int(self.imgWidth*(self.questionCount / self.choiceCount))

        pt1 = np.float32(answersSized)
        pt2 = np.float32([[0,0], [self.imgWidth, 0], [0, self.imgHeight], [self.imgWidth, self.imgHeight]])

        warp = cv2.getPerspectiveTransform(pt1, pt2)
        self.imgWarp = cv2.warpPerspective(imgGraySized, warp, (self.imgWidth, self.imgHeight))
        bs = int(self.imgWarp.shape[0]/self.questionCount)
        self.bs=bs

        return self.imgWarp
    
    def getChoice(self, r, c):
        return self.imgWarp[self.bs*r:self.bs*(r+1), self.bs*c:self.bs*(c+1)]
    
    def getAnswers(self):
        self.answersProb = np.zeros((self.questionCount, self.choiceCount))
        # _, __, ___, imgCanny = self.preProcessing(self.imgWarp)
        # contours = self.findContour(imgCanny)
        # for i in range(len(contours)):
        #     contour = self.scalePoints(contours[i],700/self.imgWidth,700*19/self.imgWidth)
        #     poly = cv2.fillPoly(self.imgWarp, contour, (0, 255, 0))

        kernelSize = self.kernelSize if hasattr(self, "kernelSize") else 0.3*((self.bs-1)*0.5 - 1) + 0.8

        gaussian2D = np.zeros((self.choiceWidth, self.choiceWidth))
        gaussian2D[self.choiceWidth//2, self.choiceWidth//2] = 1
        gaussian2D = cv2.GaussianBlur(gaussian2D, ((self.choiceWidth//2)*2-3, (self.choiceWidth//2)*2-3), 0)
        answerKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(kernelSize), int(kernelSize)))
        answerKernel = np.pad(answerKernel,(math.floor((self.choiceWidth-kernelSize)/2), math.ceil((self.choiceWidth-kernelSize)/2)))
        clearSpace = (-answerKernel+1)*gaussian2D
        answerKernel = answerKernel / answerKernel.sum()
        clearSpace = clearSpace / clearSpace.sum()

        for i in range(self.questionCount):
            for j in range(self.choiceCount):
                choice = self.getChoice(i, j)

                self.answersProb[i,j] = 1-(choice*answerKernel).sum()/255
            if (self.answersProb[i] > ORMParameters.hitThreshold).sum() > 1:
                if 'duplicate' not in self.err: self.err['duplicate'] = []
                self.err['duplicate'].append(i)
                self.studentsAnswers[i] = self.answersProb[i].argmax()
            elif self.answersProb[i].max() > ORMParameters.hitThreshold:
                self.studentsAnswers[i] = self.answersProb[i].argmax()
            else:
                self.studentsAnswers[i] = -2

    def reviewAnswers(self, correctAnswers):
        correct = 0
        for i in range(len(self.studentsAnswers)):
            correct += correctAnswers[i] == chr(65+self.studentsAnswers[i])
        self.score = correct/self.questionCount


if __name__ == '__main__':

    tests = {
        "test_01": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        "test_02": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        "test_03": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        "test_04": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        "test_05": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        "test_06": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        "test_07": ['d','c','d','c','d','c','b','d','e','c','b','a','?','d','e','c','b','a','d'],
        "test_08": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        "test_09": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        "test_10": ['c','?','c','?','c','d','?','b','d','b','c','d','c','?','e','c','b','a','c'],
        "test_11": ['e','?','?','?','c','?','d','c','e','c','d','e','?','?','?','?','?','?','?'],
        "test_12": ['c','?','c','?','c','d','?','b','d','b','c','d','c','?','e','c','b','a','c'],
        "test_13": ["e","d","c","b","c","b","c","d","c","d","d","c","b","d","c","b","c","d","e"],
        "test_14": ["e","d","c","b","c","b","c","d","c","d","d","c","b","d","c","b","c","d","e"],
        "test_15": ["e","d","c","b","c","b","c","d","c","d","d","c","b","d","c","b","c","d","e"],
        "test_16": ['d','c','d','c','d','c','b','d','e','c','b','a','?','d','e','c','b','a','d'],
        "test_17": [],
    }


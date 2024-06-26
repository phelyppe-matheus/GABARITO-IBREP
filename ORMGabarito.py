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

    def markCorrectAnswers(self, correctAnswers):
        imgShaped = np.zeros(self.imgWarp.shape, dtype = "uint8")
        img = cv2.cvtColor(cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY), cv2.COLOR_GRAY2BGR)
        imgStRight = imgShaped.copy()
        imgStWrong = imgShaped.copy()
        imgCorrect = imgShaped.copy()

        for i in range(self.questionCount):
            y = i*self.bs
            xcorrect = (ord(correctAnswers[i])-65)*self.choiceWidth
            xstudent = self.studentsAnswers[i]*self.choiceWidth
            height = self.choiceWidth
            width = self.choiceWidth

            if xcorrect == xstudent:
                imgStRight = cv2.circle(imgStRight, (xcorrect+width//2, y+height//2), 30, (255), -1)
            if xcorrect != xstudent:
                imgStWrong = cv2.circle(imgStWrong, (xcorrect+width//2, y+height//2), 30, (255), -1)
                imgCorrect = cv2.circle(imgCorrect, (xstudent+width//2, y+height//2), 30, (255), -1)

        imgPoints = cv2.merge((imgStWrong, imgStRight, imgCorrect))
        perspective = cv2.getPerspectiveTransform(self.warpAnswerPoints, self.shapeAnswerPoints)
        imgPointsOriginalPerspective = cv2.warpPerspective(imgPoints, perspective, (img.shape[1], img.shape[0]))
        imgMarked = cv2.add(img, imgPointsOriginalPerspective, (None))

        return imgMarked

    def ndarrayToJPG(self, img):
        _, buffer = cv2.imencode(".jpg", img)
        return 'data:image/jpeg;base64,'+base64.b64encode(buffer).decode("utf-8")

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

        self.shapeAnswerPoints = np.float32(answersSized)
        self.warpAnswerPoints = np.float32([[0,0], [self.imgWidth, 0], [0, self.imgHeight], [self.imgWidth, self.imgHeight]])

        warp = cv2.getPerspectiveTransform(self.shapeAnswerPoints, self.warpAnswerPoints)
        self.imgWarp = cv2.warpPerspective(imgGraySized, warp, (self.imgWidth, self.imgHeight))
        bs = int(self.imgWarp.shape[0]/self.questionCount)
        self.bs=bs

        return self.imgWarp

    def getChoice(self, column, row):
        return self.imgWarp[self.bs*column:self.bs*(column+1), self.bs*row:self.bs*(row+1)]

    def getGivenOrCalculateKernel(self):
        return self.kernelSize if hasattr(self, "kernelSize") else 0.3*((self.bs-1)*0.5 - 1) + 0.8

    def getAnswers(self):
        self.answersProb = np.zeros((self.questionCount, self.choiceCount))

        kernelSize = self.getGivenOrCalculateKernel()

        roundMiddle = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(kernelSize), int(kernelSize)))
        answerKernel = np.pad(roundMiddle,(math.floor((self.choiceWidth-kernelSize)/2), math.ceil((self.choiceWidth-kernelSize)/2)))
        answerKernel = answerKernel / answerKernel.sum()

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
        self.score = (correct/self.questionCount) * 10


if __name__ == '__main__':
    tests = {
        # "test_01.jpg": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        # "test_02.jpg": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        # "test_03.jpg": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        # "test_04.jpg": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        # "test_05.jpg": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        # "test_06.jpg": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        # "test_07.jpg": ['D','C','D','C','D','C','B','D','E','C','B','A','?','D','E','C','B','A','D'],
        # "test_08.jpg": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        # "test_09.jpg": ['?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?','?'],
        # "test_10.jpg": ['C','?','C','?','C','D','?','B','D','B','C','D','C','?','E','C','B','A','C'],
        # "test_11.jpg": ['E','?','?','?','C','?','D','C','E','C','D','E','?','?','?','?','?','?','?'],
        # "test_12.jpg": ['C','?','C','?','C','D','?','B','D','B','C','D','C','?','E','C','B','A','C'],
        # "test_13.jpg": ['E','D','C','B','C','B','C','D','C','D','D','C','B','D','C','B','C','D','E'],
        # "test_14.jpg": ['E','D','C','B','C','B','C','D','C','D','D','C','B','D','C','B','C','D','E'],
        # "test_15.jpg": ['E','D','C','B','C','B','C','D','C','D','D','C','B','D','C','B','C','D','E'],
        # "test_16.jpg": ['D','C','D','C','D','D','B','D','E','C','B','A','?','D','E','C','B','A','D'],
        "test_18.png": ['D','C','D','C','D','D','B','D','E','C','B','A','?','D','E','C','B','A','D','B'],
    }
    choices = []

    for t in tests:
        # try:
            impath = f"test/{t}"
            asrm = AnswerSheetRecognitionModel()
            asrm.setUp(len(tests[t]), 5,  impath)
            asrm.recognise()
            imgMarked = asrm.markCorrectAnswers(tests[f"{t}"])

            kernelSize = asrm.kernelSize if hasattr(asrm, "kernelSize") else 0.3*((asrm.bs-1)*0.5 - 1) + 0.8
            answerKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(kernelSize), int(kernelSize)))
            answerKernel = np.pad(answerKernel,(math.floor((asrm.choiceWidth-kernelSize)/2), math.ceil((asrm.choiceWidth-kernelSize)/2)))
            normalKernel = (answerKernel[::]).astype(np.uint8)
            inverseKernel = (answerKernel == 0).astype(np.uint8)
            print(asrm.studentsAnswers)

            cv2.imshow("img", cv2.resize(asrm.img, (0,0), fx=0.35, fy=0.35))
            cv2.imshow("imgMarked", cv2.resize(imgMarked, (0,0), fx=0.35, fy=0.35))
            cv2.waitKey()
            cv2.destroyAllWindows()

        # except Exception as e:
        #     print(t, ":",e)

import cv2
import numpy as np
import base64

class ORMParameters:
    minArea = 50

class AnswerSheetRecognitionModel:
    choiceWidth = 140
    verticalPadding = 0.22
    horizontalPadding = 0.0

    def __init__(self, questionCount, choiceCount):
        self.contours = []
        self.questionCount = questionCount
        self.choiceCount = choiceCount
        self.imgWidth = self.choiceWidth * choiceCount
    
    def readb64(self, uri):
        encoded_data = uri.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def recognise(self, path = None, base64=None, buffer=None):
        self.loadimg(path, base64, buffer)
        self.preProcessing()
        self.findRectContour()

        if len(self.contours):
            reconAnswers = self.contours[0]
            reconAnswers = self.findCornerPoints(self.contours[0])
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
        else:
            nparr = np.frombuffer(buffer, np.uint8)
            self.img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def preProcessing(self):
        self.imgResized = cv2.resize(self.img, (self.imgWidth, self.imgWidth))
        self.imgGray = cv2.cvtColor(self.imgResized, cv2.COLOR_BGR2GRAY)
        if self.choiceCount >= self.questionCount :self.imgBlur = cv2.GaussianBlur(self.imgGray, (5,5), 1)
        else: self.imgBlur = cv2.GaussianBlur(self.imgGray, (3,3), 1)
        self.imgCanny = cv2.Canny(self.imgBlur,10,50)

    def findContour(self):
        contours, _ = cv2.findContours(self.imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contours

    def findRectContour(self):
        contours = self.findContour()
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > ORMParameters.minArea:
                self.addContourIfRect(contour)
    
    def addContourIfRect(self, contour):
        approx = self.findCornerPoints(contour)
        if len(approx) == 4:
            self.contours.append(contour)
        self.contours = sorted(self.contours, key=cv2.contourArea, reverse=True)

    def findCornerPoints(self, contour):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.002*peri, True)
        return approx
    
    def reorder(self, points):
        points = points.reshape(4,2)
        newPoints = np.zeros((4,1,2))
        add = points.sum(1)
        diff = np.diff(points, axis=1)
        newPoints[0] = points[np.argmin(add)]
        newPoints[1] = points[np.argmin(diff)]
        newPoints[2] = points[np.argmax(diff)]
        newPoints[3] = points[np.argmax(add)]

        return newPoints

    def warpRect(self, answers):
        answers = self.reorder(answers)
        self.imgHeight = int(self.imgWidth*(self.questionCount / self.choiceCount))

        pt1 = np.float32(answers)
        pt2 = np.float32([[0,0], [self.imgWidth, 0], [0, self.imgHeight], [self.imgWidth, self.imgHeight]])

        warp = cv2.getPerspectiveTransform(pt1, pt2)
        self.imgWarp = cv2.warpPerspective(self.imgGray, warp, (self.imgWidth, self.imgHeight))

        return self.imgWarp
    
    def getChoice(self, r, c):
        bs = int(self.imgBlack.shape[0]/self.questionCount)
        self.bs=bs
        return self.imgBlack[bs*r:bs*(r+1), bs*c:bs*(c+1)]
    
    def getAnswers(self):
        _, self.imgBlack = cv2.threshold(self.imgWarp, 130, 255, cv2.THRESH_OTSU)
        self.answersProb = np.zeros((self.questionCount, self.choiceCount))
        self.studentsAnswers = np.int8(np.zeros((self.questionCount)))
        for i in range(self.questionCount):
            for j in range(self.choiceCount):
                choice = self.getChoice(i, j)

                kernelSize = self.kernelSize if hasattr(self, "kernelSize") else 0.3*((self.bs-1)*0.5 - 1) + 0.8

                gs = cv2.getGaussianKernel(self.bs, kernelSize)
                gs = (gs.T * gs)
                self.answersProb[i,j] = 1-(choice*gs).sum()/255
            if self.answersProb[i].max() > 0.5:
                self.studentsAnswers[i] = self.answersProb[i].argmax()
            else:
                self.studentsAnswers[i] = -2
    
    def reviewAnswers(self, correctAnswers):
        correct = 0
        for i in range(len(self.studentsAnswers)):
            correct += correctAnswers[i] == chr(65+self.studentsAnswers[i])
        self.score = correct/self.questionCount

if __name__ == '__main__':
    correctAnswers = [
        'A', 'C', 'B', 'E', 'A', 'C',
        'D', 'D', 'C', 'D', 'A', 'E',
        'D', 'C', 'E'
    ]

    img = open("test/10.jpg", "rb").read()
    asmr = AnswerSheetRecognitionModel(15, 5)
    asmr.kernelSize = 1
    asmr.recognise(buffer=img)
    cv2.imshow("Choice", asmr.getChoice(0,0))
    cv2.imshow("IMG", cv2.resize(asmr.img, None, fx=0.1, fy=0.1))
    asmr.reviewAnswers(correctAnswers)
    print(asmr.score, np.array2string(asmr.studentsAnswers, formatter={"int":lambda x: chr(65+x)}))
    cv2.imshow("bk", cv2.resize(asmr.imgWarp, None, fx=0.4, fy=0.4))
    cv2.waitKey()

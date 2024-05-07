import cv2
import numpy as np
import base64
import math

class ORMParameters:
    minArea = 1500
    hitThreshold = 0.7

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
        self.studentsAnswers = np.int8(np.zeros((self.questionCount))-2)

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

    def warpRect(self, answers):
        answers = self.reorder(answers)
        answersSized = answers*[self.img.shape[1]/self.imgWidth,self.img.shape[0]/self.imgWidth]
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
        for i in range(self.questionCount):
            for j in range(self.choiceCount):
                choice = self.getChoice(i, j)

                kernelSize = self.kernelSize if hasattr(self, "kernelSize") else 0.3*((self.bs-1)*0.5 - 1) + 0.8

                gs = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(kernelSize), int(kernelSize)))
                gs = np.pad(gs,(math.floor((self.choiceWidth-kernelSize)/2), math.ceil((self.choiceWidth-kernelSize)/2)))
                gs = gs/gs.sum()
                self.answersProb[i,j] = 1-(choice*gs).sum()/255
            if self.answersProb[i].max() > ORMParameters.hitThreshold:
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
        "test_11": ['a','?','?','?','c','?','d','c','e','c','d','e','?','?','?','?','?','?','?'],
        "test_12": ['c','?','c','?','c','d','?','b','d','b','c','d','c','?','e','c','b','a','c'],
        "test_13": ["e","d","c","b","c","b","c","d","c","d","d","c","b","d","c","b","c","d","e"],
    }

    showTest = 'test_13'
    showAllTest = True
    asw = 15

    for test in tests:
        # try:
            if showAllTest or showTest == test:
                reviewer = AnswerSheetRecognitionModel(19, 5)
                reviewer.kernelSize = 30
                reviewer.recognise(f"test/{test}.jpg")
                print(
                    f"test/{test}.jpg",
                    np.char.mod("%c", reviewer.studentsAnswers+65).tolist(),
                    tests[test],
                    sep='\n', end='\n'+"="*5*19+'\n')
            if showTest == test:
                # for c in reviewer.findContour():
                #     print(cv2.contourArea(c), len(reviewer.findCornerPoints(c)))
                #     cv2.imshow(f"Gray Image: test/{test}.jpg", cv2.drawContours(reviewer.imgResized, c[1::], -1, (0,255,0), 1))
                #     cv2.waitKey(0)
                if hasattr(reviewer, 'imgWarp'):
                    cv2.imshow(f'img {test}', cv2.resize(reviewer.imgWarp, (0,0), fx=0.25, fy=0.25))
                    cv2.imshow(f'choice {asw}, {reviewer.studentsAnswers[asw]}', reviewer.getChoice(asw, reviewer.studentsAnswers[asw]))
                else: print("Não tem warp")
                if hasattr(reviewer, 'answersProb'): print(reviewer.answersProb)
                else: print('Não há probabilidade de respostas')
                if len(reviewer.contours):
                    i = reviewer.contours[0]
                    peri = cv2.arcLength(i, True)
                    approx = reviewer.reorder(cv2.approxPolyDP(i, 0.002*peri, True))
                    print(cv2.contourArea(i))
        # except Exception as e:
        #     print(test, e)
        #     cv2.imshow(f"Error Gray Image: test/{test}.jpg", reviewer.imgGray)
        
    cv2.waitKey(0)

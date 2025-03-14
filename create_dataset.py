import os
import cv2
import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ORMGabarito import AnswerSheetRecognitionModel, ORMParameters

reviewer = AnswerSheetRecognitionModel()

data_dir = "test/data/tests"
answers_dir = "test/data/answers"
scores = np.array([])
threshold = {
    "test_01.png": 0.4,
    "test_02.png": 0.6,
    "test_03.png": 0.7,
    "test_04.png": 0.5,
    "test_05.png": 0.5,
    "test_06.png": 0.5,
}

if not os.path.exists(answers_dir):
    os.makedirs(answers_dir)

for filename in os.listdir(data_dir):
    filenameWoExt = filename.split(".")[0]
    if filename.endswith(('.png', '.jpg', '.jpeg')) \
        and not glob.glob(os.path.join(answers_dir, f"{filenameWoExt}_q*_c*")):  # Adjust file extensions as needed
        filepath = os.path.join(data_dir, filename)
        try:
            if filename in threshold:
                ORMParameters.hitThreshold = threshold[filename]
            else:
                ORMParameters.hitThreshold = 0.465
            model = AnswerSheetRecognitionModel()
            model.setUp(questionCount=20, choiceCount=5, path=filepath)
            model.datasetinfo = np.zeros((20,5))
            model.recognise()
            scores = np.concatenate((scores, (model.answersProb * 100).astype(int).flatten()))

            unique, counts = np.unique((model.datasetinfo).astype(int).flatten(), return_counts=True)
            plt.bar(x=unique, height=counts)
            plt.waitforbuttonpress()

            for i in range(model.questionCount):
                for j in range(model.choiceCount):
                    choice_img = model.getChoice(i,j)
                    if (model.studentsAnswers[i] == j):
                        choice_filename = os.path.join(answers_dir, f"{filenameWoExt}_q{i+1}_c{j+1}_full.png")
                    else:
                        choice_filename = os.path.join(answers_dir, f"{filenameWoExt}_q{i+1}_c{j+1}_blank.png")

                    cv2.imwrite(choice_filename, choice_img)
        except Exception as e:
            print(f"Error processing {filename}: {e}")


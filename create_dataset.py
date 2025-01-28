import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ORMGabarito import AnswerSheetRecognitionModel

reviewer = AnswerSheetRecognitionModel()

data_dir = "test/data/tests"
answers_dir = "test/data/answers"
scores = np.array([])

if not os.path.exists(answers_dir):
    os.makedirs(answers_dir)

for filename in os.listdir(data_dir):
    if filename.endswith(('.png', '.jpg', '.jpeg')):  # Adjust file extensions as needed
        filepath = os.path.join(data_dir, filename)
        try:
            model = AnswerSheetRecognitionModel()
            model.setUp(questionCount=20, choiceCount=5, path=filepath)
            model.recognise()
            scores = np.concatenate((scores, (model.answersProb * 100).astype(int).flatten()))

            unique, counts = np.unique((model.answersProb * 100).astype(int).flatten(), return_counts=True)
            plt.bar(x=unique, height=counts)
            plt.waitforbuttonpress()

            for i in range(model.questionCount):
              for j in range(model.choiceCount):
                  choice_img = model.getChoice(i,j)
                  choice_filename = os.path.join(answers_dir, f"{filename}_q{i+1}_c{j+1}.png")
                  cv2.imwrite(choice_filename, choice_img)
        except Exception as e:
            print(f"Error processing {filename}: {e}")


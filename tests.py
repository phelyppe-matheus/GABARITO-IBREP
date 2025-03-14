from controller import reviewController

def test_all_good():

    tests = {
        "test_01.jpg": ['C','C','A','D','B','A','B','C','C','A','E','C','D','A','A','B','D','A','C','C'],
        "test_02.png": ['A','C','E','C','B','B','D','C','B','A','E','C','B','C','E','C','D','A','B','B'],
        "test_03.png": ['A','C','E','C','B','B','D','C','B','A','E','C','B','C','E','C','D','A','B','B'],
        "test_04.png": ['C','C','B','E','A','A','C','C','D','B','E','C','E','C','A','A','D','B','C','D'],
        "test_05.png": ['B','C','C','C','B','D','A','C','C','B','E','C','A','A','A','B','D','B','C','B'],
        # TODO: (FIX) ERROR ON "test_05.png" CAUSED BY LITTLE DASH AT BOTTOM RIGHT OF ANSWERS IMG
        "test_06.png": ['B','B','C','C','C','A','A','C','C','B','E','C','D','C','A','B','E','B','C','B'],
        "test_07.png": ['B','C','C','C','C','A','D','B','D','B','E','A','D','A','A','B','D','B','C','B'],
        "test_10.jpg": ['A','C','C','D','?','?','A','C','B','E','C','A','C','C','B','E','C','B','C','B'],
    }

    for nome in tests:
        exam = {
            "examPhotoType": 3,
            "examPhoto": "test/"+nome
        }
        response = {"err": {}, "warning": {}}


        reviewController(exam=exam, response=response)

        response["marked"] = "img"
        if not response['answers'] == tests[nome]:
            print(f"\n{nome}", f"ANSWERED: {response['answers']}", f"EXPECTED: {tests[nome]}", sep="\n")
        else:
            print(".", end="")


def test_test():
    exam = {
        "examPhotoType": 3,
        "examPhoto": "test/test_23.jpg"
    }
    response = {"err": {}, "warning": {}}

    reviewController(exam=exam, response=response)

    response["marked"] = "img"

test_all_good()

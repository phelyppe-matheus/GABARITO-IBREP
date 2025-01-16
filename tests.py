from controller import reviewController

def test_all_good():
    exam = {
        "examPhotoType": 3,
        "examPhoto": "test/test_23.jpg"
    }
    response = {}

    reviewController(exam=exam, response=response)

    response["marked"] = "img"
    print(response)


def test_test():
    exam = {
        "examPhotoType": 3,
        "examPhoto": "test/test_23.jpg"
    }
    response = {}

    reviewController(exam=exam, response=response)

    response["marked"] = "img"
    print(response)

test_all_good()

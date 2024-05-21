def qrdata_to_examdata(qrdata):
    examdata = {}
    examdata["choicesCount"] = qrdata["choices"]
    examdata["questionCount"] =  qrdata["questions"]
    examdata["chosen"] =  qrdata["chosen"]

    return examdata
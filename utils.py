def qrdata_to_examdata(qrdata):
    examdata = {}
    examdata["choicesCount"] = qrdata["c"]
    examdata["questionCount"] =  qrdata["q"]
    examdata["correctAnswers"] = qrdata["r"]

    return examdata

def qrdata_to_resdata(qrdata):
    resdata = {}
    resdata["iddisciplina"] = qrdata["d"]
    resdata["idtipo"] = qrdata["t"]
    resdata["idmodelo"] = qrdata["m"]
    resdata["idprova_impressa"] = qrdata["p"]

    return resdata

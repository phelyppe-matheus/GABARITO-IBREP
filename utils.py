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

def map_answer_to_letter(answer_num, choices_count):
    """
    Mapeia um número (1, 2, 3, ...) para a respectiva letra baseada no número de opções.
    Exemplo: Se choices_count = 5, mapeia 1 -> 'A', 2 -> 'B', 3 -> 'C', 4 -> 'D', 5 -> 'E'.
    """
    # Calcula a letra de acordo com o número de alternativas
    return chr(65 + (answer_num - 1) % choices_count)  # Modulo para garantir o ciclo correto

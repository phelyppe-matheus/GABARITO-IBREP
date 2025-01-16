import collections.abc

def qrdata_to_examdata(qrdata):
    qrdata["c"] = int(qrdata["c"])
    qrdata["q"] = int(qrdata["q"])

    return qrdata["c"], qrdata["q"], qrdata["r"]

def qrdata_to_resdata(qrdata):
    resdata = {}
    resdata["iddisciplina"] = qrdata["d"]
    resdata["idtipo"] = qrdata["t"]
    resdata["idmodelo"] = qrdata["m"]
    resdata["idprova_impressa"] = qrdata["p"]

    return resdata


def map_answer_to_letter(answerNum, choicesCount):
    """
    Mapeia um número (1, 2, 3, ...) para a respectiva letra baseada no número de opções.
    Exemplo: Se choicesCount = 5, mapeia 1 -> 'A', 2 -> 'B', 3 -> 'C', 4 -> 'D', 5 -> 'E'.
    """
    # Calcula a letra de acordo com o número de alternativas
    return chr(65 + (answerNum) % choicesCount)  # Modulo para garantir o ciclo correto

def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

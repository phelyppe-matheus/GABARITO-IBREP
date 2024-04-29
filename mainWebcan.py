import cv2
import pickle
import extrairGabarito as exG


with open('campos.pkl', 'rb') as arquivo:
    campos = pickle.load(arquivo)

gabaritoCorreto = {
    1: 'A', 8: 'C', 12: 'B', 20: 'E', 21: 'A', 28: 'C',
    34: 'D', 39: 'D', 42: 'C', 49: 'D', 51: 'A', 60: 'E',
    64: 'D', 68: 'C', 75: 'E', 76: 'A', 82: 'B', 86: 'A',
    93: 'C', 99: 'D'
}

# video = cv2.VideoCapture()
# ip = "https://192.168.0.17:8080/video"
# video.open(ip)

reducao = 0.70

while True:
    # _, imagem = video.read()
    imagem = cv2.imread("2.jpg")
    imagem = cv2.resize(imagem, (600, 700))
    gabarito, bbox = exG.extrairMaiorCtn(imagem)
    imgGray = cv2.cvtColor(gabarito, cv2.COLOR_BGR2GRAY)
    ret, imgTh = cv2.threshold(imgGray, 150, 255, cv2.THRESH_BINARY_INV)

    respostasDetectadas = []
    acertos = 0

    for idcampo, vg in enumerate(campos):
        x_centro, y_centro = vg[0] + vg[2] / 2, vg[1] + vg[3] / 2
        w_reduzido, h_reduzido = int(vg[2] * reducao), int(vg[3] * reducao)
        x_novo = int(x_centro - w_reduzido / 2)
        y_novo = int(y_centro - h_reduzido / 2)

        campo = imgTh[y_novo:y_novo + h_reduzido, x_novo:x_novo + w_reduzido]
        if campo.size == 0:
            continue

        tamanho = campo.size
        pretos = cv2.countNonZero(campo)
        percentual = (pretos / tamanho) * 100

        alternativaMarcada = chr(65 + (idcampo % 5))
        cor_retangulo = (255, 0, 0)
        if idcampo + 1 in gabaritoCorreto:
            if percentual >= 30 and alternativaMarcada == gabaritoCorreto[idcampo + 1]:
                cor_retangulo = (0, 255, 0)
                acertos += 1
            elif percentual >= 30:
                cor_retangulo = (0, 0, 255)


        cv2.rectangle(gabarito, (x_novo, y_novo), (x_novo + w_reduzido, y_novo + h_reduzido), cor_retangulo, 2)
        cv2.rectangle(imgTh, (x_novo, y_novo), (x_novo + w_reduzido, y_novo + h_reduzido), cor_retangulo, 1)

    pontuacao = acertos * 0.5


    cv2.putText(imagem, f'ACERTOS: {acertos}, NOTA: {pontuacao}', (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0),
                3)

    cv2.imshow('img', imagem)
    cv2.imshow('Gabarito', gabarito)
    cv2.imshow('IMG TH', imgTh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
video.release()

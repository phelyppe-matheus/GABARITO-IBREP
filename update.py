import pickle

# Define as coordenadas para cada questão e suas 5 alternativas
novos_campos = []
x_inicial = 10
y_inicial = 20
largura = 50
altura = 50
espaco_horizontal = 55
espaco_vertical = 40

# Gerar as coordenadas para 20 questões, cada uma com 5 alternativas
for questao in range(20):
    for alternativa in range(5):
        x = x_inicial + alternativa * espaco_horizontal
        y = y_inicial + questao * espaco_vertical
        novos_campos.append((x, y, largura, altura))

novas_resp = ['A', 'B', 'C', 'D', 'E'] * 20  # Cada questão tem as alternativas de A a E

# Escrevendo no arquivo campos.pkl
with open('campos.pkl', 'wb') as arquivo:
    pickle.dump(novos_campos, arquivo)

# Escrevendo no arquivo resp.pkl
with open('resp.pkl', 'wb') as arquivo:
    pickle.dump(novas_resp, arquivo)

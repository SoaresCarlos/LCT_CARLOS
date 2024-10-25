import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import os  

# Configurações do sistema
FonteAlimentacao = 5.0
AmplitudePWM = 2.5
NumeroAmostras = 900  

# Configuração da comunicação serial com o Arduino
try:
    ser = serial.Serial('COM9', 9600, timeout=1)
    time.sleep(2)  # Aguarda o Arduino inicializar
    print("Conexão com Arduino estabelecida.")
except serial.SerialException as e:
    print(f"Erro ao abrir a porta serial: {e}")
    exit()

# Funções
def calcular_pwm(amplitude, fonte_alimentacao):
    return int((amplitude / fonte_alimentacao) * 255)

def calcular_temperatura(valor_adc):
    tensao = (valor_adc / 1023.0) * 5.0
    return (tensao - 0.5) * 100

lista_tempo = []
lista_pwm = []
lista_temperatura = []

tempo_inicial = time.time()

# Definir o caminho do arquivo CSV
caminho_diretorio = "C:/Users/Carlos Soares/Desktop/LINCE/Testes_Only_python/"
if not os.path.exists(caminho_diretorio):
    os.makedirs(caminho_diretorio)

caminho_arquivo = os.path.join(caminho_diretorio, "dados.csv")  # Adicionando o nome do arquivo

# Função para salvar os dados em um arquivo CSV
def salvar_dados_csv(caminho_arquivo):
    try:
        with open(caminho_arquivo, mode='w', newline='') as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv, delimiter=',')
            escritor_csv.writerow(['Tempo (s)', 'PWM', 'Temperatura (ºC)'])
            for i in range(len(lista_tempo)):
                escritor_csv.writerow([lista_tempo[i], lista_pwm[i], lista_temperatura[i]])
    except OSError as e:
        print(f"Erro ao salvar arquivo CSV: {e}")

def atualizar_grafico(i):
    tempo_corrente = time.time() - tempo_inicial
    lista_tempo.append(tempo_corrente)

    pwm = calcular_pwm(AmplitudePWM, FonteAlimentacao)
    print(f"PWM enviado: {pwm}")
    ser.write(f'{pwm}\n'.encode())
    lista_pwm.append(pwm)

    temperatura = None  # Inicializa como None
    if ser.in_waiting > 0:
        try:
            leitura_adc = int(ser.readline().decode().strip())
            temperatura = calcular_temperatura(leitura_adc)
            print(f'Tempo: {tempo_corrente:.2f}s, PWM: {pwm}, Temperatura: {temperatura:.2f} ºC')
        except ValueError:
            print("Erro ao converter leitura do sensor.")
    else:
        print("Nenhuma leitura de temperatura disponível.")

    if temperatura is not None:
        lista_temperatura.append(temperatura)
    else:
        lista_temperatura.append(float('nan'))  # Adiciona um valor nulo para manter o comprimento

    # Verifica se as listas têm o mesmo comprimento
    if len(lista_tempo) > 0 and len(lista_pwm) > 0 and len(lista_temperatura) >= len(lista_tempo):
        ax1.clear()
        ax2.clear()

        ax1.plot(lista_tempo, lista_pwm, label="Sinal PWM aplicado")
        ax1.set_xlabel("Tempo (s)")
        ax1.set_ylabel("PWM (0-255)")
        ax1.set_title("Sinal de Entrada (PWM)")
        ax1.legend()
        ax1.grid()

        ax2.plot(lista_tempo, lista_temperatura, label="Temperatura medida (ºC)", color='r')
        ax2.set_xlabel("Tempo (s)")
        ax2.set_ylabel("Temperatura (ºC)")
        ax2.set_title("Sinal de Saída (Temperatura)")
        ax2.legend()
        ax2.grid()

    if len(lista_tempo) >= NumeroAmostras:
        plt.close(fig)

# Configuração do gráfico
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
ani = FuncAnimation(fig, atualizar_grafico, interval=1000, cache_frame_data=False)

plt.tight_layout()
plt.show()

# Salvar os dados após a visualização do gráfico
salvar_dados_csv(caminho_arquivo)

ser.close()
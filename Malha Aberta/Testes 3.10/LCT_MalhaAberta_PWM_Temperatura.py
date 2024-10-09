import serial
import time
import csv
import matplotlib.pyplot as plt
import os

# Configurações da porta serial
arduino = serial.Serial('COM9', 9600, timeout=1)  # Altere para a sua porta
time.sleep(2)

# Função para enviar as configurações ao Arduino
def enviar_configuracao(valores_pwm, tempo_por_amostra):
    for pwm_value in valores_pwm:
        arduino.write(f"{pwm_value},{tempo_por_amostra}\n".encode())
        time.sleep(1)  # Aguarda um tempo para garantir que o Arduino receba os dados corretamente

# Definir variáveis de configuração
valores_pwm = [100, 50, 200, 0]  # Valores de PWM
tempo_amostragem = 600  # Tempo total de amostragem (em segundos)
tempo_por_amostra = tempo_amostragem / len(valores_pwm)  # Tempo para cada valor de PWM

# Envia as configurações ao Arduino
enviar_configuracao(valores_pwm, tempo_por_amostra)

# Inicializando variáveis de amostragem
amostras = []

# Criando diretório para armazenar os dados
caminho_diretorio = "C:/pasta1/armazem2/"
if not os.path.exists(caminho_diretorio):
    os.makedirs(caminho_diretorio)

# Abrindo arquivo CSV para salvar amostras
caminho_arquivo = os.path.join(caminho_diretorio, "amostras_temperatura.csv")
with open(caminho_arquivo, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Tempo (s)", "PWM Aquecedor", "Temperatura (°C)"])

    # Inicializa listas para armazenar os dados para o gráfico
    tempos = []
    temperaturas = []
    pwm_values = []

    plt.ion()  # Modo interativo
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

    # Configurações do gráfico de temperatura
    ax1.set_title("Temperatura do Aquecedor vs Tempo")
    ax1.set_xlabel("Tempo (s)")
    ax1.set_ylabel("Temperatura (°C)")
    line1, = ax1.plot(tempos, temperaturas, 'r-', label='Temperatura Aquecedor')
    
    # Configurações do gráfico de PWM
    ax2.set_title("PWM vs Tempo")
    ax2.set_xlabel("Tempo (s)")
    ax2.set_ylabel("PWM")
    line2, = ax2.plot(tempos, pwm_values, 'b-', label='PWM Aquecedor')

    plt.tight_layout()
    plt.legend()
    start_time = time.time()

    # Loop de amostragem
    for pwm_value in valores_pwm:
        pwm_start_time = time.time()  # Tempo em que este valor de PWM começou
        while (time.time() - pwm_start_time) < tempo_por_amostra:
            current_time = time.time() - start_time

            # Recebe dados do Arduino
            data = arduino.readline().decode().strip()
            if data:
                try:
                    temperatura, pwm_read = map(float, data.split(","))
                    print(f"Tempo: {current_time:.2f} s, Temp: {temperatura} °C, PWM: {pwm_read}")

                    # Atualiza dados para os gráficos
                    tempos.append(current_time)
                    temperaturas.append(temperatura)
                    pwm_values.append(pwm_read)

                    # Atualiza gráfico de temperatura
                    line1.set_xdata(tempos)
                    line1.set_ydata(temperaturas)
                    ax1.relim()
                    ax1.autoscale_view(True, True, True)

                    # Atualiza gráfico de PWM
                    line2.set_xdata(tempos)
                    line2.set_ydata(pwm_values)
                    ax2.relim()
                    ax2.autoscale_view(True, True, True)

                    plt.draw()
                    plt.pause(0.1)

                    # Salva os dados no CSV
                    writer.writerow([current_time, pwm_read, temperatura])
                except ValueError:
                    print("Erro ao processar dados recebidos do Arduino:", data)

            time.sleep(1)  # Intervalo de amostragem entre leituras

    plt.ioff()
    plt.show()

# Fechando conexão serial
arduino.close()

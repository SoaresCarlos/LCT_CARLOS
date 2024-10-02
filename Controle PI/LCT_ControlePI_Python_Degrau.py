import serial
import time
import csv
import matplotlib.pyplot as plt
import os

# Configurações da porta serial
arduino = serial.Serial('COM9', 9600, timeout=1)  # Altere para a sua porta
time.sleep(2)

# Função para enviar as configurações ao Arduino
def enviar_configuracao(temperatura_alvo, kp, ki, duracao_amostragem, numero_amostras):
    arduino.write(f"{duracao_amostragem},{numero_amostras},{temperatura_alvo},{kp},{ki}\n".encode())

# Definir variáveis de configuração
temperatura_alvo = 40.0
kp = 0.5   # Constante proporcional
ki = 0.2   # Constante integrativa
duracao_amostragem = 600  # 10 minutos = 600 segundos
numero_amostras = 600  # Número de amostras

# Envia as configurações ao Arduino
enviar_configuracao(temperatura_alvo, kp, ki, duracao_amostragem, numero_amostras)

# Inicializando variáveis de amostragem
intervalo_amostras = duracao_amostragem / numero_amostras
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
    for amostra in range(numero_amostras):
        current_time = time.time() - start_time  # Inclui o tempo de aquecimento desde o início

        # Recebe dados do Arduino
        data = arduino.readline().decode().strip()
        if data:
            try:
                temperatura, pwm_value = map(float, data.split(","))
                print(f"Tempo: {current_time:.2f} s, Temp: {temperatura} °C, PWM: {pwm_value}")

                # Atualiza dados para os gráficos
                tempos.append(current_time)
                temperaturas.append(temperatura)
                pwm_values.append(pwm_value)

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
                writer.writerow([current_time, pwm_value, temperatura])
            except ValueError:
                print("Erro ao processar dados recebidos do Arduino:", data)

        time.sleep(intervalo_amostras)

    plt.ioff()
    plt.show()

# Fechando conexão serial
arduino.close()

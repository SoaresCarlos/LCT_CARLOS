import serial
import time
import csv
import matplotlib.pyplot as plt
import os

# Configurações da porta serial
arduino = serial.Serial('COM9', 9600, timeout=1)  # Altere para a sua porta
time.sleep(2)

# Função para enviar as configurações ao Arduino

def enviar_configuracao(temperatura_alvo, kp, ki, kd, duracao_amostragem, numero_amostras):
    arduino.write(f"{duracao_amostragem},{numero_amostras},{temperatura_alvo},{kp},{ki},{kd}\n".encode())

# Definir variáveis de configuração
temperatura_alvo = 30.0
kp = 2.0   # Constante proporcional
ki = 0.1   # Constante integrativa
kd = 0.05  # Constante derivativa
duracao_amostragem = 600  # 10 minutos = 600 segundos
numero_amostras = 600  # Número de amostras

# Envia as configurações ao Arduino
enviar_configuracao(temperatura_alvo, kp, ki, kd, duracao_amostragem, numero_amostras)

# Inicializando variáveis de amostragem
intervalo_amostras = duracao_amostragem / numero_amostras
amostras = []

# Criando diretório para armazenar os dados
caminho_diretorio = "C:/Users/Carlos Soares/Desktop/LINCE/LCT_Carlos/Amostras Coletadas"
if not os.path.exists(caminho_diretorio):
    os.makedirs(caminho_diretorio)

# Abrindo arquivo CSV para salvar amostras em formato numérico (com delimitador ponto e vírgula)
caminho_arquivo = os.path.join(caminho_diretorio, "amostras_numericas.csv")
with open(caminho_arquivo, mode='w', newline='') as file:
    writer = csv.writer(file, delimiter=';')  # Usando ponto e vírgula como delimitador
    writer.writerow(["Número de Amostra", "Temperatura (°C)", "PWM Aquecedor"])

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
    for amostra in range(1, numero_amostras + 1):
        current_time = time.time() - start_time

        # Recebe dados do Arduino
        data = arduino.readline().decode().strip()
        if data:
            try:
                temperatura, pwm_value = map(float, data.split(","))
                print(f"Amostra: {amostra}, Tempo: {current_time:.2f} s, Temp: {temperatura} °C, PWM: {pwm_value}")

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

                # Salva os dados numéricos no CSV (número de amostra, temperatura, PWM)
                writer.writerow([amostra, round(temperatura, 2), int(pwm_value)])
            except ValueError:
                print("Erro ao processar dados recebidos do Arduino:", data)

        time.sleep(intervalo_amostras)

    plt.ioff()
    plt.show()

# Fechando conexão serial
arduino.close()

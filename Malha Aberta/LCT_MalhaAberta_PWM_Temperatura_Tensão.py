import serial
import time
import csv
import matplotlib.pyplot as plt
import os

# Configurações da porta serial
arduino = serial.Serial('COM9', 9600, timeout=1)  # Altere para a sua porta
time.sleep(2)

# Função para enviar as configurações ao Arduino
def enviar_configuracao(valores_pwm, duracao_amostragem):
    num_amostras = len(valores_pwm)
    arduino.write(f"{duracao_amostragem},{num_amostras},{','.join(map(str, valores_pwm))}\n".encode())

# Definir variáveis de configuração
valores_pwm = [100, 50, 200, 0]  # Lista de valores PWM
duracao_amostragem = 600  # 10 minutos = 600 segundos
tensao_fonte = 5.0  # Tensão de alimentação da fonte (em volts)

# Calcular o tempo por amostra
tempo_por_amostra = duracao_amostragem / len(valores_pwm)

# Enviar as configurações para o Arduino
enviar_configuracao(valores_pwm, duracao_amostragem)

# Inicializando variáveis de amostragem
amostras = []
tempos = []
temperaturas = []
pwm_values = []
tensoes_aplicadas = []

# Criando diretório para armazenar os dados
caminho_diretorio = "C:/pasta1/armazem2/"
if not os.path.exists(caminho_diretorio):
    os.makedirs(caminho_diretorio)

# Abrindo arquivo CSV para salvar amostras 
caminho_arquivo = os.path.join(caminho_diretorio, "amostras_temperatura.csv")
with open(caminho_arquivo, mode='w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(["Tempo (s)", "PWM Aquecedor", "Temperatura (°C)", "Tensão Aplicada (V)"])

    # Inicializando o modo interativo do gráfico
    plt.ion()
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 8))

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

    # Configurações do gráfico de tensão
    ax3.set_title("Tensão Aplicada vs Tempo")
    ax3.set_xlabel("Tempo (s)")
    ax3.set_ylabel("Tensão (V)")
    line3, = ax3.plot(tempos, tensoes_aplicadas, 'g-', label='Tensão Aplicada')

    plt.tight_layout()
    plt.legend()
    start_time = time.time()

    # Loop de amostragem
    for i in range(len(valores_pwm)):
        pwm_value = valores_pwm[i]
        current_time = time.time() - start_time

        # Calcular a tensão aplicada
        tensao_aplicada = (pwm_value / 255.0) * tensao_fonte

        # Recebe dados do Arduino
        data = arduino.readline().decode().strip()
        if data:
            try:
                temperatura, pwm_lido = map(float, data.split(","))
                print(f"Tempo: {current_time:.2f} s, Temp: {temperatura} °C, PWM: {pwm_lido}, Tensão: {tensao_aplicada:.2f} V")

                # Atualiza os dados para os gráficos
                tempos.append(current_time)
                temperaturas.append(temperatura)
                pwm_values.append(pwm_lido)
                tensoes_aplicadas.append(tensao_aplicada)

                # Atualiza o gráfico de temperatura
                line1.set_xdata(tempos)
                line1.set_ydata(temperaturas)
                ax1.relim()
                ax1.autoscale_view(True, True, True)

                # Atualiza o gráfico de PWM
                line2.set_xdata(tempos)
                line2.set_ydata(pwm_values)
                ax2.relim()
                ax2.autoscale_view(True, True, True)

                # Atualiza o gráfico de tensão
                line3.set_xdata(tempos)
                line3.set_ydata(tensoes_aplicadas)
                ax3.relim()
                ax3.autoscale_view(True, True, True)

                plt.draw()
                plt.pause(0.1)

                # Salva os dados no CSV com separador ";"
                writer.writerow([current_time, pwm_lido, temperatura, tensao_aplicada])
            except ValueError:
                print("Erro ao processar dados recebidos do Arduino:", data)

        time.sleep(tempo_por_amostra)

    plt.ioff()
    plt.show()

# Fechando conexão serial
arduino.close()

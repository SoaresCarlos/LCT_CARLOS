import serial
import time
import csv
import os
import matplotlib.pyplot as plt

# Inicializar a comunicação serial (ajuste a porta serial conforme necessário)
arduino = serial.Serial('COM3', 9600)  # Substitua 'COM3' pela porta correta no seu sistema
time.sleep(2)  # Aguarde a inicialização da porta

# Definir variáveis de configuração
valores_pwm = [100, 50, 200, 0]  # Lista de valores PWM
duracao_amostragem = 600  # 10 minutos = 600 segundos
tensao_fonte = 5.0  # Tensão de alimentação da fonte (em volts)

# Calcular o tempo por amostra
tempo_por_amostra = duracao_amostragem / len(valores_pwm)


# Definindo os setpoints para os valores de PWM conhecidos
pwmsetpoint = {
    0: 25,    # PWM 0 -> Temperatura esperada 25°C
    50: 30,   # PWM 50 -> Temperatura esperada 30°C
    100: 40,  # PWM 100 -> Temperatura esperada 40°C
    200: 55,  # PWM 200 -> Temperatura esperada 55°C
}

# Função para obter o setpoint baseado no PWM atual
def get_setpoint_from_pwm(pwm_value):
    return pwmsetpoint.get(pwm_value, None)  # Retorna None se o PWM não estiver no dicionário

# Inicializando listas de dados
tempos = []
temperaturas = []
setpoints = []  # Lista para armazenar as temperaturas setpoint
pwm_values = []
tensoes_aplicadas = []

# Abrindo arquivo CSV para salvar amostras com separador ";"
caminho_arquivo = os.path.join(os.getcwd(), "amostras_temperatura.csv")
with open(caminho_arquivo, mode='w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(["Tempo (s)", "PWM Aquecedor", "Temperatura (°C)", "Tensão Aplicada (V)", "Setpoint (°C)"])

    # Inicializando o modo interativo do gráfico
    plt.ion()
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 8))

    # Configurações do gráfico de temperatura
    ax1.set_title("Temperatura do Aquecedor vs Tempo")
    ax1.set_xlabel("Tempo (s)")
    ax1.set_ylabel("Temperatura (°C)")
    line1, = ax1.plot(tempos, temperaturas, 'r-', label='Temperatura Medida')
    line2, = ax1.plot(tempos, setpoints, 'b--', label='Setpoint (Temperatura Ideal)', linestyle='dotted')

    # Configurações do gráfico de PWM
    ax2.set_title("PWM vs Tempo")
    ax2.set_xlabel("Tempo (s)")
    ax2.set_ylabel("PWM (%)")
    line3, = ax2.plot(tempos, pwm_values, 'b-', label='PWM Aquecedor')

    # Configurações do gráfico de Tensão Aplicada
    ax3.set_title("Tensão Aplicada vs Tempo")
    ax3.set_xlabel("Tempo (s)")
    ax3.set_ylabel("Tensão (V)")
    line4, = ax3.plot(tempos, tensoes_aplicadas, 'g-', label='Tensão Aplicada')

    plt.tight_layout()
    plt.legend()

    # Início da coleta de dados
    start_time = time.time()

    for i, pwm_value in enumerate(valores_pwm):
        current_time = time.time() - start_time
        tempo_atual = current_time

        # Enviar valor de PWM para o Arduino
        arduino.write(f'{pwm_value}\n'.encode())  # Enviar valor de PWM via serial
        time.sleep(0.1)  # Aguarde a resposta

        # Receber temperatura lida pelo sensor do Arduino
        if arduino.in_waiting > 0:
            temperatura_lida = float(arduino.readline().decode().strip())

            # Obter setpoint e calcular a tensão aplicada
            setpoint_atual = get_setpoint_from_pwm(pwm_value)
            tensao_aplicada = pwm_value / 255 * tensao_fonte

            # Adicionando dados para plotagem
            tempos.append(tempo_atual)
            temperaturas.append(temperatura_lida)
            setpoints.append(setpoint_atual)
            pwm_values.append(pwm_value)
            tensoes_aplicadas.append(tensao_aplicada)

            # Atualizando gráficos
            line1.set_xdata(tempos)
            line1.set_ydata(temperaturas)
            line2.set_xdata(tempos)
            line2.set_ydata(setpoints)
            line3.set_xdata(tempos)
            line3.set_ydata(pwm_values)
            line4.set_xdata(tempos)
            line4.set_ydata(tensoes_aplicadas)

            # Ajustar os limites dos gráficos
            ax1.relim()
            ax1.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()
            ax3.relim()
            ax3.autoscale_view()

            # Salvando no arquivo CSV
            writer.writerow([tempo_atual, pwm_value, temperatura_lida, tensao_aplicada, setpoint_atual])

            # Pausar entre as amostras
            plt.pause(0.01)

        # Esperar até a próxima amostra
        time.sleep(tempo_por_amostra)

    plt.ioff()
    plt.show()

# Fechar a comunicação serial
arduino.close()

import serial
import time
import matplotlib.pyplot as plt
from collections import deque
import csv
import os

# Configurações do controlador PI
Kp = 2.70 #4.784  # Ganho proporcional
Ki = 0.05 #0.0638  # Ganho integral
setpoint = 40.0  # Temperatura desejada (em graus Celsius)
pwm_min = 0  # Limite mínimo do PWM
pwm_max = 255  # Limite máximo do PWM
limite_integral = 100  # Limite para evitar wind-up

# Configurações de comunicação serial
serial_port = 'COM9'  # Porta serial do Arduino (ajustar conforme necessário)
baud_rate = 9600
timeout = 1

# Parâmetros de amostragem
tempo_amostragem = 900  # Tempo total de amostragem (em segundos)
frequencia_amostragem = 1  # Frequência de coleta de amostras (1 por segundo)
num_amostras = int(tempo_amostragem / frequencia_amostragem)

# Inicialização do controlador PI
integral = 0.0

# Inicialização de listas para gráficos em tempo real
temperature_data = deque(maxlen=num_amostras)
pwm_data = deque(maxlen=num_amostras)
time_data = deque(maxlen=num_amostras)

# Caminho para salvar o arquivo CSV
diretorio_armazenamento = "C:/Users/Carlos Soares/Desktop/LINCE/Testes_Only_python/"  # Especificar o diretório desejado
arquivo_csv = os.path.join(diretorio_armazenamento, "dados_temperatura_PI40.csv")

# Conexão serial com o Arduino
arduino = serial.Serial(serial_port, baud_rate, timeout=timeout)
time.sleep(2)  # Aguarda inicialização do Arduino

# Configuração do gráfico
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
fig.tight_layout(pad=4.0)
ax1.set_title("Temperatura vs Tempo")
ax1.set_xlabel("Tempo (s)")
ax1.set_ylabel("Temperatura (°C)")
ax2.set_title("PWM vs Tempo")
ax2.set_xlabel("Tempo (s)")
ax2.set_ylabel("PWM")

# Função para atualizar o gráfico
def update_plot():
    ax1.clear()
    ax2.clear()
    ax1.plot(time_data, temperature_data, label="Temperatura (°C)", color='red')
    ax2.plot(time_data, pwm_data, label="PWM", color='green')
    ax1.legend()
    ax2.legend()
    ax1.set_title("Temperatura vs Tempo")
    ax1.set_xlabel("Tempo (s)")
    ax1.set_ylabel("Temperatura (°C)")
    ax2.set_title("PWM vs Tempo")
    ax2.set_xlabel("Tempo (s)")
    ax2.set_ylabel("PWM")
    plt.pause(0.01)

# Criação do arquivo CSV e cabeçalho
with open(arquivo_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Tempo (s)", "Amostra", "PWM", "Temperatura (°C)"])

# Loop principal
start_time = time.time()
try:
    for amostra in range(num_amostras):
        # Ler a temperatura do Arduino
        arduino.write(b'\n')  # Envia um sinal para iniciar a leitura
        line = arduino.readline().decode().strip()

        if line:
            try:
                sensor_value = int(line)
                temperature = (sensor_value * 5.0 / 1023.0 - 0.5) * 100  # Conversão para graus Celsius
            except ValueError:
                continue

            # Calcular erro e atualizar controlador PI
            error = setpoint - temperature
            integral += error * Ki

            # Limitar o valor da integral para evitar wind-up
            integral = max(min(integral, limite_integral), -limite_integral)

            pwm_value = int(Kp * error + integral)

            # Limitar o valor do PWM
            pwm_value = max(min(pwm_value, pwm_max), pwm_min)

            # Enviar o valor de PWM para o Arduino
            arduino.write(f"{pwm_value}\n".encode())

            # Atualizar listas de dados para os gráficos
            current_time = time.time() - start_time
            time_data.append(current_time)
            temperature_data.append(temperature)
            pwm_data.append(pwm_value)

            # Imprimir informações no terminal com legendas
            print(f"Tempo: {current_time:.2f}s ; Amostra: {amostra + 1} ; PWM: {pwm_value} ; Temperatura: {temperature:.2f}°C")

            # Salvar dados no arquivo CSV
            with open(arquivo_csv, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([f"{current_time:.2f}", amostra + 1, pwm_value, f"{temperature:.2f}"])

            # Atualizar os gráficos
            update_plot()

        # Intervalo de tempo para a próxima leitura
        time.sleep(frequencia_amostragem)

except KeyboardInterrupt:
    print("Programa interrompido pelo usuário.")

finally:
    arduino.close()
    plt.ioff()
    plt.show()
    print(f"Dados salvos em: {arquivo_csv}")

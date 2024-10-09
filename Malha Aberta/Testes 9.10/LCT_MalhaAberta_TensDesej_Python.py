import serial
import time
import csv
import matplotlib.pyplot as plt

# Configurações da comunicação serial
ser = serial.Serial('COM3', 9600)  # Ajuste 'COM3' conforme sua porta
time.sleep(2)  # Espera a inicialização do Arduino

# Parâmetros do experimento
FonteAlimentacao = 5.0  # Fonte de alimentação do aquecedor
Amplitude = 2.5  # Tensão desejada
TempoAmostragem = 600  # Tempo total de amostragem (em segundos)
NumeroAmostras = 600  # Quantidade de amostras (1 por segundo)

PWMInjetado = int((255 / FonteAlimentacao) * Amplitude)  # Calcula o valor de PWM

# Criação de listas para armazenar dados para os gráficos
tempos = []
temperaturas = []
pwm_values = []

# Inicializa a plotagem em tempo real
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1)

# Abre o arquivo CSV para salvar os dados
with open('dados_coletados.csv', mode='w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(["Amostra", "Tempo (s)", "PWM", "Temperatura (°C)"])

    # Envia o valor de PWM calculado para o Arduino
    ser.write(f"{PWMInjetado}\n".encode())

    # Loop para coletar e plotar dados
    for i in range(NumeroAmostras):
        # Lê a temperatura do Arduino
        if ser.in_waiting > 0:
            temperatura = float(ser.readline().decode().strip())
            tempo = i  # O tempo é o índice atual do loop (1 amostra por segundo)

            # Armazena os dados
            tempos.append(tempo)
            temperaturas.append(temperatura)
            pwm_values.append(PWMInjetado)

            # Print dos valores no terminal
            print(f"Amostra: {i+1}, Tempo: {tempo}s, PWM: {PWMInjetado}, Temperatura: {temperatura}°C")

            # Salva os dados no arquivo CSV
            writer.writerow([i+1, tempo, PWMInjetado, temperatura])

            # Atualiza os gráficos
            ax1.clear()
            ax2.clear()
            ax1.plot(tempos, temperaturas, label='Temperatura (°C)')
            ax2.plot(tempos, pwm_values, label='PWM')

            ax1.set_title('Temperatura vs Tempo')
            ax2.set_title('PWM vs Tempo')
            ax1.set_xlabel('Tempo (s)')
            ax2.set_xlabel('Tempo (s)')
            ax1.set_ylabel('Temperatura (°C)')
            ax2.set_ylabel('PWM')
            ax1.legend()
            ax2.legend()

            plt.pause(0.1)  # Pequena pausa para atualizar os gráficos em tempo real

ser.close()

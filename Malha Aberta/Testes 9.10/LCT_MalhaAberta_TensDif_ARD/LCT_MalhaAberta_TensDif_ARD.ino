import serial
import time
import csv
import matplotlib.pyplot as plt

# Configurações do experimento
FonteAlimentacao = 5.0  # Fonte de alimentação do aquecedor
Amplitude = [2.5, 4.0, 0.0, 3.0, 5.0]  # Tensão desejada
TempoAmostragem = 600  # Tempo total de amostragem (em segundos)
NumeroAmostras = 600  # Quantidade de amostras (1 por segundo)
AmostrasPWM = int(NumeroAmostras / len(Amplitude))  # Tempo de funcionamento para cada amplitude

# Configurações de comunicação serial com o Arduino
ser = serial.Serial('COM12', 9600)  # Altere 'COM3' para a porta correta
time.sleep(2)  # Aguarda a inicialização da comunicação

# Função para enviar PWM ao Arduino
def enviar_pwm(pwm):
    ser.write(f"{pwm}\n".encode())

# Função para ler a temperatura enviada pelo Arduino
def ler_temperatura():
    linha = ser.readline().decode().strip()
    try:
        # Se houver texto como 'Calibracao concluida', removemos essa parte
        if 'Calibracao concluida' in linha:
            linha = linha.replace('Calibracao concluida', '').strip()  # Remove a parte textual
        temperatura = float(linha)  # Tenta converter o restante para float
    except ValueError:
        print(f"Recebido um dado não numérico: {linha}")
        temperatura = None
    return temperatura

# Configurações dos gráficos
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True)

x_vals = []
temperatura_vals = []
pwm_vals = []

# Salva os dados em um arquivo CSV
with open('dados_experimento.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(['Amostra', 'Tempo (s)', 'PWM', 'Temperatura (°C)'])

    try:
        for i in range(NumeroAmostras):
            # Calcula o tempo atual
            tempo = i * (TempoAmostragem / NumeroAmostras)

            # Define o PWM com base nas amplitudes
            index_amplitude = i // AmostrasPWM
            if index_amplitude >= len(Amplitude):
                index_amplitude = len(Amplitude) - 1
            PWMInjetado = int((255 / FonteAlimentacao) * Amplitude[index_amplitude])
            enviar_pwm(PWMInjetado)

            # Lê a temperatura do Arduino
            temperatura = ler_temperatura()

            # Print dos valores no terminal
            if temperatura is not None:
                print(f"Amostra: {i + 1}, Tempo: {tempo}s, PWM: {PWMInjetado}, Temperatura: {temperatura}°C")

                # Salva os dados no arquivo CSV
                writer.writerow([i + 1, tempo, PWMInjetado, temperatura])

                # Atualiza os valores para os gráficos
                x_vals.append(tempo)
                temperatura_vals.append(temperatura)
                pwm_vals.append(PWMInjetado)

                # Atualiza os gráficos em tempo real
                ax1.clear()
                ax1.plot(x_vals, temperatura_vals, label='Temperatura (°C)', color='red')
                ax1.set_title('Temperatura vs. Tempo')
                ax1.set_xlabel('Tempo (s)')
                ax1.set_ylabel('Temperatura (°C)')
                ax1.legend()

                ax2.clear()
                ax2.plot(x_vals, pwm_vals, label='PWM', color='blue')
                ax2.set_title('PWM vs. Tempo')
                ax2.set_xlabel('Tempo (s)')
                ax2.set_ylabel('PWM')
                ax2.legend()

                # Ajuste de layout para evitar sobreposição
                plt.tight_layout(pad=2.0)

                plt.pause(0.01)

    except KeyboardInterrupt:
        print("Experimento interrompido manualmente.")

    finally:
        # Desliga o aquecedor ao finalizar o experimento
        print("Encerrando experimento. Desligando aquecedores.")
        enviar_pwm(0)  # Envia PWM = 0 para desligar o aquecedor
        ser.close()  # Fecha a conexão serial

# Mantém o gráfico aberto ao final do experimento
plt.ioff()
plt.show()

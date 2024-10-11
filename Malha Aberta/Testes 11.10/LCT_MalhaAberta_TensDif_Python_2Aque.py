import serial
import time
import csv
import matplotlib.pyplot as plt

# Configurações do experimento
FonteAlimentacao = 5.0
Amplitude = [2.5]
TempoAmostragem = 600
NumeroAmostras = 600
AmostrasPWM = int(NumeroAmostras / len(Amplitude))

# Configurações de comunicação serial
ser = serial.Serial('COM12', 9600)
time.sleep(2)

# Função para enviar PWM e LED ao Arduino
def enviar_pwm(pwm1, pwm2, led_brightness):
    ser.write(f"{pwm1},{pwm2},{led_brightness}\n".encode())

# Função para ler as temperaturas enviadas pelo Arduino
def ler_temperaturas():
    linha = ser.readline().decode().strip()
    try:
        if 'Calibracao concluida' in linha:
            linha = linha.replace('Calibracao concluida', '').strip()
        temperaturas = list(map(float, linha.split(',')))
    except ValueError:
        print(f"Recebido um dado não numérico: {linha}")
        temperaturas = [None, None]
    return temperaturas

# Gráficos
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True)

x_vals = []
temperatura1_vals = []
temperatura2_vals = []
pwm1_vals = []
pwm2_vals = []

# Salva os dados em um arquivo CSV
with open('dados_experimento.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(['Amostra', 'Tempo (s)', 'PWM1', 'Temperatura1 (°C)', 'PWM2', 'Temperatura2 (°C)'])

    try:
        for i in range(NumeroAmostras):
            tempo = i * (TempoAmostragem / NumeroAmostras)

            index_amplitude = i // AmostrasPWM
            if index_amplitude >= len(Amplitude):
                index_amplitude = len(Amplitude) - 1
            
            PWMInjetado1 = int((255 / FonteAlimentacao) * Amplitude[index_amplitude])
            PWMInjetado2 = int(PWMInjetado1 / 2)  # Segunda potência é metade
            led_brightness = int(255 * (TempoAmostragem - tempo) / TempoAmostragem)  # Brilho do LED

            enviar_pwm(PWMInjetado, PWMInjetado2, led_brightness)

            temperaturas = ler_temperaturas()

            if temperaturas[0] is not None and temperaturas[1] is not None:
                print(f"Amostra: {i + 1}, Tempo: {tempo}s, PWM1: {PWMInjetado1}, Temperatura1: {temperaturas[0]}°C, PWM2: {PWMInjetado2}, Temperatura2: {temperaturas[1]}°C")

                writer.writerow([i + 1, tempo, PWMInjetado1, temperaturas[0], PWMInjetado2, temperaturas[1]])

                x_vals.append(tempo)
                temperatura1_vals.append(temperaturas[0])
                temperatura2_vals.append(temperaturas[1])
                pwm1_vals.append(PWMInjetado1)
                pwm2_vals.append(PWMInjetado2)

                ax1.clear()
                ax1.plot(x_vals, temperatura1_vals, label='Temperatura 1 (°C)', color='red')
                ax1.plot(x_vals, temperatura2_vals, label='Temperatura 2 (°C)', color='orange')
                ax1.set_title('Temperaturas vs. Tempo')
                ax1.set_xlabel('Tempo (s)')
                ax1.set_ylabel('Temperatura (°C)')
                ax1.legend()

                ax2.clear()
                ax2.plot(x_vals, pwm1_vals, label='PWM 1', color='blue')
                ax2.plot(x_vals, pwm2_vals, label='PWM 2', color='green')
                ax2.set_title('PWM vs. Tempo')
                ax2.set_xlabel('Tempo (s)')
                ax2.set_ylabel('PWM')
                ax2.legend()

                plt.tight_layout(pad=2.0)
                plt.pause(0.01)

    except KeyboardInterrupt:
        print("Experimento interrompido manualmente.")

    finally:
        print("Encerrando experimento. Desligando aquecedores.")
        enviar_pwm(0, 0, 0)
        ser.close()

plt.ioff()
plt.show()

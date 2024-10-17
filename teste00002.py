import serial
import csv
import matplotlib.pyplot as plt
import os
import time

# Configurações da porta serial
conexao_serial = serial.Serial('COM9', 9600, timeout=1)  # Altere para a sua porta
time.sleep(2)

# Função para enviar as configurações ao Arduino
def enviar_configuracao(temperatura_alvo, kp, ki, duracao_amostragem, numero_amostras):
    conexao_serial.write(f"{duracao_amostragem},{numero_amostras},{temperatura_alvo},{kp},{ki}\n".encode())

# Definir variáveis de configuração
temperatura_alvo = 50.0
desligar_temp = temperatura_alvo - 2
kp = 6.05  # Constante proporcional
ki = 0.08  # Constante integrativa
duracao_amostragem = 600  # 10 minutos = 600 segundos
numero_amostras = 600  # Número de amostras


# Envia as configurações ao Arduino
enviar_configuracao(temperatura_alvo, kp, ki, duracao_amostragem, numero_amostras)

# Inicializando variáveis de amostragem
intervalo_amostras = duracao_amostragem / numero_amostras
amostras = []

# Criando diretório para armazenar os dados
caminho_diretorio = "C:/Users/Carlos Soares/Desktop/LINCE/LCT_Carlos/Amostras_PI"
if not os.path.exists(caminho_diretorio):
    os.makedirs(caminho_diretorio)

# Abrindo arquivo CSV para salvar amostras
caminho_arquivo = os.path.join(caminho_diretorio, "amostras_temperatura.csv")
with open(caminho_arquivo, mode='w', newline='') as file:
    escritor_csv = csv.writer(file)
    escritor_csv.writerow(["Tempo (s)", "PWM Aquecedor", "Temperatura (°C)", "Temperatura Filtrada (°C)"])

# Inicializa listas para armazenar os dados para o gráfico
tempos = []
temperaturas = []
temperaturas_filtradas = []
pwm_values = []
janela_filtro = [0] * 10  # Filtro de média móvel com janela de 10 amostras
filtro_ativo = False

# Configuração do gráfico
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10))
ax1.set_title("Temperatura Real vs Tempo")
ax1.set_xlabel("Tempo (s)")
ax1.set_ylabel("Temperatura (°C)")
line1, = ax1.plot(tempos, temperaturas, 'r-', label='Temperatura Lida')

ax2.set_title("Temperatura Filtrada vs Tempo")
ax2.set_xlabel("Tempo (s)")
ax2.set_ylabel("Temperatura Filtrada (°C)")
line2, = ax2.plot(tempos, temperaturas_filtradas, 'b-', label='Temperatura Filtrada')

ax3.set_title("PWM vs Tempo")
ax3.set_xlabel("Tempo (s)")
ax3.set_ylabel("PWM")
line3, = ax3.plot(tempos, pwm_values, 'g-', label='PWM Aquecedor')

plt.tight_layout()
plt.legend()

start_time = time.time()

# Loop de amostragem
for amostra in range(numero_amostras):
    current_time = time.time() - start_time

    # Verifica se há dados na porta serial
    data = conexao_serial.readline().decode().strip()
    if data:
        try:
            temperatura, pwm_value = map(float, data.split(","))
            
            # Filtro de média móvel (ativado após coletar 10 amostras)
            if amostra >= 10:
                filtro_ativo = True
                janela_filtro.pop(0)
                janela_filtro.append(temperatura)
                temperatura_filtrada = sum(janela_filtro) / len(janela_filtro)
            else:
                temperatura_filtrada = temperatura  # Antes de 10 amostras, usa a temperatura real

            print(f"Tempo: {current_time:.2f} s, Temp: {temperatura} °C, Temp Filtrada: {temperatura_filtrada} °C, PWM: {pwm_value}")

            # Atualiza dados para os gráficos
            tempos.append(current_time)
            temperaturas.append(temperatura)
            temperaturas_filtradas.append(temperatura_filtrada)
            pwm_values.append(pwm_value)

            # Atualiza gráficos
            line1.set_xdata(tempos)
            line1.set_ydata(temperaturas)
            line2.set_xdata(tempos)
            line2.set_ydata(temperaturas_filtradas)
            ax1.relim()
            ax1.autoscale_view(True, True, True)

            line3.set_xdata(tempos)
            line3.set_ydata(pwm_values)
            ax2.relim()
            ax2.autoscale_view(True, True, True)

            ax3.relim()
            ax3.autoscale_view(True, True, True)

            plt.draw()
            plt.pause(0.1)

            # Salva os dados no CSV
            escritor_csv.writerow([current_time, pwm_value, temperatura, temperatura_filtrada])
        except ValueError:
            print("Erro ao processar dados recebidos do Arduino:", data)

# Fechando conexão serial
conexao_serial.close()

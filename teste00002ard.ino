int pino_transistor = 8;
int sensorPin = A0;
float temperaturaAlvo = 40.0;
float desligar_temp = 35.0; // Temperatura de desligamento
float kp = 0, ki = 0;
int pwmValue = 255;
float temperaturaAtual = 0;
unsigned long inicio_tempo;
unsigned long intervalo_amostragem;
unsigned int numeroAmostras;
float erroAcumulado = 0;
unsigned long lastTime = 0;
unsigned long sampleTime = 1000;
bool controlePIAtivo = false;
int janela_filtro[10];
int filtro_index = 0;

void setup() {
    pinMode(pino_transistor, OUTPUT);
    Serial.begin(9600);

    // Recebe as configurações do Python
    while (Serial.available() == 0) {
        // Aguarda a chegada dos dados
    }

    // Parse dos dados enviados
    intervalo_amostragem = Serial.parseInt() * 1000;
    numeroAmostras = Serial.parseInt();
    temperaturaAlvo = Serial.parseFloat();
    kp = Serial.parseFloat();
    ki = Serial.parseFloat();
    desligar_temp = Serial.parseFloat(); //temperaturaAlvo - 2;

    inicio_tempo = millis();
}

void loop() {
    unsigned long currentTime = millis() - inicio_tempo;

    // Parar após o intervalo de amostragem
    if (currentTime >= intervalo_amostragem) {
        analogWrite(pino_transistor, 0);
        Serial.println("Amostragem finalizada.");
        while (1);  // Para o loop
    }

    // Controle de amostragem
    if (millis() - lastTime >= sampleTime) {
        lastTime = millis();

        // Lê a temperatura do sensor
        temperaturaAtual = lerTemperatura();

        // Atualiza o filtro de média móvel
        janela_filtro[filtro_index] = temperaturaAtual;
        filtro_index = (filtro_index + 1) % 10;
        float temperaturaFiltrada = 0;
        for (int i = 0; i < 10; i++) {
            temperaturaFiltrada += janela_filtro[i];
        }
        temperaturaFiltrada /= 10.0;

        // Lógica de controle
        if (temperaturaAtual < desligar_temp && !controlePIAtivo) {
            analogWrite(pino_transistor, 255); // Aquece até atingir desligar_temp
        } else {
            controlePIAtivo = true;
            float erro = temperaturaAlvo - temperaturaAtual;
            erroAcumulado += erro * (sampleTime / 1000.0);

            float output = kp * erro + ki * erroAcumulado;
            pwmValue = constrain(output, 0, 255);
            analogWrite(pino_transistor, pwmValue);
        }

        // Envia os dados para o Python
        Serial.print(temperaturaAtual);
        Serial.print(",");
        Serial.println(pwmValue);
    }
}

// Função para ler a temperatura
float lerTemperatura() {
    int sensorValue = analogRead(sensorPin);
    float voltage = sensorValue * (5.0 / 1023.0);
    return (voltage - 0.5) * 100.0;  // Conversão para Celsius
}

int transistorPin = 9;   // Pino PWM conectado ao transistor
int sensorPin = A0;      // Pino analógico conectado ao sensor de temperatura
float temperaturaAtual = 0;
int pwmValue = 0;
unsigned long lastSampleTime = 0;
const unsigned long sampleInterval = 1000;  // Intervalo entre amostras (1 segundo)

void setup() {
  pinMode(transistorPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // Verifica se há dados disponíveis do Python
  if (Serial.available() > 0) {
    pwmValue = Serial.parseInt();  // Recebe o valor de PWM enviado pelo Python
    analogWrite(transistorPin, pwmValue);  // Aplica o valor de PWM ao aquecedor
  }

  // Controla o intervalo de amostragem para evitar leituras rápidas demais
  if (millis() - lastSampleTime >= sampleInterval) {
    lastSampleTime = millis();  // Atualiza o tempo da última amostra
    
    // Lê a temperatura atual do sensor
    temperaturaAtual = lerTemperatura();  
    
    // Envia a temperatura e o valor de PWM para o Python
    Serial.print(temperaturaAtual);
    Serial.print(",");
    Serial.println(pwmValue);
  }
}

// Função para ler a temperatura do sensor
float lerTemperatura() {
  int sensorValue = analogRead(sensorPin);  // Lê o valor analógico do sensor
  float voltage = sensorValue * (5.0 / 1023.0);  // Converte o valor lido para tensão
  return (voltage - 0.5) * 100.0;  // Converte a tensão para temperatura em Celsius (ajuste para seu sensor)
}

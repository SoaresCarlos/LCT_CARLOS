int transistorPin = 9;
int sensorPin = A0;
float temperaturaAtual = 0;
int pwmValue = 0;
unsigned long tempoPorAmostra = 0;
unsigned long startTime;
unsigned long currentTime;

void setup() {
  pinMode(transistorPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // Verifica se há dados disponíveis do Python
  if (Serial.available() > 0) {
    pwmValue = Serial.parseInt();  // Recebe o valor de PWM
    tempoPorAmostra = Serial.parseInt() * 1000;  // Recebe o tempo por amostra em segundos e converte para milissegundos

    startTime = millis();  // Inicia o cronômetro para este valor de PWM
    analogWrite(transistorPin, pwmValue);  // Aplica o valor de PWM ao aquecedor

    // Controla o tempo de amostragem para o valor atual de PWM
    while (millis() - startTime < tempoPorAmostra) {
      temperaturaAtual = lerTemperatura();  // Lê a temperatura atual do sensor
      Serial.print(temperaturaAtual);
      Serial.print(",");
      Serial.println(pwmValue);  // Envia a temperatura e o valor de PWM para o Python
      delay(1000);  // Intervalo de 1 segundo entre leituras
    }
  }
}

float lerTemperatura() {
  int sensorValue = analogRead(sensorPin);
  float voltage = sensorValue * (5.0 / 1023.0);
  return (voltage - 0.5) * 100.0;  // Conversão para Celsius
}

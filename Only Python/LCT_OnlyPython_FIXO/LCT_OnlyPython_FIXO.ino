int pwmPin = 8;  // Pino PWM para o aquecedor
int sensorPin = A0;  // Pino analógico para o TMP36

void setup() {
  Serial.begin(9600);
  pinMode(pwmPin, OUTPUT);
}

void loop() {
  // Verificar se há dados na serial
  if (Serial.available() > 0) {
    int pwmValue = Serial.parseInt();  // Receber valor de PWM
    analogWrite(pwmPin, pwmValue);     // Aplicar PWM ao aquecedor

    // Ler o sensor de temperatura
    int sensorValue = analogRead(sensorPin);

    
    // Enviar a leitura de temperatura para o Python
    Serial.println(sensorValue);
  }

  delay(1000);  // 1 segundo entre leituras
}

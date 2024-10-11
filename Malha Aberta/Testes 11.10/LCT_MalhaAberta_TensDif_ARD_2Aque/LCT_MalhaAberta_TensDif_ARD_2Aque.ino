int pinAquecedor1 = 9;  // Pino do primeiro aquecedor
int pinSensor1 = A0;    // Pino do primeiro sensor
int pinAquecedor2 = 10; // Pino do segundo aquecedor
int pinSensor2 = A1;    // Pino do segundo sensor
int PWMInjetado1 = 0;
int PWMInjetado2 = 0;
float temperatura1 = 0.0;
float temperatura2 = 0.0;
float temperaturaAmbiente1 = 0.0;
float temperaturaAmbiente2 = 0.0;
int pinLED = 11;        // Pino do LED

void setup() {
  Serial.begin(9600);
  pinMode(pinAquecedor1, OUTPUT);
  pinMode(pinAquecedor2, OUTPUT);
  pinMode(pinLED, OUTPUT);

  // Calibração inicial
  temperaturaAmbiente1 = calibrarSensor(pinSensor1);
  temperaturaAmbiente2 = calibrarSensor(pinSensor2);
  Serial.println("Calibracao concluida");
}

float calibrarSensor(int pinSensor) {
  int leituraInicial = analogRead(pinSensor);
  return (leituraInicial * (5.0 / 1023.0) - 0.5) * 100.0;
}

void loop() {
  if (Serial.available() > 0) {
    // Lê os valores de PWM e brilho do LED enviados pelo Python
    String dados = Serial.readStringUntil('\n');
    int separator1 = dados.indexOf(',');
    int separator2 = dados.indexOf(',', separator1 + 1);

    PWMInjetado1 = dados.substring(0, separator1).toInt();
    PWMInjetado2 = dados.substring(separator1 + 1, separator2).toInt();
    int ledBrightness = dados.substring(separator2 + 1).toInt();

    // Define o PWM nos pinos dos aquecedores
    analogWrite(pinAquecedor1, PWMInjetado1);
    analogWrite(pinAquecedor2, PWMInjetado2);
    analogWrite(pinLED, ledBrightness);  // Controle do LED

    // Leitura da temperatura dos sensores
    temperatura1 = (analogRead(pinSensor1) * (5.0 / 1023.0) - 0.5) * 100.0 - temperaturaAmbiente1;
    temperatura2 = (analogRead(pinSensor2) * (5.0 / 1023.0) - 0.5) * 100.0 - temperaturaAmbiente2;

    // Envia as temperaturas de volta para o Python
    Serial.print(temperatura1);
    Serial.print(",");
    Serial.println(temperatura2);
  }
  
  delay(1000);  // Atualização a cada 1 segundo
}

int transistorPin = 9;
int sensorPin = A0;
float temperaturaAlvo = 40.0;
float kp = 0, ki = 0;
int pwmValue = 255;
float temperaturaCalibrada = 0;
float temperaturaAmbiente = 0;
unsigned long startTime;
unsigned long amostragemIntervalo;
unsigned int numeroAmostras;
float erroAcumulado = 0;
float erroAnterior = 0;
unsigned long lastTime = 0;
unsigned long sampleTime = 1000;  // 1 segundo para cálculo do PI
bool calibrado = false;

void setup() {
  pinMode(transistorPin, OUTPUT);
  Serial.begin(9600);

  // Recebe as configurações do Python (intervalo de amostragem, número de amostras, temperatura alvo, kp, ki)
  while (Serial.available() == 0) {
    // Aguarda a chegada dos dados
  }

  // Parse dos dados enviados
  amostragemIntervalo = Serial.parseInt() * 1000;  // Intervalo em segundos, convertido para ms
  numeroAmostras = Serial.parseInt();
  temperaturaAlvo = Serial.parseFloat();
  kp = Serial.parseFloat();
  ki = Serial.parseFloat();

  startTime = millis();  // Inicia a contagem de tempo

  // Realiza a calibração inicial do sensor, capturando a temperatura ambiente
  delay(2000);  // Aguarda estabilidade
  temperaturaAmbiente = lerTemperatura();
  calibrado = true;
}

void loop() {
  unsigned long currentTime = millis() - startTime;

  // Parar após o intervalo de amostragem
  if (currentTime >= amostragemIntervalo) {
    analogWrite(transistorPin, 0);  // Desliga aquecedor
    Serial.println("Amostragem finalizada.");
    while (1);  // Para o loop
  }

  if (millis() - lastTime >= sampleTime) {
    lastTime = millis();

    // Lê a temperatura do sensor e subtrai a temperatura ambiente
    float temperaturaAtual = lerTemperatura();
    if (calibrado) {
      temperaturaCalibrada = temperaturaAtual - temperaturaAmbiente;
    }

    // Calcula o erro
    float erro = temperaturaAlvo - temperaturaCalibrada;
    erroAcumulado += erro * (sampleTime / 1000.0);  // Soma o erro para a parte integrativa

    // Controle PI
    float output = kp * erro + ki * erroAcumulado;
    pwmValue = constrain(output, 0, 255);

    analogWrite(transistorPin, pwmValue);  // Ajusta o PWM do aquecedor

    // Envia temperatura e PWM para o Python
    Serial.print(temperaturaCalibrada);
    Serial.print(",");
    Serial.println(pwmValue);
  }
}

float lerTemperatura() {
  int sensorValue = analogRead(sensorPin);
  float voltage = sensorValue * (5.0 / 1023.0);
  return (voltage - 0.5) * 100.0;  // Conversão para Celsius
}

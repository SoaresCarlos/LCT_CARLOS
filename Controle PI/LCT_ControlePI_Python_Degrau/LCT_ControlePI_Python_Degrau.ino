int transistorPin = 9;
int sensorPin = A0;
float temperaturaAlvo = 40.0;
float kp = 0, ki = 0;
int pwmValue = 255;
float temperaturaAtual = 0;
unsigned long startTime;
unsigned long amostragemIntervalo;
unsigned int numeroAmostras;
float erroAcumulado = 0;
unsigned long lastTime = 0;
unsigned long sampleTime = 1000;  // 1 segundo para cálculo do PI
bool degrauAtivo = true;
int intervaloDegrau = 10000;  // 10 segundos de intervalo do degrau

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

  // Aquecer o transistor por 10 segundos no valor máximo
  analogWrite(transistorPin, 255);
}

void loop() {
  unsigned long currentTime = millis() - startTime;

  // Parar após o intervalo de amostragem
  if (currentTime >= amostragemIntervalo) {
    analogWrite(transistorPin, 0);  // Desliga aquecedor
    Serial.println("Amostragem finalizada.");
    while (1);  // Para o loop
  }

  // Controle de degrau
  if (millis() - lastTime >= sampleTime) {
    lastTime = millis();

    // Verifica se o degrau de 10 segundos já passou
    if (millis() - startTime >= intervaloDegrau) {
      degrauAtivo = false;
    }

    if (!degrauAtivo) {
      // Lê a temperatura do sensor
      temperaturaAtual = lerTemperatura();

      // Calcula o erro
      float erro = temperaturaAlvo - temperaturaAtual;
      erroAcumulado += erro * (sampleTime / 1000.0);  // Soma o erro para a parte integrativa

      // Controle PI - com ajuste em degraus
      float output = kp * erro + ki * erroAcumulado;

      // PWM em degrau
      if (output > 0) {
        pwmValue = 255;
      } else if (output < 0) {
        pwmValue = 0;
      }

      analogWrite(transistorPin, pwmValue);  // Ajusta o PWM do aquecedor

      // Envia temperatura e PWM para o Python
      Serial.print(temperaturaAtual);
      Serial.print(",");
      Serial.println(pwmValue);
    }
  }
}

float lerTemperatura() {
  int sensorValue = analogRead(sensorPin);
  float voltage = sensorValue * (5.0 / 1023.0);
  return (voltage - 0.5) * 100.0;  // Conversão para Celsius
}

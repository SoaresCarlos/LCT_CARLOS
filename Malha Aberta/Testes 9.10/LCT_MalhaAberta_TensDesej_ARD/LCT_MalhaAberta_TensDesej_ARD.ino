int pinAquecedor = 9;  // Pino onde o aquecedor está conectado (pino PWM)
int pinSensor = A0;    // Pino onde o sensor TMP36GZ está conectado (pino analógico)
int PWMInjetado = 0;
float temperatura = 0.0;

void setup() {
  Serial.begin(9600);
  pinMode(pinAquecedor, OUTPUT);  // Configura o pino do aquecedor como saída
}

void loop() {
  // Verifica se há dados disponíveis na serial
  if (Serial.available() > 0) {
    // Lê o valor de PWM enviado pelo Python
    PWMInjetado = Serial.parseInt();
    
    // Define o PWM no pino do aquecedor
    analogWrite(pinAquecedor, PWMInjetado);

    // Leitura da temperatura do sensor TMP36GZ
    int leituraAnalogica = analogRead(pinSensor);
    // Converte a leitura para temperatura em Celsius
    // Fórmula para TMP36GZ: Temp (°C) = (leitura * (5.0 / 1023.0) - 0.5) * 100
    temperatura = (leituraAnalogica * (5.0 / 1023.0) - 0.5) * 100.0;
    
    // Envia a temperatura de volta para o Python
    Serial.println(temperatura);
  }
  
  delay(1000);  // Atualização a cada 1 segundo
}

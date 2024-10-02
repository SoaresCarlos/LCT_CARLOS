// Definindo os pinos
const int pwmPin = 9;       // Pino PWM para o TIP120
const int sensorPin = A0;   // Pino analógico para TMP36
float temperaturaAlvo = 40.0; // Temperatura desejada em °C

// Definindo o número total de amostras e o tempo de amostragem
int tempoAmostragem = 10 * 60; // Tempo total em segundos (10 minutos = 600 segundos)
int amostrasTotais = 600; // Total de 600 amostras (1 amostra por segundo)
int amostrasAtual = 0;    // Contador de amostras

// Variável para armazenar a temperatura ambiente calibrada
float temperaturaAmbiente;

// Iniciar o valor do PWM em 0
int pwmValue = 0;

void setup() {
  Serial.begin(9600);       // Inicia comunicação serial
  pinMode(pwmPin, OUTPUT);  // Configura o pino PWM como saída

  // Calibrar o sensor para compensar a temperatura ambiente
  temperaturaAmbiente = lerTemperatura();
  Serial.print("Calibração feita. Temperatura ambiente: ");
  Serial.println(temperaturaAmbiente);
  
  // Adicionar um pequeno delay para leitura inicial
  delay(2000);  // Espera 2 segundos antes de começar as leituras
}

void loop() {
  if (amostrasAtual < amostrasTotais) {
    // Ler a temperatura e ajustar a temperatura com base na calibração
    float temperaturaAtual = lerTemperatura() - temperaturaAmbiente;

    // Controle simples: Incrementa ou decrementa o PWM em passos de 10
    if (temperaturaAtual > temperaturaAlvo) {
      pwmValue = max(pwmValue - 5, 0); // Reduz o PWM (não pode ser menor que 0)
    } else if (temperaturaAtual < temperaturaAlvo) {
      pwmValue = min(pwmValue + 5, 255); // Aumenta o PWM (não pode ser maior que 255)
    }

    // Aplicar o PWM no TIP31C
    analogWrite(pwmPin, pwmValue);   

    // Exibir a temperatura e o PWM no Monitor Serial de maneira mais lenta
    Serial.print("Amostra: ");
    Serial.print(amostrasAtual + 1);
    Serial.print(" | Temperatura: ");
    Serial.print(temperaturaAtual);
    Serial.print(" C | PWM: ");
    Serial.println(pwmValue);

    // Incrementar o contador de amostras
    amostrasAtual++; 

    // Esperar 1 segundo (1000 milissegundos) para coletar a próxima amostra
    delay(1000); // 1 amostra por segundo
  } else {
    // Finalizar a coleta de dados após todas as amostras serem coletadas
    Serial.println("Coleta de dados finalizada.");
    analogWrite(pwmPin, 0); // Desliga o PWM
    while (true); // Para o loop após a coleta de todas as amostras
  }
}

// Função para ler a temperatura do sensor TMP36
float lerTemperatura() {
  int valorLeitura = analogRead(sensorPin);       // Lê o valor analógico (0-1023)
  float voltagem = (valorLeitura * 5.0) / 1023.0; // Converte para voltagem
  float temperatura = (voltagem - 0.5) * 100.0;   // Converte para graus Celsius
  return temperatura;
}
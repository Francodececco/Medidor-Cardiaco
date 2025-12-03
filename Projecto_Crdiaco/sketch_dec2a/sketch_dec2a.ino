int sensorPin = A0;
int threshold = 520;   // Umbral para detectar un pulso

unsigned long lastBeat = 0;
bool pulsoDetectado = false;

int bpm = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int valor = analogRead(sensorPin);

  // Imprimir señal analógica
  Serial.print("VAL:");
  Serial.println(valor);

  // ----------- DETECCIÓN DE PULSO -----------
  if (valor > threshold && !pulsoDetectado) {
    pulsoDetectado = true;

    unsigned long tiempoActual = millis();
    unsigned long diferencia = tiempoActual - lastBeat;

    // Evita medir pulsos demasiado cercanos (ruido)
    if (diferencia > 300) { // Máximo 200 BPM
      bpm = 60000 / diferencia;

      Serial.print("BPM:");
      Serial.println(bpm);

      lastBeat = tiempoActual;
    }
  }

  // Cuando baja la señal, listo para detectar el siguiente pulso
  if (valor < threshold) {
    pulsoDetectado = false;
  }

  delay(20);  // refresco más rápido = señal más fluida
}


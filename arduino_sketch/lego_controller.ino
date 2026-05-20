/*
 * Arduino Uno serial CSV parser for LED brightness test.
 *
 * - Serial: 9600 baud
 * - Input line format: leftPercent,rightPercent
 * - Output action: analogWrite(LED_PIN, leftPercent)
 */

#define SERIAL_BAUD_RATE 9600
#define LED_PIN 6
#define BUTTON 2
#define INPUT_BUFFER_SIZE 48

char inputBuffer[INPUT_BUFFER_SIZE];
int bufferIndex = 0;

int leftPercent = 0;
int rightPercent = 0;


void parseLine(char *line) {
  int parsedLeft = 0;
  int parsedRight = 0;

  if (sscanf(line, "%d,%d", &parsedLeft, &parsedRight) == 2) {
    leftPercent = parsedLeft;
    rightPercent = parsedRight;
    int pwm = map(leftPercent,-100,100, 0, 155);
    analogWrite(LED_PIN, pwm);

  } 
}

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);
  analogWrite(LED_PIN, 0);
}

void loop() {
  if (digitalRead(BUTTON)== LOW) {
    Serial.write("B1");
    delay(100);
  }
  while (Serial.available() > 0) {
    char incomingByte = Serial.read();

    if (incomingByte == '\n' || incomingByte == '\r') {
      if (bufferIndex > 0) {
        inputBuffer[bufferIndex] = '\0';
        parseLine(inputBuffer);
        bufferIndex = 0;
      }
    } else if (bufferIndex < INPUT_BUFFER_SIZE - 1) {
      inputBuffer[bufferIndex++] = incomingByte;
    } else {
      // Buffer overflow protection: reset and report malformed line.
      bufferIndex = 0;
      Serial.println("ERR,BUFFER_OVERFLOW");
    }
  }
}

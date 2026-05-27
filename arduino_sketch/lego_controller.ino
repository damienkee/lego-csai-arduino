/*
 * Arduino Uno serial CSV parser and dual NeoPixel controller.
 *
 * - Serial: 9600 baud
 * - Input line format: leftPercent,rightPercent
 * - Output telemetry format: A0Value,ButtonValue
 */

#include <Adafruit_NeoPixel.h>

#define SERIAL_BAUD_RATE 9600
#define BUTTON_PIN 2
#define LEFT_PIXEL_PIN 4
#define RIGHT_PIXEL_PIN 5
#define PIXEL_COUNT 13
#define PIXEL_BRIGHTNESS 40
#define INPUT_BUFFER_SIZE 48
#define TELEMETRY_INTERVAL_MS 50

char inputBuffer[INPUT_BUFFER_SIZE];
int bufferIndex = 0;

int leftPercent = 0;
int rightPercent = 0;
unsigned long lastTelemetryMs = 0;

Adafruit_NeoPixel leftStrip(PIXEL_COUNT, LEFT_PIXEL_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel rightStrip(PIXEL_COUNT, RIGHT_PIXEL_PIN, NEO_GRB + NEO_KHZ800);

int clampPercent(int value) {
  if (value < -100) {
    return -100;
  }
  if (value > 100) {
    return 100;
  }
  return value;
}

uint32_t wheel(Adafruit_NeoPixel &strip, byte wheelPos) {
  wheelPos = 255 - wheelPos;
  if (wheelPos < 85) {
    return strip.Color(255 - wheelPos * 3, 0, wheelPos * 3);
  }
  if (wheelPos < 170) {
    wheelPos -= 85;
    return strip.Color(0, wheelPos * 3, 255 - wheelPos * 3);
  }
  wheelPos -= 170;
  return strip.Color(wheelPos * 3, 255 - wheelPos * 3, 0);
}

void updateLeftStrip() {
  int litCount = map(leftPercent, -100, 100, 0, PIXEL_COUNT);

  for (int i = 0; i < PIXEL_COUNT; i++) {
    if (i < litCount) {
      byte wheelPos = map(i, 0, PIXEL_COUNT - 1, 0, 255);
      leftStrip.setPixelColor(i, wheel(leftStrip, wheelPos));
    } else {
      leftStrip.setPixelColor(i, 0);
    }
  }
  leftStrip.show();
}

void updateRightStrip() {
  // 0% => red, 50% => green, 100% => blue with smooth hue interpolation.
  uint16_t hue = map(rightPercent, -100, 100, 0, 43690);
  uint32_t color = rightStrip.gamma32(rightStrip.ColorHSV(hue));

  for (int i = 0; i < PIXEL_COUNT; i++) {
    rightStrip.setPixelColor(i, color);
  }
  rightStrip.show();
}

void parseLine(char *line) {
  int parsedLeft = 0;
  int parsedRight = 0;

  if (sscanf(line, "%d,%d", &parsedLeft, &parsedRight) == 2) {
    leftPercent = clampPercent(parsedLeft);
    rightPercent = clampPercent(parsedRight);
    updateLeftStrip();
    updateRightStrip();
  }
}

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  leftStrip.begin();
  rightStrip.begin();
  leftStrip.setBrightness(PIXEL_BRIGHTNESS);
  rightStrip.setBrightness(PIXEL_BRIGHTNESS);
  leftStrip.show();
  rightStrip.show();

  updateLeftStrip();
  updateRightStrip();
}

void loop() {
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

  unsigned long now = millis();
  if (now - lastTelemetryMs >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryMs = now;

    int a0Value = analogRead(A0_PIN);
    int buttonValue = (digitalRead(BUTTON_PIN) == LOW) ? 1 : 0;

    Serial.print(a0Value);
    Serial.print(',');
    Serial.println(buttonValue);
  }
}

/*
 * LEGO Bluetooth Communication Handler
 * 
 * This Arduino sketch receives commands from a Python BLE controller
 * via serial communication and controls LEGO motors/devices accordingly.
 * 
 * Board: Arduino Uno
 * Serial Baud Rate: 9600
 */

#define SERIAL_BAUD_RATE 9600
#define COMMAND_BUFFER_SIZE 32

// LED pins for status indicators
#define STATUS_LED_PIN 13

// Motor pins (example for LEGO motor control)
#define MOTOR_A_PIN 9
#define MOTOR_B_PIN 10
#define MOTOR_C_PIN 11

// Command timeout in milliseconds
#define COMMAND_TIMEOUT 5000

char commandBuffer[COMMAND_BUFFER_SIZE];
int bufferIndex = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(SERIAL_BAUD_RATE);
  
  // Initialize LED
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, LOW);
  
  // Initialize motor pins
  pinMode(MOTOR_A_PIN, OUTPUT);
  pinMode(MOTOR_B_PIN, OUTPUT);
  pinMode(MOTOR_C_PIN, OUTPUT);
  
  // Disable all motors initially
  analogWrite(MOTOR_A_PIN, 0);
  analogWrite(MOTOR_B_PIN, 0);
  analogWrite(MOTOR_C_PIN, 0);
  
  Serial.println("READY");
  digitalWrite(STATUS_LED_PIN, HIGH);
  delay(100);
  digitalWrite(STATUS_LED_PIN, LOW);
}

void loop() {
  // Read incoming serial data
  if (Serial.available() > 0) {
    char incomingByte = Serial.read();
    
    if (incomingByte == '\n' || incomingByte == '\r') {
      if (bufferIndex > 0) {
        // Null-terminate the command string
        commandBuffer[bufferIndex] = '\0';
        
        // Process the command
        processCommand(commandBuffer);
        
        // Reset buffer
        bufferIndex = 0;
        memset(commandBuffer, 0, COMMAND_BUFFER_SIZE);
      }
    } else if (bufferIndex < COMMAND_BUFFER_SIZE - 1) {
      commandBuffer[bufferIndex++] = incomingByte;
    }
  }
}

/**
 * Process commands received from Python
 * Command format: "MOTOR_X:SPEED" where X is A/B/C and SPEED is 0-255
 */
void processCommand(char* command) {
  // Blink status LED
  digitalWrite(STATUS_LED_PIN, HIGH);
  
  Serial.print("RECV:");
  Serial.println(command);
  
  // Parse motor commands (e.g., "MOTOR_A:150" or "MOTOR_B:255")
  if (strncmp(command, "MOTOR_", 6) == 0) {
    char motor = command[6];  // A, B, or C
    int speed = 0;
    
    // Parse speed value
    if (sscanf(command, "MOTOR_%*c:%d", &speed) == 1) {
      speed = constrain(speed, 0, 255);
      
      switch (motor) {
        case 'A':
          analogWrite(MOTOR_A_PIN, speed);
          Serial.print("MOTOR_A:");
          Serial.println(speed);
          break;
        case 'B':
          analogWrite(MOTOR_B_PIN, speed);
          Serial.print("MOTOR_B:");
          Serial.println(speed);
          break;
        case 'C':
          analogWrite(MOTOR_C_PIN, speed);
          Serial.print("MOTOR_C:");
          Serial.println(speed);
          break;
        default:
          Serial.println("ERROR:INVALID_MOTOR");
          break;
      }
    }
  }
  // Stop all motors
  else if (strcmp(command, "STOP") == 0) {
    analogWrite(MOTOR_A_PIN, 0);
    analogWrite(MOTOR_B_PIN, 0);
    analogWrite(MOTOR_C_PIN, 0);
    Serial.println("STOPPED");
  }
  // Get status
  else if (strcmp(command, "STATUS") == 0) {
    Serial.print("MOTOR_A:");
    Serial.println(analogRead(MOTOR_A_PIN));
    Serial.print("MOTOR_B:");
    Serial.println(analogRead(MOTOR_B_PIN));
    Serial.print("MOTOR_C:");
    Serial.println(analogRead(MOTOR_C_PIN));
  }
  // Unknown command
  else {
    Serial.print("ERROR:UNKNOWN_COMMAND:");
    Serial.println(command);
  }
  
  digitalWrite(STATUS_LED_PIN, LOW);
}

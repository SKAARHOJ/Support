#include <Adafruit_NeoPixel.h>
//PINS USED
#define LED_STRIP_LED_NR 18
#define LED_STRIP_LED_DATA 53

#define GREEN_BTN 2
#define RED_BTN 3

#define DOME_BTN 5
#define DOME_LED 4

#define KNOB A15
#define FADER A14
#define RELAY 22
//
#define DOME_LED_ON 255
#define DOME_LED_DIMMED 50
#define DOME_LED_OFF 0

struct colorRGB {
  int red;
  int green;
  int blue;
};

// Variables will change:
int buttonState = 7;      // the current reading from the input pin
int lastButtonState = 7;  // the previous reading from the input pin

int knob;
int fader;

int lastKnob;
int lastFader;

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
unsigned long debounceDelay = 100;   // the debounce time; increase if the output flickers


// When setting up the NeoPixel library, we tell it how many pixels,
// and which pin to use to send signals. Note that for older NeoPixel
// strips you might need to change the third parameter -- see the
// strandtest example for more information on possible values.
Adafruit_NeoPixel pixels(LED_STRIP_LED_NR, LED_STRIP_LED_DATA, NEO_GRB + NEO_KHZ800);
uint16_t currentColor = 0;

void setupHW() {
  //HW initialization logic
  pinMode(GREEN_BTN, INPUT_PULLUP);
  pinMode(RED_BTN, INPUT_PULLUP);
  pinMode(DOME_BTN, INPUT_PULLUP);


  pinMode(DOME_LED, OUTPUT);
  pinMode(RELAY, OUTPUT);

  analogWrite(DOME_LED, 100);  // Up to Kasper to decide initial state of LED 0-off , 255 max
  digitalWrite(RELAY, LOW);

  pixels.begin();  // INITIALIZE NeoPixel strip object (REQUIRED)
  pixels.clear();  // Set all pixel colors to 'off'
  // The first NeoPixel in a strand is #0, second is 1, all the way up
  // to the count of pixels minus one.
  for (int i = 0; i < LED_STRIP_LED_NR; i++) {  // For each pixel...
    // pixels.Color() takes RGB values, from 0,0,0 up to 255,255,255
    pixels.setPixelColor(i, pixels.Color(0, 0, 0));
    pixels.show();  // Send the updated pixel colors to the hardware.
  }
}

// Reading hardware like buttons and analog components:
#define analogdeadzone 100
void scanHW() {

  // BUTTONS
  uint8_t btnStates = 0x00;

  // Read buttons, store bitwise result in btnStates
  btnStates ^= (-digitalRead(GREEN_BTN) ^ btnStates) & (1UL << 0);
  btnStates ^= (-digitalRead(RED_BTN) ^ btnStates) & (1UL << 1);
  btnStates ^= (-digitalRead(DOME_BTN) ^ btnStates) & (1UL << 2);

  // If the switch changed, due to noise or pressing:
  if (btnStates != lastButtonState) {
    // reset the debouncing timer
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    // whatever the reading is at, it's been there for longer than the debounce
    // delay, so take it as the actual current state:
    // if the button state has changed:
    if (btnStates != buttonState) {
      buttonState = btnStates;
    }
  }
  lastButtonState = btnStates;

  // Now analog components : knob and fader // in this case=> very simple implementation. no filtering or averaging.
  knob = analogRead(KNOB);
  knob = 1023 - knob;
  knob = constrain(map(knob, analogdeadzone, 1023 - analogdeadzone, 0, 1000), 0, 1000);

  fader = analogRead(FADER);
  fader = constrain(map(fader, analogdeadzone, 1023 - analogdeadzone, 0, 1000), 0, 1000);
}

void setDomeLED(uint8_t value) {
  analogWrite(DOME_LED, value);
}


uint8_t LEDStrip_red = 0;
uint8_t LEDStrip_green = 0;
uint8_t LEDStrip_blue = 0;
uint8_t LEDStrip_state = 0;

void updateLEDStrip() {
  uint8_t setRed = LEDStrip_red;
  uint8_t setGreen = LEDStrip_green;
  uint8_t setBlue = LEDStrip_blue;

  // Using simple bit-shifting to implement off and dimmed states... a little lazy and unflexible... :-)
  uint8_t shift = 0;
  if (LEDStrip_state == 0)  { // Off
    setRed = 0;
    setGreen = 0;
    setBlue = 0;
  } else if (LEDStrip_state == 5)  {  // Dimmed
    setRed = setRed / 6;
    setGreen = setGreen / 6;
    setBlue = setBlue / 6;
  } else if (LEDStrip_state == 1)  {  // Yellow On
    setRed = 255;
    setGreen = 135;
    setBlue = 0;
  } else if (LEDStrip_state == 2)  {  // Red On
    setRed = 255;
    setGreen = 0;
    setBlue = 0;
  } else if (LEDStrip_state == 3)  {  // Green On
    setRed = 0;
    setGreen = 255;
    setBlue = 0;
  }

  Serial.print(setRed);
  Serial.print(",");
  Serial.print(setGreen);
  Serial.print(",");
  Serial.println(setBlue);
  
  // Send over colors:
  for (int i = 0; i < LED_STRIP_LED_NR; i++) {  // For each pixel...
    // pixels.Color() takes RGB values, from 0,0,0 up to 255,255,255
    pixels.setPixelColor(i, pixels.Color(setRed / 2, setGreen / 2, setBlue / 2));
    pixels.show();  // Send the updated pixel colors to the hardware.
  }
}
void setLEDStripAll(uint8_t r, uint8_t g, uint8_t b) {
  LEDStrip_red = r;
  LEDStrip_green = g;
  LEDStrip_blue = b;

  updateLEDStrip();
}
void setLEDStripState(uint8_t state) {
  LEDStrip_state = state;

  updateLEDStrip();
}

void reportToClients(EthernetClient clients[], const char* str) {
  for (byte i = 0; i < 4; i++) {
    if (clients[i].connected()) {
      clients[i].write(str);
    }
  }
}

#define threshold 25
int lastReportedBtnStates = 7;
void reportEvents(EthernetClient clients[]) {

  //Buttons
  if (lastReportedBtnStates != lastButtonState) {
    if (bitRead(lastReportedBtnStates, 0) != bitRead(lastButtonState, 0)) {
      if (bitRead(lastButtonState, 0) == 0) {
        reportToClients(clients, "HWC#1=Down\n");
      } else {
        reportToClients(clients, "HWC#1=Up\n");
      }
    } else if (bitRead(lastReportedBtnStates, 1) != bitRead(lastButtonState, 1)) {
      if (bitRead(lastButtonState, 1) == 0) {
        reportToClients(clients, "HWC#2=Down\n");
      } else {
        reportToClients(clients, "HWC#2=Up\n");
      }
    } else if (bitRead(lastReportedBtnStates, 2) != bitRead(lastButtonState, 2)) {
      if (bitRead(lastButtonState, 2) == 0) {
        reportToClients(clients, "HWC#3=Down\n");
      } else {
        reportToClients(clients, "HWC#3=Up\n");
      }
    }
    lastReportedBtnStates = lastButtonState;
  }

  //Analogs
  if (lastKnob != knob && (abs(knob - lastKnob) > threshold || knob == 0 || knob == 1000)) {
    char text[50];
    sprintf(text, "HWC#11=Abs:%d \n", knob);
    reportToClients(clients, text);
    lastKnob = knob;
  }

  if (lastFader != fader && (abs(fader - lastFader) > threshold || fader == 0 || fader == 1000)) {
    char text[50];
    sprintf(text, "HWC#10=Abs:%d \n", fader);
    reportToClients(clients, text);
    lastFader = fader;
  }
}

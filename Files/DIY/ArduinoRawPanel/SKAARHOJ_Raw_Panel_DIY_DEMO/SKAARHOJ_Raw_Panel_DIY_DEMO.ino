/*
  SKAARHOJ Raw Panel Demo
*/

#include <SPI.h>
#include <Ethernet.h>
#include "./HARDWARE.h"
#include "./ColorUtils.h"

// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network.
// Gateway and Subnet are optional:
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 11, 99);
IPAddress gateway(192, 168, 10, 1);
IPAddress subnet(255, 255, 254, 0);

EthernetServer server(9923);
EthernetClient clients[4];

char buffer[64];
byte bufferSize = 64;
byte bufferWriteIndex = 0;




void setup() {

  // initialize the ethernet device
  Ethernet.begin(mac, ip, gateway, subnet);

  // start listening for clients
  server.begin();
  // Open serial communications and wait for port to open:
  Serial.begin(115200);
  while (!Serial) {
    ;  // wait for serial port to connect. Needed for Leonardo only
  }
  Serial.println("Hardware initialization... ");
  setupHW();

  Serial.print("Raw Panel Address: ");
  Serial.println(Ethernet.localIP());

  ResetBuffer();
}

void loop() {
  CheckEtherNetClients();
  PingPeriodic();
  //
  scanHW();
  //
  reportEvents(clients);
  delay(1);
}

// Checking for contents from clients and if any new connections came in (up to four connected clients allowed)
void CheckEtherNetClients() {

  // Check for
  EthernetClient client = server.available();

  // When the client sends the first byte, proces it:
  if (client) {

    // Checking if client is new:
    boolean newClient = true;
    for (byte i = 0; i < 4; i++) {
      //check whether this client refers to the same socket as one of the existing instances:
      if (clients[i] == client) {
        newClient = false;
        break;
      }
    }

    if (newClient) {
      //check which of the existing clients can be overridden:
      for (byte i = 0; i < 4; i++) {
        if (!clients[i] && clients[i] != client) {
          clients[i] = client;
          // clean out the input buffer:
          client.flush();
          Serial.println("New client connected.");
          break;
        }
      }
    }

    // Read content from client:
    if (client.available() > 0) {
      // Read the bytes incoming from the TCP client:
      char c = client.read();

      if (c == 10)  // Line feed, always used in Raw Panel to delimit commands
      {
        ParseCommand(client);
        ResetBuffer();
      } else if (c == 13)  // Carriage return, ignored
      {
        // Ignore.
      } else if (bufferWriteIndex < bufferSize - 1)  // one byte for null termination reserved
      {
        buffer[bufferWriteIndex] = c;
        bufferWriteIndex++;
      } else {
        Serial.println(F("ERROR: Buffer overflow."));
        client.flush();
        ResetBuffer();
      }
    }
  }
  for (byte i = 0; i < 4; i++) {
    if (!(clients[i].connected())) {
      // client.stop() invalidates the internal socket-descriptor, so next use of == will allways return false;
      clients[i].stop();
    }
  }
}

void ResetBuffer() {
  memset(buffer, 0, bufferSize);  // Reset input buffer
  bufferWriteIndex = 0;
}

// Parsing commands from client
void ParseCommand(EthernetClient client) {
  if (bufferWriteIndex > 0) {

    // List command:
    if (strcmp(buffer, "list") == 0) {
      Serial.println("'list' command received");

      client.write("_model=CUSTOM_ARDUINO\n");
      client.write("_serial=yu0r53r1a1\n");
      client.write("_version=v1.0\n");
      client.write("_name=My Arduino Raw Panel\n");
      client.write("_platform=custom\n");
      client.write("_panelType=Physical\n");
      client.write("_support=ASCII\n");
      client.write("_serverModeMaxClients=4\n");
    }

    // Ping
    else if (strcmp(buffer, "ping") == 0) {
      Serial.println("Ping command received");

      client.write("ack\n");
    }

    // ack:
    else if (strcmp(buffer, "ack") == 0) {
      Serial.println("Ack command received");
    }

    // Map (sending "overview" of all HWCs that are active on the panel. A legacy function, but important for compliance.)
    else if (strcmp(buffer, "map") == 0) {
      Serial.println("'Map' command received");

      client.write("map=1:1\n");
      client.write("map=2:2\n");
      client.write("map=3:3\n");
      client.write("map=10:10\n");
      client.write("map=12:12\n");
      client.write("map=11:11\n");
      client.write("map=100:100\n");
    }

    // Topology
    else if (strcmp(buffer, "PanelTopology?") == 0) {
      Serial.println("'PanelTopology?' command received");

      client.write("_panelTopology_HWC={\"HWc\": [{\"id\": 1,\"txt\": \"Button 1\",\"type\": 1,\"x\": 150,\"y\": 300},{\"id\": 2,\"txt\": \"Button 2\",\"type\": 1,\"x\": 380,\"y\": 300},{\"id\": 3,\"txt\": \"Dome\",\"type\": 2,\"x\": 670,\"y\": 300},{\"id\": 10,\"txt\": \"Fader\",\"type\": 23,\"x\": 900,\"y\": 420},{\"id\": 12,\"txt\": \"Relay\",\"type\": 3,\"x\": 300,\"y\": 500},{\"id\": 11,\"txt\": \"Knob\",\"type\": 18,\"x\": 670,\"y\": 600},{\"id\": 100,\"txt\": \"LED strip\",\"type\": 10,\"x\": 300,\"y\": 600}],\"typeIndex\": {\"1\": {\"desc\": \"Wall Switch\",\"h\": 200,\"w\": 200,\"in\": \"b\"},\"2\": {\"desc\": \"Stage Dome Button\",\"w\": 250,\"in\": \"b\",\"out\": \"mono\"},\"3\": {\"desc\": \"Relay output\",\"h\": 50,\"w\": 300,\"out\": \"gpo\"},\"10\": {\"desc\": \"LED strip\",\"h\": 70,\"w\": 500,\"out\": \"rgb\"},\"18\": {\"desc\": \"Potentiometer\",\"in\": \"ar\",\"w\": 160},\"23\": {\"desc\": \"Vertical Slider\",\"h\": 520,\"in\": \"av\",\"sub\": [{\"_\": \"r\",\"_h\": 100,\"_w\": 125,\"_x\": -63,\"_y\": 123}],\"w\": 30}}}\n");
      client.write("_panelTopology_svgbase=<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1000 700\" width=\"100%\" id=\"ctrlimg\"><defs><linearGradient id=\"topdownSimpleBlack\" x1=\"0%\" y1=\"0%\" x2=\"0%\" y2=\"100%\"><stop offset=\"0%\" style=\"stop-color:rgb(50,50,50);stop-opacity:1\" /><stop offset=\"100%\" style=\"stop-color:rgb(25,25,25);stop-opacity:1\" /></linearGradient></defs><style>text {font-family:Sans,Arial;}</style><rect width=\"990\" height=\"690\" x=\"5\" y=\"5\"  rx=\"50\" ry=\"50\" style=\"fill:url(#topdownSimpleBlack); stroke:rgb(0,100,104); stroke-width:10;\" /><path d=\"M 0 50 A 50 50 0 0 1 50 0 L 950 0 A 50 50 0 0 1 1000 50 L 1000 150 L 0 150 L 0 50\" style=\"fill:rgb(0,100,104);\"/><text x=\"500\" y=\"100\" style=\"text-anchor:middle; fill:#17a1a5; font-family:Verdana; font-size:55; letter-spacing:0px;\">My Arduino Raw Panel</text></svg>\n");
    }

    // State commands
    else if (strncmp(buffer, "HWC#3=", 6) == 0) {
      Serial.println("Set Dome button state");
      uint8_t state = atoi(&buffer[6]) & 0xF;
      if (state >= 1 && state <= 4) {  // On
        Serial.println("Dome light ON");
        setDomeLED(DOME_LED_ON);
      } else if (state == 5) {
        Serial.println("Dome light Dimmed");
        setDomeLED(DOME_LED_DIMMED);  // predefined value
      } else {
        Serial.println("Dome light OFF");
        setDomeLED(DOME_LED_OFF);
      }

    } else if (strncmp(buffer, "HWC#12=", 7) == 0) {
      Serial.println("Set Relay state");
      uint8_t state = atoi(&buffer[7]);
      if ((state & 0x20) > 1) {  // On
        Serial.println("Relay state ON");
        digitalWrite(RELAY, HIGH);
      } else {
        Serial.println("Relay state OFF");
        digitalWrite(RELAY, LOW);
      }

    } else if (strncmp(buffer, "HWC#100=", 8) == 0) {
      Serial.println("Set LED strip on/off/dimmed");
      uint8_t state = atoi(&buffer[8]) & 0xF;
      setLEDStripState(state);

    } else if (strncmp(buffer, "HWCc#100=", 9) == 0) {
      Serial.println("Set LED strip color");
      uint8_t color = atoi(&buffer[9]);
      Serial.print("LED strip color: ");
      Serial.println(color);
      bool isIndex = !bitRead(color, 6);
      Serial.print("LED strip indexed color: ");
      Serial.println(isIndex);
      bool isEnabled = bitRead(color, 7);
      Serial.print("LED strip enable bit: ");
      Serial.println(isEnabled);
      // TODO: Sort out whether it's index or RGB colors...
      uint16_t r = 0;
      uint16_t g = 0;
      uint16_t b = 0;
      if (isIndex) {
        ColorUtils::getRGBByIdx(static_cast<ColorUtils::ColorIndex>(color & 63), r, g, b);
        setLEDStripAll(r, g, b);
      } else {
        r = ((color >> 4) & 3) * 85;
        g = ((color >> 2) & 3) * 85;
        b = ((color >> 0) & 3) * 85;
        setLEDStripAll(r, g, b);
      }

    } else {
      Serial.println("Received this command and don't know what to do with it:");
      Serial.println(buffer);
    }
  }
}

// Quick way to ping connected clients about once every 3 seconds. Normally, this is something a client asks to enable, but we just do it. Should not harm, but can increase connection reliability with such a handshake.
uint16_t pingCounter = 0;
void PingPeriodic() {
  pingCounter++;
  if (pingCounter == 3000) {
    pingCounter = 0;
    for (byte i = 0; i < 4; i++) {
      if (clients[i].connected()) {
        clients[i].write("ping\n");
      }
    }
  }
}

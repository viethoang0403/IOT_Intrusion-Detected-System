#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// Thông tin mạng WiFi
const char* ssid = "";                                       //your wifi
const char* password = "";                                   //your password

const char* serverUrl = "http://192.168.246.46:5000/upload"; // your server (wifi2 address ipv4)

#define PIR_PIN 14
#define BUZZER_PIN 4
bool buzzerEnabled = false;
bool motionDetected = false;
bool motionDetectEnabled = false;

// Camera setup 
void setup_camera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_SVGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
    if (s != NULL) {
        s->set_vflip(s, 1);  
        s->set_hmirror(s, 1); 
    }
}

// WiFi setup
void connect_wifi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println(WiFi.localIP());
}

// Hàm chụp và gửi ảnh lên server
void capture_and_send_photo(const String& mode) {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  HTTPClient http;
  String url = String(serverUrl) + "?mode=" + mode;
  http.begin(url);
  http.addHeader("Content-Type", "image/jpeg");

  int httpResponseCode = http.POST(fb->buf, fb->len);
  if (httpResponseCode == 200) {
    Serial.println("Photo uploaded successfully");
  } else {
    Serial.printf("Failed to upload photo, code: %d\n", httpResponseCode);
  }
  http.end();
  esp_camera_fb_return(fb);
}

// ESP32 web server nhận requests từ server
WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  connect_wifi();
  setup_camera();
  server.begin();

  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  WiFiClient clientA = server.available();
  if (clientA) {
    Serial.println("New Client connected");
    String request = clientA.readStringUntil('\r');
    clientA.flush();

    // Nếu request từ server là chụp ảnh
    if (request.indexOf("/capture_photo") != -1) {
      capture_and_send_photo("register");
      clientA.println("HTTP/1.1 200 OK");
      clientA.println("Content-Type: text/html");
      clientA.println();
      clientA.println("Photo captured successfully");
    }

    // Nếu request từ server là bật cảm biển chuyển động
    else if (request.indexOf("/enable_motion") != -1) {
      motionDetectEnabled = true;
      Serial.println("Motion detection enabled");
      clientA.println("HTTP/1.1 200 OK");
      clientA.println("Content-Type: text/html");
      clientA.println();
      clientA.println("Motion detection enabled");
    }

    // Nếu request từ server là tắt cảm biến chuyển động
    else if (request.indexOf("/disable_motion") != -1) {
      motionDetectEnabled = false;
      Serial.println("Motion detection disabled by user");
      clientA.println("HTTP/1.1 200 OK");
      clientA.println("Content-Type: text/html");
      clientA.println();
      clientA.println("Motion detection disabled");
    }

    // Nếu request từ server là tắt chuông
    else if (request.indexOf("/enable_buzzer") != -1) {
      buzzerEnabled = true;
      Serial.println("Buzzer enabled");
      clientA.println("HTTP/1.1 200 OK");
      clientA.println("Content-Type: text/html");
      clientA.println();
      clientA.println("Buzzer enabled");
    }

    // Nếu request từ server là tắt chuông
    else if (request.indexOf("/disable_buzzer") != -1) {
      buzzerEnabled = false;
      Serial.println("Buzzer disabled");
      clientA.println("HTTP/1.1 200 OK");
      clientA.println("Content-Type: text/html");
      clientA.println();
      clientA.println("Buzzer disabled");
    }

    clientA.stop();
  }

  // Đọc dữ liệu từ PIR
  if (motionDetectEnabled) {
    int pirState = digitalRead(PIR_PIN);

    if (motionDetected && pirState == LOW) {
      motionDetected = false;
      Serial.println("Motion detection ended.");
    }

    if (!motionDetected && pirState == HIGH) {
      motionDetected = true;
      Serial.println("Motion detected! Sending photo...");
        capture_and_send_photo("motion");
    }
  }

  if (buzzerEnabled) {
    digitalWrite(BUZZER_PIN, HIGH);  
    delay(500);                     
    digitalWrite(BUZZER_PIN, LOW);   
  }
  delay(500); 
}

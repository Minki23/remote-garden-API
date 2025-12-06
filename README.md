🌱 SmartGrow – Inteligentny system IoT do monitorowania i zarządzania warunkami środowiskowymi w szklarni
👩‍💻 Zespół projektu

Michał Szymczak

Konrad Orzechowski

Igor Wojtun

Filip Półtoraczyk

Opiekun zespołu: dr inż. Michał Kędziora

📘 Opis projektu

SmartGrow to inteligentny system IoT przeznaczony do zdalnego monitorowania i zarządzania warunkami środowiskowymi w nowoczesnych szklarniach i obiektach uprawowych.
System umożliwia:

ciągły monitoring temperatury, wilgotności i natężenia światła,

automatyczne sterowanie urządzeniami wykonawczymi (np. pompą, wentylacją, oświetleniem),

analizę danych w czasie rzeczywistym z wykorzystaniem algorytmów AI/ML,

zdalny dostęp przez aplikację mobilną.

Projekt łączy elementy automatyki, IoT oraz sztucznej inteligencji, tworząc zintegrowane rozwiązanie, które optymalizuje zużycie zasobów (wody, energii) i zwiększa efektywność upraw.

Dzięki aplikacji mobilnej użytkownik może w czasie rzeczywistym:

podglądać parametry środowiskowe,

oglądać obraz z kamery,

sterować urządzeniami ręcznie lub automatycznie.

Całość wspierana jest przez CI/CD, szyfrowanie TLS oraz certyfikaty bezpieczeństwa, zapewniające niezawodność i ochronę danych.

⚙️ Technologie
🧠 Software
Warstwa urządzenia (Edge / IoT)

C++17 (ESP32) – obsługa czujników, komunikacja z serwerem, zarządzanie energią.

MQTT – lekki protokół komunikacji IoT (niska latencja, niezawodna transmisja).

Warstwa serwerowa (Backend / API / Dane)

Python 3.11 (FastAPI) – backend obsługujący komunikację z urządzeniami i aplikacją.

PostgreSQL – relacyjna baza danych do przechowywania pomiarów, konfiguracji i logów.

AI/ML – moduły predykcyjne i automatyzacja sterowania na podstawie danych pomiarowych.

Docker – konteneryzacja i automatyzacja wdrożeń (CI/CD).

Warstwa kliencka (Aplikacja mobilna)

Kotlin (Jetpack Compose) – natywna aplikacja mobilna umożliwiająca podgląd danych i sterowanie systemem.

🔩 Hardware
Komponent	Opis
FireBeetle 2 ESP32-S3-U	Mikrokontroler z WiFi, Bluetooth i kamerą OV2640
BH1750	Czujnik natężenia światła (lux)
DHT11	Czujnik temperatury i wilgotności
MOD-01588	Czujnik wilgotności gleby
Seeedstudio 101020635	Czujnik poziomu wody
Wentylator 12V 80×80×10,8 mm	Wentylacja i chłodzenie komponentów
Pompa wodna 6V GRL-14164	Automatyczne podlewanie
Moduł przekaźników (4 kanały)	Sterowanie urządzeniami zasilanymi wyższym napięciem
Zasilacz 12V/3A, przetwornica XL4015	Stabilne zasilanie układu
Technologia druku 3D	Dedykowana obudowa odporna na warunki szklarniowe

🔐 Bezpieczeństwo

Komunikacja szyfrowana TLS

Autoryzacja oparta na certyfikatach

Separacja środowisk (DEV / PROD)

Regularne aktualizacje w ramach CI/CD

# Многоуровневый туннелинг для обхода РКН

## Схемы туннелирования

### Цепочка 1: Client → Warsaw (прямой)
```
[Клиент] 
   ↓ (VLESS + xhttp + REALITY)
[Warsaw:185.138.90.150:443]
   ↓ (freedom)
[Internet]
```

### Цепочка 2: Client → RF Proxy → Warsaw (основная)
```
[Клиент] 
   ↓ (VLESS + xhttp + REALITY, SNI: ok.ru)
[RF Proxy:89.169.4.51:47474]
   ↓ (VLESS + xhttp + REALITY, SNI: vkvideo.ru)
[Warsaw:185.138.90.150:8443]
   ↓ (freedom)
[Internet]
```

### Цепочка 3: Client → RF Proxy (SS2022) → Warsaw
```
[Клиент]
   ↓ (Shadowsocks-2022, плагин v2ray-plugin)
[RF Proxy:89.169.4.51:47474]
   ↓ (WS + TLS, выглядит как obfs4)
[Warsaw:185.138.90.150:8443]
   ↓ (freedom)
[Internet]
```

### Цепочка 4: Nginx маскировка (если xhttp заблокирован)
```
[Клиент]
   ↓ (HTTPS to nginx, SNI: ok.ru)
[RF Proxy:89.169.4.51:443/nginx]
   ↓ (PROXY protocol → Xray)
[Warsaw upstream]
   ↓
[Internet]
```

## Генерация ссылок

### VLESS xhttp (основная)
```
vless://b831381d-6324-4d53-ad4f-8cda48b30811@89.169.4.51:47474?type=xhttp&security=reality&sni=ok.ru&pbk=xAlm6u6nEzTlVsF3KzX84ifSeey-hEnI88IMUiLPnAw&sid=&encryption=none&flow=xtls-rprx-vision&path=/api/v1/users/auth#RF-xhttp
```

### Shadowsocks-2022 (fallback)
```
ss2022://Qax35d7M-v6PcR8jDxUjx@89.169.4.51:47474?encryption=2022-blake3-aes-128-gcm&plugin=v2ray-plugin&plugin_opts=server;mux=0;path=/api/v1/stream;host=ok.ru#RF-SS2022
```

### Warsaw напрямую
```
vless://53396a4c-47d4-482a-8202-8327b485f5a0@185.138.90.150:443?type=tcp&security=reality&sni=www.microsoft.com&pbk=Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY&sid=a1b2c3d4#Warsaw-Direct
```
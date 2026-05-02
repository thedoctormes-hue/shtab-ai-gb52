// Типы для VPN Florida API

export interface ServerConfig {
  id: string;
  name: string;
  ip: string;
  port: number;
  protocol: string;
  flow: string;
  network: string;
  security: string;
  sni: string;
  pbk: string;
  sid: string;
}

export interface VlessConfig {
  server: ServerConfig;
  vless_url: string;
  qr_data?: string;
}

export interface ServerStatus {
  server: string;
  ip: string;
  port: number;
  online: boolean;
  ping_ms: number | null;
  location: string;
}

export interface PaymentRequest {
  tx_hash: string;
  email?: string;
  telegram?: string;
}

export interface PaymentStatus {
  tx_hash: string;
  status: 'pending' | 'confirmed' | 'rejected';
  created_at: string;
}

export interface PaymentResponse {
  status: string;
  tx_hash: string;
  message?: string;
  verification_status?: string;
}

export interface ApiConfigResponse {
  servers: VlessConfig[];
}

export interface ApiStatusResponse {
  server: string;
  ip: string;
  port: number;
  online: boolean;
  ping_ms: number | null;
  location: string;
}

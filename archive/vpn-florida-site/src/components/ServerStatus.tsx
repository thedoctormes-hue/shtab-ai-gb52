import { useState, useEffect } from "react";
import { Server, Activity, MapPin } from "lucide-react";

interface ServerStatusWidgetProps {
  serverIp?: string;
  serverName?: string;
}

interface ServerStatus {
  server: string;
  ip: string;
  port: number;
  online: boolean;
  ping_ms: number | null;
  location: string;
}

export default function ServerStatusWidget({ serverIp, serverName }: ServerStatusWidgetProps) {
  const [status, setStatus] = useState<ServerStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      let targetIp = serverIp;
      
      // If no IP provided, fetch the first server from config
      if (!targetIp) {
        try {
          const configRes = await fetch("/api/config");
          const configData = await configRes.json();
          const servers = configData.servers || [configData];
          if (servers.length > 0) {
            targetIp = servers[0].server.ip;
          }
        } catch {
          targetIp = "185.138.90.150"; // Fallback
        }
      }
      
      try {
        const response = await fetch(`/api/status?ip=${targetIp}`);
        const data = await response.json();
        setStatus(data);
      } catch {
        setStatus({
          server: serverName || "Florida Miami",
          ip: targetIp || "185.138.90.150",
          port: 443,
          online: false,
          ping_ms: null,
          location: "Miami, Florida, USA"
        });
      } finally {
        setLoading(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, [serverIp, serverName]);

  if (loading) {
    return (
      <div className="glass-panel rounded-lg p-4 animate-pulse">
        <div className="h-4 bg-white/10 rounded w-1/2"></div>
      </div>
    );
  }

  if (!status) return null;

  return (
    <div className={`glass-panel rounded-lg p-4 border ${status.online ? 'border-[#00FF00]/30' : 'border-red-500/30'}`}>
      <div className="flex items-center gap-2 mb-2">
        <Server size={16} className={status.online ? "text-[#00FF00]" : "text-red-400"} />
        <span className="font-mono text-xs text-gray-400 uppercase tracking-wider">
          {status.server}
        </span>
      </div>
      <div className="space-y-1 font-mono text-sm">
        <div className="flex items-center gap-2">
          <Activity size={14} />
          <span className={status.online ? "text-[#00FF00]" : "text-red-400"}>
            {status.online ? "Онлайн" : "Оффлайн"}
          </span>
          <span className={`inline-block w-2 h-2 rounded-full ${status.online ? 'bg-[#00FF00] animate-pulse' : 'bg-red-500'}`}></span>
        </div>
        <div className="flex items-center gap-2 text-gray-300">
          <MapPin size={14} className="text-[#00FFFF]" />
          <span>{status.location}</span>
        </div>
        <div className="text-gray-500 text-xs">
          {status.ip}:{status.port}
        </div>
        {status.ping_ms && (
          <div className="text-gray-500 text-xs">
            Пинг: {Math.round(status.ping_ms)}ms
          </div>
        )}
      </div>
    </div>
  );
}

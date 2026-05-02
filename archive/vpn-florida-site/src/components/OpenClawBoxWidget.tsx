import { useState, useEffect } from "react";
import { Terminal, Users, Zap, TrendingUp } from "lucide-react";

interface OpenClawStats {
  status: "online" | "offline";
  users: number;
  top_provider: string;
  api_endpoint: string;
}

export default function OpenClawBoxWidget() {
  const [stats, setStats] = useState<OpenClawStats>({
    status: "offline",
    users: 0,
    top_provider: "—",
    api_endpoint: "api.openclawbox.com"
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch("http://localhost:8000/status");
        const data = await response.json();
        
        // Find top provider by remaining tokens
        let topProvider = "—";
        let maxRemaining = 0;
        for (const [name, info] of Object.entries(data) as any) {
          if (info.remaining > maxRemaining) {
            maxRemaining = info.remaining;
            topProvider = name;
          }
        }
        
        setStats({
          status: "online",
          users: 42, // Mock - should come from DB
          top_provider: topProvider,
          api_endpoint: "api.openclawbox.com"
        });
      } catch {
        setStats(prev => ({ ...prev, status: "offline" }));
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <Terminal size={24} className="text-[#FF00FF]" />
        <h3 className="font-mono text-xl text-white">OpenClawBox API</h3>
      </div>
      
      {loading ? (
        <div className="animate-pulse font-mono text-[#00FFFF]">Загрузка...</div>
      ) : (
        <div className="space-y-4 font-mono">
          {/* Status */}
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Статус:</span>
            <span className={`flex items-center gap-2 ${
              stats.status === "online" ? "text-[#00FF00]" : "text-red-400"
            }`}>
              <span className={`w-2 h-2 rounded-full ${
                stats.status === "online" ? "bg-[#00FF00]" : "bg-red-400"
              }`}></span>
              {stats.status === "online" ? "Онлайн" : "Офлайн"}
            </span>
          </div>
          
          {/* Users */}
          <div className="flex items-center justify-between">
            <span className="text-gray-400 flex items-center gap-2">
              <Users size={16} />
              Пользователи:
            </span>
            <span className="text-white font-bold">{stats.users}</span>
          </div>
          
          {/* Top Provider */}
          <div className="flex items-center justify-between">
            <span className="text-gray-400 flex items-center gap-2">
              <TrendingUp size={16} />
              Топ провайдер:
            </span>
            <span className="text-[#00FFFF] font-bold">{stats.top_provider}</span>
          </div>
          
          {/* API Endpoint */}
          <div className="pt-3 border-t border-white/10">
            <code className="text-xs text-gray-500 bg-black/30 p-2 rounded block truncate">
              {stats.api_endpoint}
            </code>
          </div>
        </div>
      )}
    </div>
  );
}
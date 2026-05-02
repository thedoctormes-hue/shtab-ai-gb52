import { useState, useEffect } from "react";
import { MapPin, Wifi, AlertTriangle } from "lucide-react";

interface IPInfo {
  ip: string;
  city: string;
  region: string;
  country: string;
  org: string;
}

export default function IPWidget() {
  const [ipInfo, setIpInfo] = useState<IPInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchIP = async () => {
      try {
        const ipResponse = await fetch("https://api.ipify.org?format=json");
        const { ip } = await ipResponse.json();

        const infoResponse = await fetch(`https://ipapi.co/${ip}/json/`);
        const data = await infoResponse.json();

        setIpInfo({
          ip: data.ip,
          city: data.city,
          region: data.region,
          country: data.country_name,
          org: data.org,
        });
        setError(false);
      } catch (err) {
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchIP();
  }, []);

  if (loading) {
    return (
      <div className="glass-panel rounded-lg p-4 animate-pulse">
        <div className="h-4 bg-white/10 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-white/10 rounded w-1/2"></div>
      </div>
    );
  }

  if (error || !ipInfo) {
    return (
      <div className="glass-panel rounded-lg p-4 border border-red-500/50">
        <div className="flex items-center gap-2 text-red-400">
          <AlertTriangle size={16} />
          <span className="font-mono text-sm">Не удалось определить IP</span>
        </div>
      </div>
    );
  }

  const isFlorida = ipInfo.region.toLowerCase().includes("florida") || 
                    ipInfo.city.toLowerCase().includes("miami");

  return (
    <div className={`glass-panel rounded-lg p-4 border ${isFlorida ? 'border-[#00FF00]/50' : 'border-[#00FFFF]/50'}`}>
      <div className="flex items-center gap-2 mb-2">
        <MapPin size={16} className={isFlorida ? "text-[#00FF00]" : "text-[#00FFFF]"} />
        <span className="font-mono text-xs text-gray-400 uppercase tracking-wider">
          Ваше местоположение
        </span>
      </div>
      <div className="font-mono text-sm space-y-1">
        <div className="flex items-center gap-2">
          <Wifi size={14} className="text-[#FF00FF]" />
          <span className="text-white">{ipInfo.ip}</span>
        </div>
        <div className="text-[#00FFFF]">
          {ipInfo.city}, {ipInfo.region}, {ipInfo.country}
        </div>
        <div className="text-gray-500 text-xs">
          {ipInfo.org}
        </div>
      </div>
      {isFlorida && (
        <div className="mt-2 text-[#00FF00] text-xs font-mono flex items-center gap-1">
          <span className="inline-block w-2 h-2 rounded-full bg-[#00FF00] animate-pulse"></span>
          Вы уже во Флориде
        </div>
      )}
    </div>
  );
}

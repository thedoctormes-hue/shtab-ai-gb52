import { useState } from "react";
import { Shield, ShieldAlert, Loader2 } from "lucide-react";

export default function DNSTest() {
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<null | { safe: boolean; message: string; details: string[] }>(null);

  const runTest = async () => {
    setTesting(true);
    setResult(null);

    // Simulate DNS leak test
    await new Promise(resolve => setTimeout(resolve, 2000));

    const details: string[] = [];
    let safe = true;

    // Check WebRTC
    try {
      const pc = new RTCPeerConnection({ iceServers: [] });
      pc.createDataChannel("");
      
      const offer = await pc.createOffer();
      const sdp = offer.sdp || "";
      
      const ipRegex = /(\d{1,3}\.){3}\d{1,3}/g;
      const localIPs = sdp.match(ipRegex);
      
      if (localIPs && localIPs.length > 0) {
        details.push(`⚠️ WebRTC обнаружил локальные IP: ${localIPs.join(", ")}`);
        safe = false;
      } else {
        details.push("✅ WebRTC утечка не обнаружена");
      }
      
      pc.close();
    } catch (e) {
      details.push("✅ WebRTC отключен или недоступен");
    }

    // Check DNS through a simple fetch test
    try {
      const start = performance.now();
      await fetch("https://cloudflare-dns.com/dns-query?name=example.com&type=A", {
        headers: { Accept: "application/dns-json" }
      });
      const dnsTime = performance.now() - start;
      details.push(`✅ DNS запрос выполнен (${Math.round(dnsTime)}ms)`);
    } catch {
      details.push("ℹ️ DNS-over-HTTPS недоступен в этом браузере");
    }

    details.push("ℹ️ Для точной проверки используйте: dnsleaktest.com");

    setResult({
      safe,
      message: safe 
        ? "Основные проверки пройдены. Рекомендуем дополнительную проверку на dnsleaktest.com"
        : "Обнаружена потенциальная утечка! Настройте VPN-клиент правильно.",
      details
    });
    setTesting(false);
  };

  return (
    <div className="glass-panel rounded-lg p-6 space-y-4">
      <h3 className="font-mono text-lg text-[#FF00FF] mb-4">Тест на утечку DNS</h3>
      
      <button
        onClick={runTest}
        disabled={testing}
        className="neon-button-cyan w-full py-3 px-4 rounded font-mono text-sm flex items-center justify-center gap-2 disabled:opacity-50"
      >
        {testing ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Проверка...
          </>
        ) : (
          <>
            <Shield size={16} />
            Запустить тест
          </>
        )}
      </button>

      {result && (
        <div className={`mt-4 p-4 rounded border ${result.safe ? 'border-[#00FF00]/50 bg-[#00FF00]/5' : 'border-red-500/50 bg-red-500/5'}`}>
          <div className="flex items-center gap-2 mb-3">
            {result.safe ? (
              <Shield size={20} className="text-[#00FF00]" />
            ) : (
              <ShieldAlert size={20} className="text-red-400" />
            )}
            <span className={`font-mono text-sm ${result.safe ? 'text-[#00FF00]' : 'text-red-400'}`}>
              {result.safe ? "Проверка пройдена" : "Обнаружена утечка!"}
            </span>
          </div>
          <p className="text-sm text-gray-300 mb-3">{result.message}</p>
          <div className="space-y-1">
            {result.details.map((detail, i) => (
              <div key={i} className="font-mono text-xs text-gray-400">{detail}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

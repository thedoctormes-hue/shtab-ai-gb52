import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Terminal, Lock, Unlock, Link as LinkIcon } from "lucide-react";
import ConfigDisplay from "../components/ConfigDisplay";
import DNSTest from "../components/DNSTest";
import Guides from "../components/Guides";
import IPWidget from "../components/IPWidget";
import ServerStatusWidget from "../components/ServerStatus";
import OpenClawBoxWidget from "../components/OpenClawBoxWidget";

interface ServerConfig {
  server: any;
  vless_url: string;
  qr_data: string;
}

export default function Dashboard() {
  const [configs, setConfigs] = useState<ServerConfig[] | null>(null);
  const [selectedServer, setSelectedServer] = useState(0);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [accessCode, setAccessCode] = useState("");
  const [error, setError] = useState(false);
  const [copied, setCopied] = useState(false);
  const [files, setFiles] = useState<any[]>([]);
  const [shareLink, setShareLink] = useState<string | null>(null);
  const [shareCopied, setShareCopied] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch("/api/config");
        if (response.ok) {
          const data = await response.json();
          const servers = data.servers || [data];
          setConfigs(servers);
          setAuthenticated(true);
        }
      } catch {
        // Not authenticated
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  useEffect(() => {
    if (authenticated && window.location.hash) {
      setTimeout(() => {
        const el = document.getElementById(window.location.hash.slice(1));
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 500);
    }
  }, [authenticated]);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = accessCode.trim();
    if (code.length < 4) {
      setError(true);
      return;
    }
    if (code === "FLORIDA2024") {
      setAuthenticated(true);
      setError(false);
      fetch("/api/config")
        .then(r => r.json())
        .then(data => setConfigs(data.servers || [data]))
        .catch(() => setConfigs(null));
      return;
    }
    setAuthenticated(true);
    setError(false);
    fetch("/api/config")
      .then(r => r.json())
      .then(data => setConfigs(data.servers || [data]))
      .catch(() => {
        setConfigs([{
          server: { name: "Demo Server (New)", ip: "104.253.1.210" },
          vless_url: `vless://demo@104.253.1.210:443?security=reality&flow=xtls-rprx-vision&type=tcp&sni=www.cloudflare.com&pbk=YRlTGPowFb-Rggdw0JcBekgeSop6JzzJlEPtFvtq5WM&sid=01234567#VPN-Demo-New`,
          qr_data: "demo"
        }]);
      });
  };

  const handleCopyUrl = () => {
    const url = configs?.[selectedServer]?.vless_url;
    if (url) {
      navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleShare = async (filePath: string) => {
    try {
      const response = await fetch("/api/share", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: filePath, password: "zavlab" })
      });
      const data = await response.json();
      setShareLink(data.link);
      setShareCopied(false);
    } catch {
      alert("Ошибка создания ссылки");
    }
  };

  const copyShareLink = () => {
    if (shareLink) {
      navigator.clipboard.writeText(window.location.origin + shareLink);
      setShareCopied(true);
      setTimeout(() => setShareCopied(false), 2000);
    }
  };

  useEffect(() => {
    if (authenticated) {
      fetch("/api/uploads").then(r => r.json()).then(d => setFiles(d.files || []));
    }
  }, [authenticated]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="animate-pulse font-mono text-[#00FFFF]">Загрузка...</div>
      </div>
    );
  }

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <Link to="/" className="inline-flex items-center gap-2 text-gray-500 hover:text-[#00FFFF] transition-colors mb-8 font-mono text-sm">
            <ArrowLeft size={16} />
            На главную
          </Link>
          <div className="glass-panel rounded-xl p-8 border border-[#FF00FF]/30">
            <div className="text-center mb-8">
              <Lock size={40} className="text-[#FF00FF] mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-white mb-2">Личный кабинет</h1>
              <p className="text-gray-400 text-sm">Введите код доступа или TXID оплаты</p>
            </div>
            <form onSubmit={handleAuth} className="space-y-4">
              <div>
                <input
                  type="text"
                  value={accessCode}
                  onChange={(e) => { setAccessCode(e.target.value); setError(false); }}
                  placeholder="Код доступа или TXID..."
                  className={`w-full bg-black/50 border rounded p-3 font-mono text-sm text-white placeholder-gray-600 focus:outline-none ${
                    error ? 'border-red-500' : 'border-[#FF00FF]/30 focus:border-[#FF00FF]'
                  }`}
                />
                {error && <p className="text-red-400 text-xs mt-2 font-mono">Неверный код доступа</p>}
              </div>
              <button type="submit" className="neon-button w-full py-3 px-4 rounded font-mono text-sm">
                <Unlock size={16} className="inline mr-2" />
                Войти
              </button>
            </form>
            <div className="mt-6 text-center text-xs text-gray-600">
              <p>Нет доступа? <Link to="/" className="text-[#00FFFF] hover:underline">Оплатите подписку</Link></p>
              <p className="mt-2">Для демо введите любой код длиннее 3 символов</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <header className="border-b border-white/10 bg-[#0a0a0f]/80 backdrop-blur sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <Terminal size={18} className="text-[#FF00FF]" />
            <span className="font-mono text-white">VPN Florida</span>
          </Link>
          <div className="flex items-center gap-4">
            <span className="font-mono text-xs text-[#00FF00] hidden sm:inline">● Доступ активен</span>
            <IPWidget />
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <Link to="/" className="inline-flex items-center gap-2 text-gray-500 hover:text-[#00FFFF] transition-colors mb-6 font-mono text-sm">
          <ArrowLeft size={16} />
          На главную
        </Link>

        <div className="max-w-4xl mx-auto space-y-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Личный <span className="text-[#FF00FF] neon-text-pink">Кабинет</span>
            </h1>
            <p className="text-gray-400">Управление VPN-конфигурацией</p>
          </div>

          {configs && configs.length > 1 && (
            <div className="flex gap-2 flex-wrap">
              {configs.map((config, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedServer(idx)}
                  className={`px-4 py-2 rounded font-mono text-sm transition-all ${
                    selectedServer === idx
                      ? 'neon-button'
                      : 'glass-panel border border-white/10 hover:border-[#00FFFF]/50'
                  }`}
                >
                  {config.server.name}
                </button>
              ))}
            </div>
          )}

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {configs?.map((config, idx) => (
              <div
                key={idx}
                className={`cursor-pointer transition-all ${selectedServer === idx ? 'ring-2 ring-[#FF00FF]' : ''}`}
                onClick={() => setSelectedServer(idx)}
              >
                <ServerStatusWidget
                  serverIp={config.server.ip}
                  serverName={config.server.name}
                />
              </div>
            ))}
          </div>

          {configs && configs[selectedServer] && (
            <ConfigDisplay
              vlessUrl={configs[selectedServer].vless_url}
              serverName={configs[selectedServer].server.name}
            />
          )}

          {configs && configs[selectedServer] && (
            <div className="glass-panel rounded-lg p-6 space-y-4">
              <h3 className="font-mono text-lg text-[#00FFFF] mb-4">Информация сервера</h3>
              <div className="space-y-3 font-mono text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Сервер:</span>
                  <span className="text-white">{configs[selectedServer].server.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">IP:</span>
                  <span className="text-[#00FFFF]">{configs[selectedServer].server.ip}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Порт:</span>
                  <span className="text-white">{configs[selectedServer].server.port || 443}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Протокол:</span>
                  <span className="text-[#FF00FF]">VLESS + Reality</span>
                </div>
              </div>
              <div className="pt-4 border-t border-white/10">
                <button onClick={handleCopyUrl} className="neon-button-cyan w-full py-2 px-4 rounded font-mono text-sm flex items-center justify-center gap-2">
                  {copied ? <Check size={16} /> : <Copy size={16} />}
                  {copied ? "Скопировано!" : "Копировать VLESS URL"}
                </button>
              </div>
            </div>
          )}

          <div className="glass-panel rounded-lg p-6">
            <h3 className="font-mono text-lg text-[#00FFFF] mb-4">Файлы для совместного доступа</h3>
            {files.length > 0 ? (
              <div className="space-y-2">
                {files.map((file, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-black/30 rounded">
                    <div className="font-mono text-sm text-white truncate">{file.name}</div>
                    <button
                      onClick={() => handleShare(file.path)}
                      className="neon-button-cyan px-3 py-1 rounded text-xs flex items-center gap-1"
                    >
                      <LinkIcon size={14} />
                      Поделиться
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Папка uploads пуста</p>
            )}
            {shareLink && (
              <div className="mt-4 p-3 bg-[#00FFFF]/10 rounded">
                <p className="text-xs text-gray-400 mb-1">Ссылка создана:</p>
                <div className="flex items-center gap-2">
                  <code className="font-mono text-xs text-[#00FFFF] break-all">{window.location.origin + shareLink}</code>
                  <button onClick={copyShareLink} className="neon-button-cyan px-2 py-1 rounded text-xs">
                    {shareCopied ? "Скопировано!" : "Копировать"}
                  </button>
                </div>
              </div>
            )}
          </div>

          <DNSTest />
          <OpenClawBoxWidget />
          <div className="glass-panel rounded-lg p-6">
            <h3 className="font-mono text-lg text-[#FF00FF] mb-6">Гайды по настройке</h3>
            <Guides />
          </div>
        </div>
      </div>
    </div>
  );
}
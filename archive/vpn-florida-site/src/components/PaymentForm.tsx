import { useState } from "react";
import { ArrowRight, Send, Copy, Check, Loader2, Eye, EyeOff } from "lucide-react";
import { QRCodeSVG } from "qrcode.react";

interface PaymentFormProps {
  onConfigReceived?: (config: any) => void;
}

export default function PaymentForm({ onConfigReceived }: PaymentFormProps) {
  const [txHash, setTxHash] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState<any>(null);
  const [vmessUrl, setVmessUrl] = useState<string>("");
  const [showConfig, setShowConfig] = useState(false);

  const walletAddress = "TQvw8MJMdSBFXu5G74JsZm1gzg7cuXBZ2o";

  const handleCopyAddress = () => {
    navigator.clipboard.writeText(walletAddress);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!txHash.trim()) return;
    setLoading(true);

    try {
      // Submit hash
      await fetch("/api/verify-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tx_hash: txHash })
      });

      // Get VMess URL for QR code
      const vmessRes = await fetch(`/api/vmess-url/${txHash}`);
      if (vmessRes.ok) {
        const vmessData = await vmessRes.text();
        setVmessUrl(vmessData);
      }

      // Try to get config immediately (demo mode)
      const configRes = await fetch(`/api/get-config-by-txid/${txHash}`);
      if (configRes.ok) {
        const configData = await configRes.json();
        setConfig(configData);
        setSubmitted(true);
        if (onConfigReceived) {
          onConfigReceived(configData);
        }
      } else {
        setSubmitted(true);
      }
    } catch {
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyUrl = () => {
    if (config?.vless_url) {
      navigator.clipboard.writeText(config.vless_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (submitted && (config || vmessUrl)) {
    return (
      <div className="glass-panel rounded-lg p-6 space-y-4">
        <div className="border border-[#00FF00]/50 bg-[#00FF00]/5 rounded-lg p-4">
          <div className="flex items-center gap-2 text-[#00FF00] mb-2">
            <Check size={18} />
            <span className="font-mono">Доступ активен!</span>
          </div>
          <p className="text-sm text-gray-400 mb-4">
            Ваш VPN конфиг готов. Отсканируйте QR или скопируйте ссылку.
          </p>
        </div>

        <div className="flex justify-center">
          <div className="bg-white p-3 rounded-lg">
            {vmessUrl ? (
              <QRCodeSVG
                value={vmessUrl}
                size={140}
                level="H"
                includeMargin={false}
              />
            ) : (
              <QRCodeSVG
                value={walletAddress}
                size={140}
                level="H"
                includeMargin={false}
              />
            )}
          </div>
        </div>

        {vmessUrl && (
          <div className="relative">
            <div
              className="font-mono text-xs bg-black/50 rounded p-3 break-all border border-[#FF00FF]/30"
              style={{ filter: showConfig ? 'none' : 'blur(4px)' }}
            >
              {vmessUrl}
            </div>
            {!showConfig && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/60 rounded">
                <span className="font-mono text-sm text-gray-400">Нажмите, чтобы показать</span>
              </div>
            )}
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="neon-button-cyan flex-1 py-2 px-4 rounded font-mono text-sm flex items-center justify-center gap-2"
          >
            {showConfig ? <EyeOff size={16} /> : <Eye size={16} />}
            {showConfig ? "Скрыть" : "Показать"}
          </button>
          <button
            onClick={handleCopyUrl}
            className="neon-button flex-1 py-2 px-4 rounded font-mono text-sm flex items-center justify-center gap-2"
          >
            {copied ? <Check size={16} /> : <Copy size={16} />}
            {copied ? "Скопировано!" : "Копировать"}
          </button>
        </div>

        <a
          href="/#guide-mac"
          className="neon-button w-full py-3 px-4 rounded font-mono text-sm flex items-center justify-center gap-2"
        >
          <span>Как настроить устройство?</span>
          <ArrowRight size={16} />
        </a>
      </div>
    );
  }

  if (submitted && !config) {
    return (
      <div className="glass-panel rounded-lg p-6 space-y-4">
        <div className="border border-[#FF00FF]/50 bg-[#FF00FF]/5 rounded-lg p-4">
          <div className="flex items-center gap-2 text-[#FF00FF] mb-2">
            <Check size={18} />
            <span className="font-mono">Хеш отправлен!</span>
          </div>
          <p className="text-sm text-gray-400">
            ЗавЛаб уже уведомлен. Скоро доступ придет на <a href="https://t.me/DoctorMES" target="_blank" rel="noopener noreferrer" className="text-[#00FFFF] hover:underline">@DoctorMES</a>.
          </p>
          <p className="text-xs text-gray-500 mt-2 font-mono break-all">{txHash}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-lg p-6 space-y-6">
      <div>
        <h3 className="font-mono text-lg text-[#FF00FF] mb-2">Оплата USDT (TRC-20)</h3>
        <p className="text-sm text-gray-400">Стоимость: <span className="text-[#00FFFF] font-mono">$15/мес</span></p>
      </div>

      <div className="space-y-3">
        <div className="font-mono text-sm text-gray-300">Адрес кошелька:</div>
        <div className="flex items-center gap-2">
          <code className="flex-1 bg-black/50 rounded p-3 text-[0.65rem] font-mono text-[#00FFFF] whitespace-nowrap overflow-x-auto">
            {walletAddress}
          </code>
          <button
            onClick={handleCopyAddress}
            className="neon-button-cyan p-3 rounded"
            title="Копировать"
          >
            {copied ? <Check size={16} /> : <Copy size={16} />}
          </button>
        </div>
        <div className="flex justify-center mt-3">
          <div className="bg-white p-2 rounded-lg">
            <QRCodeSVG
              value={walletAddress}
              size={160}
              level="H"
              includeMargin={false}
            />
          </div>
        </div>
        <p className="text-xs text-gray-500 text-center">Отсканируйте QR для оплаты через Tron-кошелек</p>
      </div>

      <div className="space-y-2 text-sm text-gray-400">
        <p>1. Отправьте ровно <strong className="text-white">15 USDT</strong> на адрес выше</p>
        <p>2. Сеть: <strong className="text-[#00FFFF]">TRC-20 (Tron)</strong></p>
        <p>3. После оплаты введите хеш транзакции ниже</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="text"
          value={txHash}
          onChange={(e) => setTxHash(e.target.value)}
          placeholder="Введите хеш транзакции (TXID)..."
          className="w-full bg-black/50 border border-[#FF00FF]/30 rounded p-3 font-mono text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#FF00FF]"
        />
        <button
          type="submit"
          disabled={!txHash.trim() || loading}
          className="neon-button w-full py-3 px-4 rounded font-mono text-sm flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
          {loading ? "Отправка..." : "Отправить хеш"}
          {!loading && <ArrowRight size={16} />}
        </button>
      </form>

      <div className="text-xs text-gray-500 text-center">
        После подтверждения вы получите доступ к личному кабинету
      </div>
    </div>
  );
}

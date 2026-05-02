import { QRCodeSVG } from "qrcode.react";
import { useState } from "react";
import { Eye, EyeOff, Copy, Check } from "lucide-react";

interface ConfigDisplayProps {
  vlessUrl: string;
  serverName?: string;
}

export default function ConfigDisplay({ vlessUrl, serverName }: ConfigDisplayProps) {
  const [showConfig, setShowConfig] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(vlessUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-panel rounded-lg p-6 space-y-4">
      <h3 className="font-mono text-lg text-[#00FFFF] mb-4">
        VLESS Конфигурация {serverName && `- ${serverName}`}
      </h3>

      <div className="flex justify-center">
        <div className="bg-white p-3 rounded-lg">
          <QRCodeSVG
            value={vlessUrl}
            size={200}
            level="H"
            includeMargin={false}
          />
        </div>
      </div>

      <div className="relative">
        <div
          className="font-mono text-xs bg-black/50 rounded p-3 break-all border border-[#FF00FF]/30"
          style={{ filter: showConfig ? 'none' : 'blur(4px)' }}
        >
          {vlessUrl}
        </div>

        {!showConfig && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/60 rounded">
            <span className="font-mono text-sm text-gray-400">Нажмите, чтобы показать</span>
          </div>
        )}
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => setShowConfig(!showConfig)}
          className="neon-button-cyan flex-1 py-2 px-4 rounded font-mono text-sm flex items-center justify-center gap-2"
        >
          {showConfig ? <EyeOff size={16} /> : <Eye size={16} />}
          {showConfig ? "Скрыть" : "Показать"}
        </button>
        <button
          onClick={handleCopy}
          className="neon-button flex-1 py-2 px-4 rounded font-mono text-sm flex items-center justify-center gap-2"
        >
          {copied ? <Check size={16} /> : <Copy size={16} />}
          {copied ? "Скопировано!" : "Копировать"}
        </button>
      </div>
    </div>
  );
}

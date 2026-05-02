import { useState } from "react";
import { ChevronDown, ChevronUp, Monitor, Smartphone, Tablet } from "lucide-react";

interface GuideStep {
  title: string;
  description: string;
}

interface Guide {
  id: string;
  name: string;
  icon: React.ReactNode;
  app: string;
  steps: GuideStep[];
}

const guides: Guide[] = [
  {
    id: "macbook",
    name: "MacBook",
    icon: <Monitor size={20} />,
    app: "v2rayU",
    steps: [
      { title: "1. Скачайте v2rayU", description: "Перейдите на GitHub v2rayU и скачайте последний релиз .dmg файла." },
      { title: "2. Установите приложение", description: "Откройте .dmg и перетащите v2rayU в Applications." },
      { title: "3. Импорт конфигурации", description: "Откройте v2rayU → Servers → Import from clipboard. Скопируйте vless:// ссылку из личного кабинета." },
      { title: "4. Подключение", description: "Нажмите на сервер → Connect. Проверьте IP через ip8.ru — должен показывать Майами." }
    ]
  },
  {
    id: "iphone",
    name: "iPhone",
    icon: <Smartphone size={20} />,
    app: "Shadowrocket",
    steps: [
      { title: "1. Установите Shadowrocket", description: "Купите и скачайте Shadowrocket из App Store ($2.99)." },
      { title: "2. Импорт конфигурации", description: "Откройте приложение → нажмите + → Scan QR или вставьте URL." },
      { title: "3. Разрешите VPN", description: "Система запросит разрешение для VPN-профиля — подтвердите." },
      { title: "4. Подключение", description: "Включите переключатель Connect. Иконка VPN появится в статус-баре." }
    ]
  },
  {
    id: "android",
    name: "Android",
    icon: <Tablet size={20} />,
    app: "v2rayNG",
    steps: [
      { title: "1. Скачайте v2rayNG", description: "Установите v2rayNG из Google Play или GitHub releases." },
      { title: "2. Импорт конфигурации", description: "Откройте приложение → + → Import config from clipboard." },
      { title: "3. Разрешите VPN", description: "При первом запуске разрешите создание VPN-подключения." },
      { title: "4. Подключение", description: "Выберите сервер → нажмите значок подключения (▶). Проверьте IP." }
    ]
  }
];

export default function Guides() {
  const [activeGuide, setActiveGuide] = useState("macbook");
  const [expandedStep, setExpandedStep] = useState<number | null>(0);

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {guides.map((guide) => (
          <button
            key={guide.id}
            onClick={() => {
              setActiveGuide(guide.id);
              setExpandedStep(0);
            }}
            className={`flex-1 py-3 px-4 rounded font-mono text-sm flex items-center justify-center gap-2 transition-all ${
              activeGuide === guide.id
                ? 'neon-button'
                : 'glass-panel border border-white/10 hover:border-[#00FFFF]/50'
            }`}
          >
            {guide.icon}
            {guide.name}
          </button>
        ))}
      </div>

      {guides.map((guide) => (
        <div 
          key={guide.id}
          id={`guide-${guide.id === 'macbook' ? 'mac' : guide.id === 'iphone' ? 'ios' : 'android'}`}
          className={`glass-panel rounded-lg p-6 ${activeGuide === guide.id ? 'block' : 'hidden'}`}
        >
          <h4 className="font-mono text-[#00FFFF] mb-1">{guide.name}</h4>
          <p className="text-sm text-gray-400 mb-4">Приложение: {guide.app}</p>

          <div className="space-y-2">
            {guide.steps.map((step, i) => (
              <div key={i} className="border border-white/10 rounded overflow-hidden">
                <button
                  onClick={() => setExpandedStep(expandedStep === i ? null : i)}
                  className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
                >
                  <span className="font-mono text-sm">{step.title}</span>
                  {expandedStep === i ? (
                    <ChevronUp size={16} className="text-[#FF00FF]" />
                  ) : (
                    <ChevronDown size={16} className="text-gray-500" />
                  )}
                </button>
                {expandedStep === i && (
                  <div className="px-4 pb-3 text-sm text-gray-300 border-t border-white/10 pt-2">
                    {step.description}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

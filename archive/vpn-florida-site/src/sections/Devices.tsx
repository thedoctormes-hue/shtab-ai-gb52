import { Monitor, Smartphone, Tablet, ArrowDown } from "lucide-react";

const devices = [
  {
    id: "macbook",
    name: "MacBook",
    icon: <Monitor size={40} />,
    app: "v2rayU",
    color: "#FF00FF",
    guideAnchor: "guide-mac"
  },
  {
    id: "iphone",
    name: "iPhone",
    icon: <Smartphone size={40} />,
    app: "Shadowrocket",
    color: "#00FFFF",
    guideAnchor: "guide-ios"
  },
  {
    id: "android",
    name: "Android",
    icon: <Tablet size={40} />,
    app: "v2rayNG",
    color: "#FF00FF",
    guideAnchor: "guide-android"
  }
];

export default function Devices() {
  const scrollToGuide = (anchor: string) => {
    const el = document.getElementById(anchor);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      window.location.href = `/#${anchor}`;
    }
  };

  // Hardcoded guides for the landing page
  const guidesData = [
    {
      id: "guide-mac",
      title: "MacBook (v2rayU)",
      steps: [
        "Скачайте v2rayU (GitHub Releases)",
        "Откройте .dmg → перетащите в Applications",
        "Servers → Import from clipboard → вставьте vless://",
        "Connect → проверьте IP на ip8.ru"
      ]
    },
    {
      id: "guide-ios",
      title: "iPhone (Shadowrocket)",
      steps: [
        "Купите Shadowrocket в App Store ($2.99)",
        "Откройте → + → Scan QR / Import URL",
        "Разрешите VPN-профиль",
        "Connect → иконка VPN в статус-баре"
      ]
    },
    {
      id: "guide-android",
      title: "Android (v2rayNG)",
      steps: [
        "Установите v2rayNG (Google Play / GitHub)",
        "Откройте → + → Import config from clipboard",
        "Разрешите VPN-соединение",
        "▶ → проверьте IP"
      ]
    }
  ];

  return (
    <section className="py-20 relative" id="devices">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            <span className="text-white">Ваши </span>
            <span className="text-[#00FFFF] neon-text-cyan">Устройства</span>
          </h2>
          <p className="text-gray-400">Поддерживаем все платформы для гео-арбитража</p>
        </div>

        {/* Device Selection Buttons */}
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
          {devices.map((device) => (
            <button
              key={device.id}
              onClick={() => scrollToGuide(device.guideAnchor)}
              className="group glass-panel rounded-xl p-8 text-center transition-all duration-300 hover:scale-105 border border-white/10 hover:border-[#00FFFF]/50"
            >
              <div
                className="mb-4 flex justify-center transition-colors"
                style={{ color: device.color }}
              >
                {device.icon}
              </div>
              <h3 className="font-mono text-xl text-white mb-2">{device.name}</h3>
              <p className="text-sm text-gray-500 mb-4">{device.app}</p>
              <div className="flex items-center justify-center gap-1 text-[#00FFFF] text-sm font-mono opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Гайд</span>
                <ArrowDown size={14} />
              </div>
            </button>
          ))}
        </div>

        {/* Guides Section */}
        <div className="max-w-4xl mx-auto space-y-6">
          {guidesData.map((guide) => (
            <div key={guide.id} id={guide.id} className="glass-panel rounded-lg p-6">
              <h4 className="font-mono text-[#00FFFF] mb-1">{guide.title}</h4>
              <div className="space-y-2 mt-4">
                {guide.steps.map((step, i) => (
                  <div key={i} className="flex gap-3 text-sm text-gray-300">
                    <span className="text-[#FF00FF] font-mono">{String(i+1).padStart(2, '0')}</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

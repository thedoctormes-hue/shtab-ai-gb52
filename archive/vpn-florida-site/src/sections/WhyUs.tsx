import { Shield, Eye, MapPin, Terminal, Lock, Gauge } from "lucide-react";

const features = [
  {
    icon: <Terminal size={28} />,
    title: "VLESS Reality (Xray)",
    description: "Современный протокол с маскировкой трафика под HTTPS. Обходит Deep Packet Inspection.",
    color: "#FF00FF"
  },
  {
    icon: <Eye size={28} />,
    title: "Без логов трафика",
    description: "Мы не храним логи подключений, трафика и DNS-запросов. Ваша активность остается приватной.",
    color: "#00FFFF"
  },
  {
    icon: <MapPin size={28} />,
    title: "Честная локация Флорида",
    description: "Реальный сервер в Майами, не виртуальная локация. IP принадлежит американскому провайдеру.",
    color: "#FF00FF"
  },
  {
    icon: <Lock size={28} />,
    title: "Шифрование xtls-rprx-vision",
    description: "Потоковое шифрование без лишних метаданных. Максимальная производительность.",
    color: "#00FFFF"
  },
  {
    icon: <Shield size={28} />,
    title: "Защита от утечек",
    description: "Встроенная защита от DNS и WebRTC утечек. Ваш реальный IP всегда скрыт.",
    color: "#FF00FF"
  },
  {
    icon: <Gauge size={28} />,
    title: "Высокая скорость",
    description: "Канал 1Gbps. Низкая задержка для арбитража и стриминга. Без лимитов по трафику.",
    color: "#00FFFF"
  }
];

export default function WhyUs() {
  return (
    <section className="py-20 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#1a0a2e]/30 to-transparent"></div>
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            <span className="text-white">Почему </span>
            <span className="text-[#FF00FF] neon-text-pink">мы</span>
          </h2>
          <p className="text-gray-400">Преимущества для профессионалов гео-арбитража</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {features.map((feature, i) => (
            <div
              key={i}
              className="glass-panel rounded-xl p-6 border border-white/10 hover:border-white/20 transition-all duration-300 group"
            >
              <div 
                className="mb-4 transition-transform group-hover:scale-110"
                style={{ color: feature.color }}
              >
                {feature.icon}
              </div>
              <h3 className="font-mono text-lg text-white mb-3">{feature.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

import { Zap, Shield, ChevronRight, Terminal } from "lucide-react";
import IPWidget from "../components/IPWidget";
import ServerStatus from "../components/ServerStatus";

export default function Hero() {
  const scrollToPayment = () => {
    const el = document.getElementById('payment');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 gradient-bg"></div>
      <div className="absolute inset-0 scanline opacity-50"></div>
      
      {/* Grid overlay */}
      <div 
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `
            linear-gradient(rgba(0, 255, 255, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 0, 255, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px'
        }}
      ></div>

      {/* Floating particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 rounded-full animate-pulse"
            style={{
              background: i % 2 === 0 ? '#FF00FF' : '#00FFFF',
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              opacity: 0.6
            }}
          ></div>
        ))}
      </div>

      <div className="relative z-10 container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel border border-[#FF00FF]/30 mb-8">
            <Terminal size={14} className="text-[#FF00FF]" />
            <span className="font-mono text-xs text-[#FF00FF]">VLESS Reality Xray</span>
          </div>

          {/* Main title */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
            <span className="text-white">VPN </span>
            <span className="neon-text-pink text-[#FF00FF]">Флорида</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-400 mb-4 font-mono">
            Майами для гео-арбитража
          </p>
          <p className="text-sm text-gray-500 mb-10 max-w-lg mx-auto">
            Безопасный VLESS Reality сервер в Майами. 
            Без логов. Честная локация. Для профессионалов.
          </p>

          {/* CTA Button */}
          <button
            onClick={scrollToPayment}
            className="neon-button text-lg py-4 px-8 rounded font-mono inline-flex items-center gap-3 mb-12"
          >
            <Zap size={20} />
            Получить доступ за $15/мес
            <ChevronRight size={20} />
          </button>

          {/* Info widgets */}
          <div className="grid md:grid-cols-3 gap-4 max-w-2xl mx-auto">
            <IPWidget />
            <ServerStatus />
            <div className="glass-panel rounded-lg p-4 border border-[#FF00FF]/30">
              <div className="flex items-center gap-2 mb-2">
                <Shield size={16} className="text-[#FF00FF]" />
                <span className="font-mono text-xs text-gray-400 uppercase tracking-wider">Протокол</span>
              </div>
              <div className="font-mono text-sm text-white">VLESS + Reality</div>
              <div className="text-xs text-gray-500">Xray-core v1.8+</div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0a0a0f] to-transparent"></div>
    </section>
  );
}

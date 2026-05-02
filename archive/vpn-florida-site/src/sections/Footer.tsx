import { Terminal } from "lucide-react";

export default function Footer() {
  return (
    <footer className="py-12 border-t border-white/10">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <Terminal size={20} className="text-[#FF00FF]" />
            <span className="font-mono text-lg text-white">VPN Florida</span>
          </div>

          <div className="flex flex-col md:flex-row items-center gap-4 text-sm text-gray-500">
            <span>Майами, Флорида, США</span>
            <span className="hidden md:inline">|</span>
            <span>VLESS Reality Xray</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>Разработано</span>
            <span className="text-[#00FFFF] font-mono">IT/Ai</span>
            <span>лабораторией</span>
            <span className="text-[#FF00FF] font-mono">"Doctorm&Ai"</span>
          </div>
        </div>

        <div className="mt-8 text-center text-xs text-gray-700 font-mono">
          © 2024 VPN Florida. Все права защищены. Не для использования в незаконных целях.
        </div>
      </div>
    </footer>
  );
}

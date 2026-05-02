import PaymentForm from "../components/PaymentForm";
import { Wallet, MessageCircle, HelpCircle } from "lucide-react";

export default function Payment() {
  return (
    <section className="py-20 relative" id="payment">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0a1a2e]/30 to-transparent"></div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            <span className="text-white">Оплата </span>
            <span className="text-[#00FFFF] neon-text-cyan">доступа</span>
          </h2>
          <p className="text-gray-400">USDT (TRC-20) — быстро, анонимно, без комиссий банков</p>
        </div>

        {/* 2 Column Layout for Symmetry */}
        <div className="grid lg:grid-cols-2 gap-6 max-w-6xl mx-auto">
          <PaymentForm />

          {/* Merged: Instruction + Support */}
          <div className="space-y-6">
            <div className="glass-panel rounded-lg p-6 border border-[#00FFFF]/30">
              <div className="flex items-center gap-2 mb-4">
                <Wallet size={18} className="text-[#00FFFF]" />
                <h3 className="font-mono text-lg text-[#00FFFF]">Инструкция</h3>
              </div>
              <div className="space-y-4 text-sm text-gray-300">
                <div className="flex gap-3">
                  <span className="text-[#FF00FF] font-mono">01</span>
                  <p>Откройте кошелек с USDT (TronLink, Trust Wallet, Binance Pay)</p>
                </div>
                <div className="flex gap-3">
                  <span className="text-[#FF00FF] font-mono">02</span>
                  <p>Выберите сеть <strong className="text-white">TRC-20 (Tron)</strong></p>
                </div>
                <div className="flex gap-3">
                  <span className="text-[#FF00FF] font-mono">03</span>
                  <p>Отправьте ровно <strong className="text-[#00FFFF]">15.00 USDT</strong></p>
                </div>
                <div className="flex gap-3">
                  <span className="text-[#FF00FF] font-mono">04</span>
                  <p>Скопируйте TXID (хеш транзакции)</p>
                </div>
                <div className="flex gap-3">
                  <span className="text-[#FF00FF] font-mono">05</span>
                  <p>Вставьте хеш в форму слева</p>
                </div>
              </div>
            </div>

            <div className="glass-panel rounded-lg p-6 border border-[#FF00FF]/30">
              <div className="flex items-center gap-2 mb-4">
                <MessageCircle size={18} className="text-[#FF00FF]" />
                <h3 className="font-mono text-lg text-[#FF00FF]">Поддержка</h3>
              </div>
              <p className="text-sm text-gray-400 mb-6">
                После отправки хеша напишите нам для быстрого подтверждения:
              </p>
              <a
                href="https://t.me/DoctorMES"
                target="_blank"
                rel="noopener noreferrer"
                className="neon-button w-full py-3 px-4 rounded font-mono text-sm inline-flex items-center justify-center gap-2"
              >
                <MessageCircle size={16} />
                Написать @DoctorMES
              </a>
              <div className="mt-6 pt-4 border-t border-white/10">
                  <div className="flex items-center gap-2 mb-2">
                      <HelpCircle size={16} className="text-[#00FFFF]" />
                      <h4 className="font-mono text-sm text-[#00FFFF]">FAQ</h4>
                  </div>
                  <p className="text-xs text-gray-500">
                      Обычно доступ приходит в течение 15 минут после подтверждения хеша.
                  </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

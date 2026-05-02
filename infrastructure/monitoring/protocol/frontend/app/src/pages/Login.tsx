import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Brain, Loader2 } from 'lucide-react';

type LoginState = 'idle' | 'loading' | 'error';

const Login: React.FC = () => {
  const [tgId, setTgId] = useState('');
  const [state, setState] = useState<LoginState>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const { login, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate('/home', { replace: true });
    }
  }, [user, navigate]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tgId.trim() || tgId.length < 5) {
      setState('error');
      setErrorMsg('Введите корректный Telegram ID (минимум 5 цифр)');
      return;
    }

    setState('loading');
    setErrorMsg('');

    try {
      await login(tgId.trim());
      navigate('/home', { replace: true });
    } catch (err: any) {
      setState('error');
      setErrorMsg(err.response?.data?.detail || 'Ошибка входа. Проверьте ID и попробуйте снова.');
    }
  };

  return (
    <div
      className="min-h-screen w-full flex items-center justify-center px-4"
      style={{ backgroundColor: 'var(--bg-primary)' }}
    >
      <div
        className="w-full max-w-[360px] rounded-2xl p-8 md:p-10"
        style={{
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
          animation: 'fadeInUp 400ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        }}
      >
        {/* Logo */}
        <div className="flex flex-col items-center gap-2 animate-fade-in-up">
          <Brain size={48} style={{ color: 'var(--accent)' }} />
          <h1
            className="font-display text-[28px] font-bold"
            style={{ color: 'var(--text-primary)' }}
          >
            LabDoctorM
          </h1>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Ваш второй мозг
          </p>
        </div>

        {/* Divider */}
        <div
          className="my-6"
          style={{ borderTop: '1px solid var(--border-color)' }}
        />

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            <label
              className="block text-xs font-medium mb-1.5"
              style={{ color: 'var(--text-secondary)' }}
            >
              Telegram ID
            </label>
            <input
              ref={inputRef}
              type="number"
              value={tgId}
              onChange={e => {
                setTgId(e.target.value);
                if (state === 'error') setState('idle');
              }}
              placeholder="Введите ваш ID"
              className="w-full px-4 py-3 rounded-[10px] text-base outline-none transition-all duration-200"
              style={{
                backgroundColor: 'var(--bg-primary)',
                border: `1px solid ${state === 'error' ? 'var(--danger)' : 'var(--border-color)'}`,
                color: 'var(--text-primary)',
              }}
              onFocus={e => {
                if (state !== 'error') {
                  e.currentTarget.style.borderColor = 'var(--border-focus)';
                  e.currentTarget.style.boxShadow = '0 0 0 3px var(--accent-soft)';
                }
              }}
              onBlur={e => {
                e.currentTarget.style.borderColor = state === 'error' ? 'var(--danger)' : 'var(--border-color)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            />
            {state === 'error' && errorMsg && (
              <p className="mt-2 text-xs" style={{ color: 'var(--danger)' }}>
                {errorMsg}
              </p>
            )}
          </div>

          <div className="animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            <button
              type="submit"
              disabled={state === 'loading'}
              className="w-full py-3 rounded-lg text-sm font-medium text-white transition-all duration-200 flex items-center justify-center gap-2"
              style={{
                backgroundColor: state === 'loading' ? 'var(--accent-hover)' : 'var(--accent)',
                opacity: state === 'loading' ? 0.8 : 1,
              }}
              onMouseEnter={e => {
                if (state !== 'loading') {
                  e.currentTarget.style.backgroundColor = 'var(--accent-hover)';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                }
              }}
              onMouseLeave={e => {
                e.currentTarget.style.backgroundColor = 'var(--accent)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              {state === 'loading' ? (
                <>
                  <Loader2 size={16} className="animate-spin-slow" />
                  Вход...
                </>
              ) : (
                'Войти'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;

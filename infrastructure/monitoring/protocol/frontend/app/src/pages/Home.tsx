import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as fragmentsAPI from '../api/fragments';
import FragmentCard from '../components/FragmentCard';
import type { Fragment } from '../components/FragmentCard';
import { useToast } from '../hooks/useToast';
import Toast from '../components/Toast';
import {
  Send,
  Loader2,
  Check,
  ChevronDown,
  Lock,
  UserCheck,
  Globe,
  FileText,
} from 'lucide-react';

type SaveState = 'idle' | 'saving' | 'success';
type Privacy = 'private' | 'trusted' | 'public';

const privacyOptions: { value: Privacy; label: string; icon: React.ElementType }[] = [
  { value: 'private', label: 'Private', icon: Lock },
  { value: 'trusted', label: 'Trusted', icon: UserCheck },
  { value: 'public', label: 'Public', icon: Globe },
];

const privacyColors: Record<Privacy, { text: string; bg: string }> = {
  private: { text: 'var(--privacy-private)', bg: 'rgba(196, 90, 74, 0.12)' },
  trusted: { text: 'var(--privacy-trusted)', bg: 'rgba(212, 160, 72, 0.12)' },
  public: { text: 'var(--privacy-public)', bg: 'rgba(90, 154, 110, 0.12)' },
};

const Home: React.FC = () => {
  const [thought, setThought] = useState('');
  const [privacy, setPrivacy] = useState<Privacy>('private');
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [fragments, setFragments] = useState<Fragment[]>([]);
  const [loading, setLoading] = useState(true);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [showPrivacyDropdown, setShowPrivacyDropdown] = useState(false);
  const [isInputFocused, setIsInputFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { toasts, addToast, removeToast } = useToast();

  const LIMIT = 20;

  // Load draft from localStorage
  useEffect(() => {
    const draft = localStorage.getItem('thought_draft');
    const draftPrivacy = localStorage.getItem('thought_privacy') as Privacy;
    if (draft) setThought(draft);
    if (draftPrivacy && privacyOptions.some(o => o.value === draftPrivacy)) {
      setPrivacy(draftPrivacy);
    }
  }, []);

  // Save draft
  useEffect(() => {
    if (thought) {
      localStorage.setItem('thought_draft', thought);
      localStorage.setItem('thought_privacy', privacy);
    } else {
      localStorage.removeItem('thought_draft');
      localStorage.removeItem('thought_privacy');
    }
  }, [thought, privacy]);

  // Load fragments
  const loadFragments = useCallback(async (newOffset = 0, append = false) => {
    try {
      const res = await fragmentsAPI.listFragments(LIMIT, newOffset);
      const newFragments = res.data;
      if (append) {
        setFragments(prev => [...prev, ...newFragments]);
      } else {
        setFragments(newFragments);
      }
      setHasMore(newFragments.length === LIMIT);
    } catch (err) {
      addToast('Ошибка загрузки фрагментов', 'error');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [addToast]);

  useEffect(() => {
    loadFragments(0, false);
  }, [loadFragments]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowPrivacyDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSave = async () => {
    if (!thought.trim()) return;

    setSaveState('saving');
    try {
      const res = await fragmentsAPI.createFragment(thought.trim(), 'text', privacy);
      setSaveState('success');
      addToast('Мысль сохранена', 'success');
      setThought('');
      localStorage.removeItem('thought_draft');
      localStorage.removeItem('thought_privacy');

      // Add new fragment to top
      setFragments(prev => [res.data, ...prev]);

      setTimeout(() => setSaveState('idle'), 1500);
    } catch (err) {
      setSaveState('idle');
      addToast('Ошибка сохранения', 'error');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await fragmentsAPI.deleteFragment(id);
      setFragments(prev => prev.filter(f => f.id !== id));
      addToast('Мысль удалена', 'success');
    } catch (err) {
      addToast('Ошибка удаления', 'error');
    }
  };

  const handleLoadMore = () => {
    const newOffset = offset + LIMIT;
    setOffset(newOffset);
    setLoadingMore(true);
    loadFragments(newOffset, true);
  };

  const currentPrivacy = privacyOptions.find(o => o.value === privacy)!;
  const CurrentPrivacyIcon = currentPrivacy.icon;
  const pColor = privacyColors[privacy];

  return (
    <div>
      <Toast toasts={toasts} onRemove={removeToast} />

      {/* Page Title */}
      <h1
        className="font-display text-[32px] font-semibold mb-6"
        style={{ color: 'var(--text-primary)' }}
      >
        Главная
      </h1>

      {/* Input Area */}
      <div
        className="rounded-xl p-5 mb-8 transition-all duration-200"
        style={{
          backgroundColor: 'var(--bg-secondary)',
          border: `1px solid ${isInputFocused ? 'var(--border-focus)' : 'var(--border-color)'}`,
          boxShadow: isInputFocused ? '0 0 0 3px var(--accent-soft)' : 'none',
        }}
      >
        <textarea
          ref={textareaRef}
          value={thought}
          onChange={e => setThought(e.target.value)}
          placeholder="Запишите вашу мысль..."
          className="w-full bg-transparent border-0 outline-none resize-y text-base"
          style={{
            color: 'var(--text-primary)',
            lineHeight: 1.6,
            minHeight: '120px',
          }}
          onFocus={() => setIsInputFocused(true)}
          onBlur={() => setIsInputFocused(false)}
        />

        {/* Controls row */}
        <div className="flex items-center justify-between mt-4">
          {/* Privacy Selector */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowPrivacyDropdown(!showPrivacyDropdown)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150"
              style={{
                border: '1px solid var(--border-color)',
                color: pColor.text,
                backgroundColor: 'transparent',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <CurrentPrivacyIcon size={14} />
              <span>{currentPrivacy.label}</span>
              <ChevronDown
                size={14}
                className={`transition-transform duration-150 ${showPrivacyDropdown ? 'rotate-180' : ''}`}
              />
            </button>

            {showPrivacyDropdown && (
              <div
                className="absolute top-full left-0 mt-1 rounded-xl py-1.5 z-20 min-w-[160px]"
                style={{
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
                }}
              >
                {privacyOptions.map(option => {
                  const OptIcon = option.icon;
                  const optColor = privacyColors[option.value];
                  return (
                    <button
                      key={option.value}
                      onClick={() => {
                        setPrivacy(option.value);
                        setShowPrivacyDropdown(false);
                      }}
                      className="flex items-center gap-2.5 w-full px-3 py-2 text-sm transition-colors duration-150"
                      style={{ color: optColor.text }}
                      onMouseEnter={e => {
                        e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
                      }}
                      onMouseLeave={e => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }}
                    >
                      <OptIcon size={14} />
                      <span>{option.label}</span>
                      {option.value === privacy && (
                        <Check size={14} className="ml-auto" />
                      )}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={saveState === 'saving' || !thought.trim()}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium text-white transition-all duration-200"
            style={{
              backgroundColor:
                saveState === 'success'
                  ? 'var(--success)'
                  : !thought.trim()
                  ? 'var(--bg-tertiary)'
                  : 'var(--accent)',
              opacity: !thought.trim() && saveState !== 'success' ? 0.5 : 1,
              cursor: !thought.trim() && saveState !== 'success' ? 'not-allowed' : 'pointer',
            }}
            onMouseEnter={e => {
              if (thought.trim() && saveState !== 'saving') {
                e.currentTarget.style.backgroundColor =
                  saveState === 'success' ? 'var(--success)' : 'var(--accent-hover)';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }
            }}
            onMouseLeave={e => {
              e.currentTarget.style.backgroundColor =
                saveState === 'success' ? 'var(--success)' : 'var(--accent)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            {saveState === 'saving' ? (
              <Loader2 size={16} className="animate-spin-slow" />
            ) : saveState === 'success' ? (
              <Check size={16} />
            ) : (
              <Send size={16} />
            )}
            <span>
              {saveState === 'saving' ? 'Сохранение...' : saveState === 'success' ? 'Сохранено' : 'Сохранить'}
            </span>
          </button>
        </div>
      </div>

      {/* Fragments List */}
      <h2
        className="text-lg font-semibold mb-4"
        style={{ color: 'var(--text-primary)' }}
      >
        Сегодня
      </h2>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={24} className="animate-spin-slow" style={{ color: 'var(--accent)' }} />
        </div>
      ) : fragments.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <FileText size={48} style={{ color: 'var(--text-tertiary)' }} />
          <p className="mt-4 text-base" style={{ color: 'var(--text-secondary)' }}>
            Пока нет мыслей
          </p>
          <p className="mt-1 text-xs" style={{ color: 'var(--text-tertiary)' }}>
            Запишите первую ↑
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {fragments.map((fragment, i) => (
            <FragmentCard
              key={fragment.id}
              fragment={fragment}
              onDelete={handleDelete}
              index={i}
            />
          ))}

          {/* Load More */}
          {hasMore && (
            <button
              onClick={handleLoadMore}
              disabled={loadingMore}
              className="w-full py-3 rounded-xl text-sm font-medium transition-all duration-200"
              style={{
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-secondary)',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'var(--accent)';
                e.currentTarget.style.borderColor = 'rgba(212, 160, 72, 0.3)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'var(--border-color)';
              }}
            >
              {loadingMore ? (
                <Loader2 size={16} className="animate-spin-slow inline" />
              ) : (
                'Загрузить ещё'
              )}
            </button>
          )}

          {!hasMore && fragments.length > 0 && (
            <p className="text-center text-xs py-4" style={{ color: 'var(--text-tertiary)' }}>
              Все фрагменты загружены
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default Home;

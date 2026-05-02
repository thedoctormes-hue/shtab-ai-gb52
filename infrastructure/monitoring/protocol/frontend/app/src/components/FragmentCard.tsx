import React from 'react';
import { Lock, UserCheck, Globe, Trash2 } from 'lucide-react';

export interface Fragment {
  id: string;
  text: string;
  summary?: string;
  source: string;
  privacy: 'private' | 'trusted' | 'public';
  created_at: string;
  emotion?: any;
  semantic_vector?: any;
}

interface FragmentCardProps {
  fragment: Fragment;
  onDelete?: (id: number) => void;
  highlightQuery?: string;
  index?: number;
}

const privacyConfig = {
  private: { icon: Lock, label: 'Private', className: 'privacy-private' },
  trusted: { icon: UserCheck, label: 'Trusted', className: 'privacy-trusted' },
  public: { icon: Globe, label: 'Public', className: 'privacy-public' },
};

const formatDate = (iso: string) => {
  const date = new Date(iso);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();
  const isYesterday = new Date(now.getTime() - 86400000).toDateString() === date.toDateString();

  const time = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  if (isToday) return time;
  if (isYesterday) return `Вчера, ${time}`;
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
};

const FragmentCard: React.FC<FragmentCardProps> = ({ fragment, onDelete, highlightQuery, index = 0 }) => {
  const config = privacyConfig[fragment.privacy];
  const PrivacyIcon = config.icon;

  const renderText = () => {
    if (!highlightQuery) return fragment.text;
    const parts = fragment.text.split(new RegExp(`(${highlightQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === highlightQuery.toLowerCase() ? (
        <mark
          key={i}
          className="rounded px-0.5 font-medium"
          style={{ backgroundColor: 'rgba(212, 160, 72, 0.2)' }}
        >
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <div
      className="animate-fade-in-up rounded-xl p-5 transition-all duration-200 relative group"
      style={{
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-color)',
        animationDelay: `${index * 50}ms`,
      }}
      onMouseOver={e => {
        (e.currentTarget as HTMLElement).style.borderColor = 'var(--accent)';
        (e.currentTarget as HTMLElement).style.borderColor = 'rgba(212, 160, 72, 0.25)';
        (e.currentTarget as HTMLElement).style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
      }}
      onMouseOut={e => {
        (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-color)';
        (e.currentTarget as HTMLElement).style.boxShadow = 'none';
      }}
    >
      {/* Top row */}
      <div className="flex items-center justify-between">
        <span
          className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full"
          style={{
            color: fragment.privacy === 'private' ? 'var(--privacy-private)' : fragment.privacy === 'trusted' ? 'var(--privacy-trusted)' : 'var(--privacy-public)',
            backgroundColor: fragment.privacy === 'private' ? 'rgba(196, 90, 74, 0.12)' : fragment.privacy === 'trusted' ? 'rgba(212, 160, 72, 0.12)' : 'rgba(90, 154, 110, 0.12)',
          }}
        >
          <PrivacyIcon size={12} />
          {config.label}
        </span>

        {onDelete && (
          <button
            onClick={() => onDelete(fragment.id)}
            className="p-1.5 rounded-lg transition-all duration-150 opacity-0 group-hover:opacity-100"
            style={{ color: 'var(--text-tertiary)' }}
            onMouseEnter={e => {
              e.currentTarget.style.color = 'var(--danger)';
              e.currentTarget.style.backgroundColor = 'rgba(196, 90, 74, 0.1)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.color = 'var(--text-tertiary)';
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
            title="Удалить"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>

      {/* Text */}
      <p
        className="mt-3 text-base leading-relaxed whitespace-pre-wrap break-words"
        style={{ color: 'var(--text-primary)', lineHeight: 1.6 }}
      >
        {renderText() || fragment.summary}
      </p>

      {/* Bottom row */}
      <div className="flex items-center gap-3 mt-3">
        <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
          {formatDate(fragment.created_at)}
        </span>
        {fragment.source !== 'text' && (
          <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
            {fragment.source}
          </span>
        )}
      </div>
    </div>
  );
};

export default FragmentCard;

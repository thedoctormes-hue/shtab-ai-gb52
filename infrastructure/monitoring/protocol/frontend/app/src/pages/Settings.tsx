import React, { useState, useEffect } from 'react';
import * as settingsAPI from '../api/settings';
import { useToast } from '../hooks/useToast';
import Toast from '../components/Toast';
import { Loader2, Check, Archive, FileCode, FileText } from 'lucide-react';

type SaveState = 'idle' | 'loading' | 'success';

const exportFormats = [
  {
    value: 'bundle',
    label: 'Bundle',
    description: 'Полный архив со всеми данными',
    icon: Archive,
  },
  {
    value: 'json',
    label: 'JSON',
    description: 'Структурированный формат для разработчиков',
    icon: FileCode,
  },
  {
    value: 'txt',
    label: 'TXT',
    description: 'Только текст, простой и читаемый',
    icon: FileText,
  },
];

const autoDeleteOptions = [
  { value: 'never', label: 'Никогда' },
  { value: '30d', label: 'Через 30 дней' },
  { value: '90d', label: 'Через 90 дней' },
  { value: '1y', label: 'Через 1 год' },
];

const SettingsPage: React.FC = () => {
  const [exportFormat, setExportFormat] = useState('bundle');
  const [autoDelete, setAutoDelete] = useState('never');
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [loading, setLoading] = useState(true);
  const { toasts, addToast, removeToast } = useToast();

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const res = await settingsAPI.getSettings();
      if (res.data) {
        setExportFormat(res.data.export_format || 'bundle');
        setAutoDelete(res.data.auto_delete || 'never');
      }
    } catch (err) {
      // silent error — use defaults
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaveState('loading');
    try {
      await settingsAPI.saveSettings({
        export_format: exportFormat,
        auto_delete: autoDelete,
      });
      setSaveState('success');
      addToast('Настройки сохранены', 'success');
      setTimeout(() => setSaveState('idle'), 1500);
    } catch (err) {
      setSaveState('idle');
      addToast('Ошибка сохранения', 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 size={24} className="animate-spin-slow" style={{ color: 'var(--accent)' }} />
      </div>
    );
  }

  return (
    <div>
      <Toast toasts={toasts} onRemove={removeToast} />

      {/* Page Title */}
      <h1
        className="font-display text-[32px] font-semibold mb-8"
        style={{ color: 'var(--text-primary)' }}
      >
        Настройки
      </h1>

      {/* Export Section */}
      <div className="mb-8">
        <h2
          className="text-xl font-semibold mb-2"
          style={{ color: 'var(--text-primary)' }}
        >
          Экспорт
        </h2>
        <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
          Выберите формат для экспорта ваших фрагментов
        </p>

        <div className="space-y-2">
          {exportFormats.map(fmt => {
            const Icon = fmt.icon;
            const isSelected = exportFormat === fmt.value;
            return (
              <label
                key={fmt.value}
                className="flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all duration-150"
                style={{
                  backgroundColor: isSelected ? 'var(--accent-soft)' : 'transparent',
                  border: `1px solid ${isSelected ? 'var(--accent)' : 'var(--border-color)'}`,
                }}
                onMouseEnter={e => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
                  }
                }}
                onMouseLeave={e => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }
                }}
              >
                <input
                  type="radio"
                  name="export_format"
                  value={fmt.value}
                  checked={isSelected}
                  onChange={() => setExportFormat(fmt.value)}
                  className="mt-0.5 flex-shrink-0"
                  style={{
                    accentColor: 'var(--accent)',
                    width: '18px',
                    height: '18px',
                  }}
                />
                <div className="flex items-start gap-3 flex-1">
                  <Icon
                    size={18}
                    className="flex-shrink-0 mt-0.5"
                    style={{ color: isSelected ? 'var(--accent)' : 'var(--text-tertiary)' }}
                  />
                  <div>
                    <span
                      className="text-sm font-medium block"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      {fmt.label}
                    </span>
                    <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                      {fmt.description}
                    </span>
                  </div>
                </div>
              </label>
            );
          })}
        </div>
      </div>

      {/* Divider */}
      <div className="my-8" style={{ borderTop: '1px solid var(--border-color)' }} />

      {/* Auto-delete Section */}
      <div className="mb-8">
        <h2
          className="text-xl font-semibold mb-2"
          style={{ color: 'var(--text-primary)' }}
        >
          Авто-удаление
        </h2>
        <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
          Автоматически удалять старые фрагменты
        </p>

        <select
          value={autoDelete}
          onChange={e => setAutoDelete(e.target.value)}
          className="px-4 py-3 rounded-[10px] text-sm outline-none transition-all duration-200 cursor-pointer"
          style={{
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-primary)',
            width: '200px',
          }}
          onFocus={e => {
            e.currentTarget.style.borderColor = 'var(--border-focus)';
            e.currentTarget.style.boxShadow = '0 0 0 3px var(--accent-soft)';
          }}
          onBlur={e => {
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          {autoDeleteOptions.map(opt => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Save Button */}
      <button
        onClick={handleSave}
        disabled={saveState === 'loading'}
        className="flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-medium text-white transition-all duration-200"
        style={{
          backgroundColor: saveState === 'success' ? 'var(--success)' : 'var(--accent)',
          opacity: saveState === 'loading' ? 0.8 : 1,
        }}
        onMouseEnter={e => {
          if (saveState !== 'loading') {
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
        {saveState === 'loading' ? (
          <>
            <Loader2 size={16} className="animate-spin-slow" />
            Сохранение...
          </>
        ) : saveState === 'success' ? (
          <>
            <Check size={16} />
            Сохранено
          </>
        ) : (
          'Сохранить настройки'
        )}
      </button>
    </div>
  );
};

export default SettingsPage;

import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as fragmentsAPI from '../api/fragments';
import FragmentCard from '../components/FragmentCard';
import { Search as SearchIcon, Loader2 } from 'lucide-react';
import type { Fragment } from '../components/FragmentCard';

type SearchState = 'idle' | 'typing' | 'loading' | 'results' | 'empty';

const Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [state, setState] = useState<SearchState>('idle');
  const [results, setResults] = useState<Fragment[]>([]);
  const [resultCount, setResultCount] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const performSearch = useCallback(async (q: string) => {
    if (!q.trim() || q.trim().length < 2) {
      setState('idle');
      setResults([]);
      return;
    }

    setState('loading');
    try {
      const res = await fragmentsAPI.searchFragments(q.trim());
      const data = res.data;
      setResults(data);
      setResultCount(data.length);
      setState(data.length > 0 ? 'results' : 'empty');
    } catch (err) {
      setState('empty');
      setResults([]);
    }
  }, []);

  useEffect(() => {
    clearTimeout(debounceRef.current);

    if (!query.trim()) {
      setState('idle');
      setResults([]);
      return;
    }

    setState('typing');
    debounceRef.current = setTimeout(() => {
      performSearch(query);
    }, 300);

    return () => clearTimeout(debounceRef.current);
  }, [query, performSearch]);

  return (
    <div>
      {/* Page Title */}
      <h1
        className="font-display text-[32px] font-semibold mb-6"
        style={{ color: 'var(--text-primary)' }}
      >
        Поиск
      </h1>

      {/* Search Input */}
      <div className="sticky top-0 z-10 pb-4" style={{ backgroundColor: 'var(--bg-primary)' }}>
        <div className="relative">
          <SearchIcon
            size={16}
            className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none"
            style={{ color: 'var(--text-tertiary)' }}
          />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Введите запрос..."
            className="w-full pl-11 pr-12 py-3.5 rounded-[10px] text-base outline-none transition-all duration-200"
            style={{
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
            }}
            onFocus={e => {
              e.currentTarget.style.borderColor = 'var(--border-focus)';
              e.currentTarget.style.boxShadow = '0 0 0 3px var(--accent-soft)';
            }}
            onBlur={e => {
              e.currentTarget.style.borderColor = 'var(--border-color)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          />
          {state === 'loading' && (
            <Loader2
              size={16}
              className="absolute right-4 top-1/2 -translate-y-1/2 animate-spin-slow"
              style={{ color: 'var(--text-tertiary)' }}
            />
          )}
        </div>
      </div>

      {/* Results */}
      {state === 'results' && (
        <div className="mb-4">
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            Найдено {resultCount} {resultCount === 1 ? 'результат' : resultCount < 5 ? 'результата' : 'результатов'}
          </span>
        </div>
      )}

      {state === 'idle' && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <SearchIcon size={48} style={{ color: 'var(--text-tertiary)' }} />
          <p className="mt-4 text-base" style={{ color: 'var(--text-secondary)' }}>
            Начните вводить запрос
          </p>
          <p className="mt-1 text-xs" style={{ color: 'var(--text-tertiary)' }}>
            Поиск работает по всем вашим фрагментам
          </p>
        </div>
      )}

      {state === 'typing' && (
        <div className="flex items-center justify-center py-16">
          <span className="text-sm" style={{ color: 'var(--text-tertiary)' }}>
            Печатаете...
          </span>
        </div>
      )}

      {state === 'loading' && (
        <div className="flex items-center justify-center py-16">
          <Loader2 size={24} className="animate-spin-slow" style={{ color: 'var(--accent)' }} />
        </div>
      )}

      {state === 'empty' && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <SearchIcon size={48} style={{ color: 'var(--text-tertiary)' }} />
          <p className="mt-4 text-base" style={{ color: 'var(--text-secondary)' }}>
            Ничего не найдено
          </p>
          <p className="mt-1 text-xs" style={{ color: 'var(--text-tertiary)' }}>
            Попробуйте другой запрос
          </p>
        </div>
      )}

      {state === 'results' && (
        <div className="space-y-3">
          {results.map((fragment, i) => (
            <FragmentCard
              key={fragment.id}
              fragment={fragment}
              index={i}
              highlightQuery={query}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Search;

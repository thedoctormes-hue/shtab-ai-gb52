import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import * as peopleAPI from '../api/people';
import { Users, Loader2, ChevronRight, User } from 'lucide-react';
import FragmentCard from '../components/FragmentCard';
import type { Fragment } from '../components/FragmentCard';

interface Person {
  id: string;
  name: string;
  fragment_count: number;
  edge_count: number;
  fragments?: Fragment[];
  edges?: { id: string; name: string; relation_type: string }[];
}

const PeopleList: React.FC = () => {
  const [people, setPeople] = useState<Person[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPeople();
  }, []);

  const loadPeople = async () => {
    try {
      const res = await peopleAPI.listPeople();
      setPeople(res.data);
    } catch (err) {
      // silent error
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 size={24} className="animate-spin-slow" style={{ color: 'var(--accent)' }} />
      </div>
    );
  }

  if (people.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Users size={48} style={{ color: 'var(--text-tertiary)' }} />
        <p className="mt-4 text-base" style={{ color: 'var(--text-secondary)' }}>
          Пока нет людей
        </p>
        <p className="mt-1 text-xs" style={{ color: 'var(--text-tertiary)' }}>
          Добавьте первого через фрагменты
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {people.map((person, i) => (
        <Link
          key={person.id}
          to={`/people/${person.id}`}
          className="flex items-center justify-between rounded-xl p-4 transition-all duration-200 animate-fade-in-up"
          style={{
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            animationDelay: `${i * 50}ms`,
          }}
          onMouseEnter={e => {
            e.currentTarget.style.borderColor = 'rgba(212, 160, 72, 0.25)';
            e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{ backgroundColor: 'var(--accent-soft)' }}
            >
              <User size={18} style={{ color: 'var(--accent)' }} />
            </div>
            <div>
              <h3 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
                {person.name}
              </h3>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                {person.fragment_count} {person.fragment_count === 1 ? 'фрагмент' : person.fragment_count < 5 ? 'фрагмента' : 'фрагментов'}
                {' · '}
                {person.edge_count} {person.edge_count === 1 ? 'связь' : person.edge_count < 5 ? 'связи' : 'связей'}
              </p>
            </div>
          </div>
          <ChevronRight size={18} style={{ color: 'var(--text-tertiary)' }} />
        </Link>
      ))}
    </div>
  );
};

const PersonDetail: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const personId = id || null;
  
  const [person, setPerson] = useState<Person | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (personId) loadPerson(personId);
  }, [personId]);

  const loadPerson = async (pid: string) => {
    try {
      const res = await peopleAPI.getPersonDetails(id);
      setPerson(res.data);
    } catch (err) {
      // silent error
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 size={24} className="animate-spin-slow" style={{ color: 'var(--accent)' }} />
      </div>
    );
  }

  if (!person) {
    return (
      <div className="text-center py-16">
        <p style={{ color: 'var(--text-secondary)' }}>Человек не найден</p>
      </div>
    );
  }

  return (
    <div>
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6 text-xs" style={{ color: 'var(--text-secondary)' }}>
        <Link to="/people" className="hover:underline transition-colors duration-150" style={{ color: 'var(--accent)' }}>
          Люди
        </Link>
        <ChevronRight size={14} />
        <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{person.name}</span>
      </div>

      {/* Person Card */}
      <div
        className="rounded-xl p-6 mb-8"
        style={{
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
        }}
      >
        <div className="flex items-center gap-4">
          <div
            className="w-14 h-14 rounded-full flex items-center justify-center"
            style={{ backgroundColor: 'var(--accent-soft)' }}
          >
            <User size={24} style={{ color: 'var(--accent)' }} />
          </div>
          <div>
            <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
              {person.name}
            </h2>
            <p className="text-sm mt-0.5" style={{ color: 'var(--text-secondary)' }}>
              {person.fragment_count} {person.fragment_count === 1 ? 'фрагмент' : person.fragment_count < 5 ? 'фрагмента' : 'фрагментов'}
              {' · '}
              {person.edge_count} {person.edge_count === 1 ? 'связь' : person.edge_count < 5 ? 'связи' : 'связей'}
            </p>
          </div>
        </div>
      </div>

      {/* Related Fragments */}
      <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Связанные фрагменты
      </h3>
      {person.fragments && person.fragments.length > 0 ? (
        <div className="space-y-3 mb-8">
          {person.fragments.map((fragment, i) => (
            <FragmentCard key={fragment.id} fragment={fragment} index={i} />
          ))}
        </div>
      ) : (
        <p className="text-sm mb-8" style={{ color: 'var(--text-tertiary)' }}>
          Нет связанных фрагментов
        </p>
      )}

      {/* Connections */}
      <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Связи
      </h3>
      {person.edges && person.edges.length > 0 ? (
        <div className="space-y-2">
          {person.edges.map(edge => (
            <Link
              key={edge.id}
              to={`/people/${edge.person_id}`}
              className="flex items-center gap-3 rounded-lg px-4 py-3 transition-all duration-150"
              style={{
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'rgba(212, 160, 72, 0.25)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'var(--border-color)';
              }}
            >
              <User size={16} style={{ color: 'var(--accent)' }} />
              <span className="text-sm flex-1" style={{ color: 'var(--text-primary)' }}>
                {edge.name}
              </span>
              <span
                className="text-xs px-2 py-0.5 rounded-full"
                style={{
                  backgroundColor: 'var(--accent-soft)',
                  color: 'var(--accent)',
                }}
              >
                {edge.relation_type}
              </span>
            </Link>
          ))}
        </div>
      ) : (
        <p className="text-sm" style={{ color: 'var(--text-tertiary)' }}>
          Нет связей
        </p>
      )}
    </div>
  );
};

const People: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const personId = id || null;

  return (
    <div>
      <h1
        className="font-display text-[32px] font-semibold mb-6"
        style={{ color: 'var(--text-primary)' }}
      >
        Люди
      </h1>

      {personId ? <PersonDetail id={personId} /> : <PeopleList />}
    </div>
  );
};

export default People;

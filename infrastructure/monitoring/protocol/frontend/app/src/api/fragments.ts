import api from './client';

export const listFragments = (limit = 20, offset = 0, privacy: string | null = null) => {
  let url = `/fragments?limit=${limit}&offset=${offset}`;
  if (privacy) url += `&privacy=${privacy}`;
  return api.get(url);
};

export const getFragment = (id: string) => api.get(`/fragments/${id}`);

export const createFragment = (text: string, source = 'text', privacy = 'private') =>
  api.post('/fragments', { text, source, privacy });

export const deleteFragment = (id: string) => api.delete(`/fragments/${id}`);

export const searchFragments = (query: string) => api.get(`/fragments/search?q=${encodeURIComponent(query)}`);

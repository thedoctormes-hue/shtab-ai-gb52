import api from './client';

export const login = (tg_id: string) => api.post('/users/register', { tg_id });

export const getMe = () => api.get('/users/me');

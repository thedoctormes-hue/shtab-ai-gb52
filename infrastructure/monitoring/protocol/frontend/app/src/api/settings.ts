import api from './client';

export const getSettings = () => api.get('/settings/exit');

export const saveSettings = (data: { export_format: string; auto_delete: string }) =>
  api.put('/settings/exit', data);

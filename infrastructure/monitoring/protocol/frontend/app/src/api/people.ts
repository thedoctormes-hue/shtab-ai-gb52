import api from './client';

export const listPeople = () => api.get('/people');

export const getPersonDetails = (id: string) => api.get(`/people/${id}`);

export const createEdge = (from_id: string, to_id: string, type = 'similar') =>
  api.post('/edges', { from_id, to_id, relation_type: type });

const API_BASE_URL = 'http://localhost:8000/api';

function authHeaders() {
  return {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json',
  };
}

export const collaborationApi = {
  async list() {
    const response = await fetch(`${API_BASE_URL}/collaborations`, { headers: authHeaders() });
    if (!response.ok) throw new Error('Failed to load collaborations');
    return response.json();
  },

  async create(name: string) {
    const response = await fetch(`${API_BASE_URL}/collaborations`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ name }),
    });
    if (!response.ok) throw new Error('Failed to create collaboration');
    return response.json();
  },

  async invite(collaborationId: number, email: string) {
    const response = await fetch(`${API_BASE_URL}/collaborations/${collaborationId}/invitations`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ email }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to create invitation');
    return data;
  },

  async getInvitation(token: string) {
    const response = await fetch(`${API_BASE_URL}/collaborations/invitations/${token}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Invalid invitation');
    return data;
  },

  async accept(token: string) {
    const response = await fetch(`${API_BASE_URL}/collaborations/invitations/${token}/accept`, {
      method: 'POST',
      headers: authHeaders(),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Could not accept invitation');
    return data;
  },
};
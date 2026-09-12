const API_BASE_URL = 'http://localhost:8000/api';

export const matchingApi = {
  async findMatches(token: string, cvId: number) {
    const response = await fetch(`${API_BASE_URL}/matching/cv/${cvId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to find matches');
    }

    return response.json();
  },

  async getUserMatches(token: string, userId: number) {
    const response = await fetch(`${API_BASE_URL}/matching/user/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user matches');
    }

    return response.json();
  },

  async updateMatchStatus(token: string, matchId: number, status: string) {
    const response = await fetch(`${API_BASE_URL}/matching/${matchId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    });

    if (!response.ok) {
      throw new Error('Failed to update match status');
    }

    return response.json();
  },
};

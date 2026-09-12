const API_BASE_URL = 'http://localhost:8000/api';

export const cvApi = {
  async uploadCV(token: string, file: File, title: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);

    const response = await fetch(`${API_BASE_URL}/cv/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('CV upload failed');
    }

    return response.json();
  },

  async getCV(token: string, cvId: number) {
    const response = await fetch(`${API_BASE_URL}/cv/${cvId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch CV');
    }

    return response.json();
  },

  async getUserCVs(token: string, userId: number) {
    const response = await fetch(`${API_BASE_URL}/cv/user/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user CVs');
    }

    return response.json();
  },

  async analyzeCV(token: string, cvId: number) {
    const response = await fetch(`${API_BASE_URL}/cv/${cvId}/analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('CV analysis failed');
    }

    return response.json();
  },
};

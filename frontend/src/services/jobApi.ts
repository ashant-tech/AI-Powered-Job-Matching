const API_BASE_URL = 'http://localhost:8000/api';

export const jobApi = {
  async getJobs(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    location?: string;
    job_type?: string;
  }) {
    const queryString = new URLSearchParams(params as any).toString();
    const url = `${API_BASE_URL}/jobs/${queryString ? `?${queryString}` : ''}`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error('Failed to fetch jobs');
    }

    return response.json();
  },

  async getJob(jobId: number) {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);

    if (!response.ok) {
      throw new Error('Failed to fetch job');
    }

    return response.json();
  },

  async createJob(token: string, jobData: any) {
    const response = await fetch(`${API_BASE_URL}/jobs/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jobData),
    });

    if (!response.ok) {
      throw new Error('Failed to create job');
    }

    return response.json();
  },
};

const API_BASE_URL = '/api';

export const FIELD_LABELS: Record<string, string> = {
  computer_it: 'Computer / IT',
  engineering: 'Engineering',
  health: 'Health & Medicine',
  business_finance: 'Business & Finance',
  education: 'Education',
  law: 'Law',
  agriculture: 'Agriculture',
  hospitality: 'Hospitality & Tourism',
  media_design: 'Media & Design',
  other: 'Other Fields',
};

export const ETHIOPIAN_CITIES = [
  'Addis Ababa',
  'Dire Dawa',
  'Mekelle',
  'Hawassa',
  'Adama',
  'Bahir Dar',
  'Gondar',
  'Jimma',
  'Dessie',
  'Shashamane',
];

export const jobApi = {
  async getJobs(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    location?: string;
    job_type?: string;
    field?: string;
    remote_only?: boolean;
    salary_min?: number;
    salary_max?: number;
    deadline_days?: number;
  }) {
    const queryString = new URLSearchParams(params as any).toString();
    const url = `${API_BASE_URL}/jobs/${queryString ? `?${queryString}` : ''}`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error('Failed to fetch jobs');
    }

    return response.json();
  },

  async getRecommendedJobs(token: string, limit = 50, signal?: AbortSignal) {
    const response = await fetch(`${API_BASE_URL}/jobs/recommended?limit=${limit}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      signal,
    });

    if (!response.ok) {
      throw new Error('Failed to fetch recommended jobs');
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

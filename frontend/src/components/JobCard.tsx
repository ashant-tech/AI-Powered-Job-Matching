'use client';

interface JobCardProps {
  job: {
    id: number;
    title: string;
    company: string;
    description: string;
    location?: string;
    job_type?: string;
    salary_min?: number;
    salary_max?: number;
    skills?: string;
  };
  onViewDetails?: (jobId: number) => void;
  onApply?: (jobId: number) => void;
}

export default function JobCard({ job, onViewDetails, onApply }: JobCardProps) {
  const skills = job.skills ? JSON.parse(job.skills) : [];

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 mb-2">{job.title}</h3>
          <p className="text-indigo-600 font-semibold mb-2">{job.company}</p>
          
          <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
            {job.location && (
              <span className="flex items-center gap-1">
                📍 {job.location}
              </span>
            )}
            {job.job_type && (
              <span className="flex items-center gap-1">
                💼 {job.job_type}
              </span>
            )}
            {job.salary_min && job.salary_max && (
              <span className="flex items-center gap-1">
                💰 ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
              </span>
            )}
          </div>

          <p className="text-gray-600 line-clamp-2 mb-3">
            {job.description}
          </p>

          {skills.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {skills.slice(0, 5).map((skill: string, index: number) => (
                <span
                  key={index}
                  className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm"
                >
                  {skill}
                </span>
              ))}
              {skills.length > 5 && (
                <span className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
                  +{skills.length - 5} more
                </span>
              )}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2 ml-4">
          {onViewDetails && (
            <button
              onClick={() => onViewDetails(job.id)}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
            >
              View Details
            </button>
          )}
          {onApply && (
            <button
              onClick={() => onApply(job.id)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
            >
              Apply
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

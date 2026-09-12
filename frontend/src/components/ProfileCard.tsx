'use client';

interface ProfileCardProps {
  user: {
    username: string;
    email: string;
    full_name?: string;
    phone?: string;
    is_seeker: boolean;
    created_at: string;
  };
  onEdit?: () => void;
}

export default function ProfileCard({ user, onEdit }: ProfileCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{user.full_name || user.username}</h2>
          <p className="text-gray-600">@{user.username}</p>
        </div>
        {onEdit && (
          <button
            onClick={onEdit}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
          >
            Edit Profile
          </button>
        )}
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <p className="text-gray-900">{user.email}</p>
        </div>

        {user.full_name && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
            <p className="text-gray-900">{user.full_name}</p>
          </div>
        )}

        {user.phone && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
            <p className="text-gray-900">{user.phone}</p>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Account Type</label>
          <p className="text-gray-900">{user.is_seeker ? 'Job Seeker' : 'Employer'}</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Member Since</label>
          <p className="text-gray-900">{new Date(user.created_at).toLocaleDateString()}</p>
        </div>
      </div>
    </div>
  );
}

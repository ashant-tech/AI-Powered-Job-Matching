'use client';

interface SkillBadgeProps {
  skill: string;
  onRemove?: () => void;
}

export default function SkillBadge({ skill, onRemove }: SkillBadgeProps) {
  return (
    <div className="inline-flex items-center gap-2 bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm">
      <span>{skill}</span>
      {onRemove && (
        <button
          onClick={onRemove}
          className="hover:bg-indigo-200 rounded-full p-1 transition"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}

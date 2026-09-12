'use client';

interface MatchScoreProps {
  score: number;
  size?: 'small' | 'medium' | 'large';
}

export default function MatchScore({ score, size = 'medium' }: MatchScoreProps) {
  const getColor = () => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return 'text-sm px-2 py-1';
      case 'large':
        return 'text-xl px-4 py-2';
      default:
        return 'text-base px-3 py-1';
    }
  };

  return (
    <div className={`inline-flex items-center gap-2 ${getColor()} text-white rounded-full font-bold ${getSizeClasses()}`}>
      <span>{score}%</span>
      <span className="text-xs">Match</span>
    </div>
  );
}

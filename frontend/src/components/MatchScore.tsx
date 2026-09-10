type Props = { score: number; size?: "sm" | "lg" };

function color(score: number) {
  if (score >= 75) return "text-emerald-600 border-emerald-500";
  if (score >= 50) return "text-amber-600 border-amber-500";
  return "text-slate-500 border-slate-300";
}

export default function MatchScore({ score, size = "sm" }: Props) {
  const dims = size === "lg" ? "h-20 w-20 text-2xl" : "h-12 w-12 text-sm";
  return (
    <div
      className={`flex shrink-0 items-center justify-center rounded-full border-4 font-bold ${dims} ${color(score)}`}
      title={`${score}% match`}
    >
      {Math.round(score)}%
    </div>
  );
}

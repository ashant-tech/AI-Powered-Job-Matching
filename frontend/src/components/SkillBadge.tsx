type Props = { name: string; variant?: "default" | "matched" | "missing" };

const styles = {
  default: "bg-slate-100 text-slate-700",
  matched: "bg-emerald-100 text-emerald-800",
  missing: "bg-rose-100 text-rose-800",
};

export default function SkillBadge({ name, variant = "default" }: Props) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${styles[variant]}`}>
      {name}
    </span>
  );
}

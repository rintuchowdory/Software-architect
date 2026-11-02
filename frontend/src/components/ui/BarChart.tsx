import { cn } from "@/lib/cn";

type Point = { label: string; value: number };

/**
 * Deliberately plain SVG: no chart library, no bundle weight, and it inherits
 * the palette tokens so it matches light/dark surfaces automatically.
 */
export function BarChart({
  data,
  format = (v) => String(v),
  height = 160,
  className,
}: {
  data: Point[];
  format?: (value: number) => string;
  height?: number;
  className?: string;
}) {
  const max = Math.max(...data.map((d) => d.value), 1);
  const hasData = data.some((d) => d.value > 0);

  return (
    <div className={cn("w-full", className)}>
      <div className="flex items-end gap-2" style={{ height }}>
        {data.map((point) => {
          const ratio = point.value / max;
          return (
            <div key={point.label} className="group flex flex-1 flex-col items-center justify-end gap-2">
              <span className="text-[11px] font-medium text-slate-400 opacity-0 transition group-hover:opacity-100">
                {format(point.value)}
              </span>
              <div
                className={cn(
                  "w-full rounded-t-md transition-all",
                  point.value > 0 ? "bg-signal-500/70 group-hover:bg-signal-400" : "bg-white/5"
                )}
                style={{ height: `${Math.max(ratio * (height - 42), 4)}px` }}
                title={`${point.label}: ${format(point.value)}`}
              />
              <span className="text-[11px] text-slate-500">{point.label}</span>
            </div>
          );
        })}
      </div>
      {!hasData && <p className="mt-2 text-xs text-slate-500">No paid invoices in this period yet.</p>}
    </div>
  );
}

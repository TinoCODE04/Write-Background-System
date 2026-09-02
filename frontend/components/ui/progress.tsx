export function Progress({ value }: { value: number }) {
  return <div className="h-2 overflow-hidden rounded-full bg-black/[.07]" role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}>
    <div className="h-full rounded-full bg-moss transition-[width] duration-500" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
  </div>;
}


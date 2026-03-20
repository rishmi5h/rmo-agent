const SUGGESTIONS = [
  "List all prod configs",
  "Add db_timeout=30 for auth-service in dev",
  "Check if cache_ttl exists for payment-service in staging",
  "Compare configs across environments for order-service",
];

interface Props {
  onSelect: (prompt: string) => void;
}

export default function SuggestedPrompts({ onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-2 px-4 pb-3">
      {SUGGESTIONS.map((s) => (
        <button
          key={s}
          onClick={() => onSelect(s)}
          className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs text-blue-700 hover:bg-blue-100 transition-colors"
        >
          {s}
        </button>
      ))}
    </div>
  );
}

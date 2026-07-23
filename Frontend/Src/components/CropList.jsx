export default function CropList({ crops }) {
  return (
    <div className="bg-white shadow border border-slate-100 rounded-2xl p-5 hover:shadow-md transition">
      <h2 className="font-bold text-slate-700 mb-3 flex items-center gap-1.5 text-base">
        Configured Crops ({crops.length})
      </h2>
      <ul className="text-slate-600 text-sm space-y-2">
        {crops.map((c) => (
          <li key={c.id} className="flex justify-between py-1 border-b border-slate-100 last:border-b-0">
            <span className="font-medium text-slate-800">{c.name}</span>
            <span className="text-xs text-slate-400">{c.typical_duration_days} days</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

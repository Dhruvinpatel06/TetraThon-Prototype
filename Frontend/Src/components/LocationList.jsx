export default function LocationList({ locations }) {
  return (
    <div className="bg-white shadow border border-slate-100 rounded-2xl p-5 hover:shadow-md transition">
      <h2 className="font-bold text-slate-700 mb-3 flex items-center gap-1.5 text-base">
        Deployed Locations ({locations.length})
      </h2>
      <ul className="text-slate-600 text-sm space-y-2">
        {locations.map((l) => (
          <li key={l.id} className="flex justify-between py-1 border-b border-slate-100 last:border-b-0">
            <span className="font-medium text-slate-800">{l.name}</span>
            <span className="text-xs text-slate-400">{l.latitude.toFixed(2)}°, {l.longitude.toFixed(2)}°</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

import React from 'react'

export default function LeafResult({ result }) {
  if (!result) return null

  if (result.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm">
        <div className="flex items-center gap-2">
          <p className="text-sm font-bold text-red-800">Leaf Analysis Failed</p>
        </div>
        <p className="text-xs text-red-600 mt-1 font-medium">{result.error}</p>
      </div>
    )
  }

  const isHealthy = result.is_healthy
  const predictedClassFormatted = result.predicted_class
    ? result.predicted_class.replace(/_/g, ' ')
    : 'Unknown'

  const statusBgClass = isHealthy ? 'bg-emerald-50 border-emerald-200' : 'bg-amber-50 border-amber-200'
  const badgeBgClass = isHealthy ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-900'
  const statusText = isHealthy
    ? 'No disease detected - crop appears healthy'
    : `Disease detected: ${predictedClassFormatted}`

  const topAlternatives = result.top_predictions
    ? result.top_predictions.slice(1).map(p => p.class.replace(/_/g, ' ')).join(', ')
    : null

  return (
    <div className={`border rounded-2xl p-5 shadow-sm transition-all duration-200 ${statusBgClass}`}>
      <div className="flex items-start gap-3.5">
        <div className="flex-1">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h4 className="text-base font-bold text-slate-800 tracking-tight">Leaf Image Analysis</h4>
            <span className={`px-2.5 py-0.5 rounded-md text-xs font-bold uppercase tracking-wider ${badgeBgClass}`}>
              {Math.round(result.confidence * 100)}% confidence
            </span>
          </div>

          <p className="text-sm font-semibold text-slate-800 mt-1 capitalize">
            {statusText}
          </p>

          {topAlternatives && (
            <p className="text-xs text-slate-500 mt-1 font-medium">
              <span className="font-semibold text-slate-600">Top alternatives:</span> {topAlternatives}
            </p>
          )}

          <p className="text-[11px] text-slate-500 mt-2.5 italic border-t border-slate-200/50 pt-2 font-medium">
            AI-assisted pre-screening. Please consult your local KVK or agricultural officer for a certified diagnosis.
          </p>
        </div>
      </div>
    </div>
  )
}

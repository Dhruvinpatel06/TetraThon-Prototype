export default function HealthCheck({ health }) {
  const isOk = health && health.status === 'OK'
  const isError = health && health.status !== 'OK'
  const statusText = health ? health.status : 'Connecting...'

  const dotColor = isOk ? 'bg-emerald-500 animate-ping' : isError ? 'bg-red-500' : 'bg-amber-500 animate-pulse'
  const textColor = isOk ? 'text-emerald-600' : isError ? 'text-red-600' : 'text-amber-600'

  return (
    <div className="bg-white shadow border border-slate-100 rounded-2xl px-6 py-4 text-center mb-8 w-64">
      <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Backend health check</p>
      <p className={`text-xl font-bold mt-1 flex items-center justify-center gap-1.5 ${textColor}`}>
        <span className={`w-2.5 h-2.5 rounded-full inline-block ${dotColor}`} />
        {statusText}
      </p>
    </div>
  )
}

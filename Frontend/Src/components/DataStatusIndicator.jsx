import React from 'react'

export default function DataStatusIndicator({ adapters }) {
  const status = adapters || { weather: 'mock', prices: 'mock' }

  const isWeatherLive = status.weather === 'live'
  const isPriceLive = status.prices === 'live'

  return (
    <div className="flex items-center justify-center gap-4 text-xs font-medium py-1.5 px-4 rounded-full bg-slate-900/90 border border-slate-700/60 text-slate-300 shadow-sm">
      <div className="flex items-center gap-1.5">
        <span className={`inline-block w-2 h-2 rounded-full ${isWeatherLive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
        <span>Weather: <strong className={isWeatherLive ? 'text-emerald-400' : 'text-amber-400'}>{isWeatherLive ? 'Live API' : 'Mock Fallback'}</strong></span>
      </div>
      <span className="text-slate-600">|</span>
      <div className="flex items-center gap-1.5">
        <span className={`inline-block w-2 h-2 rounded-full ${isPriceLive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
        <span>Mandi Prices: <strong className={isPriceLive ? 'text-emerald-400' : 'text-amber-400'}>{isPriceLive ? 'Live API' : 'CSV Fallback'}</strong></span>
      </div>
    </div>
  )
}

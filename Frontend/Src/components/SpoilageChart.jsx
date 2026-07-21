import React from 'react'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts'

export default function SpoilageChart({ crop = 'Cotton', quantity = 10, selectedStorage = 'warehouse' }) {
  // Base daily prices per quintal approx reference
  const basePrices = {
    Cotton: 6200,
    Wheat: 2400,
    Groundnut: 5800,
    Tomato: 1800
  }

  const initialPrice = basePrices[crop] || 5000
  const initialValue = initialPrice * (parseFloat(quantity) || 10)

  const cropModifiers = {
    Tomato: 2.0,
    Groundnut: 0.7,
    Cotton: 0.5,
    Wheat: 0.8
  }

  const modifier = cropModifiers[crop] || 1.0

  const storageConfigs = {
    open: { baseRate: 0.015, maxDays: 60 },
    warehouse: { baseRate: 0.006, maxDays: 150 },
    cold_storage: { baseRate: 0.0015, maxDays: 600 }
  }

  // Generate 30 days curve data
  const data = Array.from({ length: 31 }, (_, day) => {
    const calcVal = (type) => {
      const cfg = storageConfigs[type]
      if (day >= cfg.maxDays) return 0
      const rate = Math.min(1.0, Math.max(0.0, cfg.baseRate * modifier))
      const rem = initialValue * Math.pow(1.0 - rate, day)
      return Math.round(rem)
    }

    return {
      day: `Day ${day}`,
      open: calcVal('open'),
      warehouse: calcVal('warehouse'),
      cold_storage: calcVal('cold_storage')
    }
  })

  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-base font-bold text-slate-800 flex items-center gap-1.5">
          📉 30-Day Produce Spoilage Value Decay
        </h4>
        <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md font-medium">
          {quantity}q {crop}
        </span>
      </div>
      <p className="text-xs text-slate-500 mb-4">
        Projected remaining financial value (₹) over 30 days across storage environments.
      </p>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="day" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`} />
            <Tooltip formatter={(value) => [`₹${value.toLocaleString('en-IN')}`, 'Value Remaining']} />
            <Legend />
            <Line
              type="monotone"
              dataKey="open"
              name="Open Yard"
              stroke="#ef4444"
              strokeWidth={selectedStorage === 'open' ? 3 : 1.5}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="warehouse"
              name="Covered Warehouse"
              stroke="#f59e0b"
              strokeWidth={selectedStorage === 'warehouse' ? 3 : 1.5}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="cold_storage"
              name="Cold Storage"
              stroke="#10b981"
              strokeWidth={selectedStorage === 'cold_storage' ? 3 : 1.5}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

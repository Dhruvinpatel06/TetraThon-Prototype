import React from 'react'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts'

export default function SpoilageChart({ crop = 'Cotton', quantity = 10, selectedStorage = 'warehouse', realData = null }) {
  const data = realData && Array.isArray(realData) && realData.length > 0 ? realData : []

  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-base font-bold text-slate-800 flex items-center gap-1.5">
          30-Day Produce Spoilage Value Decay
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

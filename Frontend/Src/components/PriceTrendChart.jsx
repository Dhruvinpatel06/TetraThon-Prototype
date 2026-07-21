import React from 'react'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts'

export default function PriceTrendChart({ crop = 'Cotton', location = 'Ahmedabad' }) {
  // Base price ranges per quintal
  const basePrices = {
    Cotton: { Ahmedabad: 6200, Surat: 6350, Vadodara: 6150, Rajkot: 6400, Anand: 6250 },
    Wheat: { Ahmedabad: 2400, Surat: 2450, Vadodara: 2380, Rajkot: 2420, Anand: 2410 },
    Groundnut: { Ahmedabad: 5800, Surat: 5750, Vadodara: 5900, Rajkot: 6000, Anand: 5850 },
    Tomato: { Ahmedabad: 1800, Surat: 1950, Vadodara: 1750, Rajkot: 1850, Anand: 1820 }
  }

  const cropBases = basePrices[crop] || basePrices.Cotton

  // Synthetic 90-day price trend generator
  const data = Array.from({ length: 12 }, (_, idx) => {
    const dayOffset = (11 - idx) * 7
    const d = new Date()
    d.setDate(d.getDate() - dayOffset)
    const dateStr = `${d.getMonth() + 1}/${d.getDate()}`

    // Smooth variation curves
    const varA = Math.round(Math.sin(idx * 0.5) * 80)
    const varS = Math.round(Math.cos(idx * 0.4) * 90)
    const varV = Math.round(Math.sin(idx * 0.6 + 1) * 70)
    const varR = Math.round(Math.cos(idx * 0.5 + 2) * 110)
    const varAn = Math.round(Math.sin(idx * 0.3 + 3) * 60)

    return {
      date: dateStr,
      'Ahmedabad APMC': cropBases.Ahmedabad + varA,
      'Surat APMC': cropBases.Surat + varS,
      'Vadodara APMC': cropBases.Vadodara + varV,
      'Rajkot APMC': cropBases.Rajkot + varR,
      'Anand APMC': cropBases.Anand + varAn
    }
  })

  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-base font-bold text-slate-800 flex items-center gap-1.5">
          📈 APMC Mandi Price Trends (90 Days)
        </h4>
        <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-md font-medium border border-emerald-100">
          Selected: {location}
        </span>
      </div>
      <p className="text-xs text-slate-500 mb-4">
        Historical price trends (₹/quintal) across key APMC mandi markets in Gujarat.
      </p>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} />
            <YAxis domain={['auto', 'auto']} tick={{ fontSize: 10 }} tickFormatter={(val) => `₹${val}`} />
            <Tooltip formatter={(value) => [`₹${value}/q`, 'Mandi Price']} />
            <Legend />
            <Line
              type="monotone"
              dataKey="Ahmedabad APMC"
              stroke="#3b82f6"
              strokeWidth={location === 'Ahmedabad' ? 3 : 1.5}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="Surat APMC"
              stroke="#06b6d4"
              strokeWidth={location === 'Surat' ? 3 : 1.5}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="Vadodara APMC"
              stroke="#8b5cf6"
              strokeWidth={location === 'Vadodara' ? 3 : 1.5}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="Rajkot APMC"
              stroke="#f59e0b"
              strokeWidth={location === 'Rajkot' ? 3 : 1.5}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="Anand APMC"
              stroke="#10b981"
              strokeWidth={location === 'Anand' ? 3 : 1.5}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

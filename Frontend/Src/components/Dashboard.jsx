import React, { useState } from 'react'
import SpoilageChart from './SpoilageChart'
import PriceTrendChart from './PriceTrendChart'
import LeafResult from './LeafResult'

export default function Dashboard({ inputs, advisoryResult, postHarvestResult, onEditScenario, onGoHome }) {
  const [expandedAdvisory, setExpandedAdvisory] = useState(null)
  const [expandedOption, setExpandedOption] = useState(null)

  const { locationName, cropName, sowingDate, weatherObservation, quantityQuintals, storageCondition, leafResult } = inputs
  const { advisories, session_id: advSessionId } = advisoryResult
  const { recommendation, option_label, expected_return, expected_return_per_quintal, details, reason, session_id: phSessionId } = postHarvestResult

  const storageLabels = {
    open: 'Open Yard',
    warehouse: 'Covered Warehouse',
    cold_storage: 'Cold Storage'
  }

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(val).replace('INR', '₹')
  }

  const getOptionSvg = (key) => {
    switch (key) {
      case 'sell_now':
        return (
          <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      case 'store':
        return (
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5m0 0h4m-4 0V10m0 11V10" />
          </svg>
        )
      case 'transport':
        return (
          <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0zM13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1e1 1 0 001-1V9a1 1 0 00-1-1h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 00-.293.707V16m5 0h1" />
          </svg>
        )
      default:
        return null
    }
  }

  const getAdvisoryIcon = (type) => {
    switch (type) {
      case 'irrigation':
        return (
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-11.314l.707.707m11.314 11.314l.707-.707M12 5a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        )
      case 'fertiliser':
        return (
          <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        )
      case 'pest':
        return (
          <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )
      default: return null
    }
  }

  return (
    <div className="w-full max-w-6xl space-y-6">
      {/* Top Scenario Bar */}
      <div className="bg-gradient-to-r from-emerald-800 via-teal-800 to-cyan-900 text-white rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider">
              Unified Session #{advSessionId}-{phSessionId}
            </span>
            <span className="bg-teal-500/20 text-teal-300 text-xs px-2.5 py-0.5 rounded-full font-medium">
              Live Evaluation
            </span>
          </div>
          <h2 className="text-2xl font-extrabold mt-2 tracking-tight">
            Unified Farm & Post-Harvest Intelligence
          </h2>
          <p className="text-emerald-100 text-xs mt-1">
            {locationName} • {cropName} • Sown {new Date(sowingDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })} • {quantityQuintals} quintals in {storageLabels[storageCondition]}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onEditScenario}
            className="bg-white/10 hover:bg-white/20 border border-white/20 text-white font-semibold text-xs px-4 py-2.5 rounded-xl transition duration-200 flex items-center gap-1.5"
          >
            Edit Scenario
          </button>
          <button
            onClick={() => window.print()}
            className="bg-white text-slate-800 hover:bg-slate-100 font-bold text-xs px-4 py-2.5 rounded-xl shadow transition duration-200 flex items-center gap-1.5"
          >
            Export / Print
          </button>
        </div>
      </div>

      {/* Leaf Analysis Result (Full Width Banner if present) */}
      {leafResult && (
        <div className="w-full">
          <LeafResult result={leafResult} />
        </div>
      )}

      {/* 2-Column Side-by-Side Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Module A Advisory Panel */}
        <div className="bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden flex flex-col justify-between">
          <div className="bg-gradient-to-r from-emerald-600 to-teal-700 px-5 py-4 text-white flex items-center justify-between">
            <div>
              <h3 className="font-extrabold text-base flex items-center gap-2">
                Module A: Precision Crop Advisory
              </h3>
              <p className="text-emerald-100 text-xs mt-0.5">Stage & weather-aware recommendations</p>
            </div>
            <span className="bg-white/20 text-xs px-2.5 py-1 rounded-lg font-bold">
              Ranked Top 3
            </span>
          </div>

          <div className="p-5 space-y-4 flex-1">
            {advisories.map((adv) => {
              const isExpanded = expandedAdvisory === adv.type
              const details = adv.details

              return (
                <div key={adv.type} className="border border-slate-200 rounded-xl overflow-hidden hover:border-emerald-400 transition">
                  <button
                    onClick={() => setExpandedAdvisory(isExpanded ? null : adv.type)}
                    className="w-full p-3.5 bg-slate-50 flex items-center justify-between text-left focus:outline-none"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-1.5 bg-white rounded-lg border border-slate-200">{getAdvisoryIcon(adv.type)}</div>
                      <div>
                        <div className="font-bold text-slate-800 text-sm">{adv.title}</div>
                        <div className="text-[10px] text-emerald-700 font-semibold uppercase">{adv.confidence} Confidence</div>
                      </div>
                    </div>
                    <svg className={`w-4 h-4 text-slate-400 transform transition ${isExpanded ? 'rotate-180 text-emerald-600' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  <div className="p-3 text-xs text-slate-700 leading-relaxed font-medium bg-white">
                    {adv.plain_text}
                  </div>

                  {isExpanded && details && (
                    <div className="p-3 bg-slate-50 border-t border-slate-100 text-xs text-slate-600 space-y-1.5">
                      {details.stage && <div><strong>Stage:</strong> {details.stage}</div>}
                      {details.water_cm && <div><strong>Watering:</strong> {details.water_cm} cm every {details.interval_days} days</div>}
                      {details.npk_kg_per_acre && (
                        <div><strong>NPK (kg/acre):</strong> N:{details.npk_kg_per_acre.N}, P:{details.npk_kg_per_acre.P}, K:{details.npk_kg_per_acre.K}</div>
                      )}
                      {details.pest_or_disease && <div><strong>Target Pest:</strong> {details.pest_or_disease} ({details.calculated_risk} Risk)</div>}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Right Column: Module B Post-Harvest Planner Panel */}
        <div className="bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden flex flex-col justify-between">
          <div className="bg-gradient-to-r from-teal-700 to-cyan-800 px-5 py-4 text-white flex items-center justify-between">
            <div>
              <h3 className="font-extrabold text-base flex items-center gap-2">
                Module B: Post-Harvest Loss Planner
              </h3>
              <p className="text-teal-100 text-xs mt-0.5">Financial net return decision engine</p>
            </div>
            <div className="p-1.5 bg-white/20 rounded-lg">
              {getOptionSvg(recommendation)}
            </div>
          </div>

          <div className="p-5 space-y-4 flex-1">
            {/* Top Recommendation Banner */}
            <div className="bg-emerald-50 border-2 border-emerald-500 rounded-xl p-4 text-center">
              <span className="text-[10px] font-extrabold uppercase text-emerald-800 bg-emerald-200/60 px-2.5 py-0.5 rounded-full">
                Optimal Decision
              </span>
              <h4 className="text-lg font-bold text-slate-800 mt-1">{option_label}</h4>
              <p className="text-2xl font-black text-emerald-700 mt-1">{formatCurrency(expected_return)}</p>
              <p className="text-xs text-slate-500 mt-0.5 font-medium">({formatCurrency(expected_return_per_quintal)} per quintal)</p>
              <p className="text-xs text-slate-600 italic bg-white/70 rounded-lg p-2.5 mt-3 border border-emerald-100 font-medium">
                "{reason}"
              </p>
            </div>

            {/* Quick Alternatives Accordion */}
            <div className="space-y-2">
              <div className="text-[11px] font-bold text-slate-400 uppercase">Financial Alternatives</div>
              
              <div className="border border-slate-200 rounded-xl text-xs overflow-hidden">
                <button
                  onClick={() => setExpandedOption(expandedOption === 'sell_now' ? null : 'sell_now')}
                  className="w-full p-2.5 bg-slate-50 flex justify-between items-center text-slate-700 font-bold"
                >
                  <span className="flex items-center gap-2">
                    {getOptionSvg('sell_now')}
                    Sell Now ({details.sell_now.market})
                  </span>
                  <span className="text-emerald-700">{formatCurrency(details.sell_now.net_return)}</span>
                </button>
                {expandedOption === 'sell_now' && (
                  <div className="p-3 bg-white border-t border-slate-100 text-slate-600 space-y-1">
                    <div>Price: {formatCurrency(details.sell_now.price_per_quintal)}/q</div>
                    <div>Transport Cost: {formatCurrency(details.sell_now.transport_cost)} ({details.sell_now.distance_km} km)</div>
                  </div>
                )}
              </div>

              <div className="border border-slate-200 rounded-xl text-xs overflow-hidden">
                <button
                  onClick={() => setExpandedOption(expandedOption === 'store' ? null : 'store')}
                  className="w-full p-2.5 bg-slate-50 flex justify-between items-center text-slate-700 font-bold"
                >
                  <span className="flex items-center gap-2">
                    {getOptionSvg('store')}
                    Store 14 Days ({storageLabels[details.store.storage]})
                  </span>
                  <span className="text-emerald-700">{formatCurrency(details.store.net_return)}</span>
                </button>
                {expandedOption === 'store' && (
                  <div className="p-3 bg-white border-t border-slate-100 text-slate-600 space-y-1">
                    <div>Future Price: {formatCurrency(details.store.future_price_per_quintal)}/q</div>
                    <div>Spoilage Loss: -{formatCurrency(details.store.spoilage_loss)}</div>
                    <div>Storage Cost: -{formatCurrency(details.store.storage_cost)}</div>
                  </div>
                )}
              </div>

              <div className="border border-slate-200 rounded-xl text-xs overflow-hidden">
                <button
                  onClick={() => setExpandedOption(expandedOption === 'transport' ? null : 'transport')}
                  className="w-full p-2.5 bg-slate-50 flex justify-between items-center text-slate-700 font-bold"
                >
                  <span className="flex items-center gap-2">
                    {getOptionSvg('transport')}
                    Transport ({details.transport.market})
                  </span>
                  <span className="text-emerald-700">{formatCurrency(details.transport.net_return)}</span>
                </button>
                {expandedOption === 'transport' && (
                  <div className="p-3 bg-white border-t border-slate-100 text-slate-600 space-y-1">
                    <div>Market Price: {formatCurrency(details.transport.price_per_quintal)}/q</div>
                    <div>Transport Cost: -{formatCurrency(details.transport.transport_cost)} ({details.transport.distance_km} km)</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SpoilageChart crop={cropName} quantity={quantityQuintals} selectedStorage={storageCondition} />
        <PriceTrendChart crop={cropName} location={locationName} />
      </div>

      {/* Footer Nav Bar */}
      <div className="flex gap-4 pt-2">
        <button
          onClick={onGoHome}
          className="flex-1 py-3 px-4 bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-bold rounded-xl transition duration-200"
        >
          Return to Home
        </button>
        <button
          onClick={onEditScenario}
          className="flex-1 py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow transition duration-200"
        >
          Analyze Another Scenario
        </button>
      </div>
    </div>
  )
}

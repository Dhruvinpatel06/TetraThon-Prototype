import { useState } from 'react'

export default function PostHarvestResult({ result, inputs, onNewPlan, onGoHome }) {
  const [expandedOption, setExpandedOption] = useState(null) // 'sell_now' | 'store' | 'transport' | null

  const { cropName, quantityQuintals, storageCondition, locationName } = inputs
  const { recommendation, option_label, expected_return, expected_return_per_quintal, details, reason, session_id } = result

  const storageLabels = {
    open: 'Open Yard',
    warehouse: 'Warehouse (Covered)',
    cold_storage: 'Cold Storage',
  }

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(val).replace('INR', '₹')
  }

  const toggleExpand = (option) => {
    setExpandedOption(expandedOption === option ? null : option)
  }

  // Icons for recommended strategy
  const getRecommendationIcon = (rec) => {
    switch (rec) {
      case 'sell_now':
        return '💰'
      case 'store':
        return '🏢'
      case 'transport':
        return '🚚'
      default:
        return '🏆'
    }
  }

  return (
    <div className="w-full max-w-xl bg-slate-50 rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-700 p-6 text-white text-center">
        <span className="text-xs font-semibold bg-emerald-800 bg-opacity-40 text-emerald-100 px-3 py-1 rounded-full uppercase tracking-wider">
          Plan #{session_id} • Analysis Complete
        </span>
        <h2 className="text-2xl font-extrabold mt-3">Post-Harvest Plan</h2>
        <p className="text-emerald-100 text-sm mt-1">
          🌾 {cropName} • {quantityQuintals} Quintals • {storageLabels[storageCondition]} @ {locationName}
        </p>
      </div>

      <div className="p-6 space-y-6">
        {/* Recommended Option Card */}
        <div className="bg-white rounded-2xl shadow-md border-2 border-emerald-500 overflow-hidden">
          <div className="bg-gradient-to-r from-emerald-500 to-teal-600 px-5 py-4 text-white flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider bg-white bg-opacity-20 px-2.5 py-0.5 rounded-full">
              Recommended Strategy
            </span>
            <span className="text-2xl">{getRecommendationIcon(recommendation)}</span>
          </div>

          <div className="p-5 space-y-4">
            <div className="text-center py-2">
              <h3 className="text-xl font-bold text-slate-800">{option_label}</h3>
              <p className="text-3xl font-extrabold text-emerald-600 mt-2">
                {formatCurrency(expected_return)}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Expected Net Return ({formatCurrency(expected_return_per_quintal)}/quintal)
              </p>
            </div>

            <p className="text-sm text-slate-600 bg-emerald-50 bg-opacity-50 border border-emerald-100 rounded-xl p-3.5 italic font-medium leading-relaxed">
              "{reason}"
            </p>
          </div>
        </div>

        {/* Options Comparison / Details */}
        <div className="space-y-3.5">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider pl-1">Compare Alternative Options</h4>

          {/* Option: Sell Now */}
          <div className={`bg-white rounded-xl border transition-all duration-200 ${recommendation === 'sell_now' ? 'border-emerald-300' : 'border-slate-200 hover:border-slate-300'}`}>
            <button
              onClick={() => toggleExpand('sell_now')}
              className="w-full flex items-center justify-between p-4 focus:outline-none text-left"
            >
              <div className="flex items-center gap-3">
                <span className="p-1.5 bg-slate-100 rounded-lg text-sm">💰</span>
                <div>
                  <h5 className="font-bold text-slate-700 text-sm">Sell Now</h5>
                  <p className="text-xs text-slate-400">Sell at nearest market immediately</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-bold text-slate-800 text-sm">{formatCurrency(details.sell_now.net_return)}</span>
                <svg className={`w-4 h-4 text-slate-400 transform transition-transform duration-300 ${expandedOption === 'sell_now' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>
            {expandedOption === 'sell_now' && (
              <div className="px-4 pb-4 pt-1 border-t border-slate-100 bg-slate-50 bg-opacity-50 text-xs text-slate-600 space-y-2">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Market Name:</span>
                  <span className="font-semibold text-slate-800">{details.sell_now.market}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Distance:</span>
                  <span className="font-semibold text-slate-800">{details.sell_now.distance_km} km</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Current Market Price:</span>
                  <span className="font-semibold text-slate-800">{formatCurrency(details.sell_now.price_per_quintal)} / quintal</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 text-red-600">
                  <span>Transport Cost (Min ₹500):</span>
                  <span>- {formatCurrency(details.sell_now.transport_cost)}</span>
                </div>
                <div className="flex justify-between py-1 font-bold text-slate-800">
                  <span>Net Return:</span>
                  <span className="text-emerald-600">{formatCurrency(details.sell_now.net_return)}</span>
                </div>
              </div>
            )}
          </div>

          {/* Option: Store */}
          <div className={`bg-white rounded-xl border transition-all duration-200 ${recommendation === 'store' ? 'border-emerald-300' : 'border-slate-200 hover:border-slate-300'}`}>
            <button
              onClick={() => toggleExpand('store')}
              className="w-full flex items-center justify-between p-4 focus:outline-none text-left"
            >
              <div className="flex items-center gap-3">
                <span className="p-1.5 bg-slate-100 rounded-lg text-sm">🏢</span>
                <div>
                  <h5 className="font-bold text-slate-700 text-sm">Store for 14 Days</h5>
                  <p className="text-xs text-slate-400">Delay sale to hedge for higher future price</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-bold text-slate-800 text-sm">{formatCurrency(details.store.net_return)}</span>
                <svg className={`w-4 h-4 text-slate-400 transform transition-transform duration-300 ${expandedOption === 'store' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>
            {expandedOption === 'store' && (
              <div className="px-4 pb-4 pt-1 border-t border-slate-100 bg-slate-50 bg-opacity-50 text-xs text-slate-600 space-y-2">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Storage Period:</span>
                  <span className="font-semibold text-slate-800">{details.store.store_days} Days</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Storage Type Used:</span>
                  <span className="font-semibold text-slate-800">{storageLabels[details.store.storage]}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 text-blue-600">
                  <span>Projected Future Price:</span>
                  <span className="font-semibold">{formatCurrency(details.store.future_price_per_quintal)} / quintal</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 text-red-600">
                  <span>Estimated Spoilage Loss:</span>
                  <span>- {formatCurrency(details.store.spoilage_loss)}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 text-red-600">
                  <span>Storage Cost (Rent):</span>
                  <span>- {formatCurrency(details.store.storage_cost)}</span>
                </div>
                <div className="flex justify-between py-1 font-bold text-slate-800">
                  <span>Net Return:</span>
                  <span className="text-emerald-600">{formatCurrency(details.store.net_return)}</span>
                </div>
              </div>
            )}
          </div>

          {/* Option: Transport */}
          <div className={`bg-white rounded-xl border transition-all duration-200 ${recommendation === 'transport' ? 'border-emerald-300' : 'border-slate-200 hover:border-slate-300'}`}>
            <button
              onClick={() => toggleExpand('transport')}
              className="w-full flex items-center justify-between p-4 focus:outline-none text-left"
            >
              <div className="flex items-center gap-3">
                <span className="p-1.5 bg-slate-100 rounded-lg text-sm">🚚</span>
                <div>
                  <h5 className="font-bold text-slate-700 text-sm">Transport to Best Market</h5>
                  <p className="text-xs text-slate-400">Sell at market with highest net price</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-bold text-slate-800 text-sm">{formatCurrency(details.transport.net_return)}</span>
                <svg className={`w-4 h-4 text-slate-400 transform transition-transform duration-300 ${expandedOption === 'transport' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>
            {expandedOption === 'transport' && (
              <div className="px-4 pb-4 pt-1 border-t border-slate-100 bg-slate-50 bg-opacity-50 text-xs text-slate-600 space-y-2">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Best Market:</span>
                  <span className="font-semibold text-slate-800">{details.transport.market}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Distance:</span>
                  <span className="font-semibold text-slate-800">{details.transport.distance_km} km</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Market Price:</span>
                  <span className="font-semibold text-slate-800">{formatCurrency(details.transport.price_per_quintal)} / quintal</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 text-red-600">
                  <span>Transport Cost (₹5/km/q):</span>
                  <span>- {formatCurrency(details.transport.transport_cost)}</span>
                </div>
                <div className="flex justify-between py-1 font-bold text-slate-800">
                  <span>Net Return:</span>
                  <span className="text-emerald-600">{formatCurrency(details.transport.net_return)}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer Navigation Buttons */}
      <div className="bg-slate-100 border-t border-slate-200 p-4 flex gap-3">
        <button
          onClick={onGoHome}
          className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 text-sm font-semibold rounded-xl hover:bg-slate-50 transition duration-200"
        >
          Home Dashboard
        </button>
        <button
          onClick={onNewPlan}
          className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold py-2.5 px-4 rounded-xl shadow-md transition duration-200"
        >
          New Plan
        </button>
      </div>
    </div>
  )
}

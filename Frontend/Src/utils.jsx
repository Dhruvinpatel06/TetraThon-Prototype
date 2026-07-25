import React from 'react'

export const storageLabels = {
  open: 'Open Yard',
  warehouse: 'Warehouse (Covered)',
  cold_storage: 'Cold Storage',
}

export const formatCurrency = (val) => {
  if (val === undefined || val === null || isNaN(val)) return '₹0.00'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2
  }).format(val).replace('INR', '₹')
}

export const getOptionSvg = (key) => {
  switch (key) {
    case 'sell_now':
      return (
        <svg className="w-5 h-5 text-emerald-600" aria-label="Sell now option icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    case 'store':
      return (
        <svg className="w-5 h-5 text-blue-600" aria-label="Storage option icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5m0 0h4m-4 0V10m0 11V10" />
        </svg>
      )
    case 'transport':
      return (
        <svg className="w-5 h-5 text-indigo-600" aria-label="Transport option icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0zM13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1a1 1 0 001-1V9a1 1 0 00-1-1h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 00-.293.707V16m5 0h1" />
        </svg>
      )
    default:
      return null
  }
}

export const getStorageLabel = (key) => {
  if (!key) return 'Unknown Storage'
  return storageLabels[key] || key.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())
}

export const getAdvisoryIcon = (type) => {
  switch (type) {
    case 'irrigation':
      return (
        <svg className="w-5 h-5 text-blue-600" aria-label="Irrigation icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L5.6 15.12a2 2 0 00-1.144.12l-1.026.41a2 2 0 00-1.127 2.052l.228 1.826a2 2 0 001.986 1.752h14.864a2 2 0 001.986-1.752l.228-1.826a2 2 0 00-1.127-2.052l-1.026-.41z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v9" />
        </svg>
      )
    case 'fertiliser':
      return (
        <svg className="w-5 h-5 text-emerald-600" aria-label="Fertiliser icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      )
    case 'pest':
      return (
        <svg className="w-5 h-5 text-amber-600" aria-label="Pest alert icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      )
    default:
      return null
  }
}

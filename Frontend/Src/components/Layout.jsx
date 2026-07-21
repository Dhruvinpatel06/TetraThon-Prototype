import React from 'react'

export default function Layout({ children, currentView = 'home', onNavigate }) {
  const navItems = [
    { id: 'home', label: '🏠 Home' },
    { id: 'form', label: '🌾 Crop Advisory' },
    { id: 'ph-form', label: '📦 Post-Harvest' },
    { id: 'dashboard-form', label: '📊 Unified Dashboard' },
  ]

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center pb-12">
      {/* Top Navbar */}
      <header className="w-full bg-slate-900 text-white shadow-md border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex flex-col sm:flex-row items-center justify-between gap-3">
          {/* Brand Logo & Title */}
          <div 
            onClick={() => onNavigate && onNavigate('home')} 
            className="flex items-center gap-2.5 cursor-pointer hover:opacity-90 transition"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-slate-950 text-lg font-black shadow-lg">
              🌾
            </div>
            <div>
              <h1 className="text-lg font-extrabold tracking-tight text-white flex items-center gap-2">
                AgriTech
                <span className="text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded uppercase tracking-wider font-semibold">
                  v1.0 Phase 0
                </span>
              </h1>
              <p className="text-[11px] text-slate-400 font-medium">
                Precision Crop Advisory & Post-Harvest Loss Engine
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          {onNavigate && (
            <nav className="flex items-center gap-1 bg-slate-800/80 p-1 rounded-xl border border-slate-700/50 text-xs">
              {navItems.map((item) => {
                const isActive = currentView === item.id || (item.id === 'dashboard-form' && currentView === 'dashboard')
                return (
                  <button
                    key={item.id}
                    onClick={() => onNavigate(item.id)}
                    className={`px-3 py-1.5 rounded-lg font-semibold transition duration-150 ${
                      isActive
                        ? 'bg-emerald-600 text-white shadow-sm'
                        : 'text-slate-300 hover:text-white hover:bg-slate-700/60'
                    }`}
                  >
                    {item.label}
                  </button>
                )
              })}
            </nav>
          )}
        </div>
      </header>

      {/* Main Content Container */}
      <main className="w-full max-w-6xl px-4 pt-8 flex flex-col items-center flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="mt-16 text-center text-slate-400 text-xs font-semibold uppercase tracking-wider">
        Built for **TetraTHON 2026** — Precision AgriTech Track.
      </footer>
    </div>
  )
}

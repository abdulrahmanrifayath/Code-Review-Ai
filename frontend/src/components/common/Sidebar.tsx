import React from 'react'
import { NavLink } from 'react-router-dom'
import { LayoutDashboard, FolderGit2, FileCode2, FileText, BarChart3 } from 'lucide-react'

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/repositories', label: 'Repositories', icon: FolderGit2 },
    { to: '/reviews', label: 'Code Reviews', icon: FileCode2 },
    { to: '/reports', label: 'Reports', icon: FileText },
  ]

  return (
    <aside className="w-64 border-r border-dark-border bg-dark-card/30 p-4 flex flex-col justify-between hidden md:flex">
      <div className="space-y-1">
        <div className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Platform
        </div>
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-600/10 text-brand-500 border border-brand-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </div>
    </aside>
  )
}

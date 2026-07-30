import React from 'react'
import { Outlet } from 'react-router-dom'
import { Header } from '../components/common/Header'
import { Sidebar } from '../components/common/Sidebar'

export const DashboardLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-[#0b0f17]">
      <Header />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

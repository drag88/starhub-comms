import { Outlet } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';

export function DashboardLayout() {
  return (
    <div className="grid min-h-screen w-full md:grid-cols-[240px_1fr] lg:grid-cols-[260px_1fr] bg-background selection:bg-primary/20">
      <div className="hidden border-r border-white/5 md:block h-screen sticky top-0 overflow-hidden">
        <div className="flex h-full flex-col">
          <Sidebar />
        </div>
      </div>
      <div className="flex flex-col min-h-screen relative">
        <Header />
        <main className="flex flex-1 flex-col gap-6 p-6 lg:p-8 overflow-x-hidden">
          <Outlet />
        </main>
        {/* Ambient Background Effects */}
        <div className="fixed top-0 left-0 right-0 h-[500px] bg-primary/5 blur-[120px] rounded-full pointer-events-none -z-10 transform -translate-y-1/2" />
        <div className="fixed bottom-0 right-0 w-[500px] h-[500px] bg-blue-500/5 blur-[120px] rounded-full pointer-events-none -z-10 transform translate-y-1/3 translate-x-1/3" />
      </div>
    </div>
  );
}

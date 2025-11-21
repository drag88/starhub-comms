import { NavLink } from 'react-router-dom';
import { LayoutDashboard, PlusCircle, Library, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';
import starhubLogo from '@/assets/starhub-logo.png';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'New Campaign', href: '/campaigns/new', icon: PlusCircle },
  { name: 'Library', href: '/library', icon: Library },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  return (
    <div className="flex h-full w-full flex-col glass-panel border-r-0 border-white/5">
      <div className="flex h-16 items-center px-4 border-b border-white/5">
        <div className="flex items-center gap-3 font-semibold min-w-0">
          <img src={starhubLogo} alt="StarHub" className="h-8 w-auto flex-shrink-0" />
          <div className="flex flex-col whitespace-nowrap overflow-hidden">
            <span className="text-xs font-bold tracking-wide text-white uppercase truncate">Customer Comms</span>
            <span className="text-[10px] text-primary tracking-wider uppercase truncate">Generator</span>
          </div>
        </div>
      </div>
      <div className="flex-1 overflow-auto py-4 px-3">
        <nav className="grid items-start gap-1 text-sm font-medium">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-md px-3 py-2.5 transition-all duration-200 group relative overflow-hidden",
                  isActive
                    ? "text-white bg-white/5 shadow-[0_0_15px_rgba(0,166,81,0.1)]"
                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                )
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary shadow-[0_0_10px_#00A651]" />
                  )}
                  <item.icon className={cn("h-4 w-4 transition-colors", isActive ? "text-primary" : "group-hover:text-white")} />
                  <span className="tracking-wide">{item.name}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="mt-auto p-6">
        <p className="text-[10px] text-zinc-600 text-center uppercase tracking-widest font-medium">
          Powered by StarHub CLM Team
        </p>
      </div>
    </div>
  );
}

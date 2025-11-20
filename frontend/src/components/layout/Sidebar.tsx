import { NavLink } from 'react-router-dom';
import { LayoutDashboard, PlusCircle, Library, Settings, Sparkles } from 'lucide-react';
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
    <div className="flex h-full w-64 flex-col border-r bg-card">
      <div className="flex h-14 items-center border-b px-4 lg:h-[60px]">
        <div className="flex items-center gap-2 font-semibold">
          <img src={starhubLogo} alt="StarHub" className="h-6 w-auto" />
          <span className="text-sm font-bold tracking-tight">Customer Comms</span>
        </div>
      </div>
      <div className="flex-1 overflow-auto py-2">
        <nav className="grid items-start px-2 text-sm font-medium">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-primary",
                  isActive
                    ? "bg-muted text-primary"
                    : "text-muted-foreground"
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="mt-auto p-4">
        <div className="rounded-lg border bg-muted/50 p-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <h4 className="font-semibold">AI Generation</h4>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            Powered by StarHub Analytics
          </p>
        </div>
      </div>
    </div>
  );
}


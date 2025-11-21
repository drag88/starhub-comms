import { Bell, User, Menu, Search } from 'lucide-react';
import { Button } from '@/components/shared/Button';

export function Header({ onMenuClick }: { onMenuClick?: () => void }) {
  return (
    <header className="flex h-16 items-center gap-4 border-b border-white/5 glass-panel px-6 sticky top-0 z-50">
      <button onClick={onMenuClick} className="lg:hidden p-2 text-zinc-400 hover:text-white">
        <Menu className="h-6 w-6" />
        <span className="sr-only">Toggle navigation menu</span>
      </button>
      
      <div className="w-full flex-1 flex items-center gap-4">
         <div className="relative hidden md:block w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
            <input 
              type="text" 
              placeholder="Search campaigns, templates..." 
              className="w-full h-9 bg-black/20 border border-white/10 rounded-md pl-9 pr-4 text-sm text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
            />
         </div>
      </div>
      
      <div className="flex items-center gap-3">
        <button className="relative p-2 rounded-full hover:bg-white/5 transition-colors group">
          <Bell className="h-5 w-5 text-zinc-400 group-hover:text-primary transition-colors" />
          <span className="absolute top-2.5 right-2.5 h-2 w-2 rounded-full bg-primary shadow-[0_0_8px_#00A651]" />
          <span className="sr-only">Notifications</span>
        </button>
        
        <div className="h-8 w-[1px] bg-white/10 mx-1" />
        
        <button className="flex items-center gap-3 pl-2 pr-1 py-1 rounded-full hover:bg-white/5 transition-colors">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 border border-white/10 flex items-center justify-center">
            <User className="h-4 w-4 text-zinc-300" />
          </div>
          <div className="hidden md:block text-left mr-2">
            <p className="text-xs font-medium text-white">Admin User</p>
            <p className="text-[10px] text-zinc-500">Marketing Lead</p>
          </div>
        </button>
      </div>
    </header>
  );
}

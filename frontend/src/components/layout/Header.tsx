import { Bell, User, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header({ onMenuClick }: { onMenuClick?: () => void }) {
  return (
    <header className="flex h-14 items-center gap-4 border-b bg-muted/40 px-6 lg:h-[60px]">
      <Button variant="ghost" size="icon" className="lg:hidden" onClick={onMenuClick}>
        <Menu className="h-6 w-6" />
        <span className="sr-only">Toggle navigation menu</span>
      </Button>
      <div className="w-full flex-1">
        {/* Add breadcrumbs or page title here later */}
      </div>
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-4 w-4" />
          <span className="absolute top-2.5 right-2.5 h-2 w-2 rounded-full bg-primary" />
          <span className="sr-only">Notifications</span>
        </Button>
        <Button variant="ghost" size="icon" className="rounded-full">
          <User className="h-5 w-5" />
          <span className="sr-only">User menu</span>
        </Button>
      </div>
    </header>
  );
}


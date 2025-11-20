import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from '@/contexts/ConfigContext';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { Dashboard } from '@/pages/Dashboard';
import { CampaignWizard } from '@/pages/CampaignWizard';
import { CampaignDetails } from '@/pages/CampaignDetails';

function App() {
  return (
    <ConfigProvider>
      <Router>
        <Routes>
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/campaigns/new" element={<CampaignWizard />} />
            <Route path="/campaigns/:id" element={<CampaignDetails />} />
            <Route path="/library" element={<div className="p-8 text-center text-muted-foreground">Library feature coming soon</div>} />
            <Route path="/settings" element={<div className="p-8 text-center text-muted-foreground">Settings feature coming soon</div>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </ConfigProvider>
  );
}

export default App;

import React from 'react';
import MainLayout from './components/Layout/MainLayout';
import TradingDashboard from './components/TradingDashboard';

const App: React.FC = () => {
  return (
    <MainLayout>
      <TradingDashboard />
    </MainLayout>
  );
};

export default App; 
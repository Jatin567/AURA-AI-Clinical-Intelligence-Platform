import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { GlobalErrorBoundary } from './components/GlobalErrorBoundary';

// Screens
import Auth from './screens/Auth';
import Dashboard from './screens/Dashboard';
import Timeline from './screens/Timeline';
import Workspace from './screens/Workspace';
import Profile from './screens/Profile';
import Settings from './screens/Settings';
import Diagnostics from './screens/Diagnostics';
import PatientList from './screens/PatientList';
import Reports from './screens/Reports';

import './App.css';

function App() {
  return (
    <BrowserRouter>
      <GlobalErrorBoundary>
        <AuthProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/auth" element={<Auth />} />
            
            {/* Protected Routes inside Layout */}
            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                
                {/* Single Canvas OS */}
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/history" element={<Dashboard />} />
                <Route path="/assessments" element={<Dashboard />} />
                <Route path="/timeline" element={<Timeline />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/diagnostics" element={<Diagnostics />} />
                <Route path="/patients" element={<PatientList />} />
                <Route path="/workspace/:patientId" element={<Workspace />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/settings" element={<Settings />} />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </GlobalErrorBoundary>
    </BrowserRouter>
  );
}

export default App;

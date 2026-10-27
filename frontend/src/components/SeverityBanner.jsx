import React from 'react';
import { AlertOctagon, AlertTriangle, Clock, CheckCircle } from 'lucide-react';

const SeverityBanner = ({ level, label }) => {
  const badgeClass = level?.toLowerCase().replace('_', '') || 'routine';
  
  return (
    <div className={`status-badge ${badgeClass}`}>
      {label}
    </div>
  );
};

export default SeverityBanner;

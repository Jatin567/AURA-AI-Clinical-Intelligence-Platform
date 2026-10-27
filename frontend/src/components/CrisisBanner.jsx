import React from 'react';
import { AlertCircle } from 'lucide-react';

const CrisisBanner = ({ resources }) => {
  if (!resources || resources.length === 0) return null;

  return (
    <div className="crisis-banner" role="alert" aria-live="assertive">
      <div className="crisis-header">
        <AlertCircle size={20} className="text-error" />
        <h3>CRISIS RESOURCES AVAILABLE</h3>
      </div>
      <div className="crisis-content">
        {resources.map((resource, index) => (
          <p key={index}>{resource}</p>
        ))}
        <p className="crisis-footer">You are not alone. Help is available.</p>
      </div>
    </div>
  );
};

export default CrisisBanner;

import React from 'react';
import { Phone } from 'lucide-react';

const EmergencyButton = () => {
  return (
    <a 
      href="tel:911"
      className="emergency-btn"
      aria-label="Call Emergency Services 911"
    >
      <Phone size={18} />
      <span>Call 911</span>
    </a>
  );
};

export default EmergencyButton;

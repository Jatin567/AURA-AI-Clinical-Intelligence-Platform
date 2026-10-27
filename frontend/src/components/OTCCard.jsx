import React from 'react';

const OTCCard = ({ suggestion }) => {
  const { medicine, approved, rejection_reason } = suggestion;

  return (
    <div className={`otc-card ${!approved ? 'rejected' : ''}`}>
      <div className="otc-header">
        <h4 className="otc-name">{medicine.name}</h4>
        <span className="otc-common-names">({medicine.common_names.join(', ')})</span>
      </div>
      
      {approved ? (
        <div className="otc-info">
          <p className="otc-disclaimer">⚠️ {medicine.standard_disclaimer}</p>
        </div>
      ) : (
        <p className="otc-rejection text-error">
          Not recommended: {rejection_reason || 'Does not meet safety criteria for your profile.'}
        </p>
      )}
    </div>
  );
};

export default OTCCard;

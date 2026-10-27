import React from 'react';

// Stubbing some base cards for the registry
const GenericCard = ({ manifest }) => (
  <div className="generic-card">
    <h4>{manifest.title || "Generic Card"}</h4>
    <pre>{JSON.stringify(manifest.content, null, 2)}</pre>
  </div>
);

const RiskCard = ({ manifest }) => (
  <div className="risk-card" style={{ border: '1px solid red', padding: '10px' }}>
    <h4>{manifest.title}</h4>
    <p>{manifest.content.risk_level}</p>
  </div>
);

const MarkdownCard = ({ manifest }) => (
  <div className="markdown-card">
    <p>{manifest.content}</p>
  </div>
);

const Registry = {
  ConditionCard: GenericCard,
  RiskCard: RiskCard,
  RecommendationCard: GenericCard,
  EvidenceCard: GenericCard,
  GuidelineCard: GenericCard,
  DrugCard: GenericCard,
  CalculatorCard: GenericCard,
  EducationCard: GenericCard,
  WarningCard: GenericCard,
  TimelineCard: GenericCard,
  FollowupCard: GenericCard,
  CitationCard: GenericCard,
  MissingInformationCard: GenericCard,
  ExpandableReasoningCard: GenericCard,
  MarkdownCard: MarkdownCard
};

export const getCardComponent = (type) => {
  return Registry[type] || GenericCard;
};

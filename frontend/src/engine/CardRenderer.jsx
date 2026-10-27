import React, { Component } from 'react';
import { getCardComponent } from './CardRegistry';
import { LayoutEngine } from './LayoutEngine';
import { AnimationType, AnimationVariants } from './AnimationEngine';

export class CardErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Card rendering error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="card-error" style={{ border: '1px solid red', padding: '10px' }}>
          <h4>Error rendering card</h4>
          <p>{this.state.error.toString()}</p>
        </div>
      );
    }
    return this.props.children;
  }
}

export const CardRenderer = ({ manifest }) => {
  const layout = manifest.layout || 'inline';
  
  return (
    <CardErrorBoundary>
      <LayoutEngine layoutType={layout}>
        {React.createElement(getCardComponent(manifest.type), { manifest })}
      </LayoutEngine>
    </CardErrorBoundary>
  );
};

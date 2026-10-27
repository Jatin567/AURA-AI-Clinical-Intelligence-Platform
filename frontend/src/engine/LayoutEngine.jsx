/* eslint-disable react-refresh/only-export-components */
import React from 'react';

export const LayoutType = {
  INLINE: 'inline',
  SIDEBAR: 'sidebar',
  MODAL: 'modal',
  FLOATING: 'floating',
  EXPANDABLE: 'expandable',
  CAROUSEL: 'carousel',
  FULL_WIDTH: 'full-width',
  DRAWER: 'drawer',
  POPOVER: 'popover',
  SHEET: 'sheet',
  BOTTOM_SHEET: 'bottom-sheet'
};

export const LayoutEngine = ({ layoutType, children }) => {
  // A sophisticated layout engine would render different wrapper components here.
  // For the moment, we just render a simple wrapper with a data-layout attribute.
  return (
    <div data-layout={layoutType} className={`layout-${layoutType}`}>
      {children}
    </div>
  );
};

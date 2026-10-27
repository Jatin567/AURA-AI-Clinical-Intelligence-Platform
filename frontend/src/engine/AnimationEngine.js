export const AnimationType = {
  FADE_IN: "FADE_IN",
  FADE_UP: "FADE_UP",
  SLIDE_LEFT: "SLIDE_LEFT",
  SLIDE_RIGHT: "SLIDE_RIGHT",
  SPRING: "SPRING",
  COLLAPSE: "COLLAPSE",
  EXPAND: "EXPAND",
  SCALE: "SCALE",
  STREAM: "STREAM",
};

export const AnimationVariants = {
  [AnimationType.FADE_IN]: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.3 }
  },
  [AnimationType.FADE_UP]: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 },
    transition: { duration: 0.4, ease: "easeOut" }
  },
  [AnimationType.SLIDE_LEFT]: {
    initial: { opacity: 0, x: 50 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 50 },
    transition: { duration: 0.3 }
  },
  [AnimationType.SLIDE_RIGHT]: {
    initial: { opacity: 0, x: -50 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -50 },
    transition: { duration: 0.3 }
  },
  [AnimationType.SPRING]: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.9 },
    transition: { type: "spring", stiffness: 300, damping: 20 }
  },
  [AnimationType.COLLAPSE]: {
    initial: { height: 0, opacity: 0 },
    animate: { height: "auto", opacity: 1 },
    exit: { height: 0, opacity: 0 },
    transition: { duration: 0.3 }
  },
  [AnimationType.EXPAND]: {
    initial: { height: 0, opacity: 0 },
    animate: { height: "auto", opacity: 1 },
    exit: { height: 0, opacity: 0 },
    transition: { duration: 0.3 }
  },
  [AnimationType.SCALE]: {
    initial: { opacity: 0, scale: 0.5 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.5 },
    transition: { duration: 0.3 }
  },
  [AnimationType.STREAM]: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.1 }
  }
};

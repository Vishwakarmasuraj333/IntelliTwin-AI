import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NORMAL' | 'ANOMALY' | 'cyan' | 'purple' | 'default';
  className?: string;
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  className = '',
  dot = false,
}) => {
  const styles: Record<string, string> = {
    CRITICAL: 'bg-red-950/40 text-red-400 border border-red-500/30',
    HIGH: 'bg-orange-950/40 text-orange-400 border border-orange-500/30',
    MEDIUM: 'bg-amber-950/40 text-amber-400 border border-amber-500/30',
    LOW: 'bg-blue-950/40 text-blue-400 border border-blue-500/30',
    NORMAL: 'bg-emerald-950/40 text-emerald-400 border border-emerald-500/30',
    ANOMALY: 'bg-red-950/50 text-red-300 border border-red-500/40 font-semibold',
    cyan: 'bg-cyan-950/40 text-cyan-400 border border-cyan-500/30',
    purple: 'bg-purple-950/40 text-purple-400 border border-purple-500/30',
    default: 'bg-slate-800 text-slate-300 border border-slate-700',
  };

  const dotColors: Record<string, string> = {
    CRITICAL: 'bg-red-500 animate-pulse',
    HIGH: 'bg-orange-500',
    MEDIUM: 'bg-amber-500',
    LOW: 'bg-blue-400',
    NORMAL: 'bg-emerald-400',
    ANOMALY: 'bg-red-400 animate-pulse',
    cyan: 'bg-cyan-400',
    purple: 'bg-purple-400',
    default: 'bg-slate-400',
  };

  const chosenStyle = styles[variant] || styles.default;
  const chosenDot = dotColors[variant] || dotColors.default;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-xs font-mono tracking-wide ${chosenStyle} ${className}`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${chosenDot}`} />}
      {children}
    </span>
  );
};

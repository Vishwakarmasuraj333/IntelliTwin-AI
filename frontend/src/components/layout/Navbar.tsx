'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ShieldAlert, Activity, Radio, Cpu, FileText, Settings, Sparkles, Terminal } from 'lucide-react';

export const Navbar = () => {
  const pathname = usePathname();
  const [time, setTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const navLinks = [
    { href: '/dashboard', label: 'Command Center', icon: Activity },
    { href: '/detection', label: 'ML Simulator', icon: Terminal },
    { href: '/models', label: 'Models & XAI', icon: Cpu },
    { href: '/reports', label: 'AI Reports', icon: FileText },
    { href: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-[#070b14]/90 backdrop-blur-md border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-lg bg-cyan-950/60 border border-cyan-500/40 flex items-center justify-center relative shadow-[0_0_15px_-3px_rgba(0,240,255,0.3)]">
            <ShieldAlert className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-500" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-wider text-slate-100 font-mono">
                INTELLITWIN<span className="text-cyan-400">.AI</span>
              </span>
              <span className="hidden sm:inline-block px-1.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/30 text-[10px] font-mono text-cyan-300">
                v1.0 SOC
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono hidden sm:block">
              Cyber Anomaly Detection & GenAI Analyst
            </p>
          </div>
        </Link>

        {/* Center Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-mono transition-colors ${
                  isActive
                    ? 'bg-cyan-950/60 text-cyan-400 border border-cyan-500/40 shadow-[0_0_10px_-2px_rgba(0,240,255,0.2)]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Right Telemetry Widget */}
        <div className="flex items-center gap-3">
          {/* Active Model Pill */}
          <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded bg-[#0D1322] border border-slate-800 text-xs font-mono">
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span className="text-slate-400">MODEL:</span>
            <span className="text-emerald-400 font-semibold">XGBoost / RF (UNSW-NB15)</span>
          </div>

          {/* UTC Clock */}
          <div className="hidden sm:block text-right font-mono">
            <div className="text-[11px] text-cyan-400 font-medium">{time || 'SYNCHRONIZING UTC...'}</div>
            <div className="text-[10px] text-slate-500">DEFCON 4 // NORMAL STATUS</div>
          </div>
        </div>
      </div>
    </header>
  );
};

'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  ShieldAlert,
  Activity,
  Radio,
  Cpu,
  FileText,
  Settings,
  Terminal,
  Menu,
  X,
  Sun,
  Moon,
  Clock,
  ShieldCheck,
} from 'lucide-react';

export const Navbar = () => {
  const pathname = usePathname();
  const [time, setTime] = useState<string>('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [modelName, setModelName] = useState<string>('XGBoost');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [mounted, setMounted] = useState(false);

  // Sync theme with localStorage & document class on mount
  useEffect(() => {
    setMounted(true);
    const saved = typeof window !== 'undefined' ? localStorage.getItem('intellitwin_theme') : null;
    if (saved === 'light') {
      document.documentElement.classList.remove('dark');
      setTheme('light');
    } else {
      document.documentElement.classList.add('dark');
      setTheme('dark');
    }
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    if (nextTheme === 'dark') {
      document.documentElement.classList.add('dark');
      localStorage.setItem('intellitwin_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('intellitwin_theme', 'light');
    }
  };

  // Compact UTC Time (One-line format)
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const pad = (n: number) => n.toString().padStart(2, '0');
      setTime(`${pad(now.getUTCHours())}:${pad(now.getUTCMinutes())}:${pad(now.getUTCSeconds())} UTC`);
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Live Backend Status
  useEffect(() => {
    let isMounted = true;
    const checkBackend = async () => {
      try {
        const res = await fetch('/api/models/metrics');
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setBackendStatus('online');
            if (data.best_model) setModelName(data.best_model);
          }
        } else {
          if (isMounted) setBackendStatus('offline');
        }
      } catch {
        if (isMounted) setBackendStatus('online');
      }
    };
    checkBackend();
    const interval = setInterval(checkBackend, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Close mobile drawer on navigation
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);

  const navLinks = [
    { href: '/dashboard', label: 'Command Center', icon: Activity },
    { href: '/detection', label: 'ML Simulator', icon: Terminal },
    { href: '/models', label: 'Models & XAI', icon: Cpu },
    { href: '/reports', label: 'AI Reports', icon: FileText },
    { href: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-white/95 dark:bg-[#070B14]/90 backdrop-blur-xl border-b border-slate-200 dark:border-slate-800/80 transition-colors duration-250">
      {/* Top Cyber Accent Line */}
      <div className="h-[2px] w-full bg-gradient-to-r from-transparent via-cyan-500/80 via-emerald-500/80 to-transparent shadow-[0_0_10px_rgba(0,240,255,0.4)]" />

      {/* Main Single-Line Navbar Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 sm:h-15 flex items-center justify-between gap-3">
        {/* Left: Brand Logo & Title (One Line) */}
        <Link href="/" className="flex items-center gap-2.5 group flex-shrink-0 select-none">
          <div className="relative w-8 h-8 rounded-lg bg-cyan-950/70 border border-cyan-500/40 flex items-center justify-center shadow-[0_0_12px_rgba(0,240,255,0.3)] group-hover:scale-105 transition-transform duration-200">
            <ShieldAlert className="w-4 h-4 text-cyan-400 group-hover:text-cyan-300" />
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_#10b981]" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-base sm:text-lg tracking-wider text-slate-900 dark:text-slate-100 font-mono whitespace-nowrap">
              INTELLITWIN<span className="text-cyan-500 dark:text-cyan-400">.AI</span>
            </span>
            <span className="hidden sm:inline-block px-1.5 py-0.5 rounded bg-cyan-100 dark:bg-cyan-950/80 border border-cyan-300 dark:border-cyan-500/30 text-[10px] font-mono font-bold text-cyan-700 dark:text-cyan-300">
              v1.0 SOC
            </span>
          </div>
        </Link>

        {/* Center: Desktop Navigation Links (Single Line Pill) */}
        <nav className="hidden lg:flex items-center gap-1 bg-slate-100 dark:bg-slate-950/80 p-1 rounded-xl border border-slate-200 dark:border-slate-800/80 shadow-inner">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium whitespace-nowrap transition-all duration-200 ${
                  isActive
                    ? 'bg-white dark:bg-cyan-950/80 text-cyan-600 dark:text-cyan-300 border border-slate-200 dark:border-cyan-500/40 shadow-sm dark:shadow-[0_0_12px_-2px_rgba(0,240,255,0.25)]'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-200/60 dark:hover:bg-slate-800/40'
                }`}
              >
                <Icon
                  className={`w-3.5 h-3.5 transition-transform ${
                    isActive ? 'text-cyan-500 dark:text-cyan-400 scale-110' : 'text-slate-500 dark:text-slate-400'
                  }`}
                />
                <span>{link.label}</span>
                {isActive && (
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-[2px] bg-cyan-500 dark:bg-cyan-400 rounded-full shadow-[0_0_6px_#00f0ff]" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right: Telemetry Widgets + Dark/Light Toggle (Single Line) */}
        <div className="flex items-center gap-2 sm:gap-2.5 flex-shrink-0">
          {/* Active Model Pill */}
          <div className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800 text-[11px] font-mono whitespace-nowrap">
            <Radio className="w-3 h-3 text-emerald-500 dark:text-emerald-400 animate-pulse" />
            <span className="text-slate-500 dark:text-slate-400">ENGINE:</span>
            <span className="text-emerald-600 dark:text-emerald-400 font-bold">{modelName}</span>
          </div>

          {/* SOC Online Status Beacon */}
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-[#0D1322] border border-slate-200 dark:border-slate-800/80 font-mono text-[11px] whitespace-nowrap">
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === 'online'
                  ? 'bg-emerald-400 shadow-[0_0_8px_#10b981]'
                  : backendStatus === 'checking'
                  ? 'bg-amber-400 animate-pulse'
                  : 'bg-rose-500'
              }`}
            />
            <span className="text-slate-600 dark:text-slate-300 font-semibold uppercase tracking-wider">
              {backendStatus === 'online' ? 'SOC ONLINE' : backendStatus === 'checking' ? 'SYNCING' : 'OFFLINE'}
            </span>
          </div>

          {/* DEFCON Badge */}
          <div className="hidden md:flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950/70 border border-emerald-300 dark:border-emerald-500/40 text-[10px] font-mono font-bold text-emerald-700 dark:text-emerald-300 whitespace-nowrap">
            <ShieldCheck className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
            <span>DEFCON 4</span>
          </div>

          {/* Compact UTC Clock */}
          <div className="hidden md:flex items-center gap-1 px-2 py-1 text-[11px] font-mono text-cyan-700 dark:text-cyan-300 whitespace-nowrap">
            <Clock className="w-3 h-3 text-cyan-500 dark:text-cyan-400" />
            <span>{time || 'UTC'}</span>
          </div>

          {/* Real Dark / Light Mode Toggle Switch */}
          <button
            type="button"
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            className="flex items-center gap-1.5 p-1.5 sm:px-2.5 sm:py-1 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:border-cyan-500/50 hover:text-cyan-500 dark:hover:text-cyan-400 transition-all duration-200 focus:outline-none shadow-sm cursor-pointer"
          >
            {mounted && theme === 'dark' ? (
              <>
                <Sun className="w-4 h-4 text-amber-400 animate-pulse" />
                <span className="hidden sm:inline font-mono text-[10px] font-bold text-amber-300">LIGHT</span>
              </>
            ) : (
              <>
                <Moon className="w-4 h-4 text-cyan-600" />
                <span className="hidden sm:inline font-mono text-[10px] font-bold text-cyan-700">DARK</span>
              </>
            )}
          </button>

          {/* Mobile Hamburger Menu Button */}
          <button
            type="button"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-1.5 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-cyan-500 dark:hover:text-cyan-400 transition-colors focus:outline-none"
            aria-label="Toggle Navigation Menu"
          >
            {isMobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {isMobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-200 dark:border-slate-800/90 bg-white/98 dark:bg-[#070B14]/98 backdrop-blur-2xl px-4 py-3 space-y-2 font-mono text-sm shadow-xl">
          <div className="grid grid-cols-1 gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-3 px-3.5 py-2 rounded-lg text-xs transition-colors ${
                    isActive
                      ? 'bg-cyan-100 dark:bg-cyan-950/80 text-cyan-700 dark:text-cyan-300 border border-cyan-300 dark:border-cyan-500/40 font-bold'
                      : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-500 dark:text-cyan-400' : 'text-slate-400'}`} />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </div>

          <div className="pt-2 border-t border-slate-200 dark:border-slate-800/80 text-xs space-y-1.5 px-2 text-slate-500">
            <div className="flex items-center justify-between">
              <span>Active Engine:</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-semibold">{modelName}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Defense Status:</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-semibold">DEFCON 4 (Normal)</span>
            </div>
            <div className="flex items-center justify-between">
              <span>UTC Time:</span>
              <span className="text-cyan-600 dark:text-cyan-400">{time || 'UTC'}</span>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

import type { Metadata } from 'next';
import './globals.css';
import { Navbar } from '@/components/layout/Navbar';

export const metadata: Metadata = {
  title: 'IntelliTwin AI | Cybersecurity Anomaly Detection & GenAI Platform',
  description:
    'Production-grade Cybersecurity Intrusion Detection System powered by Machine Learning on UNSW-NB15, Explainable AI (SHAP), and Google Gemini SOC Analyst.',
  keywords: ['Cybersecurity', 'Anomaly Detection', 'UNSW-NB15', 'SHAP', 'XAI', 'Gemini AI', 'SOC Analyst', 'Machine Learning'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#070B14] text-slate-100 cyber-grid">
        <Navbar />
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="w-full border-t border-slate-900 bg-[#070B14]/80 py-4 text-center font-mono text-[11px] text-slate-500">
          IntelliTwin AI &copy; 2026 &mdash; Enterprise SOC AI Platform & M.Sc. IT Capstone Project &mdash; Powered by UNSW-NB15, SHAP & Google Gemini
        </footer>
      </body>
    </html>
  );
}

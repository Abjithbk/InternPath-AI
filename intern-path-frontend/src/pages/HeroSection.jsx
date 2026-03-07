import React from 'react'
import { useNavigate } from 'react-router-dom';
import { useContext } from 'react';
import { UserContext } from '../context/UserContext';
import Logo from '../component/Logo';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
  Legend
);

const HeroSection = () => {
    const navigate = useNavigate();
    const { user } = useContext(UserContext);

     const handleExploreNow = () => {
    if (!user) {
      navigate("/Login");
    } else {
      navigate("/dashboard");
    }
  };
    
  return (
    <div className="bg-white min-h-screen">
      {/* Navbar */}
      <nav className="flex justify-between items-center px-6 py-3 bg-slate-100">
        <div className="flex items-center gap-2 min-w-fit">
          <Logo width={34} showText={false} className="self-center" />
          <span className="text-lg font-bold text-indigo-600">InternPath</span>
        </div>
        {
          user ? (
             <div className="flex items-center gap-4">
            <span className="text-slate-700 font-medium">
              Welcome, {user.name}
            </span>
          </div>
          ) : (
            <div className="space-x-4">
              <button
                onClick={() => navigate("/Signup")}
                className="px-5 py-2 rounded-full text-blue-600 font-medium hover:bg-blue-50 transition"
              >
                Sign in
              </button>
            </div>
          )
        }
      </nav>

      {/* Hero Section */}
      <section className="px-6 py-16 max-w-7xl mx-auto">
        <h1 className="text-3xl sm:text-4xl font-semibold text-center text-slate-900 mb-16">
          Your tailored internship pathway awaits
        </h1>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          
          {/* Left Panel */}
          <div>
            <h2 className="text-lg font-medium text-slate-800 mb-4">
               readiness insights
            </h2>
            <div className="h-72 rounded-xl bg-blue-50 border border-blue-100 p-4 animate-fade-in">
              <ReadinessChart />
            </div>
          </div>

          {/* Right Panel */}
          <div>
            <h2 className="text-lg font-medium text-slate-800 mb-6">
              Your personalised dashboard
            </h2>

            <div className="flex flex-wrap gap-4 mb-6">
              <DashboardCard title="Strengths" bg="bg-green-100" text="text-green-700" />
              <DashboardCard title="Weakness" bg="bg-red-100" text="text-red-700" />
              <DashboardCard title="Skill gap" bg="bg-yellow-100" text="text-yellow-700" />
              <DashboardCard title="Internship Match" bg="bg-emerald-100" text="text-emerald-700" />
            </div>

            <p className="text-sm text-slate-600">
              Get actionable insights to improve your skills and match with the
              right internships.
            </p>
          </div>
        </div>

        {/* Features */}
        <div className="mt-20 text-center">
          <h2 className="text-lg font-medium text-slate-900 mb-10">
            Your features include
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-y-6 text-slate-700">
            <p>Skill gap assessment</p>
            <p>Readiness scoring system</p>
            <p>Curated internship listings</p>
            <p>Personalized recommendations</p>
            <p>AI driven mentorship insights</p>
            <p>24/7 support chat</p>
          </div>

          {/* CTA */}
          <button 
            onClick={handleExploreNow}
            className="mt-12 px-10 py-3 rounded-full bg-blue-600 text-white font-medium
                       hover:bg-blue-700 transition active:scale-95"
          >
            Explore Now
          </button>
        </div>
      </section>

      {/* Animations */}
      <style>
        {`
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .animate-fade-in {
            animation: fadeIn 0.6s ease-out;
          }
        `}
      </style>
    </div>
  )
}

const ReadinessChart = () => {
  const chartData = {
    labels: [
      'Technical Skills',
      'Communication',
      'Problem Solving',
      'Projects',
      'Resume Strength',
      'Interview Prep',
    ],
    datasets: [
      {
        label: 'Internship Readiness Score',
        data: [70, 60, 76, 63, 50, 55],
        borderColor: '#4f46e5',
        backgroundColor: 'rgba(79, 70, 229, 0.18)',
        fill: true,
        borderWidth: 3,
        pointRadius: 4,
        pointHoverRadius: 5,
        pointBackgroundColor: '#ffffff',
        pointBorderColor: '#4f46e5',
        pointBorderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: '#4b5563',
          boxWidth: 42,
        },
      },
      tooltip: { enabled: true },
    },
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: {
          stepSize: 10,
          backdropColor: 'transparent',
          color: '#6b7280',
        },
        pointLabels: {
          color: '#4b5563',
          font: {
            size: 12,
            weight: 500,
          },
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.30)',
        },
        angleLines: {
          color: 'rgba(156, 163, 175, 0.30)',
        },
      },
    },
  };

  return <Radar data={chartData} options={chartOptions} />;
};

const DashboardCard = ({ title, bg, text }) => {
  return (
    <div
      className={`w-32 h-32 rounded-xl ${bg} flex items-center justify-center
                  shadow-sm transition hover:scale-105`}
    >
      <span className={`font-medium text-sm ${text}`}>{title}</span>
    </div>
  );
};

export default HeroSection;
import { useCallback, useState, useEffect } from 'react';
import Particles from 'react-particles';
import { loadSlim } from 'tsparticles-slim';

const ProfileCard = () => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [glowIntensity, setGlowIntensity] = useState(0);
  const [rotation, setRotation] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setGlowIntensity(prev => (prev + 0.05) % (Math.PI * 2));
      setRotation(prev => (prev + 0.5) % 360);
    }, 30);
    return () => clearInterval(interval);
  }, []);

  const glowOpacity = 0.5 + Math.sin(glowIntensity) * 0.3;
  const glowScale = 1 + Math.sin(glowIntensity) * 0.1;

  return (
    <div 
      className="relative w-80 h-[480px] cursor-pointer group transition-transform duration-300"
      onClick={() => setIsFlipped(!isFlipped)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ 
        perspective: '1000px',
        transform: isHovered ? 'scale(1.05)' : 'scale(1)'
      }}
    >
      {/* Multi-layered animated glow effect */}
      <div 
        className="absolute -inset-6 rounded-3xl blur-3xl transition-all duration-500"
        style={{ 
          opacity: glowOpacity,
          transform: `scale(${glowScale}) rotate(${rotation}deg)`,
          background: `conic-gradient(from ${rotation}deg, #ec4899, #a855f7, #3b82f6, #ec4899)`
        }}
      />
      <div 
        className="absolute -inset-4 rounded-3xl bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 blur-2xl"
        style={{ 
          opacity: glowOpacity * 0.7,
          transform: `scale(${glowScale * 0.9}) rotate(${-rotation}deg)`
        }}
      />
      
      <div 
        className="relative w-full h-full transition-transform duration-700 preserve-3d"
        style={{
          transformStyle: 'preserve-3d',
          transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)'
        }}
      >
        {/* Front of card */}
        <div 
          className="absolute w-full h-full backface-hidden rounded-3xl overflow-hidden shadow-2xl border-2 border-white/20"
          style={{ backfaceVisibility: 'hidden' }}
        >
          {/* Card content */}
          <div className="relative h-full bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            {/* Profile Image */}
            <div className="h-[320px] relative overflow-hidden">
              {/* Gradient background */}
              <div className="absolute inset-0 bg-gradient-to-br from-pink-600/30 via-purple-600/30 to-blue-600/30" />
              
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative">
                  {/* Outer animated glow rings */}
                  <div className="absolute inset-0 -m-6 rounded-full bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 blur-2xl opacity-50 animate-spin-slow animate-pulse-scale" />
                  <div className="absolute inset-0 -m-4 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 blur-xl opacity-60 animate-spin-reverse animate-pulse-scale-delayed" />
                  <div className="absolute inset-0 -m-2 rounded-full bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 blur-lg opacity-40 animate-spin-slow" />
                  
                  {/* Animated rotating border ring */}
                  <div className="absolute inset-0 -m-1 rounded-full animate-rotate-border" style={{
                    width: 'calc(100% + 8px)',
                    height: 'calc(100% + 8px)',
                    background: 'conic-gradient(from 0deg, #ec4899, #a855f7, #3b82f6, #ec4899)',
                    borderRadius: '50%',
                    padding: '4px',
                    mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                    WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                    maskComposite: 'exclude',
                    WebkitMaskComposite: 'xor'
                  }}>
                    <div className="w-full h-full rounded-full bg-transparent"></div>
                  </div>
                  
                  {/* Floating particles around avatar */}
                  {[...Array(8)].map((_, i) => {
                    const angle = (i / 8) * Math.PI * 2;
                    const radius = 140;
                    const x = Math.cos(angle) * radius;
                    const y = Math.sin(angle) * radius;
                    return (
                      <div
                        key={i}
                        className="absolute w-3 h-3 rounded-full bg-gradient-to-r from-pink-400 to-purple-400 animate-particle-cycle"
                        style={{
                          top: '50%',
                          left: '50%',
                          transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`,
                          animationDelay: `${i * 0.5}s`,
                          boxShadow: '0 0 10px rgba(236, 72, 153, 0.8), 0 0 20px rgba(168, 85, 247, 0.6)'
                        }}
                      />
                    );
                  })}
                  
                  {/* Avatar */}
                  <div className="relative w-52 h-52 rounded-full overflow-hidden shadow-2xl border-4 border-white/30">
                    <img 
                      src="/georgeliu.jpeg" 
                      alt="George Liu" 
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        // Fallback to initials if image fails to load
                        e.target.style.display = 'none';
                        e.target.parentElement.classList.add('bg-gradient-to-br', 'from-pink-500', 'via-purple-500', 'to-blue-500', 'flex', 'items-center', 'justify-center');
                        e.target.parentElement.innerHTML = '<span class="text-white text-7xl font-bold">GL</span>';
                      }}
                    />
                  </div>
                  
                  {/* Inner glow pulse */}
                  <div className="absolute inset-0 -m-3 rounded-full bg-gradient-to-r from-pink-400/50 via-purple-400/50 to-blue-400/50 blur-md animate-pulse-glow-inner" />
                </div>
              </div>
              
              {/* Subtle ambient glow effect */}
              <div 
                className="absolute inset-0 animate-gentle-pulse pointer-events-none"
                style={{
                  background: 'radial-gradient(circle at center, rgba(236, 72, 153, 0.05) 0%, transparent 70%)'
                }}
              />
            </div>
            
            {/* Profile Info */}
            <div className="p-8 space-y-3 text-center flex items-center justify-center flex-col" style={{ minHeight: 'calc(100% - 320px)' }}>
              <h3 className="text-4xl font-bold text-white tracking-tight">
                George Liu
              </h3>
              
              <div className="space-y-2 pt-2">
                <div className="text-white/90 text-lg font-medium">
                  CS @uwaterloo
                </div>
                <div className="text-white/90 text-lg font-medium">
                  SWE @Tesla
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Back of card */}
        <div 
          className="absolute w-full h-full backface-hidden rounded-3xl overflow-hidden shadow-2xl border-4 border-pink-400/30 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"
          style={{ 
            backfaceVisibility: 'hidden',
            transform: 'rotateY(180deg)'
          }}
        >
          <div className="h-full flex flex-col items-center justify-center p-8 text-center space-y-4">
            <div className="w-20 h-20 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full flex items-center justify-center text-4xl shadow-2xl">
              💝
            </div>
            <h4 className="text-2xl font-bold text-white">Want to connect?</h4>
            <p className="text-white/70 text-sm">
              Open your daily pack to see if George is one of your 5 matches today!
            </p>
            <button className="mt-4 px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full font-semibold hover:scale-105 transition-transform shadow-lg">
              Open Today's Pack
            </button>
          </div>
        </div>
      </div>
      
      {/* Hover instruction */}
      <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 text-white/50 text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
        Click to flip card
      </div>
    </div>
  );
};

export default function DatingLandingPage() {
  const particlesInit = useCallback(async (engine) => {
    await loadSlim(engine);
  }, []);

  const particlesConfig = {
    particles: {
      number: {
        value: 200,
        density: {
          enable: true,
          value_area: 800
        }
      },
      color: {
        value: "#ffffff"
      },
      shape: {
        type: "circle"
      },
      opacity: {
        value: 0.8,
        random: true,
        animation: {
          enable: true,
          speed: 1,
          minimumValue: 0.1,
          sync: false
        }
      },
      size: {
        value: 2,
        random: true,
        animation: {
          enable: true,
          speed: 2,
          minimumValue: 0.1,
          sync: false
        }
      },
      links: {
        enable: false
      },
      move: {
        enable: true,
        speed: 0.5,
        direction: "none",
        random: false,
        straight: false,
        outModes: {
          default: "out"
        },
        bounce: false,
        attract: {
          enable: false,
          rotateX: 600,
          rotateY: 1200
        }
      }
    },
    interactivity: {
      detectsOn: "canvas",
      events: {
        onHover: {
          enable: false
        },
        onClick: {
          enable: false
        },
        resize: true
      }
    },
    detectRetina: true
  };

  return (
    <div className="h-screen w-screen bg-black text-white overflow-hidden fixed inset-0">
      {/* Starfield Background */}
      <div className="absolute inset-0 z-0">
        <Particles
          id="tsparticles"
          init={particlesInit}
          options={particlesConfig}
        />
      </div>

      {/* Hero Content */}
      <div className="relative z-20 h-full flex items-center justify-center px-6">
        <div className="max-w-7xl w-full grid lg:grid-cols-2 gap-12 items-center">
          {/* Left side - Text content */}
          <div className="text-left lg:pl-8">
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6 text-white drop-shadow-2xl">
              Swipe Less,<br />Connect More
            </h1>
            <p className="text-lg md:text-xl lg:text-2xl mb-10 text-white/80 drop-shadow-lg max-w-xl">
              Quality over quantity. Get 5 meaningful matches daily based on your interests, major, and goals.
            </p>
            <div className="relative inline-block">
              {/* Neon glow layers */}
              <div className="absolute inset-0 rounded-full bg-pink-500 blur-xl opacity-75 animate-pulse-glow"></div>
              <div className="absolute inset-0 rounded-full bg-pink-400 blur-2xl opacity-50 animate-pulse-glow-delayed"></div>
              <div className="absolute -inset-1 rounded-full bg-pink-300 blur-sm opacity-60 animate-pulse-glow-slow"></div>
              {/* Button */}
              <button className="relative bg-gradient-to-r from-pink-500 via-pink-400 to-pink-500 text-white px-12 py-5 rounded-full text-xl font-semibold transition-all duration-300 shadow-[0_0_20px_rgba(236,72,153,0.6),0_0_40px_rgba(236,72,153,0.4)] hover:shadow-[0_0_30px_rgba(236,72,153,0.8),0_0_60px_rgba(236,72,153,0.6)] hover:scale-105 active:scale-95">
                Sign in with LinkedIn
              </button>
            </div>
            
            {/* Quick stats */}
            <div className="mt-12 flex gap-8 text-sm">
              <div>
                <div className="text-3xl font-bold text-pink-400">10K+</div>
                <div className="text-white/60">Active Users</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-pink-400">50K+</div>
                <div className="text-white/60">Matches Made</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-pink-400">4.9★</div>
                <div className="text-white/60">User Rating</div>
              </div>
            </div>
          </div>
          
          {/* Right side - Card demo */}
          <div className="flex items-center justify-center lg:justify-end lg:pr-8">
            <ProfileCard />
          </div>
        </div>
      </div>

    </div>
  );
}
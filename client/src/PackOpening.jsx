import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import Particles from 'react-particles';
import { loadSlim } from 'tsparticles-slim';
import { FaLinkedin } from 'react-icons/fa';

const rawApiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE_URL = rawApiBase.replace(/\/$/, '');
const BEAUTY_SCORE_ENDPOINT = `${API_BASE_URL}/beauty-score`;

// Enhanced sample cards data with more content
const SAMPLE_CARDS = [
  {
    id: 2,
    name: 'Sarah Chen',
    major: 'Engineering @MIT',
    company: 'Product Manager @Google',
    image: '/good.jpeg',
    rarity: 'common',
    bio: 'Building products that matter. Avid reader and yoga enthusiast.',
    location: 'Mountain View, CA',
    interests: ['Product Design', 'Reading', 'Yoga', 'Travel'],
    age: 26,
    experience: '4 years',
    email: 'sarah.chen@google.com',
    linkedin: 'https://linkedin.com/in/sarah-chen'
  },
  {
    id: 3,
    name: 'Alex Rodriguez',
    major: 'Business @Stanford',
    company: 'Founder @TechStartup',
    image: '/jhts.jpg',
    rarity: 'common',
    bio: 'Serial entrepreneur. Love building things from scratch.',
    location: 'Palo Alto, CA',
    interests: ['Entrepreneurship', 'Startups', 'Basketball', 'Networking'],
    age: 28,
    experience: '6 years',
    email: 'alex.rodriguez@techstartup.com',
    linkedin: 'https://linkedin.com/in/alex-rodriguez'
  },
  {
    id: 4,
    name: 'Emma Wilson',
    major: 'Design @RISD',
    company: 'UX Designer @Apple',
    image: '/meganfox.jpg',
    rarity: 'rare',
    bio: 'Designing beautiful experiences. Art lover and foodie.',
    location: 'Cupertino, CA',
    interests: ['Design', 'Art', 'Food', 'Photography'],
    age: 25,
    experience: '3 years',
    email: 'emma.wilson@apple.com',
    linkedin: 'https://linkedin.com/in/emma-wilson'
  },
  {
    id: 5,
    name: 'Michael Park',
    major: 'Data Science @CMU',
    company: 'ML Engineer @OpenAI',
    image: '/Kristin_Kreuk_Photo_Op_GalaxyCon_Columbus_2022_(cropped).jpg',
    rarity: 'legendary', // Keep one legendary
    bio: 'Pushing the boundaries of AI. Chess player and music producer.',
    location: 'San Francisco, CA',
    interests: ['AI/ML', 'Chess', 'Music', 'Research'],
    age: 27,
    experience: '5 years',
    email: 'michael.park@openai.com',
    linkedin: 'https://linkedin.com/in/michael-park'
  },
  {
    id: 6,
    name: 'Jessica Brown',
    major: 'Finance @Wharton',
    company: 'Investment Banker @Goldman Sachs',
    image: '/neon.jpg',
    rarity: 'common',
    bio: 'Finance professional by day, fitness enthusiast by night.',
    location: 'New York, NY',
    interests: ['Finance', 'Fitness', 'Cooking', 'Wine'],
    age: 29,
    experience: '7 years',
    email: 'jessica.brown@gs.com',
    linkedin: 'https://linkedin.com/in/jessica-brown'
  },
  {
    id: 7,
    name: 'David Kim',
    major: 'CS @Berkeley',
    company: 'Software Engineer @Meta',
    image: '/thailand.jpeg',
    rarity: 'rare',
    bio: 'Full-stack developer. Love open source and gaming.',
    location: 'Menlo Park, CA',
    interests: ['Coding', 'Gaming', 'Open Source', 'Biking'],
    age: 24,
    experience: '2 years',
    email: 'david.kim@meta.com',
    linkedin: 'https://linkedin.com/in/david-kim'
  },
  {
    id: 8,
    name: 'Olivia Martinez',
    major: 'Marketing @NYU',
    company: 'Brand Manager @Nike',
    image: '/tw.jpeg',
    rarity: 'common',
    bio: 'Building brands that inspire. Runner and adventure seeker.',
    location: 'Portland, OR',
    interests: ['Marketing', 'Running', 'Travel', 'Fashion'],
    age: 26,
    experience: '4 years',
    email: 'olivia.martinez@nike.com',
    linkedin: 'https://linkedin.com/in/olivia-martinez'
  },
  {
    id: 9,
    name: 'James Taylor',
    major: 'Physics @Caltech',
    company: 'Research Scientist @NASA',
    image: '/chopped1.jpg',
    rarity: 'epic', // Keep one epic
    bio: 'Exploring the cosmos. Amateur astronomer and sci-fi fan.',
    location: 'Pasadena, CA',
    interests: ['Space', 'Physics', 'Astronomy', 'Sci-Fi'],
    age: 30,
    experience: '8 years',
    email: 'james.taylor@nasa.gov',
    linkedin: 'https://linkedin.com/in/james-taylor'
  }
];

// Swipeable Card Component - matches ProfileCard format exactly
const SwipeableCard = ({ card, onSwipe, isRevealed, isActive, onFlip, attractivenessScore }) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [rotation, setRotation] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [glowIntensity, setGlowIntensity] = useState(0);
  const [rotationGlow, setRotationGlow] = useState(0);
  const startPosRef = useRef({ x: 0, y: 0 });
  const currentPosRef = useRef({ x: 0, y: 0 });
  const cardRef = useRef(null);
  const animationFrameRef = useRef(null);
  const hasMovedRef = useRef(false);
  const prevRevealedRef = useRef(isRevealed);
  const prevActiveRef = useRef(isActive);

  // Reset flip state when card becomes revealed or when it becomes active
  useEffect(() => {
    // Reset when card becomes revealed - show front
    if (isRevealed && !prevRevealedRef.current) {
      console.log(`🔄 Card ${card?.name} became revealed - resetting flip state`);
      setIsFlipped(false); // false = show front for revealed cards
    }
    // Reset when card becomes active (new card) - ensure proper state
    if (isActive && !prevActiveRef.current) {
      console.log(`🔄 Card ${card?.name} became active - resetting state. Revealed: ${isRevealed}`);
      // When card becomes active, reset flip state
      // If not revealed, it will show back (effectiveFlip will be true)
      // If revealed, it will show front (effectiveFlip will be false)
      setIsFlipped(false);
      // Reset dragging state when card becomes active
      setIsDragging(false);
      setPosition({ x: 0, y: 0 });
      setRotation(0);
      hasMovedRef.current = false;
      currentPosRef.current = { x: 0, y: 0 };
    }
    // Reset when card becomes inactive
    if (!isActive && prevActiveRef.current) {
      console.log(`🔄 Card ${card?.name} became inactive - resetting flip state`);
      setIsFlipped(false);
    }
    prevRevealedRef.current = isRevealed;
    prevActiveRef.current = isActive;
  }, [isRevealed, isActive, card?.name]);

  useEffect(() => {
    const interval = setInterval(() => {
      setGlowIntensity(prev => (prev + 0.05) % (Math.PI * 2));
      setRotationGlow(prev => (prev + 0.5) % 360);
    }, 30);
    return () => clearInterval(interval);
  }, []);

  const glowOpacity = 0.5 + Math.sin(glowIntensity) * 0.3;
  const glowScale = 1 + Math.sin(glowIntensity) * 0.1;

  const updatePosition = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    
    animationFrameRef.current = requestAnimationFrame(() => {
      setPosition({ ...currentPosRef.current });
      setRotation(currentPosRef.current.x * 0.1);
    });
  }, []);

  const handleStart = useCallback((clientX, clientY) => {
    if (!isActive) return;
    // Allow dragging only if card is revealed, otherwise it's just a click to reveal
    if (!isRevealed) {
      // Don't start dragging for unrevealed cards - let onClick handle it
      return;
    }
    setIsDragging(true);
    hasMovedRef.current = false;
    startPosRef.current = { x: clientX, y: clientY };
    currentPosRef.current = { x: 0, y: 0 };
    setPosition({ x: 0, y: 0 });
    setRotation(0);
  }, [isRevealed, isActive]);

  const handleMove = useCallback((clientX, clientY) => {
    // Don't allow movement if card is not revealed
    if (!isRevealed) {
      return;
    }
    
    const deltaX = clientX - startPosRef.current.x;
    const deltaY = clientY - startPosRef.current.y;
    
    // Check if user has moved significantly (more than 5px)
    if (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5) {
      hasMovedRef.current = true;
    }
    
    currentPosRef.current = { x: deltaX, y: deltaY };
    updatePosition();
  }, [updatePosition, isRevealed]);

  const handleEnd = useCallback(() => {
    // Don't allow swiping if card is not revealed
    if (!isRevealed) {
      setIsDragging(false);
      currentPosRef.current = { x: 0, y: 0 };
      hasMovedRef.current = false;
      setPosition({ x: 0, y: 0 });
      setRotation(0);
      return;
    }
    
    const threshold = 30; // Very low threshold for easier swiping
    const currentX = currentPosRef.current.x;
    
    // If user didn't move much, it's a click - let onClick handler deal with it
    // Don't toggle flip here to avoid double-toggling
    if (!hasMovedRef.current && Math.abs(currentX) < 5) {
      setIsDragging(false);
      currentPosRef.current = { x: 0, y: 0 };
      hasMovedRef.current = false;
      setPosition({ x: 0, y: 0 });
      setRotation(0);
      // onClick handler will handle the flip toggle
      return;
    }
    
    if (Math.abs(currentX) > threshold) {
      // Swipe detected - animate off screen
      const direction = currentX > 0 ? 1 : -1;
      const exitX = direction * window.innerWidth * 1.5;
      
      setPosition({ x: exitX, y: currentPosRef.current.y });
      setRotation(direction * 25);
      
      // Immediately make this card non-interactive
      setIsDragging(false);
      
      // Trigger swipe callback
      setTimeout(() => {
        if (currentX > 0) {
          onSwipe('right'); // Like
        } else {
          onSwipe('left'); // Pass
        }
      }, 200);
    } else {
      // Return to center with smooth animation
      setPosition({ x: 0, y: 0 });
      setRotation(0);
    }
    
    setIsDragging(false);
    currentPosRef.current = { x: 0, y: 0 };
    hasMovedRef.current = false;
  }, [onSwipe, isFlipped, isRevealed, onFlip]);

  // Mouse events
  const handleMouseDown = useCallback((e) => {
    // For unrevealed cards, don't do anything - let click handler work
    // Don't prevent default or stop propagation for unrevealed cards
    if (!isRevealed || !isActive) {
      // Let the click event bubble up normally
      return;
    }
    // Only for revealed, active cards - start dragging
    e.preventDefault();
    e.stopPropagation();
    handleStart(e.clientX, e.clientY);
  }, [handleStart, isRevealed, isActive]);
  
  const handleMouseMove = useCallback((e) => {
    e.preventDefault();
    handleMove(e.clientX, e.clientY);
  }, [handleMove]);
  
  const handleMouseUp = useCallback((e) => {
    e.preventDefault();
    handleEnd();
  }, [handleEnd]);

  // Touch events
  const handleTouchStart = useCallback((e) => {
    // For unrevealed cards, don't do anything - let click handler work
    // Don't prevent default or stop propagation for unrevealed cards
    if (!isRevealed || !isActive) {
      // Let the click event bubble up normally
      return;
    }
    // Only for revealed, active cards - start dragging
    e.preventDefault();
    e.stopPropagation();
    const touch = e.touches[0];
    handleStart(touch.clientX, touch.clientY);
  }, [handleStart, isRevealed, isActive]);
  
  const handleTouchMove = useCallback((e) => {
    e.preventDefault();
    const touch = e.touches[0];
    handleMove(touch.clientX, touch.clientY);
  }, [handleMove]);
  
  const handleTouchEnd = useCallback((e) => {
    e.preventDefault();
    handleEnd();
  }, [handleEnd]);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.addEventListener('touchmove', handleTouchMove, { passive: false });
      document.addEventListener('touchend', handleTouchEnd);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.removeEventListener('touchmove', handleTouchMove);
        document.removeEventListener('touchend', handleTouchEnd);
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp, handleTouchMove, handleTouchEnd]);

  const scale = isActive ? 1 : 0.98; // Slight scale for inactive cards

  // Unrevealed cards should show back (flipped), revealed cards show front
  // Show back if: card is not revealed OR (revealed AND user flipped it to show back)
  const effectiveFlip = !isRevealed || (isRevealed && isFlipped);

  const scoreLabel = (() => {
    if (attractivenessScore === undefined) {
      return 'Scoring...';
    }
    if (attractivenessScore === null) {
      return 'N/A';
    }
    if (typeof attractivenessScore === 'number' && !Number.isNaN(attractivenessScore)) {
      return attractivenessScore.toFixed(2);
    }
    if (typeof attractivenessScore === 'string' && attractivenessScore.trim().length > 0) {
      const parsed = Number(attractivenessScore);
      if (!Number.isNaN(parsed)) {
        return parsed.toFixed(2);
      }
      return attractivenessScore;
    }
    return null;
  })();

  return (
    <div
      ref={cardRef}
      className={`absolute w-80 h-[480px] group transition-transform duration-300 ${
        !isDragging ? 'transition-transform duration-300 ease-out' : ''
      } ${isActive ? 'cursor-pointer' : 'cursor-default'}`}
      style={{ 
        perspective: '1000px',
        transform: `translate(${position.x}px, ${position.y}px) rotate(${rotation}deg) scale(${isHovered && !isDragging ? 1.05 : scale})`,
        opacity: 1,
        willChange: isDragging ? 'transform' : 'auto'
      }}
      onMouseDown={handleMouseDown}
      onTouchStart={handleTouchStart}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={(e) => {
        console.log(`🔵 CLICK: Card ${card?.name} | Active: ${isActive} | Revealed: ${isRevealed} | HasMoved: ${hasMovedRef.current}`);
        
        // Always stop propagation to prevent event bubbling
        e.stopPropagation();
        
        // Only handle clicks on active cards
        if (!isActive) {
          console.log('  ❌ Click ignored - card not active');
          return;
        }
        
        // Don't handle click if user moved (it was a drag attempt, not a click)
        if (hasMovedRef.current) {
          console.log('  ⏸️  Click ignored - user moved (drag attempt)');
          return;
        }
        
        // For unrevealed cards, we want to reveal them on click
        // For revealed cards, we want to toggle flip
        if (!isRevealed) {
          // First click: reveal the card
          console.log('  ✅ Revealing card via onFlip()');
          e.preventDefault();
          if (onFlip) {
            onFlip();
          }
        } else {
          // Subsequent clicks: toggle between front and back
          console.log('  🔄 Toggling card flip (front/back)');
          e.preventDefault();
          setIsFlipped(!isFlipped);
        }
      }}
    >
      {scoreLabel && (
        <div className="absolute top-4 right-4 z-50">
          <span className="px-3 py-1 rounded-full bg-black/80 text-white text-sm font-semibold border border-white/20">
            {scoreLabel}
          </span>
        </div>
      )}
      {/* Swipe indicators - only show for revealed cards */}
      {isDragging && isRevealed && (
        <>
          {position.x > 20 && (
            <div 
              className="absolute inset-0 flex items-center justify-center bg-green-500/40 rounded-3xl border-4 border-green-400 transition-opacity duration-100 z-50"
              style={{ opacity: Math.min(Math.abs(position.x) / 80, 1) }}
            >
              <div className="text-6xl font-bold text-green-400 drop-shadow-lg">✓ LIKE</div>
            </div>
          )}
          {position.x < -20 && (
            <div 
              className="absolute inset-0 flex items-center justify-center bg-red-500/40 rounded-3xl border-4 border-red-400 transition-opacity duration-100 z-50"
              style={{ opacity: Math.min(Math.abs(position.x) / 80, 1) }}
            >
              <div className="text-6xl font-bold text-red-400 drop-shadow-lg">✗ PASS</div>
            </div>
          )}
        </>
      )}

      {/* Multi-layered animated glow effect */}
      <div 
        className="absolute -inset-6 rounded-3xl blur-3xl transition-all duration-500"
        style={{ 
          opacity: glowOpacity,
          transform: `scale(${glowScale}) rotate(${rotationGlow}deg)`,
          background: `conic-gradient(from ${rotationGlow}deg, #ec4899, #a855f7, #3b82f6, #ec4899)`
        }}
      />
      <div 
        className="absolute -inset-4 rounded-3xl bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 blur-2xl"
        style={{ 
          opacity: glowOpacity * 0.7,
          transform: `scale(${glowScale * 0.9}) rotate(${-rotationGlow}deg)`
        }}
      />
      
      <div 
        className="relative w-full h-full transition-transform duration-700 preserve-3d z-20"
        style={{
          transformStyle: 'preserve-3d',
          transform: effectiveFlip ? 'rotateY(180deg)' : 'rotateY(0deg)'
        }}
      >
        {/* Prestigious solid metallic gold border - only border frame */}
        <div 
          className="absolute inset-0 rounded-3xl z-10 backface-hidden pointer-events-none"
          style={{
            padding: '3px',
            background: 'linear-gradient(135deg, #8b6914 0%, #A57B00 25%, #b8860b 50%, #A57B00 75%, #8b6914 100%)',
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            maskComposite: 'exclude',
            backfaceVisibility: 'visible'
          }}
        >
          <div className="w-full h-full rounded-3xl bg-transparent"></div>
        </div>
        <div 
          className="absolute inset-0 rounded-3xl z-10 animate-metallic-shine backface-hidden pointer-events-none"
          style={{
            padding: '2px',
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            maskComposite: 'exclude',
            backfaceVisibility: 'visible'
          }}
        >
          <div 
            className="w-full h-full rounded-3xl"
            style={{
              background: 'linear-gradient(135deg, #A57B00 0%, #c99a1a 20%, #d4af37 40%, #c99a1a 60%, #A57B00 100%)'
            }}
          ></div>
        </div>
        
        {/* Front of card */}
        <div
          className="absolute w-full h-full backface-hidden rounded-3xl overflow-hidden shadow-2xl border-2 border-white/20"
          style={{ backfaceVisibility: 'hidden' }}
        >
          {/* Card content */}
          <div className="relative h-full flex flex-col bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            {/* Profile Image */}
            <div className="h-[280px] relative overflow-hidden flex-shrink-0">
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
                  
                  {/* Avatar */}
                  <div className="relative w-52 h-52 rounded-full overflow-hidden shadow-2xl border-4 border-white/30">
                    {card.image ? (
                      <img 
                        src={card.image}
                        alt={card.name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          // Fallback to initials if image fails to load
                          e.target.style.display = 'none';
                          e.target.parentElement.classList.add('bg-gradient-to-br', 'from-pink-500', 'via-purple-500','to-blue-500', 'flex', 'items-center', 'justify-center');
                          const initials = card.name.split(' ').map((n) => n[0]).join('');
                          e.target.parentElement.innerHTML = `<span class="text-white text-7xl font-bold">${initials}</span>`;
                        }}
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-pink-500 via-purple-500 to-blue-500 flex items-center justify-center">
                        <span className="text-white text-7xl font-bold">
                          {card.name.split(' ').map((n) => n[0]).join('')}
                        </span>
                      </div>
                    )}
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
            
            {/* Border divider */}
            <div className="h-px bg-gradient-to-r from-transparent via-white/20 to-transparent flex-shrink-0"></div>
            
            {/* Profile Info */}
            <div className="flex-1 flex flex-col items-center justify-center p-8 space-y-3 text-center min-h-0">
              <h3 className="text-4xl font-bold text-white tracking-tight">
                {card.name}
              </h3>
              
              <div className="space-y-2">
                <div className="text-white/90 text-lg font-medium">
                  {card.major}
                </div>
                <div className="text-white/90 text-lg font-medium">
                  {card.company}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Back of card */}
        <div 
          className="absolute w-full h-full backface-hidden rounded-3xl overflow-hidden shadow-2xl border-4 border-pink-400/30 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative"
          style={{
            backfaceVisibility: 'hidden',
            transform: 'rotateY(180deg)'
          }}
        >
          {/* Shine animation overlay */}
          <div className="absolute inset-0 animate-shine pointer-events-none rounded-3xl"></div>
          
          <div className="h-full flex items-center justify-center p-8 relative z-10">
            {/* LinkedIn Logo */}
            <a 
              href={card.linkedin || "https://www.linkedin.com/"} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-white/60 hover:text-white transition-all duration-300 hover:scale-125"
              onClick={(e) => e.stopPropagation()}
            >
              <FaLinkedin size={48} />
            </a>
          </div>
        </div>
      </div>
      
      {/* Hover instruction */}
      <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 text-white/50 text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
        {isRevealed ? 'Click to flip card' : 'Click to reveal card'}
      </div>
    </div>
  );
};

// Pack Opening Component
const PackOpening = ({
  onCardLiked = null,
  cards: cardsProp = null,
  fetchError = null
}) => {
  const [packOpened, setPackOpened] = useState(false);
  const [currentPack, setCurrentPack] = useState([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [revealedCards, setRevealedCards] = useState([]);
  const [isRevealing, setIsRevealing] = useState(false);
  const [attractivenessScores, setAttractivenessScores] = useState({});
  const [isScoring, setIsScoring] = useState(false);
  const [packCompleted, setPackCompleted] = useState(() => {
    try {
      return localStorage.getItem('daily-pack-claimed') === new Date().toISOString().slice(0, 10);
    } catch {
      return false;
    }
  });
  const fetchRequestIdRef = useRef(0);

  const cardsPool = useMemo(() => {
    if (Array.isArray(cardsProp) && cardsProp.length > 0) {
      const sanitized = cardsProp.map((card, index) => {
        const rawName = typeof card?.name === 'string' ? card.name.trim() : '';
        const fallbackName = rawName || `LinkedIn Candidate ${index + 1}`;
        const hasImage = typeof card?.image === 'string' && card.image.trim();
        const imageUrl =
          hasImage
            ? card.image.trim()
            : `https://ui-avatars.com/api/?name=${encodeURIComponent(fallbackName)}&background=111111&color=ff66cc`;
        const rarity =
          card?.rarity ||
          (index === 0 ? 'legendary' : index === 1 ? 'epic' : index <= 3 ? 'rare' : 'common');
        const headline = typeof card?.headline === 'string' ? card.headline : card?.bio;
        const derivedInterests =
          Array.isArray(card?.interests) && card.interests.length
            ? card.interests
            : headline
                ?.split(/[,;•|]/)
                .map((segment) => segment.trim())
                .filter(Boolean)
                .slice(0, 4) ?? [];

        return {
          ...card,
          id: card?.id ?? `search-card-${index}`,
          name: fallbackName,
          image: imageUrl,
          rarity,
          major: card?.major || headline || 'LinkedIn Search Result',
          company: card?.company || headline || 'Open to opportunities',
          bio: card?.bio || headline || '',
          location: card?.location || '',
          interests: derivedInterests,
          linkedin: card?.linkedin || 'https://www.linkedin.com'
        };
      });

      if (sanitized.length < 5) {
        const needed = 5 - sanitized.length;
        const filler = SAMPLE_CARDS.slice(0, needed).map((card, idx) => ({
          ...card,
          id: `filler-${card.id}-${idx}`
        }));
        return [...sanitized, ...filler];
      }

      return sanitized;
    }

    return SAMPLE_CARDS;
  }, [cardsProp]);

  useEffect(() => {
    if (Array.isArray(cardsProp)) {
      setPackOpened(false);
      setCurrentPack([]);
      setCurrentCardIndex(0);
      setRevealedCards([]);
      setAttractivenessScores({});
      setIsScoring(false);
      setPackCompleted(false);
      try {
        localStorage.removeItem('daily-pack-claimed');
      } catch {
        // ignore storage errors
      }
    }
  }, [cardsProp]);

  const resetDailyLock = useCallback(() => {
    try {
      localStorage.removeItem('daily-pack-claimed');
    } catch {
      // ignore storage errors
    }
    setPackCompleted(false);
  }, []);

  const fetchAttractivenessScores = useCallback(async (packCards, requestId) => {
    setIsScoring(true);
    await Promise.all(
      packCards.map(async (card) => {
        try {
          const imageResponse = await fetch(card.image);
          if (!imageResponse.ok) {
            throw new Error(`Image fetch failed with status ${imageResponse.status}`);
          }

          const blob = await imageResponse.blob();
          const formData = new FormData();
          formData.append('image', blob, card.image.split('/').pop() ?? `${card.id}.jpg`);

          if (card.name) {
            formData.append('name', card.name);
          }

          if (card.gender) {
            formData.append('gender', card.gender);
          }

          const response = await fetch(BEAUTY_SCORE_ENDPOINT, {
            method: 'POST',
            body: formData
          });

          if (!response.ok) {
            throw new Error(`Beauty score request failed with status ${response.status}`);
          }

          const payload = await response.json();
          let scoreValue = payload?.score ?? null;

          if (scoreValue === null) {
            const raw = payload?.raw;
            if (Array.isArray(raw)) {
              scoreValue = raw[0];
            } else if (raw?.data && Array.isArray(raw.data)) {
              scoreValue = raw.data[0];
            } else if (raw !== undefined) {
              scoreValue = raw;
            }
          }

          if (typeof scoreValue === 'string') {
            const parsed = Number(scoreValue);
            if (!Number.isNaN(parsed)) {
              scoreValue = parsed;
            }
          }

          console.debug('Beauty score fetched', {
            card: card.name,
            score: scoreValue,
            raw: payload
          });

          if (requestId !== fetchRequestIdRef.current) {
            return;
          }

          setAttractivenessScores((prev) => ({
            ...prev,
            [card.id]: scoreValue
          }));
        } catch (error) {
          console.error('Failed to fetch beauty score for card', card?.name, error);
          if (requestId !== fetchRequestIdRef.current) {
            return;
          }
          setAttractivenessScores((prev) => ({
            ...prev,
            [card.id]: null
          }));
        }
      })
    );
    if (requestId === fetchRequestIdRef.current) {
      setIsScoring(false);
    }
  }, []);

  const particlesInit = useCallback(async (engine) => {
    await loadSlim(engine);
  }, []);

  const particlesConfig = {
    particles: {
      number: {
        value: 100,
        density: {
          enable: true,
          value_area: 800
        }
      },
      color: {
        value: '#ffffff'
      },
      shape: {
        type: 'circle'
      },
      opacity: {
        value: 0.6,
        random: true,
        animation: {
          enable: true,
          speed: 1,
          minimumValue: 0.1,
          sync: false
        }
      },
      size: {
        value: 3,
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
        direction: 'none',
        random: false,
        straight: false,
        outModes: {
          default: 'out'
        },
        bounce: false
      }
    },
    interactivity: {
      detectsOn: 'canvas',
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

  const openPack = () => {
    if (packCompleted) {
      return;
    }
    if (!cardsPool.length) {
      console.warn('No cards available to open a pack.');
      return;
    }
    // Rarity order: legendary > epic > rare > common
    const rarityOrder = { legendary: 4, epic: 3, rare: 2, common: 1 };
    
    // Find all cards with the highest rarity
    const sortedByRarity = [...cardsPool].sort((a, b) => {
      return rarityOrder[b.rarity] - rarityOrder[a.rarity];
    });
    
    // Get the highest rarity value
    const highestRarity = sortedByRarity[0]?.rarity ?? 'common';
    
    // Find all cards with the highest rarity
    const highestRarityCards = cardsPool.filter(card => card.rarity === highestRarity);
    
    // Randomly select one card from the highest rarity tier
    const bestCardSource = highestRarityCards.length ? highestRarityCards : cardsPool;
    const bestCard = bestCardSource[Math.floor(Math.random() * bestCardSource.length)];
    
    // Get remaining cards (excluding the best card)
    const remainingCards = cardsPool.filter(card => card.id !== bestCard.id);
    
    // Randomly select 4 cards from remaining
    const shuffled = [...remainingCards].sort(() => Math.random() - 0.5);
    const randomCards = shuffled.slice(0, Math.min(4, shuffled.length));
    
    // Create pack with best card at the end (index 4)
    const pack = [...randomCards, bestCard].slice(0, Math.min(cardsPool.length, 5));
    
    setCurrentPack(pack);
    setPackOpened(true);
    setIsScoring(true);
    setCurrentCardIndex(0);
    setRevealedCards([]);
    setIsRevealing(false);
    setAttractivenessScores({});

    const nextRequestId = fetchRequestIdRef.current + 1;
    fetchRequestIdRef.current = nextRequestId;
    fetchAttractivenessScores(pack, nextRequestId);
  };

  const handleSwipe = (direction) => {
    if (currentCardIndex >= currentPack.length) return;
    console.log(`🎯 SWIPE ${direction.toUpperCase()}: Current index ${currentCardIndex}`);
    const currentCard = currentPack[currentCardIndex];
    
    if (direction === 'right') {
      // Like - add to roster
      if (onCardLiked && typeof onCardLiked === 'function') {
        onCardLiked(currentCard);
      } else {
        console.log('  ⚠️  onCardLiked callback not provided, skipping like action');
      }
    }
    // Left swipe - just remove
    
    // Move to next card immediately (don't auto-reveal - user must flip it)
    setCurrentCardIndex((prev) => {
      const nextIndex = prev + 1;
      console.log(`  ➡️  Moving from index ${prev} to ${nextIndex}`);
      if (nextIndex < currentPack.length) {
        console.log(`  📋 Next card will be: ${currentPack[nextIndex]?.name || 'N/A'}`);
      }
      if (nextIndex >= currentPack.length) {
        // All cards processed
        try {
          const today = new Date().toISOString().slice(0, 10);
          localStorage.setItem('daily-pack-claimed', today);
        } catch {
          // ignore storage errors
        }
        setPackCompleted(true);
        setTimeout(() => {
          setPackOpened(false);
        }, 1000);
      }
      return nextIndex;
    });
  };

  const handleCardFlip = (cardIndex) => {
    console.log(`💫 REVEAL: Card index ${cardIndex}`);
    // Mark card as revealed when flipped
    setRevealedCards((prevRevealed) => {
      if (!prevRevealed.includes(cardIndex)) {
        console.log(`  ✨ Adding card ${cardIndex} to revealed list. Was: [${prevRevealed}] → Now: [${[...prevRevealed, cardIndex]}]`);
        setIsRevealing(true);
        setTimeout(() => {
          setIsRevealing(false);
        }, 600);
        return [...prevRevealed, cardIndex];
      }
      console.log(`  ⚠️  Card ${cardIndex} already revealed`);
      return prevRevealed;
    });
  };

  const resetPack = () => {
    setPackOpened(false);
    setCurrentCardIndex(0);
    setRevealedCards([]);
    setCurrentPack([]);
    setIsRevealing(false);
  };

  const currentCard = currentCardIndex < currentPack.length ? currentPack[currentCardIndex] : null;
  const isCurrentCardRevealed = currentCardIndex < currentPack.length && revealedCards.includes(currentCardIndex);
  const hasMoreCards = currentCardIndex < currentPack.length - 1;
  const isPackComplete = currentCardIndex >= currentPack.length;

  return (
    <div className="h-screen w-screen bg-black text-white overflow-hidden fixed inset-0">
      {/* Starfield Background */}
      <div className="absolute inset-0 z-0">
        <Particles
          id="tsparticles-pack"
          init={particlesInit}
          options={particlesConfig}
        />
      </div>

      {/* Content */}
      <div className="relative z-20 h-full flex flex-col items-center justify-center px-6 py-12">
        {fetchError && (
          <div className="mb-6 max-w-3xl text-center px-4 py-3 rounded-2xl border border-red-500/40 bg-red-500/10 text-red-200 backdrop-blur">
            {fetchError}
          </div>
        )}
        {!packOpened ? (
          packCompleted ? (
            // Pack completed screen
            <div className="text-center space-y-8">
              <h1 className="text-6xl md:text-8xl font-bold mb-6 text-white drop-shadow-2xl">
                No More Cards Today
              </h1>
              <p className="text-xl md:text-2xl mb-10 text-white/80 drop-shadow-lg max-w-2xl mx-auto">
                You've already opened today's pack. Come back tomorrow for fresh matches!
              </p>
              <div className="space-y-4 flex flex-col items-center">
                <div className="text-6xl">🕒</div>
                <button
                  onClick={resetDailyLock}
                  className="px-6 py-3 rounded-full bg-white/10 text-white/80 hover:bg-white/20 transition-all"
                >
                  Unlock another pack for testing
                </button>
              </div>
            </div>
          ) : (
            // Pack selection screen
            <div className="text-center space-y-8">
              <h1 className="text-6xl md:text-8xl font-bold mb-6 text-white drop-shadow-2xl animate-fade-in">
                Open Your First Pack
              </h1>
              <p className="text-xl md:text-2xl mb-10 text-white/80 drop-shadow-lg max-w-2xl mx-auto">
                Get 5 new matches today! Cards will reveal one by one.
              </p>
              <div className="relative inline-block">
                {/* Multiple dramatic glow layers */}
                <div className="absolute inset-0 rounded-2xl bg-pink-500 blur-3xl opacity-80 animate-pulse-glow"></div>
                <div className="absolute inset-0 rounded-2xl bg-purple-400 blur-2xl opacity-60 animate-pulse-glow-delayed"></div>
                <div className="absolute -inset-2 rounded-2xl bg-pink-400 blur-xl opacity-50 animate-pulse-glow-slow"></div>
                <div className="absolute -inset-4 rounded-2xl bg-purple-500 blur-2xl opacity-30 animate-pulse-glow"></div>
                
                {/* Shimmer effect overlay */}
                <div className="absolute inset-0 rounded-2xl overflow-hidden">
                  <div className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12"></div>
                </div>
                
                {/* 3D Pack Box Visual */}
                <div className="absolute -top-24 left-1/2 transform -translate-x-1/2 pointer-events-none z-0">
                  <div className="relative w-40 h-40 animate-float">
                    {/* Box shadow */}
                    <div className="absolute inset-0 bg-black/40 blur-3xl transform translate-y-12 scale-150"></div>
                    {/* Glowing box */}
                    <div className="relative w-full h-full">
                      {/* Main box with 3D effect */}
                      <div className="absolute inset-0 bg-gradient-to-br from-pink-400 via-purple-500 to-pink-600 rounded-xl shadow-2xl border-4 border-pink-300 transform rotate-3 perspective-1000">
                        <div className="absolute inset-0 flex items-center justify-center">
                          <span className="text-7xl drop-shadow-2xl">📦</span>
                        </div>
                        {/* Shine overlay */}
                        <div className="absolute inset-0 bg-gradient-to-br from-white/30 via-transparent to-transparent rounded-xl"></div>
                        {/* Top highlight */}
                        <div className="absolute top-0 left-0 right-0 h-1/3 bg-gradient-to-b from-white/40 to-transparent rounded-t-xl"></div>
                      </div>
                      {/* Glow rings */}
                      <div className="absolute -inset-4 bg-pink-400/30 rounded-xl blur-xl animate-pulse"></div>
                      <div className="absolute -inset-8 bg-purple-400/20 rounded-xl blur-2xl animate-pulse" style={{ animationDelay: '0.5s' }}></div>
                    </div>
                  </div>
                </div>
                
                {/* Pack button */}
                <button
                  onClick={openPack}
                  className="relative bg-gradient-to-r from-pink-500 via-purple-500 to-pink-600 text-white px-20 py-10 rounded-2xl text-4xl font-bold transition-all duration-300 shadow-[0_0_40px_rgba(236,72,153,0.8),0_0_80px_rgba(168,85,247,0.6),inset_0_2px_10px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_rgba(236,72,153,1),0_0_120px_rgba(168,85,247,0.8),inset_0_2px_15px_rgba(255,255,255,0.5)] hover:scale-110 active:scale-95 transform hover:-translate-y-1 border-2 border-pink-300/50 overflow-hidden group cursor-pointer"
                >
                  {/* Button shine effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent transform -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                  
                  {/* Button content */}
                  <div className="relative z-10 flex items-center justify-center gap-4">
                    <span className="text-5xl animate-bounce-slow">✨</span>
                    <span className="tracking-wide">OPEN YOUR PACK</span>
                    <span className="text-5xl animate-bounce-slow" style={{ animationDelay: '0.2s' }}>✨</span>
                  </div>
                  
                  {/* Sparkle particles */}
                  <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-pink-300 rounded-full animate-sparkle opacity-80"></div>
                    <div className="absolute top-3/4 right-1/4 w-2 h-2 bg-purple-300 rounded-full animate-sparkle opacity-80" style={{ animationDelay: '0.3s' }}></div>
                    <div className="absolute bottom-1/4 left-1/2 w-2 h-2 bg-pink-400 rounded-full animate-sparkle opacity-80" style={{ animationDelay: '0.6s' }}></div>
                  </div>
                </button>
              </div>
            </div>
          )
        ) : isScoring ? (
          <div className="flex flex-col items-center justify-center space-y-6">
            <div className="relative">
              <div className="w-24 h-24 border-4 border-pink-400 border-t-transparent rounded-full animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center text-3xl">📊</div>
            </div>
            <div className="text-xl text-white/80">Scoring your pack...</div>
          </div>
        ) : (
          // Pack opening screen
          <div className="w-full max-w-4xl h-full flex flex-col items-center justify-center">
            <div className="text-center mb-6">
              <h2 className="text-3xl font-bold mb-2">
                Card {Math.min(currentCardIndex + 1, currentPack.length)} of {currentPack.length}
              </h2>
              {isCurrentCardRevealed && currentCardIndex < currentPack.length && (
                <p className="text-white/70 text-sm">
                  Swipe left to pass, right to like
                </p>
              )}
            </div>

            {/* Card stack */}
            <div className="relative w-full max-w-md h-[480px] touch-none overflow-visible flex items-center justify-center">
              {currentPack.map((card, index) => {
                const isRevealed = revealedCards.includes(index);
                const isActive = index === currentCardIndex;
                const isBehind = index > currentCardIndex;
                const stackOffset = index - currentCardIndex;
                
                // Debug logging for card rendering
                if (isActive) {
                  console.log(`🎴 RENDERING ACTIVE CARD ${index}:`, {
                    cardName: card?.name,
                    isRevealed,
                    isActive,
                    currentCardIndex,
                    revealedCards
                  });
                }
                
                // Show all cards: current card, cards behind it (stack), and next card if not revealed
                if (index < currentCardIndex) {
                  return null; // Don't show cards we've already swiped past
                }
                
                // Calculate z-index and position for stack effect
                // Active card should have highest z-index, then cards behind it
                // Use a high base z-index to ensure active card is always on top
                const baseZIndex = 1000;
                const zIndex = isActive ? baseZIndex + 100 : (isBehind ? baseZIndex - (stackOffset * 10) : baseZIndex);
                // Stack effect: each card behind is slightly offset down and to the side
                // This creates the effect where you can see cards behind through the top
                const translateY = isBehind ? stackOffset * 15 : 0;
                const translateX = isBehind ? stackOffset * 8 : 0;
                // Slight scale reduction for depth
                const scale = isBehind ? 1 - (stackOffset * 0.02) : 1;
                // Cards are solid (opacity 1)
                
                // Cards that are swiped (index < currentCardIndex) are already removed from DOM
                // Only render cards from currentCardIndex onwards
                return (
                  <div
                    key={`card-${index}-${card.id}`}
                    className="absolute"
                    style={{
                      zIndex: zIndex,
                      left: `calc(50% - 160px + ${translateX}px)`,
                      top: `calc(50% - 240px + ${translateY}px)`,
                      transform: `scale(${scale})`,
                      opacity: 1,
                      pointerEvents: isActive ? 'auto' : 'none'
                    }}
                  >
                    <SwipeableCard
                      key={`swipeable-${index}-${isActive}`}
                      card={card}
                      isRevealed={isRevealed}
                      isActive={isActive}
                      onSwipe={handleSwipe}
                      onFlip={() => {
                        console.log(`🎯 onFlip callback for card ${index} (${card?.name})`);
                        handleCardFlip(index);
                      }}
                      attractivenessScore={attractivenessScores[card.id]}
                    />
                  </div>
                );
              })}

              {/* No more cards message */}
              {!hasMoreCards && isCurrentCardRevealed && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-4xl mb-4">✨</div>
                    <div className="text-2xl font-bold mb-2">Pack Complete!</div>
                    <button
                      onClick={resetPack}
                      className="mt-4 px-8 py-4 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full font-semibold hover:scale-105 transition-transform shadow-lg"
                    >
                      Open Another Pack
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PackOpening;

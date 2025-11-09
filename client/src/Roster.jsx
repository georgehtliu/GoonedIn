import { useState, useCallback } from 'react';
import Particles from 'react-particles';
import { loadSlim } from 'tsparticles-slim';

const Roster = ({ likedCards, onRemoveCard }) => {
  const [expandedCardId, setExpandedCardId] = useState(null);
  const [showConfirmRemove, setShowConfirmRemove] = useState(false);
  const [cardToRemove, setCardToRemove] = useState(null);
  const [aiOverview, setAiOverview] = useState({});
  const [satiricalInsights, setSatiricalInsights] = useState({});
  const [socialProfiles, setSocialProfiles] = useState({});
  const [loadingAI, setLoadingAI] = useState(false);
  const [loadingSatirical, setLoadingSatirical] = useState(false);
  const [loadingSocials, setLoadingSocials] = useState(false);
  const [showSatirical, setShowSatirical] = useState({});
  
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

  const getRarityColor = (rarity) => {
    switch (rarity) {
      case 'legendary':
        return 'from-yellow-400 via-yellow-500 to-yellow-600';
      case 'epic':
        return 'from-purple-500 via-purple-600 to-purple-700';
      case 'rare':
        return 'from-blue-500 via-blue-600 to-blue-700';
      case 'uncommon':
        return 'from-gray-500 via-gray-600 to-gray-700';
      case 'common':
        return 'from-green-500 via-green-600 to-green-700';
      default:
        return 'from-gray-500 via-gray-600 to-gray-700';
    }
  };

  const handleCardClick = (cardId) => {
    if (expandedCardId === cardId) {
      setExpandedCardId(null);
    } else {
      setExpandedCardId(cardId);
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      setExpandedCardId(null);
    }
  };

  const handleRemoveClick = (card) => {
    setCardToRemove(card);
    setShowConfirmRemove(true);
  };

  const confirmRemove = () => {
    if (cardToRemove && onRemoveCard) {
      onRemoveCard(cardToRemove);
      setExpandedCardId(null);
      setShowConfirmRemove(false);
      setCardToRemove(null);
    }
  };

  const cancelRemove = () => {
    setShowConfirmRemove(false);
    setCardToRemove(null);
  };

  const fetchAIOverview = async (card) => {
    if (aiOverview[card.id]) return; // Already fetched

    setLoadingAI(true);
    try {
      const response = await fetch('http://localhost:8000/api/ai-overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile: {
            name: card.name,
            major: card.major,
            company: card.company,
            bio: card.bio,
            location: card.location,
            interests: card.interests || [],
            experience: card.experience,
            age: card.age
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAiOverview(prev => ({ ...prev, [card.id]: data }));
      }
    } catch (err) {
      console.error('Failed to fetch AI overview:', err);
    } finally {
      setLoadingAI(false);
    }
  };

  const fetchSatiricalInsights = async (card) => {
    if (satiricalInsights[card.id]) return; // Already fetched

    setLoadingSatirical(true);
    try {
      const response = await fetch('http://localhost:8000/api/satirical-insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile: {
            name: card.name,
            major: card.major,
            company: card.company,
            bio: card.bio,
            interests: card.interests || []
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSatiricalInsights(prev => ({ ...prev, [card.id]: data }));
      }
    } catch (err) {
      console.error('Failed to fetch satirical insights:', err);
    } finally {
      setLoadingSatirical(false);
    }
  };

  const fetchSocialProfiles = async (card) => {
    if (socialProfiles[card.id]) return; // Already fetched

    setLoadingSocials(true);
    try {
      const response = await fetch('http://localhost:8000/api/find-socials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: card.name,
          company: card.company,
          location: card.location
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSocialProfiles(prev => ({ ...prev, [card.id]: data }));
      }
    } catch (err) {
      console.error('Failed to fetch social profiles:', err);
    } finally {
      setLoadingSocials(false);
    }
  };

  return (
    <div className="h-screen w-screen bg-black text-white overflow-auto fixed inset-0">
      {/* Starfield Background */}
      <div className="absolute inset-0 z-0">
        <Particles
          id="tsparticles-roster"
          init={particlesInit}
          options={particlesConfig}
        />
      </div>

      {/* Content */}
      <div className="relative z-20 min-h-full px-6 pt-24 pb-12">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-7xl font-bold mb-4 text-white drop-shadow-2xl">
              Your Roster
            </h1>
            <p className="text-xl text-white/80 drop-shadow-lg">
              {likedCards.length === 0
                ? "You haven't liked any cards yet. Swipe right on cards to add them here!"
                : `You have ${likedCards.length} card${likedCards.length !== 1 ? 's' : ''} in your roster`}
            </p>
          </div>

          {likedCards.length === 0 ? (
            <div className="text-center py-20">
              <div className="text-8xl mb-6">💔</div>
              <p className="text-2xl text-white/60">No cards in your roster yet</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {likedCards.map((card) => {
                  const isExpanded = expandedCardId === card.id;
                  
                  // Don't render expanded card in grid
                  if (isExpanded) return null;
                  
                  return (
                    <div
                      key={card.id}
                      onClick={() => handleCardClick(card.id)}
                      className="relative w-full h-[600px] rounded-3xl overflow-hidden shadow-2xl border-4 border-white/20 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 cursor-pointer transition-all duration-300 ease-out hover:scale-105"
                    >
                    {/* Glow effect */}
                    <div
                      className={`absolute -inset-4 rounded-3xl bg-gradient-to-r ${getRarityColor(
                        card.rarity
                      )} blur-2xl opacity-60 animate-pulse-glow`}
                    />

                    {/* Close button for expanded card */}
                    {isExpanded && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setExpandedCardId(null);
                        }}
                        className="absolute top-4 left-4 z-50 w-10 h-10 rounded-full bg-black/50 hover:bg-black/70 text-white flex items-center justify-center text-xl font-bold transition-all duration-200 hover:scale-110"
                      >
                        ✕
                      </button>
                    )}

                    {/* Rarity indicator */}
                    <div
                      className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold text-white bg-gradient-to-r ${getRarityColor(
                        card.rarity
                      )} shadow-lg z-20`}
                    >
                      {card.rarity.toUpperCase()}
                    </div>

                    {/* Profile Image */}
                    <div className={`relative overflow-hidden transition-all duration-500 ${isExpanded ? 'h-[350px]' : 'h-[280px]'}`}>
                      <div className="absolute inset-0 bg-gradient-to-br from-pink-600/30 via-purple-600/30 to-blue-600/30" />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="relative">
                          {/* Glow rings */}
                          <div
                            className={`absolute inset-0 -m-6 rounded-full bg-gradient-to-r ${getRarityColor(
                              card.rarity
                            )} blur-2xl opacity-50 animate-spin-slow animate-pulse-scale`}
                          />
                          <div
                            className={`absolute inset-0 -m-4 rounded-full bg-gradient-to-r ${getRarityColor(
                              card.rarity
                            )} blur-xl opacity-60 animate-spin-reverse animate-pulse-scale-delayed`}
                          />

                          {/* Avatar */}
                          <div className={`relative rounded-full overflow-hidden shadow-2xl border-4 border-white/30 transition-all duration-500 ${
                            isExpanded ? 'w-64 h-64' : 'w-48 h-48'
                          }`}>
                            {card.image ? (
                              <img
                                src={card.image}
                                alt={card.name}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div
                                className={`w-full h-full bg-gradient-to-br ${getRarityColor(
                                  card.rarity
                                )} flex items-center justify-center text-white font-bold transition-all duration-500 ${
                                  isExpanded ? 'text-7xl' : 'text-5xl'
                                }`}
                              >
                                {card.name
                                  .split(' ')
                                  .map((n) => n[0])
                                  .join('')}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Profile Info */}
                    <div className={`p-5 space-y-3 bg-black/40 backdrop-blur-sm transition-all duration-500 ${
                      isExpanded ? 'h-[calc(100%-350px)] overflow-y-auto' : ''
                    }`}>
                      <div className="text-center">
                        <h3 className={`font-bold text-white tracking-tight mb-1 drop-shadow-lg transition-all duration-500 ${
                          isExpanded ? 'text-4xl' : 'text-3xl'
                        }`}>
                          {card.name}
                        </h3>
                        <div className="text-white text-base font-semibold">{card.age} years old</div>
                      </div>

                      <div className="space-y-2 text-center">
                        <div className="text-white text-lg font-semibold drop-shadow-md">
                          {card.major}
                        </div>
                        <div className="text-white text-lg font-semibold drop-shadow-md">
                          {card.company}
                        </div>
                        <div className="text-white text-base flex items-center justify-center gap-2 font-medium">
                          <span>📍</span>
                          {card.location}
                        </div>
                      </div>

                      {/* Bio */}
                      <div className="pt-3 border-t border-white/20">
                        <p className={`text-white leading-relaxed text-center font-medium drop-shadow-md px-2 transition-all duration-500 ${
                          isExpanded ? 'text-lg' : 'text-base'
                        }`}>
                          {card.bio}
                        </p>
                      </div>

                      {/* Interests */}
                      <div className="pt-3">
                        <div className="text-white text-sm mb-2 text-center font-semibold">Interests</div>
                        <div className="flex flex-wrap gap-2 justify-center">
                          {card.interests.map((interest, idx) => (
                            <span
                              key={idx}
                              className="px-4 py-2 rounded-full bg-white/20 text-white text-sm font-semibold border border-white/30 drop-shadow-md"
                            >
                              {interest}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Experience */}
                      <div className="pt-3 text-center border-t border-white/20">
                        <div className="text-white/90 text-sm mb-1 font-semibold">Experience</div>
                        <div className="text-white text-base font-bold">{card.experience}</div>
                      </div>

                      {/* Email and LinkedIn - Only shown when expanded */}
                      {isExpanded && card.email && card.linkedin && (
                        <div className="pt-4 mt-4 border-t-2 border-white/30 space-y-4">
                          <div className="text-center">
                            <div className="text-white text-lg font-bold mb-3">Contact Information</div>
                            
                            {/* Email */}
                            <div className="mb-3">
                              <a
                                href={`mailto:${card.email}`}
                                onClick={(e) => e.stopPropagation()}
                                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-full font-semibold hover:from-blue-600 hover:to-cyan-600 transition-all duration-200 hover:scale-105 shadow-lg"
                              >
                                <span>📧</span>
                                <span>{card.email}</span>
                              </a>
                            </div>

                            {/* LinkedIn */}
                            <div>
                              <a
                                href={card.linkedin}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 hover:scale-105 shadow-lg"
                              >
                                <span>💼</span>
                                <span>LinkedIn Profile</span>
                              </a>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  );
                })}
              </div>

              {/* Expanded Card - Rendered outside grid */}
              {expandedCardId && (() => {
                const expandedCard = likedCards.find(card => card.id === expandedCardId);
                if (!expandedCard) return null;
                
                return (
                  <>
                    {/* Backdrop */}
                    <div
                      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 transition-opacity duration-300"
                      onClick={handleBackdropClick}
                    />
                    
                    {/* Expanded Card */}
                    <div
                      className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-[90vw] max-w-2xl h-[90vh] max-h-[800px] rounded-3xl overflow-hidden shadow-2xl border-4 border-white/20 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 transition-all duration-500 ease-out"
                    >
                      {/* Glow effect */}
                      <div
                        className={`absolute -inset-4 rounded-3xl bg-gradient-to-r ${getRarityColor(
                          expandedCard.rarity
                        )} blur-2xl opacity-60 animate-pulse-glow`}
                      />

                      {/* Close button */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setExpandedCardId(null);
                        }}
                        className="absolute top-4 left-4 z-50 w-10 h-10 rounded-full bg-black/70 hover:bg-black/90 text-white flex items-center justify-center text-xl font-bold transition-all duration-200 hover:scale-110 shadow-lg"
                      >
                        ✕
                      </button>

                      {/* Rarity indicator */}
                      <div
                        className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold text-white bg-gradient-to-r ${getRarityColor(
                          expandedCard.rarity
                        )} shadow-lg z-20`}
                      >
                        {expandedCard.rarity.toUpperCase()}
                      </div>

                      {/* Profile Image */}
                      <div className="relative h-[350px] overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-br from-pink-600/30 via-purple-600/30 to-blue-600/30" />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="relative">
                            {/* Glow rings */}
                            <div
                              className={`absolute inset-0 -m-6 rounded-full bg-gradient-to-r ${getRarityColor(
                                expandedCard.rarity
                              )} blur-2xl opacity-50 animate-spin-slow animate-pulse-scale`}
                            />
                            <div
                              className={`absolute inset-0 -m-4 rounded-full bg-gradient-to-r ${getRarityColor(
                                expandedCard.rarity
                              )} blur-xl opacity-60 animate-spin-reverse animate-pulse-scale-delayed`}
                            />

                            {/* Avatar */}
                            <div className="relative w-64 h-64 rounded-full overflow-hidden shadow-2xl border-4 border-white/30">
                              {expandedCard.image ? (
                                <img
                                  src={expandedCard.image}
                                  alt={expandedCard.name}
                                  className="w-full h-full object-cover"
                                />
                              ) : (
                                <div
                                  className={`w-full h-full bg-gradient-to-br ${getRarityColor(
                                    expandedCard.rarity
                                  )} flex items-center justify-center text-white text-7xl font-bold`}
                                >
                                  {expandedCard.name
                                    .split(' ')
                                    .map((n) => n[0])
                                    .join('')}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Profile Info */}
                      <div className="p-5 space-y-3 bg-black/40 backdrop-blur-sm h-[calc(100%-350px)] overflow-y-auto">
                        <div className="text-center">
                          <h3 className="text-4xl font-bold text-white tracking-tight mb-1 drop-shadow-lg">
                            {expandedCard.name}
                          </h3>
                          <div className="text-white text-base font-semibold">{expandedCard.age} years old</div>
                        </div>

                        <div className="space-y-2 text-center">
                          <div className="text-white text-lg font-semibold drop-shadow-md">
                            {expandedCard.major}
                          </div>
                          <div className="text-white text-lg font-semibold drop-shadow-md">
                            {expandedCard.company}
                          </div>
                          <div className="text-white text-base flex items-center justify-center gap-2 font-medium">
                            <span>📍</span>
                            {expandedCard.location}
                          </div>
                        </div>

                        {/* Bio */}
                        <div className="pt-3 border-t border-white/20">
                          <p className="text-white text-lg leading-relaxed text-center font-medium drop-shadow-md px-2">
                            {expandedCard.bio}
                          </p>
                        </div>

                        {/* Interests */}
                        <div className="pt-3">
                          <div className="text-white text-sm mb-2 text-center font-semibold">Interests</div>
                          <div className="flex flex-wrap gap-2 justify-center">
                            {expandedCard.interests.map((interest, idx) => (
                              <span
                                key={idx}
                                className="px-4 py-2 rounded-full bg-white/20 text-white text-sm font-semibold border border-white/30 drop-shadow-md"
                              >
                                {interest}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Experience */}
                        <div className="pt-3 text-center border-t border-white/20">
                          <div className="text-white/90 text-sm mb-1 font-semibold">Experience</div>
                          <div className="text-white text-base font-bold">{expandedCard.experience}</div>
                        </div>

                        {/* AI Overview Section */}
                        <div className="pt-4 mt-4 border-t-2 border-purple-500/30">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              fetchAIOverview(expandedCard);
                            }}
                            disabled={loadingAI}
                            className="w-full mb-3 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all duration-200 hover:scale-105 shadow-lg disabled:opacity-50"
                          >
                            {loadingAI ? '🤖 Generating AI Insights...' : '✨ Get AI Overview'}
                          </button>

                          {aiOverview[expandedCard.id] && (
                            <div className="space-y-3 bg-purple-900/20 p-4 rounded-xl border border-purple-500/30">
                              <div>
                                <h4 className="text-yellow-400 font-bold mb-1">Summary</h4>
                                <p className="text-white/90 text-sm">{aiOverview[expandedCard.id].summary}</p>
                              </div>
                              <div>
                                <h4 className="text-yellow-400 font-bold mb-1">Personality Insights</h4>
                                <p className="text-white/90 text-sm">{aiOverview[expandedCard.id].personality_insights}</p>
                              </div>
                              <div>
                                <h4 className="text-yellow-400 font-bold mb-1">Compatibility</h4>
                                <p className="text-white/90 text-sm">{aiOverview[expandedCard.id].compatibility_notes}</p>
                              </div>
                              <div>
                                <h4 className="text-yellow-400 font-bold mb-1">Conversation Starters</h4>
                                <ul className="space-y-1">
                                  {aiOverview[expandedCard.id].conversation_starters.map((starter, idx) => (
                                    <li key={idx} className="text-white/90 text-sm">💬 {starter}</li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          )}

                          {/* Satirical Insights Toggle */}
                          <div className="mt-3">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                if (!satiricalInsights[expandedCard.id]) {
                                  fetchSatiricalInsights(expandedCard);
                                }
                                setShowSatirical(prev => ({ ...prev, [expandedCard.id]: !prev[expandedCard.id] }));
                              }}
                              disabled={loadingSatirical}
                              className="w-full px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-xl font-semibold hover:from-orange-600 hover:to-red-600 transition-all duration-200 hover:scale-105 shadow-lg disabled:opacity-50"
                            >
                              {loadingSatirical ? '😄 Generating Roasts...' : showSatirical[expandedCard.id] ? '😏 Hide Satirical Insights' : '😂 Show Satirical Insights'}
                            </button>

                            {showSatirical[expandedCard.id] && satiricalInsights[expandedCard.id] && (
                              <div className="mt-3 space-y-2 bg-orange-900/20 p-4 rounded-xl border border-orange-500/30">
                                <h4 className="text-orange-400 font-bold mb-2">Probably...</h4>
                                {satiricalInsights[expandedCard.id].insights.map((insight, idx) => (
                                  <p key={idx} className="text-white/90 text-sm italic">• {insight}</p>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Email and LinkedIn */}
                        {expandedCard.email && expandedCard.linkedin && (
                          <div className="pt-4 mt-4 border-t-2 border-white/30 space-y-4">
                            <div className="text-center">
                              <div className="text-white text-lg font-bold mb-3">Contact Information</div>

                              {/* Email */}
                              <div className="mb-3">
                                <a
                                  href={`mailto:${expandedCard.email}`}
                                  onClick={(e) => e.stopPropagation()}
                                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-full font-semibold hover:from-blue-600 hover:to-cyan-600 transition-all duration-200 hover:scale-105 shadow-lg"
                                >
                                  <span>📧</span>
                                  <span>{expandedCard.email}</span>
                                </a>
                              </div>

                              {/* LinkedIn */}
                              <div className="mb-3">
                                <a
                                  href={expandedCard.linkedin}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  onClick={(e) => e.stopPropagation()}
                                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 hover:scale-105 shadow-lg"
                                >
                                  <span>💼</span>
                                  <span>LinkedIn Profile</span>
                                </a>
                              </div>

                              {/* Remove Button */}
                              <div>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleRemoveClick(expandedCard);
                                  }}
                                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-full font-semibold hover:from-red-600 hover:to-red-700 transition-all duration-200 hover:scale-105 shadow-lg"
                                >
                                  <span>🗑️</span>
                                  <span>Remove from Roster</span>
                                </button>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Social Profiles - "More ways to reach" */}
                        <div className="pt-4 mt-4 border-t-2 border-cyan-500/30">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              fetchSocialProfiles(expandedCard);
                            }}
                            disabled={loadingSocials}
                            className="w-full mb-3 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-xl font-semibold hover:from-cyan-600 hover:to-blue-600 transition-all duration-200 hover:scale-105 shadow-lg disabled:opacity-50"
                          >
                            {loadingSocials ? '🔍 Searching...' : `🌐 More ways to reach ${expandedCard.name.split(' ')[0]}`}
                          </button>

                          {socialProfiles[expandedCard.id] && socialProfiles[expandedCard.id].profiles.length > 0 && (
                            <div className="space-y-2 bg-cyan-900/20 p-4 rounded-xl border border-cyan-500/30">
                              <h4 className="text-cyan-400 font-bold mb-2">Potential Social Profiles</h4>
                              <p className="text-white/70 text-xs mb-2">Note: These are educated guesses based on name patterns</p>
                              {socialProfiles[expandedCard.id].profiles.map((profile, idx) => (
                                <a
                                  key={idx}
                                  href={profile.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  onClick={(e) => e.stopPropagation()}
                                  className="block p-3 bg-white/10 hover:bg-white/20 rounded-lg transition-all"
                                >
                                  <div className="flex justify-between items-center">
                                    <span className="text-white font-semibold">{profile.platform}</span>
                                    <span className={`text-xs px-2 py-1 rounded ${
                                      profile.confidence === 'high' ? 'bg-green-500/30 text-green-300' :
                                      profile.confidence === 'medium' ? 'bg-yellow-500/30 text-yellow-300' :
                                      'bg-gray-500/30 text-gray-300'
                                    }`}>
                                      {profile.confidence} confidence
                                    </span>
                                  </div>
                                  <div className="text-white/60 text-sm mt-1 truncate">{profile.url}</div>
                                </a>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </>
                );
              })()}
            </>
          )}
        </div>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmRemove && cardToRemove && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/90 backdrop-blur-sm"
            onClick={cancelRemove}
          />
          
          {/* Dialog */}
          <div className="relative z-50 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-3xl p-8 max-w-md w-[90vw] border-4 border-red-500/50 shadow-2xl">
            <div className="text-center">
              <div className="text-6xl mb-4">⚠️</div>
              <h3 className="text-3xl font-bold text-white mb-4">Remove from Roster?</h3>
              <p className="text-white/80 text-lg mb-6">
                Are you sure you want to remove <span className="font-bold text-white">{cardToRemove.name}</span> from your roster? This action cannot be undone.
              </p>
              
              <div className="flex gap-4 justify-center">
                <button
                  onClick={cancelRemove}
                  className="px-6 py-3 bg-white/10 text-white rounded-full font-semibold hover:bg-white/20 transition-all duration-200 hover:scale-105"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmRemove}
                  className="px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-full font-semibold hover:from-red-600 hover:to-red-700 transition-all duration-200 hover:scale-105 shadow-lg"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Roster;

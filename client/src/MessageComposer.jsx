import { useState } from 'react';

const MessageComposer = ({ rosterCards }) => {
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [tone, setTone] = useState('flirty');
  const [messageType, setMessageType] = useState('cold_dm');
  const [context, setContext] = useState('');
  const [generatedMessage, setGeneratedMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const tones = [
    { value: 'flirty', label: 'Flirty', icon: '😏', color: 'from-pink-500 to-rose-500' },
    { value: 'polite', label: 'Polite', icon: '🤝', color: 'from-blue-500 to-cyan-500' },
    { value: 'direct', label: 'Direct', icon: '🎯', color: 'from-orange-500 to-amber-500' },
    { value: 'professional', label: 'Professional', icon: '💼', color: 'from-gray-500 to-slate-500' },
    { value: 'casual', label: 'Casual', icon: '😊', color: 'from-green-500 to-emerald-500' },
    { value: 'witty', label: 'Witty', icon: '🎭', color: 'from-purple-500 to-violet-500' }
  ];

  const messageTypes = [
    { value: 'cold_dm', label: 'Cold DM', description: 'First message to someone new' },
    { value: 'warm_dm', label: 'Warm DM', description: 'Message after matching' },
    { value: 'follow_up', label: 'Follow-up', description: 'Continue conversation' }
  ];

  const handleGenerateMessage = async () => {
    if (!selectedPerson) {
      setError('Please select a person from your roster');
      return;
    }

    setLoading(true);
    setError('');
    setGeneratedMessage('');
    setCopied(false);

    try {
      const response = await fetch('http://localhost:8000/api/draft-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipient: {
            name: selectedPerson.name,
            major: selectedPerson.major,
            company: selectedPerson.company,
            bio: selectedPerson.bio,
            location: selectedPerson.location,
            interests: selectedPerson.interests || [],
            experience: selectedPerson.experience,
            age: selectedPerson.age
          },
          tone,
          message_type: messageType,
          context: context || null
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate message');
      }

      const data = await response.json();
      setGeneratedMessage(data.message);
    } catch (err) {
      setError('Failed to generate message. Make sure the server is running and Gemini API is configured.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(generatedMessage);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="h-full w-full overflow-y-auto bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto pb-12">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-yellow-400 via-pink-500 to-purple-600 bg-clip-text text-transparent mb-2">
            AI Message Composer
          </h1>
          <p className="text-gray-300 text-lg">
            Craft the perfect LinkedIn DM with AI assistance
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Configuration */}
          <div className="space-y-6">
            {/* Person Selector */}
            <div className="bg-gradient-to-br from-slate-800/50 to-purple-900/30 backdrop-blur-sm p-6 rounded-2xl border border-yellow-500/20 shadow-xl">
              <h2 className="text-2xl font-bold text-yellow-400 mb-4">Select Recipient</h2>
              <select
                value={selectedPerson?.id || ''}
                onChange={(e) => {
                  const person = rosterCards.find(c => c.id === parseInt(e.target.value));
                  setSelectedPerson(person);
                }}
                className="w-full bg-slate-900/80 text-white border border-yellow-500/30 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-yellow-500 transition-all"
              >
                <option value="">Choose from your roster...</option>
                {rosterCards.map(card => (
                  <option key={card.id} value={card.id}>
                    {card.name} - {card.major}
                  </option>
                ))}
              </select>

              {selectedPerson && (
                <div className="mt-4 p-4 bg-slate-900/60 rounded-xl border border-purple-500/20">
                  <div className="flex items-center gap-3 mb-2">
                    <img
                      src={selectedPerson.image}
                      alt={selectedPerson.name}
                      className="w-12 h-12 rounded-full object-cover border-2 border-yellow-500"
                    />
                    <div>
                      <p className="text-white font-bold">{selectedPerson.name}</p>
                      <p className="text-gray-400 text-sm">{selectedPerson.company}</p>
                    </div>
                  </div>
                  <p className="text-gray-300 text-sm">{selectedPerson.bio}</p>
                </div>
              )}
            </div>

            {/* Tone Selector */}
            <div className="bg-gradient-to-br from-slate-800/50 to-purple-900/30 backdrop-blur-sm p-6 rounded-2xl border border-yellow-500/20 shadow-xl">
              <h2 className="text-2xl font-bold text-yellow-400 mb-4">Select Tone</h2>
              <div className="grid grid-cols-2 gap-3">
                {tones.map((t) => (
                  <button
                    key={t.value}
                    onClick={() => setTone(t.value)}
                    className={`p-4 rounded-xl font-semibold transition-all transform hover:scale-105 ${
                      tone === t.value
                        ? `bg-gradient-to-r ${t.color} text-white shadow-lg scale-105`
                        : 'bg-slate-800/60 text-gray-300 hover:bg-slate-700/60'
                    }`}
                  >
                    <div className="text-2xl mb-1">{t.icon}</div>
                    <div className="text-sm">{t.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Message Type */}
            <div className="bg-gradient-to-br from-slate-800/50 to-purple-900/30 backdrop-blur-sm p-6 rounded-2xl border border-yellow-500/20 shadow-xl">
              <h2 className="text-2xl font-bold text-yellow-400 mb-4">Message Type</h2>
              <div className="space-y-2">
                {messageTypes.map((mt) => (
                  <button
                    key={mt.value}
                    onClick={() => setMessageType(mt.value)}
                    className={`w-full p-4 rounded-xl text-left transition-all ${
                      messageType === mt.value
                        ? 'bg-gradient-to-r from-yellow-500 to-pink-500 text-white shadow-lg'
                        : 'bg-slate-800/60 text-gray-300 hover:bg-slate-700/60'
                    }`}
                  >
                    <div className="font-bold">{mt.label}</div>
                    <div className="text-sm opacity-80">{mt.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Optional Context */}
            <div className="bg-gradient-to-br from-slate-800/50 to-purple-900/30 backdrop-blur-sm p-6 rounded-2xl border border-yellow-500/20 shadow-xl">
              <h2 className="text-2xl font-bold text-yellow-400 mb-4">Additional Context (Optional)</h2>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="Add any extra details or context for the AI..."
                className="w-full bg-slate-900/80 text-white border border-yellow-500/30 rounded-xl p-3 h-24 focus:outline-none focus:ring-2 focus:ring-yellow-500 transition-all resize-none"
              />
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerateMessage}
              disabled={loading || !selectedPerson}
              className={`w-full py-4 rounded-xl font-bold text-xl transition-all transform ${
                loading || !selectedPerson
                  ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-yellow-400 via-pink-500 to-purple-600 text-white hover:scale-105 hover:shadow-2xl'
              }`}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating...
                </span>
              ) : (
                '✨ Generate Message'
              )}
            </button>
          </div>

          {/* Right Panel - Generated Message */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-slate-800/50 to-purple-900/30 backdrop-blur-sm p-6 rounded-2xl border border-yellow-500/20 shadow-xl h-full">
              <h2 className="text-2xl font-bold text-yellow-400 mb-4">Generated Message</h2>

              {error && (
                <div className="bg-red-900/30 border border-red-500 text-red-200 p-4 rounded-xl mb-4">
                  {error}
                </div>
              )}

              {generatedMessage ? (
                <div className="space-y-4">
                  <div className="bg-slate-900/80 p-6 rounded-xl border border-purple-500/30 min-h-[300px]">
                    <p className="text-white text-lg leading-relaxed whitespace-pre-wrap">
                      {generatedMessage}
                    </p>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={handleCopyToClipboard}
                      className="flex-1 bg-gradient-to-r from-green-500 to-emerald-600 text-white py-3 px-6 rounded-xl font-bold hover:scale-105 transition-transform"
                    >
                      {copied ? '✓ Copied!' : '📋 Copy to Clipboard'}
                    </button>
                    <button
                      onClick={handleGenerateMessage}
                      className="flex-1 bg-gradient-to-r from-blue-500 to-cyan-600 text-white py-3 px-6 rounded-xl font-bold hover:scale-105 transition-transform"
                    >
                      🔄 Regenerate
                    </button>
                  </div>

                  <div className="bg-gradient-to-r from-yellow-500/10 to-pink-500/10 border border-yellow-500/30 p-4 rounded-xl">
                    <p className="text-yellow-200 text-sm">
                      💡 <strong>Tip:</strong> Personalize this message before sending! Add specific details or adjust the tone to match your style.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-[400px] text-gray-400">
                  <svg className="w-24 h-24 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                  <p className="text-lg">Your AI-generated message will appear here</p>
                  <p className="text-sm mt-2">Select a person, choose your tone, and hit generate!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageComposer;

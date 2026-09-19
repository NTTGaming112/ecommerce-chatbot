import { useState, useRef, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const CUSTOMERS = [
  { id: 'cust_001', name: 'Nguyen Van An', loyalty: 'Gold', city: 'HCM' },
  { id: 'cust_002', name: 'Tran Thi Binh', loyalty: 'Silver', city: 'Ha Noi' },
  { id: 'cust_003', name: 'Le Minh Canh', loyalty: 'Platinum', city: 'Da Nang' },
  { id: 'cust_004', name: 'Pham Thu Dung', loyalty: 'Bronze', city: 'Hai Phong' },
  { id: 'cust_005', name: 'Hoang Duc Em', loyalty: 'Gold', city: 'Can Tho' },
];

const QUICK_ACTIONS = [
  { label: 'Tim san pham', icon: '🛍️', message: 'Xem san pham' },
  { label: 'Theo doi don hang', icon: '📦', message: 'Don hang cua toi' },
  { label: 'Tra hang', icon: '🔄', message: 'Muon tra hang' },
  { label: 'Ho tro ky thuat', icon: '🔧', message: 'Can ho tro ky thuat' },
];

// Simple markdown renderer
function renderMarkdown(text: string): JSX.Element[] {
  const lines = text.split('\n');
  return lines.map((line, i) => {
    // Bold: **text**
    let parts: JSX.Element[] = [];
    const boldRegex = /\*\*(.*?)\*\*/g;
    let lastIndex = 0;
    let match;
    while ((match = boldRegex.exec(line)) !== null) {
      if (match.index > lastIndex) {
        parts.push(<span key={`t${lastIndex}`}>{line.slice(lastIndex, match.index)}</span>);
      }
      parts.push(<strong key={`b${match.index}`} className="font-semibold text-white">{match[1]}</strong>);
      lastIndex = boldRegex.lastIndex;
    }
    if (lastIndex < line.length) {
      parts.push(<span key={`e${lastIndex}`}>{line.slice(lastIndex)}</span>);
    }

    // Bullet points starting with - or •
    if (/^\s*[-•]\s/.test(line)) {
      const bulletContent = line.replace(/^\s*[-•]\s*/, '');
      // Process bold within bullet content
      const bParts: JSX.Element[] = [];
      let bi = 0;
      let bm;
      const bRe = /\*\*(.*?)\*\*/g;
      while ((bm = bRe.exec(bulletContent)) !== null) {
        if (bm.index > bi) bParts.push(<span key={'b'+bi}>{bulletContent.slice(bi, bm.index)}</span>);
        bParts.push(<strong key={'bb'+bm.index} className="font-semibold text-white">{bm[1]}</strong>);
        bi = bRe.lastIndex;
      }
      if (bi < bulletContent.length) bParts.push(<span key={'be'+bi}>{bulletContent.slice(bi)}</span>);
      return (
        <div key={i} className="flex gap-2 ml-2">
          <span className="text-blue-400 shrink-0">•</span>
          <span>{bParts.length > 0 ? bParts : bulletContent}</span>
        </div>
      );
    }

    // Numbered items like "1. " "2. "
    if (/^\s*\d+\.\s/.test(line)) {
      const num = line.match(/^\s*(\d+)\.\s/)?.[1] || '';
      const content = line.replace(/^\s*\d+\.\s*/, '');
      // Process bold within the content
      const contentParts: JSX.Element[] = [];
      let ci = 0;
      let cm;
      const cbRe = /\*\*(.*?)\*\*/g;
      while ((cm = cbRe.exec(content)) !== null) {
        if (cm.index > ci) contentParts.push(<span key={'c'+ci}>{content.slice(ci, cm.index)}</span>);
        contentParts.push(<strong key={'cb'+cm.index} className="font-semibold text-white">{cm[1]}</strong>);
        ci = cbRe.lastIndex;
      }
      if (ci < content.length) contentParts.push(<span key={'ce'+ci}>{content.slice(ci)}</span>);
      return (
        <div key={i} className="flex gap-2 ml-2">
          <span className="text-blue-400 font-semibold shrink-0">{num}.</span>
          <span>{contentParts.length > 0 ? contentParts : content}</span>
        </div>
      );
    }

    // Empty line
    if (line.trim() === '') {
      return <div key={i} className="h-2" />;
    }

    return <div key={i}>{parts.length > 0 ? parts : line}</div>;
  });
}

function LoginScreen({ onLogin }: { onLogin: (customerId: string, name: string) => void }) {
  const [selected, setSelected] = useState(CUSTOMERS[0].id);

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-2xl p-8 w-full max-w-md border border-slate-700 shadow-2xl">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white">AI Customer Support</h1>
          <p className="text-slate-400 mt-2">He thong ho tro da phuong tien</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Chon khach hang</label>
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              className="w-full bg-slate-900 border border-slate-600 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              {CUSTOMERS.map(c => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.id}) - {c.loyalty} - {c.city}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => {
              const c = CUSTOMERS.find(c => c.id === selected)!;
              onLogin(c.id, c.name);
            }}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-xl transition-colors"
          >
            Dang nhap voi {CUSTOMERS.find(c => c.id === selected)?.name}
          </button>
        </div>

        <div className="mt-6 text-center text-xs text-slate-500">
          Demo mode - Chon khach hang de bat dau chat
        </div>
      </div>
    </div>
  );
}

function ChatApp({ customerId, customerName, onLogout }: { customerId: string; customerName: string; onLogout: () => void }) {
  const [messages, setMessages] = useState<{role: 'user' | 'bot', content: string}[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => { scrollToBottom(); }, [messages]);

  const handleSend = async (message: string) => {
    if (!message.trim()) return;
    setInputMessage('');
    setShowQuickActions(false);
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    setIsTyping(true);
    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: customerId, question: message }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to get answer');
      setMessages(prev => [...prev, { role: 'bot', content: data.answer }]);
    } catch (error: any) {
      setMessages(prev => [...prev, { role: 'bot', content: `Error: ${error.message}` }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend(inputMessage);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 flex flex-col md:flex-row">
      {/* Sidebar */}
      <div className="w-full md:w-80 bg-slate-800 border-b md:border-b-0 md:border-r border-slate-700 p-6 flex flex-col shrink-0">
        <div className="mb-6">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            AI Support
          </h1>
          <p className="text-sm text-slate-400 mt-1">Multi-Agent System</p>
        </div>

        {/* Customer Info */}
        <div className="bg-slate-700/50 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
              {customerName.charAt(0)}
            </div>
            <div>
              <p className="font-medium text-white">{customerName}</p>
              <p className="text-xs text-slate-400">{customerId}</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="mt-3 w-full text-xs text-slate-400 hover:text-red-400 transition-colors"
          >
            Dang xuat
          </button>
        </div>

        {/* Quick Actions Sidebar */}
        <div className="mb-6">
          <h2 className="text-sm font-semibold mb-3 text-slate-400 uppercase tracking-wider">Thao tac nhanh</h2>
          <div className="space-y-2">
            {QUICK_ACTIONS.map((action, i) => (
              <button
                key={i}
                onClick={() => handleSend(action.message)}
                className="w-full text-left bg-slate-700/50 hover:bg-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-300 hover:text-white transition-colors flex items-center gap-2"
              >
                <span>{action.icon}</span>
                <span>{action.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Knowledge Base Upload */}
        <div className="flex-1">
          <h2 className="text-sm font-semibold mb-3 text-slate-400 uppercase tracking-wider">Knowledge Base</h2>
          <div
            className="border-2 border-dashed border-slate-600 rounded-xl p-4 text-center hover:border-blue-500 hover:bg-slate-700/50 transition-all cursor-pointer group"
            onClick={() => fileInputRef.current?.click()}
          >
            <input type="file" ref={fileInputRef} className="hidden" accept=".pdf,.txt,.docx" onChange={(e) => {
              // placeholder
            }} />
            <svg className="w-8 h-8 text-slate-500 mx-auto mb-2 group-hover:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-xs font-medium text-slate-300">Tai len tai lieu</p>
            <p className="text-xs text-slate-500 mt-1">PDF, DOCX, TXT</p>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col max-h-screen">
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-6">
              <div className="w-20 h-20 bg-slate-800 rounded-3xl flex items-center justify-center">
                <svg className="w-10 h-10 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div className="text-center">
                <p className="text-xl text-slate-300">Xin chao {customerName}!</p>
                <p className="text-sm text-slate-500 mt-2">Toi co the giup ban gi?</p>
              </div>
              {/* Quick action cards in welcome */}
              <div className="grid grid-cols-2 gap-3 max-w-md">
                {QUICK_ACTIONS.map((action, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(action.message)}
                    className="bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-blue-500/50 rounded-xl p-4 text-left transition-all group"
                  >
                    <span className="text-2xl">{action.icon}</span>
                    <p className="text-sm text-slate-300 mt-2 group-hover:text-white transition-colors">{action.label}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'bot' && (
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold mr-2 mt-1 shrink-0">
                    AI
                  </div>
                )}
                <div className={`max-w-[75%] rounded-2xl px-5 py-3 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-sm'
                    : 'bg-slate-800 text-slate-200 rounded-tl-sm border border-slate-700 shadow-sm'
                }`}>
                  {msg.role === 'user' ? (
                    <p>{msg.content}</p>
                  ) : (
                    <div className="space-y-0.5 text-sm leading-relaxed">
                      {renderMarkdown(msg.content)}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {isTyping && (
            <div className="flex justify-start">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold mr-2 mt-1 shrink-0">AI</div>
              <div className="bg-slate-800 rounded-2xl rounded-tl-sm px-5 py-4 border border-slate-700">
                <div className="flex space-x-1.5">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Quick action chips above input */}
        {showQuickActions && messages.length > 0 && (
          <div className="px-4 pb-2 flex gap-2 overflow-x-auto">
            {QUICK_ACTIONS.map((action, i) => (
              <button
                key={i}
                onClick={() => handleSend(action.message)}
                className="shrink-0 bg-slate-800 hover:bg-slate-700 border border-slate-600 hover:border-blue-500/50 rounded-full px-4 py-2 text-sm text-slate-300 hover:text-white transition-all flex items-center gap-1.5"
              >
                <span>{action.icon}</span>
                <span>{action.label}</span>
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="p-4 bg-slate-800/50 border-t border-slate-700 backdrop-blur-sm">
          <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto relative flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Nhap tin nhan..."
              className="flex-1 bg-slate-900 border border-slate-700 rounded-full py-3 pl-5 pr-12 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-slate-200 placeholder-slate-500"
              disabled={isTyping}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isTyping}
              className="p-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-full transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [customerId, setCustomerId] = useState('');
  const [customerName, setCustomerName] = useState('');

  if (!loggedIn) {
    return (
      <LoginScreen onLogin={(id, name) => {
        setCustomerId(id);
        setCustomerName(name);
        setLoggedIn(true);
      }} />
    );
  }

  return (
    <ChatApp
      customerId={customerId}
      customerName={customerName}
      onLogout={() => {
        setLoggedIn(false);
        setCustomerId('');
        setCustomerName('');
      }}
    />
  );
}

export default App;

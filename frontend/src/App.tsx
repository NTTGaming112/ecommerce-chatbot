import { useState, useRef, useEffect, useMemo } from "react";
import type { ReactElement } from "react";

const API_BASE_URL = "http://localhost:8000/api/v1";

interface Customer {
  customer_id: string;
  name: string;
  email?: string;
  phone?: string;
  address?: { street?: string; district?: string; city?: string } | string;
  loyalty_tier: string;
  total_spent?: number;
}

interface OrderItem {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  size?: string;
  color?: string;
}

interface Order {
  order_id: string;
  customer_id: string;
  status: string;
  items: OrderItem[];
  total: number;
  shipping_fee?: number;
  payment_method?: string;
  shipping_address?: { street?: string; district?: string; city?: string } | string;
  tracking_number?: string;
  carrier?: string;
  created_at?: string;
  delivered_at?: string;
  cancelled_at?: string;
  cancel_reason?: string;
  shipping_info?: any;
}

interface Product {
  product_id: string;
  name: string;
  price: number;
  original_price?: number;
  category: string;
  rating?: number;
  review_count?: number;
  description?: string;
  colors?: string[];
  sizes?: string[];
  tags?: string[];
  stock_info?: Record<string, number>;
  in_stock: boolean;
}

interface KBArticle {
  article_id: string;
  title: string;
  category: string;
  slug: string;
  content: string;
  tags?: string[];
  file_path?: string;
}

interface TroubleshootingGuide {
  id: number;
  product_key: string;
  product_name: string;
  symptom: string;
  solutions: string[];
}

interface ChatMessage {
  id: string;
  role: "user" | "bot";
  content: string;
  intent?: string;
  confidence?: number;
  actions_taken?: string[];
  needs_confirmation?: boolean;
  timestamp: string;
}

const DEFAULT_CUSTOMERS: Customer[] = [
  { customer_id: "cust_001", name: "Nguyễn Văn An", loyalty_tier: "gold", total_spent: 5800000, address: "45 Nguyễn Trãi, Quận 1, TP.HCM" },
  { customer_id: "cust_002", name: "Trần Thị Bình", loyalty_tier: "silver", total_spent: 2100000, address: "12 Hoàng Diệu, Ba Đình, Hà Nội" },
  { customer_id: "cust_003", name: "Lê Minh Cảnh", loyalty_tier: "platinum", total_spent: 15200000, address: "78 Trần Phú, Hải Châu, Đà Nẵng" },
  { customer_id: "cust_004", name: "Phạm Thu Dung", loyalty_tier: "bronze", total_spent: 750000, address: "23 Lê Lợi, Ngô Quyền, Hải Phòng" },
  { customer_id: "cust_005", name: "Hoàng Đức Em", loyalty_tier: "gold", total_spent: 4200000, address: "56 3 Tháng 2, Ninh Kiều, Cần Thơ" },
  { customer_id: "cust_006", name: "Vũ Thị Phương", loyalty_tier: "silver", total_spent: 1850000, address: "88 Điện Biên Phủ, Bình Thạnh, TP.HCM" },
  { customer_id: "cust_007", name: "Đỗ Quốc Hùng", loyalty_tier: "platinum", total_spent: 22500000, address: "34 Cầu Giấy, Cầu Giấy, Hà Nội" },
  { customer_id: "cust_008", name: "Ngô Thị Lan", loyalty_tier: "bronze", total_spent: 420000, address: "15 Nguyễn Hữu Thọ, Nhà Bè, TP.HCM" },
];

const QUICK_ACTIONS = [
  { label: "📦 Đơn hàng của tôi", message: "Cho tôi xem các đơn hàng gần nhất của tôi" },
  { label: "🔍 Tra cứu đơn ORD-10001", message: "Tra cứu tình trạng vận chuyển đơn hàng ORD-10001" },
  { label: "🔄 Chính sách đổi trả 30 ngày", message: "Quy định đổi trả hàng trong 30 ngày như thế nào?" },
  { label: "🛍️ Tư vấn áo khoác nam", message: "Tư vấn cho tôi các mẫu áo khoác nam hot hiện nay" },
  { label: "🔧 Sửa lỗi máy lọc nước", message: "Máy lọc nước bị lỗi đèn đỏ nhấp nháy xử lý thế nào?" },
];

function formatCurrency(amount?: number): string {
  if (typeof amount !== "number") return "0 ₫";
  return new Intl.NumberFormat("vi-VN").format(amount) + " ₫";
}

function getTierBadge(tier: string) {
  const t = tier.toLowerCase();
  if (t === "platinum") {
    return <span className="bg-purple-900/60 text-purple-300 border border-purple-500/40 text-xs px-2.5 py-0.5 rounded-full font-semibold">👑 Platinum</span>;
  }
  if (t === "gold") {
    return <span className="bg-amber-900/60 text-amber-300 border border-amber-500/40 text-xs px-2.5 py-0.5 rounded-full font-semibold">🥇 Gold</span>;
  }
  if (t === "silver") {
    return <span className="bg-slate-700/80 text-slate-200 border border-slate-500/40 text-xs px-2.5 py-0.5 rounded-full font-semibold">🥈 Silver</span>;
  }
  return <span className="bg-orange-950/60 text-orange-300 border border-orange-700/40 text-xs px-2.5 py-0.5 rounded-full font-semibold">🥉 Bronze</span>;
}

function getStatusBadge(status: string) {
  const s = status.toLowerCase();
  if (s === "delivered") {
    return <span className="bg-emerald-950/70 text-emerald-400 border border-emerald-500/40 text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1"><span>✓</span> Đã giao hàng</span>;
  }
  if (s === "shipping" || s === "in_transit") {
    return <span className="bg-sky-950/70 text-sky-400 border border-sky-500/40 text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1"><span>🚚</span> Đang giao</span>;
  }
  if (s === "processing" || s === "confirmed") {
    return <span className="bg-amber-950/70 text-amber-400 border border-amber-500/40 text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1"><span>⏳</span> Chờ xử lý</span>;
  }
  if (s === "cancelled") {
    return <span className="bg-rose-950/70 text-rose-400 border border-rose-500/40 text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1"><span>✕</span> Đã hủy</span>;
  }
  return <span className="bg-slate-800 text-slate-300 border border-slate-700 text-xs px-2.5 py-1 rounded-full">{status}</span>;
}

function renderMarkdown(text: string): ReactElement[] {
  const lines = text.split("\n");
  return lines.map((line, i) => {
    let parts: ReactElement[] = [];
    const boldRegex = /\*\*(.*?)\*\*/g;
    let lastIndex = 0;
    let match;
    while ((match = boldRegex.exec(line)) !== null) {
      if (match.index > lastIndex) {
        parts.push(<span key={`t${lastIndex}`}>{line.slice(lastIndex, match.index)}</span>);
      }
      parts.push(
        <strong key={`b${match.index}`} className="font-semibold text-white">
          {match[1]}
        </strong>,
      );
      lastIndex = boldRegex.lastIndex;
    }
    if (lastIndex < line.length) {
      parts.push(<span key={`e${lastIndex}`}>{line.slice(lastIndex)}</span>);
    }

    if (/^\s*[-•]\s/.test(line)) {
      const bulletContent = line.replace(/^\s*[-•]\s*/, "");
      return (
        <div key={i} className="flex gap-2 ml-3 my-0.5">
          <span className="text-blue-400 shrink-0 font-bold">•</span>
          <span>{bulletContent}</span>
        </div>
      );
    }

    if (/^\s*\d+\.\s/.test(line)) {
      const num = line.match(/^\s*(\d+)\.\s/)?.[1] || "";
      const content = line.replace(/^\s*\d+\.\s*/, "");
      return (
        <div key={i} className="flex gap-2 ml-3 my-0.5">
          <span className="text-blue-400 font-semibold shrink-0">{num}.</span>
          <span>{content}</span>
        </div>
      );
    }

    if (line.trim() === "") {
      return <div key={i} className="h-2" />;
    }

    return <div key={i} className="my-0.5">{parts.length > 0 ? parts : line}</div>;
  });
}

export function App() {
  const [activeTab, setActiveTab] = useState<"chat" | "orders" | "products" | "kb" | "tech">("chat");
  const [customers, setCustomers] = useState<Customer[]>(DEFAULT_CUSTOMERS);
  const [currentCustomer, setCurrentCustomer] = useState<Customer>(DEFAULT_CUSTOMERS[0]);
  const [customerOrders, setCustomerOrders] = useState<Order[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [kbArticles, setKbArticles] = useState<KBArticle[]>([]);
  const [troubleshooting, setTroubleshooting] = useState<TroubleshootingGuide[]>([]);

  // Search and filter states
  const [productSearch, setProductSearch] = useState("");
  const [productCategory, setProductCategory] = useState("all");
  const [kbSearch, setKbSearch] = useState("");
  const [kbCategory, setKbCategory] = useState("all");

  // Chat states
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [activePendingConfirmation, setActivePendingConfirmation] = useState(false);

  // Status & toast
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isSyncingKb, setIsSyncingKb] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Load initial backend data
  useEffect(() => {
    fetch(`${API_BASE_URL}/customers`)
      .then((res) => res.json())
      .then((data) => {
        if (data.customers && data.customers.length > 0) {
          setCustomers(data.customers);
          setCurrentCustomer(data.customers[0]);
        }
      })
      .catch((err) => console.log("Using default demo customers:", err));

    fetch(`${API_BASE_URL}/products`)
      .then((res) => res.json())
      .then((data) => {
        if (data.products) setProducts(data.products);
      })
      .catch((err) => console.log("Failed to load products:", err));

    fetch(`${API_BASE_URL}/kb-articles`)
      .then((res) => res.json())
      .then((data) => {
        if (data.articles) setKbArticles(data.articles);
      })
      .catch((err) => console.log("Failed to load KB:", err));

    fetch(`${API_BASE_URL}/troubleshooting`)
      .then((res) => res.json())
      .then((data) => {
        if (data.guides) setTroubleshooting(data.guides);
      })
      .catch((err) => console.log("Failed to load troubleshooting:", err));
  }, []);

  // Fetch orders when currentCustomer changes
  useEffect(() => {
    if (!currentCustomer?.customer_id) return;
    fetch(`${API_BASE_URL}/orders/${currentCustomer.customer_id}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.orders) setCustomerOrders(data.orders);
      })
      .catch((err) => console.log("Failed to fetch customer orders:", err));
  }, [currentCustomer]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Send message to Multi-Agent API
  const handleSend = async (messageText: string) => {
    if (!messageText.trim()) return;
    setActivePendingConfirmation(false);
    const userMsg: ChatMessage = {
      id: "u-" + Date.now(),
      role: "user",
      content: messageText,
      timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputMessage("");
    setIsTyping(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: currentCustomer.customer_id,
          message: messageText,
          session_id: currentCustomer.customer_id,
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Không thể kết nối đến máy chủ");

      const botMsg: ChatMessage = {
        id: "b-" + Date.now(),
        role: "bot",
        content: data.answer,
        intent: data.intent,
        confidence: data.confidence,
        actions_taken: data.actions_taken,
        needs_confirmation: data.needs_confirmation,
        timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, botMsg]);
      setActivePendingConfirmation(Boolean(data.needs_confirmation));

      // Refresh orders in case an order was updated/cancelled
      if (data.intent === "order_cancellation" || data.intent === "cancel_order" || data.intent === "return_request") {
        fetch(`${API_BASE_URL}/orders/${currentCustomer.customer_id}`)
          .then((r) => r.json())
          .then((d) => d.orders && setCustomerOrders(d.orders));
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: "err-" + Date.now(),
        role: "bot",
        content: `⚠️ Lỗi: ${err.message}. Vui lòng thử lại.`,
        timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const triggerChatAction = (msg: string) => {
    setActiveTab("chat");
    handleSend(msg);
  };

  const handleSyncKB = async () => {
    setIsSyncingKb(true);
    try {
      const res = await fetch(`${API_BASE_URL}/ingest/sync-kb`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        showToast(`✅ ${data.message || "Đồng bộ Knowledge Base thành công!"}`);
      } else {
        throw new Error(data.detail || "Thất bại");
      }
    } catch (e: any) {
      showToast(`❌ Lỗi đồng bộ KB: ${e.message}`);
    } finally {
      setIsSyncingKb(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    showToast(`Đang tải lên và nạp vector cho: ${file.name}...`);
    try {
      const res = await fetch(`${API_BASE_URL}/ingest/file`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        showToast(`✅ Đã nạp tài liệu thành công: ${file.name}`);
      } else {
        throw new Error(data.detail || "Không thể xử lý file");
      }
    } catch (err: any) {
      showToast(`❌ Lỗi upload: ${err.message}`);
    }
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // Filtered Products
  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      const matchSearch = productSearch === "" ||
        p.name.toLowerCase().includes(productSearch.toLowerCase()) ||
        p.category.toLowerCase().includes(productSearch.toLowerCase()) ||
        (p.tags && p.tags.some((t) => t.toLowerCase().includes(productSearch.toLowerCase())));
      const matchCat = productCategory === "all" || p.category.toLowerCase() === productCategory.toLowerCase();
      return matchSearch && matchCat;
    });
  }, [products, productSearch, productCategory]);

  // Product categories list
  const productCategories = useMemo(() => {
    const set = new Set<string>();
    products.forEach((p) => p.category && set.add(p.category));
    return ["all", ...Array.from(set)];
  }, [products]);

  // Filtered KB Articles
  const filteredKb = useMemo(() => {
    return kbArticles.filter((a) => {
      const matchSearch = kbSearch === "" ||
        a.title.toLowerCase().includes(kbSearch.toLowerCase()) ||
        a.content.toLowerCase().includes(kbSearch.toLowerCase()) ||
        (a.tags && a.tags.some((t) => t.toLowerCase().includes(kbSearch.toLowerCase())));
      const matchCat = kbCategory === "all" || a.category.toLowerCase() === kbCategory.toLowerCase();
      return matchSearch && matchCat;
    });
  }, [kbArticles, kbSearch, kbCategory]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-5 right-5 z-50 bg-slate-800 text-white px-5 py-3 rounded-xl shadow-2xl border border-slate-600 flex items-center gap-3 animate-slide-in">
          <span className="text-blue-400">ℹ️</span>
          <span className="text-sm font-medium">{toastMessage}</span>
          <button onClick={() => setToastMessage(null)} className="text-slate-400 hover:text-white text-xs ml-2">✕</button>
        </div>
      )}

      {/* Top Header */}
      <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40 px-4 md:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-sky-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <span className="text-xl">🛍️</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-lg text-white tracking-tight">StyleHub</h1>
              <span className="bg-blue-600/30 text-blue-400 border border-blue-500/30 text-[11px] font-semibold px-2 py-0.5 rounded-full">Multi-Agent AI</span>
            </div>
            <p className="text-xs text-slate-400">Relational DB & Vector RAG Assistant</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center bg-slate-800/80 p-1 rounded-xl border border-slate-700/60 overflow-x-auto">
          <button
            onClick={() => setActiveTab("chat")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeTab === "chat" ? "bg-blue-600 text-white shadow-md" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span>💬</span>
            <span>Trợ lý AI</span>
            {messages.length > 0 && <span className="bg-blue-400/30 text-[10px] px-1.5 py-0.2 rounded-full">{messages.length}</span>}
          </button>

          <button
            onClick={() => setActiveTab("orders")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeTab === "orders" ? "bg-blue-600 text-white shadow-md" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span>📦</span>
            <span>Đơn hàng</span>
            {customerOrders.length > 0 && <span className="bg-sky-500/30 text-[10px] px-1.5 py-0.2 rounded-full font-mono">{customerOrders.length}</span>}
          </button>

          <button
            onClick={() => setActiveTab("products")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeTab === "products" ? "bg-blue-600 text-white shadow-md" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span>🛍️</span>
            <span>Sản phẩm</span>
            <span className="bg-slate-700 text-[10px] px-1.5 py-0.2 rounded-full text-slate-300 font-mono">{products.length || 16}</span>
          </button>

          <button
            onClick={() => setActiveTab("kb")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeTab === "kb" ? "bg-blue-600 text-white shadow-md" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span>📚</span>
            <span>Chính sách & KB</span>
          </button>

          <button
            onClick={() => setActiveTab("tech")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeTab === "tech" ? "bg-blue-600 text-white shadow-md" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span>🔧</span>
            <span>Kỹ thuật</span>
          </button>
        </nav>

        {/* Customer Selector */}
        <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700/60">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
            {currentCustomer.name.charAt(0)}
          </div>
          <div className="text-left">
            <div className="flex items-center gap-1.5">
              <select
                value={currentCustomer.customer_id}
                onChange={(e) => {
                  const c = customers.find((cust) => cust.customer_id === e.target.value);
                  if (c) {
                    setCurrentCustomer(c);
                    showToast(`Đã đổi khách hàng: ${c.name} (${c.loyalty_tier.toUpperCase()})`);
                  }
                }}
                className="bg-transparent text-xs font-semibold text-white focus:outline-none cursor-pointer pr-1"
              >
                {customers.map((c) => (
                  <option key={c.customer_id} value={c.customer_id} className="bg-slate-800 text-slate-100">
                    {c.name} ({c.loyalty_tier})
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-1">
              {getTierBadge(currentCustomer.loyalty_tier)}
              <span className="text-[11px] text-slate-400 font-mono">
                Chi tiêu: {formatCurrency(currentCustomer.total_spent)}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden">
        {/* ======================= TAB 1: AI CHAT ======================= */}
        {activeTab === "chat" && (
          <div className="flex-1 flex flex-col md:flex-row h-[calc(100vh-65px)]">
            {/* Chat Sidebar: Context & Actions */}
            <div className="w-full md:w-80 bg-slate-900/90 border-r border-slate-800 p-5 flex flex-col justify-between shrink-0 overflow-y-auto">
              <div className="space-y-6">
                {/* Active Profile Info */}
                <div className="bg-slate-800/60 rounded-2xl p-4 border border-slate-700/50">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center font-bold text-white text-sm">
                      {currentCustomer.name.charAt(0)}
                    </div>
                    <div>
                      <h2 className="text-sm font-bold text-white">{currentCustomer.name}</h2>
                      <p className="text-xs text-slate-400 font-mono">{currentCustomer.customer_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-300 pt-2 border-t border-slate-700/50">
                    <span>Hạng thành viên:</span>
                    {getTierBadge(currentCustomer.loyalty_tier)}
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-300 pt-1">
                    <span>Đơn hàng gần đây:</span>
                    <span className="font-semibold text-sky-400">{customerOrders.length} đơn</span>
                  </div>
                  <button
                    onClick={() => setActiveTab("orders")}
                    className="mt-3 w-full bg-slate-700/50 hover:bg-slate-700 text-slate-200 text-xs py-1.5 px-3 rounded-lg transition-colors border border-slate-600/50 flex items-center justify-center gap-1"
                  >
                    <span>📦 Xem lịch sử đơn</span>
                  </button>
                </div>

                {/* Quick Prompts */}
                <div>
                  <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5">
                    Gợi ý câu hỏi nhanh
                  </h3>
                  <div className="space-y-2">
                    {QUICK_ACTIONS.map((action, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(action.message)}
                        className="w-full text-left bg-slate-800/50 hover:bg-slate-800 hover:border-blue-500/50 border border-slate-700/60 rounded-xl p-2.5 text-xs text-slate-300 hover:text-white transition-all"
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Agent Ecosystem Info */}
                <div className="bg-slate-900 rounded-xl p-3 border border-slate-800 text-[11px] text-slate-400 space-y-1.5">
                  <div className="font-semibold text-slate-300 flex items-center gap-1.5">
                    <span>🤖</span> Multi-Agent Pipeline
                  </div>
                  <div className="grid grid-cols-2 gap-1 text-[10px]">
                    <span className="bg-slate-800 px-1.5 py-0.5 rounded text-blue-300">OrderAgent</span>
                    <span className="bg-slate-800 px-1.5 py-0.5 rounded text-emerald-300">BillingAgent</span>
                    <span className="bg-slate-800 px-1.5 py-0.5 rounded text-amber-300">RefundAgent</span>
                    <span className="bg-slate-800 px-1.5 py-0.5 rounded text-indigo-300">ProductAgent</span>
                    <span className="bg-slate-800 px-1.5 py-0.5 rounded text-purple-300">TechSupport</span>
                    <span className="bg-slate-800 px-1.5 py-0.5 rounded text-rose-300">AnswerAgent</span>
                  </div>
                </div>
              </div>

              {/* Fast KB Sync Action */}
              <div className="pt-4 border-t border-slate-800">
                <button
                  onClick={handleSyncKB}
                  disabled={isSyncingKb}
                  className="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-2 px-3 rounded-xl border border-slate-700 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                >
                  <span className={isSyncingKb ? "animate-spin" : ""}>🔄</span>
                  <span>{isSyncingKb ? "Đang đồng bộ..." : "Đồng bộ Vector DB"}</span>
                </button>
              </div>
            </div>

            {/* Chat Thread */}
            <div className="flex-1 flex flex-col justify-between bg-slate-950">
              {/* Message List */}
              <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-5">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-3xl shadow-xl shadow-blue-500/20">
                      🤖
                    </div>
                    <div className="max-w-md">
                      <h2 className="text-xl font-bold text-white">Xin chào {currentCustomer.name}!</h2>
                      <p className="text-sm text-slate-400 mt-1.5">
                        Tôi là trợ lý AI StyleHub, được trang bị hệ thống Multi-Agent truy cập trực tiếp Relational Database và Vector Knowledge Base.
                      </p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-w-lg w-full text-left">
                      {QUICK_ACTIONS.slice(0, 4).map((qa, i) => (
                        <button
                          key={i}
                          onClick={() => handleSend(qa.message)}
                          className="p-3 bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-blue-500/40 rounded-xl transition-all group"
                        >
                          <p className="text-xs font-medium text-slate-300 group-hover:text-white">{qa.label}</p>
                          <p className="text-[11px] text-slate-500 mt-0.5 truncate">{qa.message}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                      {msg.role === "bot" && (
                        <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center text-white text-xs font-bold mr-2.5 mt-1 shrink-0 shadow-md">
                          AI
                        </div>
                      )}
                      <div
                        className={`max-w-[85%] md:max-w-[75%] rounded-2xl p-4 ${
                          msg.role === "user"
                            ? "bg-blue-600 text-white rounded-tr-sm shadow-md"
                            : "bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-sm shadow-md"
                        }`}
                      >
                        <div className="text-sm leading-relaxed space-y-1">
                          {renderMarkdown(msg.content)}
                        </div>

                        {/* Interactive Confirmation Banner */}
                        {msg.needs_confirmation && (
                          <div className="mt-3.5 pt-3 border-t border-amber-500/30 bg-amber-950/40 -mx-4 -mb-4 p-3 rounded-b-2xl">
                            <div className="flex items-center gap-2 text-amber-300 text-xs font-semibold mb-2">
                              <span>⚠️</span>
                              <span>Yêu cầu xác nhận thao tác quan trọng</span>
                            </div>
                            <p className="text-[11px] text-amber-200/80 mb-3">
                              Hành động này sẽ thay đổi trạng thái trong hệ thống (Hủy đơn hàng hoặc Tạo yêu cầu trả hàng). Vui lòng chọn:
                            </p>
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => handleSend("Xác nhận")}
                                className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold py-2 px-3 rounded-lg shadow transition-all flex items-center justify-center gap-1"
                              >
                                <span>✅</span>
                                <span>Đồng ý / Xác nhận</span>
                              </button>
                              <button
                                onClick={() => handleSend("Hủy")}
                                className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold py-2 px-3 rounded-lg border border-slate-600 transition-all flex items-center justify-center gap-1"
                              >
                                <span>❌</span>
                                <span>Hủy bỏ</span>
                              </button>
                            </div>
                          </div>
                        )}

                        {/* Metadata pills */}
                        {msg.role === "bot" && (msg.intent || msg.actions_taken) && (
                          <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex flex-wrap items-center gap-1.5 text-[10px] text-slate-400">
                            {msg.intent && (
                              <span className="bg-slate-800 px-2 py-0.5 rounded-full border border-slate-700 text-slate-300">
                                Ý định: <strong>{msg.intent}</strong>
                              </span>
                            )}
                            {msg.confidence !== undefined && (
                              <span className="bg-slate-800 px-2 py-0.5 rounded-full border border-slate-700 text-slate-300">
                                Độ tin cậy: {(msg.confidence * 100).toFixed(0)}%
                              </span>
                            )}
                            {msg.actions_taken && msg.actions_taken.length > 0 && (
                              <div className="flex items-center gap-1">
                                <span>Agents:</span>
                                {msg.actions_taken.map((act, i) => (
                                  <span key={i} className="bg-blue-950/80 text-blue-300 border border-blue-800/60 px-1.5 py-0.5 rounded">
                                    {act}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}

                {/* Typing animation */}
                {isTyping && (
                  <div className="flex items-center gap-2 text-slate-400 text-xs">
                    <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center text-white text-xs font-bold mr-1 shrink-0">
                      AI
                    </div>
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" />
                      <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce [animation-delay:0.2s]" />
                      <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce [animation-delay:0.4s]" />
                      <span className="text-xs text-slate-400 ml-2">Agents đang xử lý...</span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Input Bar */}
              <div className="p-4 bg-slate-900/80 border-t border-slate-800 backdrop-blur-sm space-y-2.5">
                {activePendingConfirmation && (
                  <div className="max-w-4xl mx-auto bg-amber-950/70 border border-amber-500/50 rounded-xl p-2.5 px-4 flex flex-wrap items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-2 text-amber-300">
                      <span>⚠️</span>
                      <span className="font-semibold">Hệ thống đang chờ xác nhận:</span>
                      <span className="text-amber-200">Bạn muốn tiếp tục hay hủy bỏ yêu cầu này?</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => handleSend("Xác nhận")}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-3 py-1 rounded-lg transition-all"
                      >
                        ✅ Xác nhận
                      </button>
                      <button
                        type="button"
                        onClick={() => handleSend("Hủy")}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 font-semibold px-3 py-1 rounded-lg transition-all"
                      >
                        ❌ Hủy bỏ
                      </button>
                    </div>
                  </div>
                )}
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSend(inputMessage);
                  }}
                  className="max-w-4xl mx-auto flex items-center gap-2"
                >
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={`Hỏi về đơn hàng, đổi trả, tư vấn sản phẩm cho ${currentCustomer.name}...`}
                    disabled={isTyping}
                    className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                  />
                  <button
                    type="submit"
                    disabled={!inputMessage.trim() || isTyping}
                    className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl text-sm font-semibold transition-all shadow-md shadow-blue-600/20 flex items-center gap-1.5 shrink-0"
                  >
                    <span>Gửi</span>
                    <span>➔</span>
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* ======================= TAB 2: MY ORDERS ======================= */}
        {activeTab === "orders" && (
          <div className="flex-1 overflow-y-auto p-6 md:p-10 max-w-6xl mx-auto w-full space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div>
                <h2 className="text-2xl font-extrabold text-white">Đơn hàng của {currentCustomer.name}</h2>
                <p className="text-sm text-slate-400 mt-1">Dữ liệu đơn hàng thực tế từ Relational Database SQLite</p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => triggerChatAction("Cho tôi xem tất cả các đơn hàng của tôi")}
                  className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-all shadow"
                >
                  💬 Hỏi AI về đơn hàng
                </button>
              </div>
            </div>

            {customerOrders.length === 0 ? (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center">
                <span className="text-4xl">📦</span>
                <p className="text-base font-semibold text-white mt-3">Chưa có đơn hàng nào</p>
                <p className="text-xs text-slate-400 mt-1">Khách hàng {currentCustomer.name} chưa đặt đơn nào trong hệ thống.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-5">
                {customerOrders.map((order) => (
                  <div key={order.order_id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all space-y-4">
                    {/* Header */}
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                      <div className="flex items-center gap-3">
                        <span className="text-base font-bold text-white font-mono">{order.order_id}</span>
                        {getStatusBadge(order.status)}
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-slate-400">Tổng tiền: </span>
                        <span className="text-base font-extrabold text-blue-400 font-mono">{formatCurrency(order.total)}</span>
                      </div>
                    </div>

                    {/* Items List */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sản phẩm trong đơn</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {order.items?.map((it, idx) => (
                          <div key={idx} className="bg-slate-850/80 p-2.5 rounded-xl border border-slate-800/80 flex items-center justify-between text-xs">
                            <div>
                              <p className="font-semibold text-slate-200">{it.name}</p>
                              <p className="text-[11px] text-slate-400">
                                SL: {it.quantity} {it.size ? `| Size: ${it.size}` : ""} {it.color ? `| Màu: ${it.color}` : ""}
                              </p>
                            </div>
                            <span className="font-mono text-slate-300 font-medium">{formatCurrency(it.price)}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Shipping info */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs bg-slate-850/40 p-3 rounded-xl border border-slate-800/60">
                      <div>
                        <span className="text-slate-400">Mã vận đơn: </span>
                        <span className="font-mono font-semibold text-sky-400">{order.tracking_number || "Chưa có"}</span>
                        {order.carrier && <span className="text-slate-400 ml-1">({order.carrier})</span>}
                      </div>
                      <div>
                        <span className="text-slate-400">Địa chỉ giao: </span>
                        <span className="text-slate-200">
                          {typeof order.shipping_address === "string"
                            ? order.shipping_address
                            : `${order.shipping_address?.street || ""}, ${order.shipping_address?.district || ""}, ${order.shipping_address?.city || ""}`}
                        </span>
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex flex-wrap items-center gap-2 pt-2">
                      <button
                        onClick={() => triggerChatAction(`Tra cứu tình trạng vận chuyển đơn hàng ${order.order_id}`)}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-700 transition-colors flex items-center gap-1"
                      >
                        <span>🔍</span>
                        <span>Tra cứu trạng thái</span>
                      </button>

                      {order.status !== "cancelled" && (
                        <button
                          onClick={() => triggerChatAction(`Tôi muốn hủy đơn hàng ${order.order_id}`)}
                          className="bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-700/50 text-xs font-medium px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1"
                        >
                          <span>✕</span>
                          <span>Hủy đơn hàng</span>
                        </button>
                      )}

                      <button
                        onClick={() => triggerChatAction(`Tôi muốn đổi trả sản phẩm trong đơn ${order.order_id}`)}
                        className="bg-amber-950/40 hover:bg-amber-900/60 text-amber-300 border border-amber-700/50 text-xs font-medium px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1"
                      >
                        <span>🔄</span>
                        <span>Yêu cầu đổi trả</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ======================= TAB 3: PRODUCTS ======================= */}
        {activeTab === "products" && (
          <div className="flex-1 overflow-y-auto p-6 md:p-10 max-w-6xl mx-auto w-full space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div>
                <h2 className="text-2xl font-extrabold text-white">Danh mục sản phẩm StyleHub</h2>
                <p className="text-sm text-slate-400 mt-1">Sản phẩm thời trang, công nghệ và gia dụng được quản lý trong Relational DB</p>
              </div>
              <div className="flex items-center gap-2 w-full md:w-auto">
                <input
                  type="text"
                  placeholder="Tìm kiếm sản phẩm..."
                  value={productSearch}
                  onChange={(e) => setProductSearch(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 w-full md:w-64"
                />
              </div>
            </div>

            {/* Category Filter Chips */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1">
              {productCategories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setProductCategory(cat)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                    productCategory === cat
                      ? "bg-blue-600 text-white"
                      : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-white"
                  }`}
                >
                  {cat === "all" ? "Tất cả" : cat}
                </button>
              ))}
            </div>

            {/* Product Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredProducts.map((p) => (
                <div key={p.product_id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4">
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-md font-mono">{p.category}</span>
                      {p.in_stock ? (
                        <span className="text-[11px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded-full font-medium">Còn hàng</span>
                      ) : (
                        <span className="text-[11px] text-rose-400 bg-rose-950/60 border border-rose-800/40 px-2 py-0.5 rounded-full font-medium">Hết hàng</span>
                      )}
                    </div>
                    <h3 className="text-base font-bold text-white line-clamp-1">{p.name}</h3>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">{p.description}</p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-baseline gap-2">
                      <span className="text-lg font-extrabold text-blue-400 font-mono">{formatCurrency(p.price)}</span>
                      {p.original_price && p.original_price > p.price && (
                        <span className="text-xs text-slate-500 line-through font-mono">{formatCurrency(p.original_price)}</span>
                      )}
                    </div>

                    {/* Color & Size tags */}
                    <div className="flex flex-wrap gap-1 text-[10px]">
                      {p.colors?.map((c, i) => (
                        <span key={i} className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">{c}</span>
                      ))}
                      {p.sizes?.map((s, i) => (
                        <span key={i} className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">{s}</span>
                      ))}
                    </div>

                    {/* AI Triggers */}
                    <div className="flex items-center gap-2 pt-2 border-t border-slate-800">
                      <button
                        onClick={() => triggerChatAction(`Tư vấn cho tôi về sản phẩm ${p.name}, còn các màu và size nào?`)}
                        className="flex-1 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2 px-3 rounded-xl transition-all shadow"
                      >
                        💬 Hỏi AI tư vấn
                      </button>
                      <button
                        onClick={() => triggerChatAction(`Sản phẩm ${p.name} có chính sách bảo hành và đổi trả thế nào?`)}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-2 px-3 rounded-xl border border-slate-700 transition-all"
                        title="Hỏi về bảo hành / đổi trả"
                      >
                        🛡️
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ======================= TAB 4: KNOWLEDGE BASE ======================= */}
        {activeTab === "kb" && (
          <div className="flex-1 overflow-y-auto p-6 md:p-10 max-w-6xl mx-auto w-full space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div>
                <h2 className="text-2xl font-extrabold text-white">Trung tâm Tri thức & Chính sách (KB)</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Được đồng bộ giữa Relational DB (kb_articles) và Vector DB (ChromaDB)
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleSyncKB}
                  disabled={isSyncingKb}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-md flex items-center gap-2 disabled:opacity-50"
                >
                  <span className={isSyncingKb ? "animate-spin" : ""}>🔄</span>
                  <span>{isSyncingKb ? "Đang đồng bộ Vector DB..." : "⚡ Đồng bộ KB vào ChromaDB"}</span>
                </button>
              </div>
            </div>

            {/* Ingest Document Box */}
            <div className="bg-slate-900 border border-dashed border-slate-700 rounded-2xl p-5 flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-xl">
                  📄
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">Nạp thêm tài liệu vào Vector DB</h4>
                  <p className="text-xs text-slate-400">Hỗ trợ định dạng PDF, DOCX, TXT. Hệ thống sẽ tự động chunk và embed vào ChromaDB.</p>
                </div>
              </div>
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".pdf,.docx,.txt"
                onChange={handleFileUpload}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-4 py-2.5 rounded-xl border border-slate-600 transition-all flex items-center gap-2 shrink-0"
              >
                <span>📤</span>
                <span>Tải lên tài liệu</span>
              </button>
            </div>

            {/* Search & Category Filter */}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                {["all", "policy", "guide", "faq"].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setKbCategory(cat)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium uppercase transition-all ${
                      kbCategory === cat
                        ? "bg-blue-600 text-white"
                        : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-white"
                    }`}
                  >
                    {cat === "all" ? "Tất cả" : cat}
                  </button>
                ))}
              </div>
              <input
                type="text"
                placeholder="Tìm bài viết chính sách..."
                value={kbSearch}
                onChange={(e) => setKbSearch(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 w-full sm:w-64"
              />
            </div>

            {/* Articles List */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredKb.map((art) => (
                <div key={art.article_id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between space-y-3">
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="text-[10px] uppercase font-bold text-blue-400 bg-blue-950/60 border border-blue-800/40 px-2 py-0.5 rounded">
                        {art.category}
                      </span>
                      <span className="text-xs text-slate-500 font-mono">{art.article_id}</span>
                    </div>
                    <h3 className="text-base font-bold text-white">{art.title}</h3>
                    <p className="text-xs text-slate-300 mt-2 line-clamp-4 leading-relaxed">{art.content}</p>
                  </div>

                  <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                    <div className="flex flex-wrap gap-1">
                      {art.tags?.map((t, idx) => (
                        <span key={idx} className="text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                          #{t}
                        </span>
                      ))}
                    </div>
                    <button
                      onClick={() => triggerChatAction(`Tóm tắt và giải thích chi tiết: ${art.title}`)}
                      className="bg-slate-800 hover:bg-slate-700 text-blue-400 hover:text-blue-300 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-700 transition-all flex items-center gap-1 shrink-0"
                    >
                      <span>💬</span>
                      <span>Hỏi AI</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ======================= TAB 5: TECH SUPPORT ======================= */}
        {activeTab === "tech" && (
          <div className="flex-1 overflow-y-auto p-6 md:p-10 max-w-6xl mx-auto w-full space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div>
                <h2 className="text-2xl font-extrabold text-white">Hỗ trợ Kỹ thuật & Khắc phục Sự cố</h2>
                <p className="text-sm text-slate-400 mt-1">Cung cấp giải pháp xử lý sự cố thiết bị điện tử, gia dụng và đồ dùng</p>
              </div>
              <button
                onClick={() => triggerChatAction("Tôi cần kỹ thuật viên hỗ trợ kiểm tra thiết bị")}
                className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow"
              >
                🔧 Mở ticket hỗ trợ kỹ thuật
              </button>
            </div>

            {troubleshooting.length === 0 ? (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center">
                <span className="text-4xl">🔧</span>
                <p className="text-base font-semibold text-white mt-3">Đang cập nhật hướng dẫn kỹ thuật</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {troubleshooting.map((guide) => (
                  <div key={guide.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all space-y-4">
                    <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-3">
                      <div>
                        <span className="text-xs text-blue-400 font-mono uppercase">{guide.product_key}</span>
                        <h3 className="text-base font-bold text-white">{guide.product_name}</h3>
                      </div>
                      <span className="text-2xl">⚙️</span>
                    </div>

                    <div className="space-y-2">
                      <div className="bg-amber-950/40 border border-amber-800/40 p-2.5 rounded-xl">
                        <span className="text-xs font-semibold text-amber-300">Triệu chứng: </span>
                        <span className="text-xs text-amber-200">{guide.symptom}</span>
                      </div>

                      <div className="space-y-1.5 pt-1">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Các bước khắc phục:</p>
                        {guide.solutions?.map((step, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                            <span className="text-blue-400 font-bold shrink-0">{idx + 1}.</span>
                            <span>{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="pt-3 border-t border-slate-800 flex items-center justify-end">
                      <button
                        onClick={() => triggerChatAction(`Tôi gặp lỗi: ${guide.symptom} trên ${guide.product_name}, hãy hướng dẫn tôi từng bước xử lý`)}
                        className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-all shadow flex items-center gap-1.5"
                      >
                        <span>🔧</span>
                        <span>Khắc phục cùng AI</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

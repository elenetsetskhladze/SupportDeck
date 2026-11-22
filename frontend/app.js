const app = document.getElementById("app");

let currentUser = null;
let pollTimer = null;

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text ?? "";
    return div.innerHTML;
}

function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = isError ? "show error" : "show";
    setTimeout(() => (toast.className = ""), 2500);
}

function formatDate(value) {
    const hasZone = /(Z|[+-]\d\d:\d\d)$/.test(value);
    return new Date(hasZone ? value : value + "Z").toLocaleString([], {
        month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
    });
}

function percent(value) {
    return value == null ? "—" : Math.round(value * 100) + "%";
}

const ICON_PATHS = {
    chat: '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
    inbox: '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.5 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.7 4H7.3a2 2 0 0 0-1.8 1.1z"/>',
    ticket: '<path d="M3 9a3 3 0 0 0 0 6v3a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3a3 3 0 0 0 0-6V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2z"/><path d="M13 5v2M13 11v2M13 17v2"/>',
    pen: '<path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    book: '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z"/><path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>',
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    chart: '<path d="M3 3v18h18"/><path d="M7 16v-4M12 16V8M17 16v-7"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    card: '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
    alert: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    sparkle: '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 17l.7 1.8 1.8.7-1.8.7L19 22l-.7-1.8-1.8-.7 1.8-.7z"/>',
    gauge: '<path d="M3 15a9 9 0 0 1 18 0"/><path d="M12 15l4-5"/><circle cx="12" cy="15" r="1"/>',
    doc: '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    up: '<path d="M12 19V5M5 12l7-7 7 7"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    message: '<path d="M4 4h16v12H8l-4 4z"/>',
    logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    trash: '<path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14"/>',
    empty: '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.5 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.7 4H7.3a2 2 0 0 0-1.8 1.1z"/>',
    smile: '<circle cx="12" cy="12" r="9"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/>',
    neutral: '<circle cx="12" cy="12" r="9"/><path d="M8 15h8M9 9h.01M15 9h.01"/>',
    frown: '<circle cx="12" cy="12" r="9"/><path d="M16 16s-1.5-2-4-2-4 2-4 2M9 9h.01M15 9h.01"/>',
    angry: '<circle cx="12" cy="12" r="9"/><path d="M16 16s-1.5-2-4-2-4 2-4 2M8 9l2 1M16 9l-2 1"/>',
    flag: '<path d="M4 22V4M4 4h13l-2 4 2 4H4"/>',
    send: '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>',
    box: '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
    phone: '<rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M11 18h2"/>'
};

function icon(name, size = 16) {
    return `<svg class="icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON_PATHS[name] || ""}</svg>`;
}

const PHONE_COLORS = ["#3A3833", "#7C8F74", "#C9694A", "#3D5A73", "#C8B48E", "#E4DCCB", "#8B5A6B", "#5E6B7A"];

function phoneColor(name) {
    let sum = 0;
    for (const letter of name) sum += letter.charCodeAt(0);
    return PHONE_COLORS[sum % PHONE_COLORS.length];
}

function phoneArt(name, height = 110) {
    const color = phoneColor(name);
    const line = `stroke="#22201C" stroke-width="2"`;
    const lens = (x, y, r = 5) => `<circle cx="${x}" cy="${y}" r="${r}" fill="#22201C"/><circle cx="${x - 1.5}" cy="${y - 1.5}" r="${r / 3}" fill="#6B6457"/>`;
    const big = name.includes("Max") || name.includes("Ultra") || name.includes("+");
    const top = big ? 10 : 18;
    const tall = big ? 140 : 124;
    let body;

    if (name.includes("Fold")) {
        body = `
            <rect x="14" y="22" width="92" height="116" rx="10" fill="${color}" ${line}/>
            <rect x="20" y="28" width="80" height="104" rx="6" fill="#22201C" opacity="0.88"/>
            <line x1="60" y1="22" x2="60" y2="138" stroke="#F6F1E7" stroke-width="1.5" opacity="0.5"/>`;
    } else if (name.includes("Flip")) {
        body = `
            <rect x="30" y="34" width="60" height="92" rx="14" fill="${color}" ${line}/>
            <rect x="36" y="40" width="48" height="40" rx="8" fill="#22201C" opacity="0.88"/>
            <line x1="30" y1="96" x2="90" y2="96" stroke="#22201C" stroke-width="1.5" opacity="0.4"/>
            <circle cx="48" cy="60" r="5" fill="#22201C" stroke="#C9BFA9" stroke-width="1.5"/>
            <circle cx="62" cy="60" r="5" fill="#22201C" stroke="#C9BFA9" stroke-width="1.5"/>`;
    } else if (name.startsWith("Samsung")) {
        const ultra = name.includes("Ultra");
        body = `
            <rect x="32" y="${top}" width="56" height="${tall}" rx="${ultra ? 6 : 12}" fill="${color}" ${line}/>
            ${lens(46, top + 18)}${lens(46, top + 34)}${lens(46, top + 50)}
            ${ultra ? lens(60, top + 26, 3.5) : ""}`;
    } else {
        const pro = name.includes("Pro");
        body = `
            <rect x="32" y="${top}" width="56" height="${tall}" rx="14" fill="${color}" ${line}/>
            <rect x="37" y="${top + 5}" width="${pro ? 30 : 24}" height="${pro ? 30 : 26}" rx="8" fill="#22201C" opacity="0.18"/>
            ${pro ? lens(45, top + 13) + lens(45, top + 27) + lens(59, top + 20) : lens(44, top + 12, 4.5) + lens(55, top + 23, 4.5)}`;
    }

    return `<svg width="${height * 0.75}" height="${height}" viewBox="0 0 120 160" role="img" aria-label="${escapeHtml(name)}">${body}</svg>`;
}

async function api(path, options = {}) {
    const headers = {};
    const token = localStorage.getItem("token");

    if (token) headers["Authorization"] = `Bearer ${token}`;

    let body = options.body;

    if (options.form) {
        headers["Content-Type"] = "application/x-www-form-urlencoded";
        body = new URLSearchParams(options.form);
    } else if (body) {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(body);
    }

    const response = await fetch("/api" + path, { method: options.method || "GET", headers, body });

    if (response.status === 401 && token) {
        logout();
        throw new Error("Session expired, please log in again");
    }

    if (response.status === 204) return null;

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        let message = data?.detail || `Error ${response.status}`;
        if (Array.isArray(message)) message = message.map((e) => e.msg).join(", ");
        throw new Error(message);
    }

    return data;
}

const STATUS_COLORS = {
    new: "", triaging: "blue", awaiting_review: "orange",
    replied: "green", escalated: "red", spam: ""
};

const PRIORITY_COLORS = { low: "", medium: "blue", high: "orange", urgent: "red" };

const STATUS_ICONS = {
    new: "inbox", triaging: "sparkle", awaiting_review: "clock",
    replied: "check", escalated: "up", spam: "trash"
};

const PRIORITY_ICONS = { low: "flag", medium: "flag", high: "alert", urgent: "alert" };

const SENTIMENT_ICONS = { positive: "smile", neutral: "neutral", negative: "frown", angry: "angry" };

function statusBadge(status) {
    const label = (status || "new").replace("_", " ");
    return `<span class="badge ${STATUS_COLORS[status] ?? ""}">${icon(STATUS_ICONS[status] || "inbox", 14)}${escapeHtml(label)}</span>`;
}

function priorityBadge(priority) {
    if (!priority) return "";
    return `<span class="badge ${PRIORITY_COLORS[priority] ?? ""}">${icon(PRIORITY_ICONS[priority] || "flag", 14)}${escapeHtml(priority)}</span>`;
}

function categoryBadge(category) {
    if (!category) return "";
    return `<span class="badge purple">${icon(category === "billing" ? "card" : "ticket", 14)}${escapeHtml(category)}</span>`;
}

function sentimentBadge(sentiment) {
    if (!sentiment) return "";
    return `<span class="badge">${icon(SENTIMENT_ICONS[sentiment] || "neutral", 14)}${escapeHtml(sentiment)}</span>`;
}

function renderAuth(mode = "login") {
    app.innerHTML = `
        <div class="auth-page">
            <div class="card auth-card">
                <div class="logo"><div class="logo-icon">${icon("chat", 18)}</div> <span>SupportDesk<span class="dot">.</span></span></div>
                <p class="subtitle">AI-powered customer support</p>

                <div class="tabs">
                    <button class="${mode === "login" ? "active" : ""}" id="tab-login">Log in</button>
                    <button class="${mode === "register" ? "active" : ""}" id="tab-register">Sign up</button>
                </div>

                <form id="auth-form">
                    ${mode === "register" ? `
                        <div class="field">
                            <label>Full name</label>
                            <input name="full_name" required minlength="2" placeholder="Your name">
                        </div>` : ""}
                    <div class="field">
                        <label>Email</label>
                        <input name="email" type="email" required placeholder="you@example.com">
                    </div>
                    <div class="field">
                        <label>Password</label>
                        <input name="password" type="password" required minlength="6" placeholder="••••••••">
                    </div>
                    <button class="btn full" type="submit">${mode === "login" ? "Log in" : "Create account"}</button>
                </form>
            </div>
        </div>
    `;

    document.getElementById("tab-login").onclick = () => renderAuth("login");
    document.getElementById("tab-register").onclick = () => renderAuth("register");

    document.getElementById("auth-form").onsubmit = async (event) => {
        event.preventDefault();
        const form = Object.fromEntries(new FormData(event.target));

        try {
            if (mode === "register") {
                await api("/auth/register", { method: "POST", body: form });
                showToast("Account created!");
            }

            const data = await api("/auth/login", {
                method: "POST",
                form: { username: form.email, password: form.password }
            });

            localStorage.setItem("token", data.access_token);
            await start();
        } catch (error) {
            showToast(error.message, true);
        }
    };
}

function logout() {
    localStorage.removeItem("token");
    currentUser = null;
    location.hash = "";
    renderAuth();
}

function menuItems() {
    const role = currentUser.role;

    if (role === "costumer") {
        return [
            ["#/shop", "phone", "Shop"],
            ["#/tickets", "ticket", "My tickets"],
            ["#/orders", "box", "My orders"],
            ["#/new", "pen", "New ticket"]
        ];
    }

    const items = [
        ["#/review", "inbox", "Review queue"],
        ["#/workflow", "gauge", "Load workflow"],
        ["#/tickets", "ticket", "All tickets"],
        ["#/orders", "box", "Orders"],
        ["#/kb", "book", "Knowledge base"]
    ];

    if (role === "admin") {
        items.push(["#/users", "users", "Users"]);
        items.push(["#/analytics", "chart", "Analytics"]);
    }

    return items;
}

function renderLayout(content) {
    const hash = location.hash || "#/";

    const links = menuItems().map(([href, iconName, label]) => `
        <a href="${href}" class="${hash.startsWith(href) ? "active" : ""}">${icon(iconName, 18)} ${label}</a>
    `).join("");

    app.innerHTML = `
        <div class="layout">
            <aside class="sidebar">
                <div class="logo"><div class="logo-icon">${icon("chat", 18)}</div> <span>SupportDesk<span class="dot">.</span></span></div>
                <nav class="nav">${links}</nav>
                <div class="user-card">
                    <div class="avatar">${escapeHtml(currentUser.full_name[0].toUpperCase())}</div>
                    <div class="user-info">
                        <div class="name">${escapeHtml(currentUser.full_name)}</div>
                        <div class="role">${escapeHtml(currentUser.role)}</div>
                    </div>
                    <button class="btn secondary small icon-only" id="logout" aria-label="Log out" title="Log out">${icon("logout", 16)}</button>
                </div>
            </aside>
            <main class="main">${content}</main>
        </div>
    `;

    document.getElementById("logout").onclick = logout;
}

function renderLoading() {
    renderLayout(`<div class="empty"><div class="spinner" style="margin: 0 auto"></div></div>`);
}

function ticketRow(ticket) {
    return `
        <div class="ticket-row" data-id="${ticket.id}">
            <div class="id">#${ticket.id}</div>
            <div class="main-info">
                <div class="subject">${escapeHtml(ticket.subject)}</div>
                <div class="summary">${escapeHtml(ticket.ai_summary || ticket.body)}</div>
            </div>
            <div class="badges">
                ${categoryBadge(ticket.category)}
                ${priorityBadge(ticket.priority)}
                ${statusBadge(ticket.status)}
            </div>
            <div class="date">${formatDate(ticket.created_at)}</div>
        </div>
    `;
}

function ticketList(tickets, emptyText) {
    if (!tickets.length) {
        return `<div class="card empty"><div class="empty-icon">${icon("empty", 32)}</div>${emptyText}</div>`;
    }
    return `<div class="card list-card" id="ticket-list">${tickets.map(ticketRow).join("")}</div>`;
}

function makeRowsClickable(linkPrefix) {
    document.querySelectorAll(".ticket-row").forEach((row) => {
        row.onclick = () => (location.hash = linkPrefix + row.dataset.id);
    });
}

async function pageTickets() {
    const isCostumer = currentUser.role === "costumer";
    const params = new URLSearchParams(sessionStorage.getItem("filters") || "");

    const tickets = await api("/tickets/?" + params.toString());

    const filters = isCostumer ? "" : `
        <form class="filters" id="filters">
            <input name="search" placeholder="Search subject or text..." value="${escapeHtml(params.get("search") || "")}">
            <select name="status">
                <option value="">All statuses</option>
                ${["new", "triaging", "awaiting_review", "replied", "escalated", "spam"]
                    .map((s) => `<option ${params.get("status") === s ? "selected" : ""}>${s}</option>`).join("")}
            </select>
            <select name="priority">
                <option value="">All priorities</option>
                ${["low", "medium", "high", "urgent"]
                    .map((p) => `<option ${params.get("priority") === p ? "selected" : ""}>${p}</option>`).join("")}
            </select>
            <select name="category">
                <option value="">All categories</option>
                ${["billing", "technical", "account", "shipping", "general", "spam"]
                    .map((c) => `<option ${params.get("category") === c ? "selected" : ""}>${c}</option>`).join("")}
            </select>
            <button class="btn" type="submit">${icon("search", 16)} Filter</button>
        </form>
    `;

    renderLayout(`
        <div class="page-header">
            <div>
                <h1>${isCostumer ? "My tickets" : "All tickets"}</h1>
                <p class="subtitle">${tickets.length} ticket${tickets.length === 1 ? "" : "s"}</p>
            </div>
            ${isCostumer ? `<a class="btn" href="#/new">${icon("plus", 16)} New ticket</a>` : ""}
        </div>
        ${filters}
        ${ticketList(tickets, isCostumer ? "You have no tickets yet." : "No tickets found.")}
    `);

    makeRowsClickable("#/tickets/");

    const filterForm = document.getElementById("filters");
    if (filterForm) {
        filterForm.onsubmit = (event) => {
            event.preventDefault();
            const values = new URLSearchParams();
            for (const [key, value] of new FormData(filterForm)) {
                if (value) values.set(key, value);
            }
            sessionStorage.setItem("filters", values.toString());
            pageTickets();
        };
    }
}

function pageNewTicket(orderNumber) {
    const subject = orderNumber ? `Question about order #${orderNumber}` : "";
    const body = orderNumber ? `Order #${orderNumber}: ` : "";

    renderLayout(`
        <a class="back" href="#/tickets">← Back to tickets</a>
        <div class="page-header">
            <div>
                <h1>New ticket</h1>
                <p class="subtitle">Describe your problem — our AI assistant will reply in seconds.</p>
            </div>
        </div>
        <div class="card">
            <form id="new-ticket">
                <div class="field">
                    <label>Subject</label>
                    <input name="subject" required maxlength="255" placeholder="e.g. I can't log in" value="${escapeHtml(subject)}">
                </div>
                <div class="field">
                    <label>Message</label>
                    <textarea name="body" required maxlength="5000" placeholder="Tell us what happened...">${escapeHtml(body)}</textarea>
                </div>
                <button class="btn" type="submit">${icon("send", 16)} Send ticket</button>
            </form>
        </div>
    `);

    document.getElementById("new-ticket").onsubmit = async (event) => {
        event.preventDefault();
        const button = event.target.querySelector("button");
        button.disabled = true;

        try {
            const ticket = await api("/tickets/", {
                method: "POST",
                body: Object.fromEntries(new FormData(event.target))
            });
            showToast("Ticket sent!");
            location.hash = "#/tickets/" + ticket.id;
        } catch (error) {
            showToast(error.message, true);
            button.disabled = false;
        }
    };
}

function messageBubble(message) {
    const isMine = message.author_id === currentUser.id && message.author_type === currentUser.role;
    const who = { costumer: "Customer", ai: "AI assistant", agent: "Support agent" }[message.author_type] || message.author_type;

    const avatar = message.author_type === "ai"
        ? `<div class="avatar ai">${icon("sparkle", 16)}</div>`
        : `<div class="avatar">${escapeHtml(who[0])}</div>`;

    return `
        <div class="message ${isMine ? "mine" : message.author_type}">
            ${isMine ? "" : avatar}
            <div class="body">
                <div class="bubble">${escapeHtml(message.content)}</div>
                <div class="meta">${isMine ? "You" : escapeHtml(who)} · ${formatDate(message.created_at)}</div>
            </div>
        </div>
    `;
}

function ticketThread(ticket) {
    const firstMessage = {
        author_type: "costumer",
        author_id: ticket.costumer_id,
        content: ticket.body,
        created_at: ticket.created_at
    };

    const typing = ticket.status === "triaging" ? `
        <div class="message ai">
            <div class="avatar ai">${icon("sparkle", 16)}</div>
            <div class="typing"><div class="spinner"></div> AI is writing a reply…</div>
        </div>` : "";

    return `<div class="thread">${[firstMessage, ...ticket.messages].map(messageBubble).join("")}${typing}</div>`;
}

async function pageTicket(id) {
    const ticket = await api("/tickets/" + id);
    const isOwner = ticket.costumer_id === currentUser.id;

    const statusInfo = {
        awaiting_review: `<div class="working orange">${icon("clock", 18)} A support agent is checking the reply before it is sent.</div>`,
        escalated: `<div class="working red">${icon("up", 18)} Escalated to a senior support specialist.</div>`
    }[ticket.status] || "";

    renderLayout(`
        <a class="back" href="#/tickets">← Back to tickets</a>
        <div class="page-header">
            <div>
                <p class="eyebrow">Ticket No. ${ticket.id} — ${formatDate(ticket.created_at)}</p>
                <h1>${escapeHtml(ticket.subject)}</h1>
                <div class="detail-header">
                    ${statusBadge(ticket.status)}
                    ${categoryBadge(ticket.category)}
                    ${priorityBadge(ticket.priority)}
                    ${sentimentBadge(ticket.sentiment)}
                    ${ticket.language ? `<span class="badge">${icon("globe", 14)}${escapeHtml(ticket.language)}</span>` : ""}
                </div>
            </div>
        </div>

        ${statusInfo}

        ${ticket.ai_summary && !isOwner ? `
            <div class="ai-box">
                <div class="label">${icon("sparkle", 14)} AI summary</div>
                <p>${escapeHtml(ticket.ai_summary)}</p>
            </div>` : ""}

        <div class="card">
            <h2>${icon("message", 18)} Conversation</h2>
            ${ticketThread(ticket)}

            ${isOwner ? `
                <form class="composer" id="add-message">
                    <label for="message-input" class="sr-only">Message</label>
                    <textarea id="message-input" name="content" required placeholder="Write a message…"></textarea>
                    <button type="submit" aria-label="Send message">${icon("send", 18)}</button>
                </form>` : ""}
        </div>
    `);

    const form = document.getElementById("add-message");
    if (form) {
        form.onsubmit = async (event) => {
            event.preventDefault();
            try {
                await api(`/tickets/${id}/messages`, {
                    method: "POST",
                    body: Object.fromEntries(new FormData(form))
                });
                pageTicket(id);
            } catch (error) {
                showToast(error.message, true);
            }
        };
    }

    if (ticket.status === "triaging") {
        pollTimer = setTimeout(() => {
            if (location.hash === "#/tickets/" + id) pageTicket(id);
        }, 3000);
    }
}

async function pageReviewQueue() {
    const tickets = await api("/review/queue");

    renderLayout(`
        <div class="page-header">
            <div>
                <h1>Review queue</h1>
                <p class="subtitle">Tickets where the AI needs a human decision · most urgent first</p>
            </div>
            <span class="badge orange">${tickets.length} waiting</span>
        </div>
        ${ticketList(tickets, "Nothing to review — the queue is empty.")}
    `);

    makeRowsClickable("#/review/");
}

function meter(label, value) {
    const width = value == null ? 0 : Math.round(value * 100);
    const color = width >= 80 ? "var(--green)" : width >= 50 ? "var(--orange)" : "var(--red)";

    return `
        <div class="meter">
            <div class="meter-top"><span>${label}</span><span>${percent(value)}</span></div>
            <div class="meter-bar"><div class="meter-fill" style="width: ${width}%; background: ${color}"></div></div>
        </div>
    `;
}

async function pageReview(id) {
    const [review, ticket] = await Promise.all([
        api("/review/" + id),
        api("/tickets/" + id)
    ]);
    const isWaiting = ticket.status === "awaiting_review";
    const draftPercent = (value) => (value == null ? "—" : Math.round(value * 100) + "%");

    renderLayout(`
        <div class="actions" style="justify-content: space-between; margin-bottom: 14px">
            <a class="back" href="#/review" style="margin: 0">← Back to queue</a>
            <a class="btn secondary small" href="#/workflow/ticket-${id}">${icon("gauge", 14)} View workflow</a>
        </div>
        <div class="page-header">
            <div>
                <p class="eyebrow">Ticket No. ${ticket.id} — ${formatDate(ticket.created_at)}</p>
                <h1>${escapeHtml(ticket.subject)}</h1>
                <div class="detail-header">
                    ${statusBadge(ticket.status)}
                    ${categoryBadge(ticket.category)}
                    ${priorityBadge(ticket.priority)}
                    ${sentimentBadge(ticket.sentiment)}
                </div>
            </div>
        </div>

        <div class="grid grid-2">
            <div>
                <div class="card">
                    <h2>${icon("message", 18)} Conversation</h2>
                    ${ticketThread(ticket)}
                </div>
                <div class="ai-box">
                    <div class="label">${icon("sparkle", 14)} AI summary</div>
                    <p>${escapeHtml(ticket.ai_summary || "—")}</p>
                </div>
                <div class="card">
                    <h2>${icon("gauge", 18)} How sure the AI is</h2>
                    <div class="big-numbers">
                        <div><div class="number">${draftPercent(review.classification_confidence)}</div><div class="what">classification</div></div>
                        <div><div class="number accent">${draftPercent(review.draft_confidence)}</div><div class="what">draft reply</div></div>
                    </div>
                    <div class="sources">
                        Based on:
                        ${review.cited_article_ids.length
                            ? review.cited_article_ids.map((a) => `<span>${icon("doc", 16)} KB article #${a}</span>`).join("")
                            : "<span>no KB article</span>"}
                    </div>
                </div>
            </div>

            <div class="card">
                <h2><label for="reply" style="margin: 0; display: flex; align-items: center; gap: 8px; font: inherit">${icon("pen", 18)} Proposed reply</label></h2>
                <div class="field">
                    <textarea id="reply" class="letter" style="min-height: 280px" ${isWaiting ? "" : "disabled"}>${escapeHtml(review.draft_reply)}</textarea>
                </div>
                <div class="field">
                    <label for="comment">Comment (optional)</label>
                    <input id="comment" placeholder="Note for the team" ${isWaiting ? "" : "disabled"}>
                </div>
                ${isWaiting ? `
                    <div class="actions">
                        <button class="btn" data-decision="approve">${icon("check", 16)} Approve &amp; send</button>
                        <button class="btn secondary" data-decision="edit">${icon("pen", 16)} Send my edit</button>
                        <button class="btn red" data-decision="reject">${icon("up", 16)} Reject &amp; escalate</button>
                    </div>` : `<p class="muted">This ticket was already handled.</p>`}
            </div>
        </div>
    `);

    document.querySelectorAll("[data-decision]").forEach((button) => {
        button.onclick = async () => {
            const decision = button.dataset.decision;
            const body = { decision, comment: document.getElementById("comment").value || null };

            if (decision === "edit") body.edited_reply = document.getElementById("reply").value;

            document.querySelectorAll("[data-decision]").forEach((b) => (b.disabled = true));

            try {
                const result = await api(`/review/${id}/decision`, { method: "POST", body });
                showToast(`Done — ticket is now ${result.status}`);
                location.hash = "#/review";
            } catch (error) {
                showToast(error.message, true);
                document.querySelectorAll("[data-decision]").forEach((b) => (b.disabled = false));
            }
        };
    });
}

const STEP_NAMES = {
    prepare_ticket: "Prepare ticket",
    categorize_ticket: "Categorize ticket",
    mark_spam: "Mark as spam",
    find_order: "Find order",
    find_kb_article: "Find KB articles",
    draft_reply: "Draft reply",
    check_quality: "Check quality",
    decide_route: "Decide route",
    human_review: "Human review",
    apply_decision: "Apply decision",
    send_reply: "Send reply",
    escalate_to_senior: "Escalate to senior"
};

function workflowStatus(workflow) {
    if (workflow.waiting_for_human) {
        return `<div class="working orange">${icon("clock", 18)} Waiting for human approval</div>`;
    }
    if (workflow.next_step) {
        return `<div class="working">${icon("sparkle", 18)} Running — next step: ${escapeHtml(STEP_NAMES[workflow.next_step] || workflow.next_step)}</div>`;
    }
    return `<div class="working" style="background: var(--green-soft); color: var(--green)">${icon("check", 18)} Workflow finished</div>`;
}

function workflowSteps(workflow) {
    return workflow.steps.map((step, index) => {
        const isCurrent = index === workflow.steps.length - 1 && workflow.next_step === step;
        return `
            <div class="step ${isCurrent ? "current" : "done"}">
                <span class="step-dot">${icon(isCurrent ? "clock" : "check", 12)}</span>
                <span>${escapeHtml(STEP_NAMES[step] || step)}</span>
            </div>`;
    }).join("");
}

async function pageWorkflow(threadId) {
    let result = "";

    if (threadId) {
        try {
            const workflow = await api("/review/workflow/" + encodeURIComponent(threadId));
            const percentOf = (value) => (value == null ? "—" : Math.round(value * 100) + "%");

            result = `
                ${workflowStatus(workflow)}

                <div class="grid grid-2">
                    <div>
                        <div class="card">
                            <h2>${icon("ticket", 18)} Thread</h2>
                            <p class="muted">Thread ID</p>
                            <p style="font-family: var(--serif); font-size: 20px; margin-bottom: 12px">${escapeHtml(workflow.thread_id)}</p>
                            <div class="detail-header" style="margin-top: 0">
                                ${categoryBadge(workflow.category)}
                                ${priorityBadge(workflow.priority)}
                                ${sentimentBadge(workflow.sentiment)}
                            </div>
                            <div class="actions" style="margin-top: 16px">
                                <a class="btn secondary small" href="#/tickets/${workflow.ticket_id}">${icon("message", 14)} Open ticket</a>
                                ${workflow.waiting_for_human ? `<a class="btn small" href="#/review/${workflow.ticket_id}">${icon("pen", 14)} Review now</a>` : ""}
                            </div>
                        </div>

                        <div class="card">
                            <h2>${icon("gauge", 18)} AI numbers</h2>
                            <div class="big-numbers">
                                <div><div class="number">${percentOf(workflow.classification_confidence)}</div><div class="what">classification</div></div>
                                <div><div class="number accent">${percentOf(workflow.draft_confidence)}</div><div class="what">draft reply</div></div>
                                <div><div class="number">${workflow.attempts}</div><div class="what">attempts</div></div>
                            </div>
                            <div class="sources">
                                Quality issues:
                                ${workflow.quality_issues.length
                                    ? workflow.quality_issues.map((issue) => `<span style="color: var(--red)">${icon("alert", 14)} ${escapeHtml(issue)}</span>`).join("")
                                    : `<span style="color: var(--green)">${icon("check", 14)} none</span>`}
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <h2>${icon("chart", 18)} Steps</h2>
                        <div class="steps">${workflowSteps(workflow)}</div>
                    </div>
                </div>

                <div class="card">
                    <h2>${icon("pen", 18)} AI draft reply</h2>
                    <p class="text-block letter-text">${escapeHtml(workflow.draft_reply || "—")}</p>
                </div>

                <div class="card">
                    <h2>${icon("users", 18)} Reviewer verdict</h2>
                    <p>${workflow.review_decision
                        ? `<span class="badge ${workflow.review_decision === "reject" ? "red" : "green"}">${escapeHtml(workflow.review_decision)}</span>`
                        : `<span class="muted">No decision yet</span>`}</p>
                    ${workflow.final_reply ? `<p class="text-block letter-text" style="margin-top: 12px">${escapeHtml(workflow.final_reply)}</p>` : ""}
                </div>
            `;
        } catch (error) {
            result = `<div class="card empty"><div class="empty-icon">${icon("alert", 32)}</div>${escapeHtml(error.message)}</div>`;
        }
    }

    renderLayout(`
        <div class="page-header">
            <div>
                <h1>Load workflow</h1>
                <p class="subtitle">Enter a thread ID to see where the AI is and what it decided</p>
            </div>
        </div>

        <form class="filters" id="workflow-form">
            <label for="thread-id" class="sr-only">Thread ID</label>
            <input id="thread-id" name="thread_id" required placeholder="Thread ID, e.g. ticket-25" value="${escapeHtml(threadId || "")}">
            <button class="btn" type="submit">${icon("search", 16)} Load workflow</button>
        </form>

        ${result}
    `);

    document.getElementById("workflow-form").onsubmit = (event) => {
        event.preventDefault();
        const value = document.getElementById("thread-id").value.trim();
        location.hash = "#/workflow/" + encodeURIComponent(value);
    };
}

const CATEGORIES = ["billing", "technical", "account", "shipping", "general"];

async function pageKB() {
    const articles = await api("/kb/articles");
    const isAdmin = currentUser.role === "admin";

    renderLayout(`
        <div class="page-header">
            <div>
                <h1>Knowledge base</h1>
                <p class="subtitle">${articles.length} articles · the AI uses these to answer tickets</p>
            </div>
            ${isAdmin ? `<a class="btn" href="#/kb/new">${icon("plus", 16)} New article</a>` : ""}
        </div>

        <div class="card">
            <h2>${icon("search", 18)} Test the search</h2>
            <form class="filters" id="kb-search" style="margin-bottom: 0">
                <input name="query" required placeholder="e.g. I was charged twice">
                <button class="btn" type="submit">${icon("search", 16)} Search</button>
            </form>
            <div id="search-results"></div>
        </div>

        <div class="card list-card">
            ${articles.map((a) => `
                <div class="kb-item">
                    <div class="top">
                        <div class="title">
                            ${icon("doc", 16)}
                            <strong>${escapeHtml(a.title)}</strong>
                            ${categoryBadge(a.category)}
                            ${a.is_published ? "" : `<span class="badge">draft</span>`}
                        </div>
                        ${isAdmin ? `
                            <div class="actions">
                                <a class="btn secondary small" href="#/kb/${a.id}">Edit</a>
                                <button class="btn secondary small" data-delete="${a.id}">Delete</button>
                            </div>` : ""}
                    </div>
                    <p class="content">${escapeHtml(a.content)}</p>
                </div>
            `).join("") || `<div class="empty">No articles yet.</div>`}
        </div>
    `);

    document.getElementById("kb-search").onsubmit = async (event) => {
        event.preventDefault();
        const query = new FormData(event.target).get("query");
        const box = document.getElementById("search-results");
        box.innerHTML = `<p class="muted" style="margin-top: 12px">Searching...</p>`;

        try {
            const results = await api("/kb/search", { method: "POST", body: { query } });
            box.innerHTML = results.length ? results.map((r) => `
                <div style="margin-top: 14px">
                    ${meter(escapeHtml(r.title), r.score)}
                </div>
            `).join("") : `<p class="muted" style="margin-top: 12px">No results.</p>`;
        } catch (error) {
            box.innerHTML = "";
            showToast(error.message, true);
        }
    };

    document.querySelectorAll("[data-delete]").forEach((button) => {
        button.onclick = async () => {
            if (!confirm("Delete this article?")) return;
            try {
                await api("/kb/articles/" + button.dataset.delete, { method: "DELETE" });
                showToast("Article deleted");
                pageKB();
            } catch (error) {
                showToast(error.message, true);
            }
        };
    });
}

async function pageKBForm(id) {
    const isNew = id === "new";
    let article = { title: "", category: "general", content: "", is_published: true };

    if (!isNew) {
        const articles = await api("/kb/articles");
        article = articles.find((a) => String(a.id) === id) || article;
    }

    renderLayout(`
        <a class="back" href="#/kb">← Back to knowledge base</a>
        <div class="page-header"><h1>${isNew ? "New article" : "Edit article"}</h1></div>
        <div class="card">
            <form id="kb-form">
                <div class="field">
                    <label>Title</label>
                    <input name="title" required value="${escapeHtml(article.title)}">
                </div>
                <div class="field">
                    <label>Category</label>
                    <select name="category">
                        ${CATEGORIES.map((c) => `<option ${article.category === c ? "selected" : ""}>${c}</option>`).join("")}
                    </select>
                </div>
                <div class="field">
                    <label>Content</label>
                    <textarea name="content" required style="min-height: 220px">${escapeHtml(article.content)}</textarea>
                </div>
                <div class="field">
                    <label style="display: flex; gap: 8px; align-items: center; font-weight: 500">
                        <input type="checkbox" name="is_published" style="width: auto" ${article.is_published ? "checked" : ""}>
                        Published (the AI can use it)
                    </label>
                </div>
                <button class="btn" type="submit">Save</button>
            </form>
        </div>
    `);

    document.getElementById("kb-form").onsubmit = async (event) => {
        event.preventDefault();
        const form = event.target;
        const body = {
            title: form.title.value,
            category: form.category.value,
            content: form.content.value,
            is_published: form.is_published.checked
        };

        try {
            if (isNew) {
                await api("/kb/articles", { method: "POST", body });
            } else {
                await api("/kb/articles/" + id, { method: "PUT", body });
            }
            showToast("Article saved");
            location.hash = "#/kb";
        } catch (error) {
            showToast(error.message, true);
        }
    };
}

async function pageUsers() {
    const users = await api("/auth/users");

    renderLayout(`
        <div class="page-header">
            <div>
                <h1>Users</h1>
                <p class="subtitle">Change roles: costumer, agent or admin</p>
            </div>
        </div>
        <div class="card list-card">
            <table>
                <thead><tr><th>User</th><th>Email</th><th>Joined</th><th>Role</th></tr></thead>
                <tbody>
                    ${users.map((u) => `
                        <tr>
                            <td><strong>${escapeHtml(u.full_name)}</strong></td>
                            <td class="muted">${escapeHtml(u.email)}</td>
                            <td class="muted">${formatDate(u.created_at)}</td>
                            <td>
                                <select data-user="${u.id}" ${u.id === currentUser.id ? "disabled" : ""}>
                                    ${["costumer", "agent", "admin"]
                                        .map((r) => `<option ${u.role === r ? "selected" : ""}>${r}</option>`).join("")}
                                </select>
                            </td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `);

    document.querySelectorAll("[data-user]").forEach((select) => {
        select.onchange = async () => {
            try {
                await api(`/auth/users/${select.dataset.user}/role`, {
                    method: "PATCH",
                    body: { role: select.value }
                });
                showToast("Role updated");
            } catch (error) {
                showToast(error.message, true);
            }
        };
    });
}

function bars(data) {
    const entries = Object.entries(data || {});
    if (!entries.length) return `<p class="muted">No data yet.</p>`;

    const max = Math.max(...entries.map(([, value]) => value), 1);

    return entries.map(([name, value]) => `
        <div class="bar-row">
            <div class="bar-label">${escapeHtml(name === "null" ? "unclassified" : name.replace("_", " "))}</div>
            <div class="meter-bar"><div class="meter-fill" style="width: ${(value / max) * 100}%"></div></div>
            <div class="bar-value">${value}</div>
        </div>
    `).join("");
}

function splitData(data) {
    const numbers = [];
    const groups = [];

    for (const [key, value] of Object.entries(data || {})) {
        if (value !== null && typeof value === "object") groups.push([key, value]);
        else numbers.push([key, value]);
    }

    return { numbers, groups };
}

function statCard(name, value) {
    let shown = value ?? "—";
    if (typeof value === "number" && !Number.isInteger(value)) {
        shown = value <= 1 ? percent(value) : value.toFixed(1);
    }
    if (name.includes("percent") || name.includes("rate")) shown = (value ?? 0) + "%";

    return `
        <div class="card stat">
            <div class="stat-label">${escapeHtml(name.replaceAll("_", " "))}</div>
            <div class="stat-value">${escapeHtml(String(shown))}</div>
        </div>
    `;
}

function analyticsSection(title, data) {
    const { numbers, groups } = splitData(data);

    return `
        <h2 style="margin-top: 8px">${title}</h2>
        ${numbers.length ? `<div class="grid grid-4">${numbers.map(([k, v]) => statCard(k, v)).join("")}</div>` : ""}
        ${groups.length ? `
            <div class="grid grid-2">
                ${groups.map(([k, v]) => `
                    <div class="card">
                        <h2 style="text-transform: capitalize">${escapeHtml(k.replaceAll("_", " "))}</h2>
                        ${bars(v)}
                    </div>`).join("")}
            </div>` : ""}
    `;
}

async function pageAnalytics() {
    const [overview, automation, accuracy] = await Promise.all([
        api("/analytics/overview"),
        api("/analytics/automation-rate"),
        api("/analytics/ai-accuracy")
    ]);

    renderLayout(`
        <div class="page-header">
            <div>
                <h1>Analytics</h1>
                <p class="subtitle">How well the AI is handling support</p>
            </div>
        </div>
        ${analyticsSection("Tickets", overview)}
        ${analyticsSection("Automation", automation)}
        ${analyticsSection("AI accuracy", accuracy)}
    `);
}

const ORDER_STEPS = ["paid", "shipped", "delivered"];
const ORDER_STATUSES = ["paid", "shipped", "delivered", "cancelled", "refunded"];
const ORDER_COLORS = { paid: "blue", shipped: "orange", delivered: "green", cancelled: "red", refunded: "" };

function orderBadge(status) {
    return `<span class="badge ${ORDER_COLORS[status] ?? ""}">${escapeHtml(status)}</span>`;
}

function orderSteps(status) {
    if (!ORDER_STEPS.includes(status)) return "";

    const current = ORDER_STEPS.indexOf(status);

    return `<div class="order-steps">${ORDER_STEPS.map((step, index) => `
        <span class="order-step ${index <= current ? "done" : ""}"><span class="order-dot"></span>${step}</span>
    `).join('<span class="step-line"></span>')}</div>`;
}

function orderCard(order) {
    return `
        <div class="card order-card">
            <div class="order-top">
                <div class="order-icon">${phoneArt(order.product, 48)}</div>
                <div class="order-info">
                    <div class="order-number">Order #${escapeHtml(order.order_number)}</div>
                    <div class="order-product">${escapeHtml(order.product)}</div>
                </div>
                <div class="order-total">${order.total} ₾</div>
            </div>
            ${orderSteps(order.status)}
            <div class="order-bottom">
                <span class="muted">${orderBadge(order.status)} ${order.tracking_number ? "Tracking " + escapeHtml(order.tracking_number) : formatDate(order.created_at)}</span>
                <a class="btn secondary small" href="#/new/${order.order_number}">${icon("chat", 14)} Get help</a>
            </div>
        </div>
    `;
}

async function pageMyOrders() {
    const orders = await api("/orders/my");

    const content = orders.length
        ? `<div class="orders-grid">${orders.map(orderCard).join("")}</div>`
        : `<div class="card empty"><div class="empty-icon">${icon("box", 32)}</div>You have no orders yet.</div>`;

    renderLayout(`
        <div class="page-header">
            <div>
                <h1>My orders</h1>
                <p class="subtitle">Question about an order? Click Get help and our AI will look it up.</p>
            </div>
        </div>
        ${content}
    `);
}

async function pageAllOrders() {
    const orders = await api("/orders");

    renderLayout(`
        <div class="page-header">
            <div>
                <h1>Orders</h1>
                <p class="subtitle">Update status and tracking. The AI uses this when customers ask about an order.</p>
            </div>
        </div>
        <div class="card list-card">
            <table>
                <thead><tr><th>Order</th><th>Product</th><th>Total</th><th>Status</th><th>Tracking</th><th></th></tr></thead>
                <tbody>
                    ${orders.map((o) => `
                        <tr data-order="${o.id}">
                            <td><strong>#${escapeHtml(o.order_number)}</strong></td>
                            <td>${escapeHtml(o.product)}</td>
                            <td class="muted">${o.total} ₾</td>
                            <td>
                                <select name="status">
                                    ${ORDER_STATUSES.map((s) => `<option ${o.status === s ? "selected" : ""}>${s}</option>`).join("")}
                                </select>
                            </td>
                            <td><input name="tracking" value="${escapeHtml(o.tracking_number || "")}" placeholder="—"></td>
                            <td><button class="btn small" type="button">Save</button></td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `);

    document.querySelectorAll("[data-order]").forEach((row) => {
        row.querySelector("button").onclick = async () => {
            try {
                await api(`/orders/${row.dataset.order}`, {
                    method: "PATCH",
                    body: {
                        status: row.querySelector("[name=status]").value,
                        tracking_number: row.querySelector("[name=tracking]").value || null
                    }
                });
                showToast("Order updated");
            } catch (error) {
                showToast(error.message, true);
            }
        };
    });
}

async function pageShop() {
    const products = await api("/orders/products");

    renderLayout(`
        <div class="page-header">
            <div>
                <h1>Shop</h1>
                <p class="subtitle">Free delivery in Tbilisi. Questions after you buy? Our AI is here to help.</p>
            </div>
        </div>
        <div class="products-grid">
            ${products.map((p) => `
                <div class="card product-card">
                    <div class="product-image">${phoneArt(p.name, 120)}</div>
                    <div class="product-name">${escapeHtml(p.name)}</div>
                    <div class="product-bottom">
                        <span class="product-price">${p.price} ₾</span>
                        <button class="btn small" data-buy="${escapeHtml(p.name)}">${icon("box", 14)} Buy</button>
                    </div>
                </div>
            `).join("")}
        </div>
    `);

    document.querySelectorAll("[data-buy]").forEach((button) => {
        button.onclick = async () => {
            button.disabled = true;
            try {
                const order = await api("/orders", { method: "POST", body: { product: button.dataset.buy } });
                showToast(`Order #${order.order_number} placed!`);
                location.hash = "#/orders";
            } catch (error) {
                showToast(error.message, true);
                button.disabled = false;
            }
        };
    });
}

async function router() {
    clearTimeout(pollTimer);

    if (!currentUser) return;

    const hash = location.hash || "";
    const parts = hash.replace("#/", "").split("/");
    const isStaff = currentUser.role !== "costumer";
    const isAdmin = currentUser.role === "admin";

    renderLoading();

    try {
        if (parts[0] === "new") return pageNewTicket(parts[1]);
        if (parts[0] === "shop") return await pageShop();
        if (parts[0] === "orders") return await (isStaff ? pageAllOrders() : pageMyOrders());
        if (parts[0] === "tickets" && parts[1]) return await pageTicket(parts[1]);
        if (parts[0] === "tickets") return await pageTickets();
        if (parts[0] === "review" && parts[1] && isStaff) return await pageReview(parts[1]);
        if (parts[0] === "review" && isStaff) return await pageReviewQueue();
        if (parts[0] === "workflow" && isStaff) return await pageWorkflow(parts[1]);
        if (parts[0] === "kb" && parts[1] && isStaff) return await pageKBForm(parts[1]);
        if (parts[0] === "kb" && isStaff) return await pageKB();
        if (parts[0] === "users" && isAdmin) return await pageUsers();
        if (parts[0] === "analytics" && isAdmin) return await pageAnalytics();

        location.hash = isStaff ? "#/review" : "#/shop";
    } catch (error) {
        renderLayout(`<div class="card empty"><div class="empty-icon">${icon("alert", 32)}</div>${escapeHtml(error.message)}</div>`);
    }
}

async function start() {
    if (!localStorage.getItem("token")) return renderAuth();

    try {
        currentUser = await api("/auth/me");
        router();
    } catch {
        logout();
    }
}

window.addEventListener("hashchange", router);
start();
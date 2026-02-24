// Auto-generated constants from Python
const TEAM_SHORT_NAMES = {"Boston Celtics": "Celtics", "Brooklyn Nets": "Nets", "New York Knicks": "Knicks", "Philadelphia 76ers": "76ers", "Toronto Raptors": "Raptors", "Chicago Bulls": "Bulls", "Cleveland Cavaliers": "Cavaliers", "Detroit Pistons": "Pistons", "Indiana Pacers": "Pacers", "Milwaukee Bucks": "Bucks", "Atlanta Hawks": "Hawks", "Charlotte Hornets": "Hornets", "Miami Heat": "Heat", "Orlando Magic": "Magic", "Washington Wizards": "Wizards", "Denver Nuggets": "Nuggets", "Minnesota Timberwolves": "Timberwolves", "Oklahoma City Thunder": "Thunder", "Portland Trail Blazers": "Trail Blazers", "Utah Jazz": "Jazz", "Golden State Warriors": "Warriors", "Los Angeles Clippers": "Clippers", "Los Angeles Lakers": "Lakers", "Phoenix Suns": "Suns", "Sacramento Kings": "Kings", "Dallas Mavericks": "Mavericks", "Houston Rockets": "Rockets", "Memphis Grizzlies": "Grizzlies", "New Orleans Pelicans": "Pelicans", "San Antonio Spurs": "Spurs"};
const TEAM_CODES = {"Boston Celtics": "BOS", "Brooklyn Nets": "BKN", "New York Knicks": "NYK", "Philadelphia 76ers": "PHI", "Toronto Raptors": "TOR", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE", "Detroit Pistons": "DET", "Indiana Pacers": "IND", "Milwaukee Bucks": "MIL", "Atlanta Hawks": "ATL", "Charlotte Hornets": "CHA", "Miami Heat": "MIA", "Orlando Magic": "ORL", "Washington Wizards": "WAS", "Denver Nuggets": "DEN", "Minnesota Timberwolves": "MIN", "Oklahoma City Thunder": "OKC", "Portland Trail Blazers": "POR", "Utah Jazz": "UTA", "Golden State Warriors": "GSW", "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Phoenix Suns": "PHX", "Sacramento Kings": "SAC", "Dallas Mavericks": "DAL", "Houston Rockets": "HOU", "Memphis Grizzlies": "MEM", "New Orleans Pelicans": "NOP", "San Antonio Spurs": "SAS"};
const MILESTONE_CATEGORIES = {"multi": ["quadruple_doubles", "triple_doubles", "double_doubles", "near_triple_doubles", "near_double_doubles", "five_by_fives", "all_around_games"], "scoring": ["seventy_point_games", "sixty_point_games", "fifty_point_games", "forty_five_point_games", "forty_point_games", "thirty_five_point_games", "thirty_point_games", "twenty_five_point_games", "twenty_point_games"], "rebounding": ["twenty_five_rebound_games", "twenty_rebound_games", "eighteen_rebound_games", "fifteen_rebound_games", "twelve_rebound_games", "ten_rebound_games"], "assists": ["twenty_assist_games", "fifteen_assist_games", "twelve_assist_games", "ten_assist_games"], "steals": ["ten_steal_games", "seven_steal_games", "five_steal_games", "four_steal_games"], "blocks": ["ten_block_games", "seven_block_games", "five_block_games", "four_block_games"], "threes": ["ten_three_games", "eight_three_games", "seven_three_games", "six_three_games", "five_three_games", "perfect_from_three"], "efficiency": ["hot_shooting_games", "perfect_ft_games", "perfect_fg_games", "efficient_scoring_games", "high_game_score"], "combined": ["thirty_ten_games", "twenty_five_ten_games", "twenty_ten_games", "twenty_ten_five_games", "twenty_twenty_games", "points_assists_double_double"], "defensive": ["defensive_monster_games", "zero_turnover_games"], "plusminus": ["plus_25_games", "plus_20_games", "minus_25_games"]};

function getShortName(fullName) {
    return TEAM_SHORT_NAMES[fullName] || fullName;
}

function getTeamCode(fullName) {
    if (fullName && fullName.includes(', ')) {
        return fullName.split(', ').map(t => TEAM_CODES[t.trim()] || t.trim().slice(0,3).toUpperCase()).join(', ');
    }
    return TEAM_CODES[fullName] || fullName;
}

let arenaMap = null;
let filteredPlayers = [];
let playerSortCol = null;
let playerSortAsc = false;

// Lazy initialization flags
let dashboardInitialized = false;
let gamesInitialized = false;
let onThisDayInitialized = false;
let recordsInitialized = false;
let scorigamiInitialized = false;
let matchupsInitialized = false;
let calendarInitialized = false;
let seasonsInitialized = false;
let divisionsInitialized = false;

// Navigation stack for back button
let navStack = [];

// Theme
function toggleTheme() {
    const html = document.documentElement;
    const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    if (arenaMap) setTimeout(() => arenaMap.invalidateSize(), 100);
}
(function() {
    const saved = localStorage.getItem('theme');
    if (saved) document.documentElement.setAttribute('data-theme', saved);
    else if (window.matchMedia('(prefers-color-scheme: dark)').matches)
        document.documentElement.setAttribute('data-theme', 'dark');
})();

// URL Deep Linking
let _suppressURLUpdate = false;

function updateURL(section, params) {
    if (_suppressURLUpdate) return;
    let hash = '#' + section;
    if (params) {
        const query = Object.entries(params).map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
        if (query) hash += '?' + query;
    }
    if (window.location.hash !== hash) {
        history.pushState(null, '', hash);
    }
}

function parseURL() {
    const hash = window.location.hash.slice(1);
    if (!hash) return { section: '', params: {} };
    const [section, queryStr] = hash.split('?');
    const params = {};
    if (queryStr) {
        queryStr.split('&').forEach(pair => {
            const [k, v] = pair.split('=');
            if (k) params[k] = decodeURIComponent(v || '');
        });
    }
    return { section, params };
}

function handleURLNavigation() {
    const { section, params } = parseURL();

    // Backward compat: calendar?sub=calendar-onthisday -> onthisday
    if (section === 'calendar' && params.sub === 'calendar-onthisday') {
        _suppressURLUpdate = true;
        showSection('onthisday');
        _suppressURLUpdate = false;
        return;
    }

    // Handle boxscore deep link
    if (section === 'boxscore-view' || (section === 'boxscore' && params.game)) {
        _suppressURLUpdate = true;
        showBoxScore(params.game);
        _suppressURLUpdate = false;
        return;
    }

    if (!section) {
        showSection('dashboard');
        return;
    }
    const tab = document.querySelector(`[data-section="${section}"]`);
    if (!tab) {
        showSection('dashboard');
        return;
    }
    _suppressURLUpdate = true;
    showSection(section);
    if (params.sub) {
        if (section === 'records') showRecordsSubTab(params.sub);
        else if (section === 'matchups') showMatchupsSubTab(params.sub);
    }
    _suppressURLUpdate = false;
    if (params.player) showPlayerDetail(params.player);
}

// Sections
function showSection(id) {
    // Track nav stack for back button (don't push boxscore-view)
    const currentActive = document.querySelector('.section.active');
    if (currentActive && currentActive.id !== id && id !== 'boxscore-view') {
        navStack.push(currentActive.id);
        if (navStack.length > 20) navStack.shift();
    }

    // Update sidebar nav items
    document.querySelectorAll('.nav-item').forEach(t => t.classList.remove('active'));
    const navBtn = document.querySelector(`.sidebar .nav-item[data-section="${id}"]`);
    if (navBtn) navBtn.classList.add('active');

    // Update mobile bottom nav
    document.querySelectorAll('.mobile-nav-btn').forEach(b => b.classList.remove('active'));
    const mobileBtn = document.querySelector(`.mobile-nav-btn[data-section="${id}"]`);
    if (mobileBtn) mobileBtn.classList.add('active');

    // Hide all sections, show target
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    const el = document.getElementById(id);
    if (el) el.classList.add('active');

    // Close mobile sidebar
    closeSidebar();

    // Scroll to top of content
    const contentArea = document.querySelector('.content-area');
    if (contentArea) contentArea.scrollTop = 0;
    window.scrollTo(0, 0);

    // Lazy init
    if (id === 'dashboard' && !dashboardInitialized) { dashboardInitialized = true; renderDashboard(); }
    if (id === 'games' && !gamesInitialized) { gamesInitialized = true; renderGamesGrid(); }
    if (id === 'map' && !arenaMap) initMap();
    if (id === 'records' && !recordsInitialized) { recordsInitialized = true; renderRecords(); renderPlayerRecords(); }
    if (id === 'scorigami' && !scorigamiInitialized) { scorigamiInitialized = true; renderScorigami(); }
    if (id === 'matchups' && !matchupsInitialized) { matchupsInitialized = true; renderMatchups(); }
    if (id === 'calendar' && !calendarInitialized) { calendarInitialized = true; renderCalendar(); }
    if (id === 'onthisday' && !onThisDayInitialized) { onThisDayInitialized = true; renderOnThisDay(); }
    if (id === 'seasons' && !seasonsInitialized) { seasonsInitialized = true; renderSeasonStats(); }
    if (id === 'divisions' && !divisionsInitialized) { divisionsInitialized = true; renderDivisionProgress(); }

    updateURL(id);
}

function goBack() {
    if (navStack.length > 0) {
        const prev = navStack.pop();
        _suppressURLUpdate = true;
        showSection(prev);
        _suppressURLUpdate = false;
        updateURL(prev);
    } else {
        showSection('games');
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('active');
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('active');
}

// Modals
function openModal(id) { document.getElementById(id).classList.add('active'); document.body.style.overflow = 'hidden'; }
function closeModal(id) { document.getElementById(id).classList.remove('active'); document.body.style.overflow = ''; }
function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg; t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

// Player Panel (slide-out)
function openPlayerPanel() {
    document.getElementById('player-panel').classList.add('active');
    document.getElementById('panel-overlay').classList.add('active');
    document.body.style.overflow = 'hidden';
}
function closePlayerPanel() {
    document.getElementById('player-panel').classList.remove('active');
    document.getElementById('panel-overlay').classList.remove('active');
    document.body.style.overflow = '';
    if (playerChart) { playerChart.destroy(); playerChart = null; }
}

// Command Palette
function openCommandPalette() {
    document.getElementById('cmd-palette-overlay').classList.add('active');
    const input = document.getElementById('cmd-palette-input');
    input.value = '';
    document.getElementById('cmd-palette-results').innerHTML = '';
    setTimeout(() => input.focus(), 50);
}
function closeCommandPalette() {
    document.getElementById('cmd-palette-overlay').classList.remove('active');
    _cmdHighlightIdx = -1;
}

let _cmdSearchTimeout = null;
let _cmdHighlightIdx = -1;

function handleCmdSearch(event) {
    if (event.key === 'Escape') { closeCommandPalette(); return; }
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp' || event.key === 'Enter') {
        const items = document.querySelectorAll('.cmd-result-item');
        if (event.key === 'ArrowDown') {
            event.preventDefault();
            _cmdHighlightIdx = Math.min(_cmdHighlightIdx + 1, items.length - 1);
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            _cmdHighlightIdx = Math.max(_cmdHighlightIdx - 1, 0);
        } else if (event.key === 'Enter') {
            if (_cmdHighlightIdx >= 0 && items[_cmdHighlightIdx]) {
                items[_cmdHighlightIdx].click();
            }
            return;
        }
        items.forEach((el, i) => el.classList.toggle('highlighted', i === _cmdHighlightIdx));
        if (items[_cmdHighlightIdx]) items[_cmdHighlightIdx].scrollIntoView({ block: 'nearest' });
        return;
    }

    clearTimeout(_cmdSearchTimeout);
    const query = event.target.value.trim();
    if (query.length < 2) { document.getElementById('cmd-palette-results').innerHTML = ''; _cmdHighlightIdx = -1; return; }
    _cmdSearchTimeout = setTimeout(() => {
        _cmdHighlightIdx = -1;
        const results = performGlobalSearch(query);
        renderCmdResults(results);
    }, 120);
}

function renderCmdResults(results) {
    const container = document.getElementById('cmd-palette-results');
    const hasResults = results.games.length || results.players.length || results.arenas.length;
    if (!hasResults) {
        container.innerHTML = '<div style="padding:1.5rem;text-align:center;color:var(--text-muted);">No results found</div>';
        return;
    }
    let html = '';
    if (results.games.length) {
        html += '<div class="cmd-result-category"><div class="cmd-result-category-label">Games</div>';
        results.games.forEach(g => {
            html += `<div class="cmd-result-item" onclick="selectCmdResult('game','${g.game_id}')">
                <span>${getTeamCode(g.away_team)} @ ${getTeamCode(g.home_team)} (${g.away_score}-${g.home_score})</span>
                <span class="cmd-result-meta">${g.date}</span>
            </div>`;
        });
        html += '</div>';
    }
    if (results.players.length) {
        html += '<div class="cmd-result-category"><div class="cmd-result-category-label">Players</div>';
        results.players.forEach(p => {
            const safeName = (p.Player || '').replace(/'/g, "\\'");
            html += `<div class="cmd-result-item" onclick="selectCmdResult('player','${safeName}')">
                <span>${p.Player}</span>
                <span class="cmd-result-meta">${getTeamCode(p.Team)} | ${p.Games || 0}G</span>
            </div>`;
        });
        html += '</div>';
    }
    if (results.arenas.length) {
        html += '<div class="cmd-result-category"><div class="cmd-result-category-label">Arenas</div>';
        results.arenas.forEach(v => {
            html += `<div class="cmd-result-item" onclick="selectCmdResult('arena','${v.code}')">
                <span>${v.name}</span>
                <span class="cmd-result-meta">${v.team}</span>
            </div>`;
        });
        html += '</div>';
    }
    container.innerHTML = html;
}

function selectCmdResult(type, id) {
    closeCommandPalette();
    if (type === 'game') showBoxScore(id);
    else if (type === 'player') showPlayerDetail(id);
    else if (type === 'arena') showSection('venues');
}

// Dashboard
function renderDashboard() {
    // Last game card
    const games = DATA.games || [];
    const lastGameEl = document.getElementById('dash-last-game');
    if (lastGameEl && games.length > 0) {
        const g = games[0]; // sorted by date descending
        const awayTeam = getShortName(g.away_team) || g.away_team || 'Away';
        const homeTeam = getShortName(g.home_team) || g.home_team || 'Home';
        const awayWon = (g.away_score || 0) > (g.home_score || 0);
        lastGameEl.innerHTML = `<h4>Last Game</h4>
            <div class="game-card" onclick="showBoxScore('${g.game_id}')" style="cursor:pointer;">
                <div class="game-card-date">${g.date}</div>
                <div class="game-card-matchup">
                    <span class="team-score ${awayWon ? 'win' : ''}">${awayTeam} <strong>${g.away_score || 0}</strong></span>
                    <span class="at-symbol">@</span>
                    <span class="team-score ${!awayWon ? 'win' : ''}"><strong>${g.home_score || 0}</strong> ${homeTeam}</span>
                </div>
            </div>`;
    } else if (lastGameEl) {
        lastGameEl.innerHTML = '<h4>Last Game</h4><p style="color:var(--text-muted)">No games yet</p>';
    }

    // On This Day callout
    const onThisDayEl = document.getElementById('dash-onthisday');
    if (onThisDayEl) {
        const today = new Date();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December'];
        const matchingGames = games.filter(g => {
            const d = g.date_yyyymmdd || '';
            return d.length >= 8 && d.slice(4, 6) === mm && d.slice(6, 8) === dd;
        });
        if (matchingGames.length > 0) {
            let html = `<h4>On This Day (${monthNames[parseInt(mm)]} ${parseInt(dd)})</h4>`;
            matchingGames.slice(0, 3).forEach(g => {
                const year = (g.date_yyyymmdd || '').slice(0, 4);
                html += `<div class="dash-milestone-item" style="cursor:pointer" onclick="showBoxScore('${g.game_id}')">
                    <span>${year}: ${getTeamCode(g.away_team)} ${g.away_score} @ ${getTeamCode(g.home_team)} ${g.home_score}</span>
                </div>`;
            });
            if (matchingGames.length > 3) {
                html += `<div style="font-size:0.8rem;color:var(--accent-color);cursor:pointer;padding-top:0.5rem;" onclick="showSection('onthisday')">View all ${matchingGames.length} games...</div>`;
            }
            onThisDayEl.innerHTML = html;
        } else {
            onThisDayEl.innerHTML = `<h4>On This Day (${monthNames[parseInt(mm)]} ${parseInt(dd)})</h4><p style="color:var(--text-muted);font-size:0.88rem;">No games on this date</p>`;
        }
    }

    // Recent milestones (deduplicate by game+player, keep highest tier)
    const recentEl = document.getElementById('dash-recent-milestones');
    if (recentEl) {
        const milestones = DATA.milestones || {};
        const descriptions = DATA.milestone_descriptions || {};
        // Tier priority: earlier in MILESTONE_ORDER = higher tier
        const tierPriority = {};
        MILESTONE_ORDER.forEach((k, i) => { tierPriority[k] = i; });
        const allMilestones = [];
        Object.entries(milestones).forEach(([key, list]) => {
            if (!Array.isArray(list)) return;
            list.forEach(m => {
                allMilestones.push({ ...m, milestoneType: key, description: descriptions[key] || key.replace(/_/g, ' '), _tier: tierPriority[key] ?? 999 });
            });
        });
        // Deduplicate: for same game_id + player, keep the highest tier (lowest _tier number)
        const seen = {};
        const deduped = [];
        // Sort by tier first so we encounter highest tier first
        allMilestones.sort((a, b) => a._tier - b._tier);
        allMilestones.forEach(m => {
            const key = (m.game_id || '') + '|' + (m.player || '');
            if (!seen[key]) {
                seen[key] = true;
                deduped.push(m);
            }
        });
        deduped.sort((a, b) => (b.date_yyyymmdd || '').localeCompare(a.date_yyyymmdd || ''));
        const top5 = deduped.slice(0, 5);

        if (top5.length > 0) {
            let html = '<h4>Recent Milestones</h4>';
            top5.forEach(m => {
                let shortDate = m.date || '';
                const dp = m.date_yyyymmdd || '';
                if (dp.length === 8) {
                    const dt = new Date(dp.slice(0,4)+'-'+dp.slice(4,6)+'-'+dp.slice(6,8)+'T12:00:00');
                    if (!isNaN(dt)) shortDate = dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                }
                const safeName = (m.player || '').replace(/'/g, "\\'");
                html += `<div class="dash-milestone-item">
                    <span><span class="dash-milestone-player" onclick="showPlayerDetail('${safeName}')">${m.player || ''}</span> <span class="dash-milestone-detail">${m.description}</span></span>
                    <span class="dash-milestone-date">${shortDate}</span>
                </div>`;
            });
            recentEl.innerHTML = html;
        } else {
            recentEl.innerHTML = '<h4>Recent Milestones</h4><p style="color:var(--text-muted);font-size:0.88rem;">No milestones yet</p>';
        }
    }

    // Animate number counters
    document.querySelectorAll('.dash-card-number[data-count]').forEach(el => {
        const target = parseInt(el.dataset.count) || 0;
        animateCount(el, 0, target, 800);
    });
}

function animateCount(el, start, end, duration) {
    if (start === end) { el.textContent = end.toLocaleString(); return; }
    const startTime = performance.now();
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease-out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (end - start) * eased);
        el.textContent = current.toLocaleString();
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// Games Grid
function renderGamesGrid() {
    const games = DATA.games || [];
    const grid = document.getElementById('games-grid');

    if (!games.length) {
        grid.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No games found</p>';
        return;
    }

    grid.innerHTML = games.map((g, i) => {
        const awayTeam = getShortName(g.away_team) || g.away_team || 'Away';
        const homeTeam = getShortName(g.home_team) || g.home_team || 'Home';
        const awayScore = g.away_score || 0;
        const homeScore = g.home_score || 0;
        const gameType = g.game_type && g.game_type !== 'regular' ? `<span style="font-size:0.75rem;opacity:0.7;margin-left:0.5rem;">(${g.game_type})</span>` : '';

        // Format: "Away Team 105 @ Home Team 110" or show winner highlighted
        const awayWon = awayScore > homeScore;
        const awayClass = awayWon ? 'win' : '';
        const homeClass = !awayWon ? 'win' : '';

        return `
        <div class="game-card" onclick="showBoxScore('${g.game_id}')">
            <div class="game-card-date">${g.date}${gameType}</div>
            <div class="game-card-matchup">
                <span class="team-score ${awayClass}">${awayTeam} <strong>${awayScore}</strong></span>
                <span class="at-symbol">@</span>
                <span class="team-score ${homeClass}"><strong>${homeScore}</strong> ${homeTeam}</span>
            </div>
        </div>`;
    }).join('');
}

// Format minutes (handles both decimal and MM:SS formats)
function formatMinutes(mp) {
    if (mp == null || mp === '' || mp === '-') return '-';
    if (typeof mp === 'string' && mp.includes(':')) return mp;
    const num = parseFloat(mp);
    if (isNaN(num)) return '-';
    const mins = Math.floor(num);
    const secs = Math.round((num - mins) * 60);
    return secs > 0 ? `${mins}:${secs.toString().padStart(2, '0')}` : `${mins}:00`;
}

function formatPeriod(p) {
    if (p <= 4) return 'Q' + p;
    if (p === 5) return 'OT';
    return (p - 4) + 'OT';
}


function chronoSort(a, b) {
    if (a.startPeriod !== b.startPeriod) return a.startPeriod - b.startPeriod;
    // Higher time remaining = earlier in the period
    return parseFloat(b.startTime || '0') - parseFloat(a.startTime || '0');
}

// Format "away-home" score with leading team label: "114-113 GSW"
function formatScore(scoreStr, awayTeam, homeTeam) {
    if (!scoreStr || !scoreStr.includes('-')) return scoreStr;
    const [away, home] = scoreStr.split('-').map(Number);
    const awayCode = getTeamCode(awayTeam);
    const homeCode = getTeamCode(homeTeam);
    if (away === home) return `${away}-${home}`;
    if (away > home) return `${away}-${home} ${awayCode}`;
    return `${home}-${away} ${homeCode}`;
}

// Box Score Modal
function showBoxScore(gameId) {
    const playerGames = (DATA.player_games || []).filter(p => p.game_id === gameId);
    const gameInfo = (DATA.games || []).find(g => g.game_id === gameId);

    if (!playerGames.length) { showToast('No box score data'); return; }

    const detail = document.getElementById('boxscore-detail');
    const gameType = gameInfo?.game_type && gameInfo.game_type !== 'regular' ? ` (${gameInfo.game_type})` : '';

    // Get away/home info
    const awayTeam = gameInfo?.away_team || '';
    const homeTeam = gameInfo?.home_team || '';
    const awayScore = gameInfo?.away_score || 0;
    const homeScore = gameInfo?.home_score || 0;

    // Group players by team, organizing into away and home
    const teams = {};
    playerGames.forEach(p => {
        const team = p.team || 'Unknown';
        if (!teams[team]) teams[team] = { starters: [], bench: [], isHome: team === homeTeam };
        if (p.starter) {
            teams[team].starters.push(p);
        } else {
            teams[team].bench.push(p);
        }
    });

    // Sort each group by minutes played (descending)
    Object.values(teams).forEach(t => {
        t.starters.sort((a, b) => (b.mp || 0) - (a.mp || 0));
        t.bench.sort((a, b) => (b.mp || 0) - (a.mp || 0));
    });

    // Sort teams: away first, then home
    const sortedTeams = Object.entries(teams).sort((a, b) => a[1].isHome - b[1].isHome);

    const awayWon = awayScore > homeScore;

    const hasBrData = gameInfo?.brShotChart || gameInfo?.brPlusMinus || gameInfo?.brPbp;

    let html = `
    <div class="boxscore-header">
        <div class="boxscore-matchup">
            <span class="boxscore-team-away ${awayWon ? 'winner' : ''}">${awayTeam} <strong>${awayScore}</strong></span>
            <span class="boxscore-at">@</span>
            <span class="boxscore-team-home ${!awayWon ? 'winner' : ''}"><strong>${homeScore}</strong> ${homeTeam}</span>
        </div>
        <div class="date">${gameInfo?.date || ''}${gameType}</div>
    </div>`;

    if (hasBrData) {
        html += `<div class="sub-tabs" style="justify-content:center;">
            <button class="sub-tab active" onclick="showBoxScoreTab('box',this)">Box Score</button>
            ${gameInfo.brShotChart ? '<button class="sub-tab" onclick="showBoxScoreTab(\'shots\',this)">Shot Chart</button>' : ''}
            ${gameInfo.brPlusMinus ? '<button class="sub-tab" onclick="showBoxScoreTab(\'plusminus\',this)">Plus-Minus</button>' : ''}
            ${gameInfo.brPbp ? '<button class="sub-tab" onclick="showBoxScoreTab(\'pbp\',this)">Play-by-Play</button>' : ''}
        </div>`;
    }

    // Box Score tab content
    html += '<div class="bs-tab-content" id="bs-tab-box">';

    // Advanced Game Analysis
    const pbp = gameInfo?.espnPbpAnalysis;
    if (pbp) {
        html += '<div class="game-analysis-section"><h4>Advanced Game Analysis</h4>';

        // Comeback card
        const cb = pbp.biggestComeback;
        if (cb && cb.deficit > 0) {
            html += `<div class="analysis-comeback-card">
                <strong>${cb.team}</strong> overcame a <strong>${cb.deficit}-point</strong> deficit
                (${cb.deficitScore} at ${cb.deficitTime} ${formatPeriod(cb.deficitPeriod)})
                to win ${cb.finalScore}
            </div>`;
        }

        // Scoring Runs (chronological)
        const runs = (pbp.teamScoringRuns || []).slice().sort(chronoSort);
        if (runs.length > 0) {
            html += '<div class="analysis-label">Scoring Runs</div><div class="analysis-pills">';
            runs.forEach(r => {
                const period = r.startPeriod === r.endPeriod ? formatPeriod(r.startPeriod) : `${formatPeriod(r.startPeriod)}-${formatPeriod(r.endPeriod)}`;
                html += `<span class="analysis-pill analysis-pill-run">${r.team} ${r.points}-0 run in ${period} (${formatScore(r.startScore, awayTeam, homeTeam)} → ${formatScore(r.endScore, awayTeam, homeTeam)})</span>`;
            });
            html += '</div>';
        }

        // Decisive Shot
        const shot = pbp.gameWinningShots?.decisiveShot;
        if (shot) {
            html += '<div class="analysis-label">Decisive Shot</div><div class="analysis-pills">';
            html += `<span class="analysis-pill analysis-pill-shot">${shot.player} (${shot.team}) with ${shot.time} left in ${formatPeriod(shot.period)} → ${formatScore(shot.score, awayTeam, homeTeam)}</span>`;
            html += '</div>';
        }

        // Player Scoring Streaks (top 5, chronological)
        const streaks = (pbp.playerPointStreaks || []).slice(0, 5).sort(chronoSort);
        if (streaks.length > 0) {
            html += '<div class="analysis-label">Player Scoring Streaks</div><div class="analysis-pills">';
            streaks.forEach(s => {
                const period = s.startPeriod === s.endPeriod ? formatPeriod(s.startPeriod) : `${formatPeriod(s.startPeriod)}-${formatPeriod(s.endPeriod)}`;
                html += `<span class="analysis-pill analysis-pill-streak">${s.player} scored ${s.points} consecutive pts in ${period} (${formatScore(s.startScore, awayTeam, homeTeam)} → ${formatScore(s.endScore, awayTeam, homeTeam)})</span>`;
            });
            html += '</div>';
        }

        html += '</div>';
    }

    // Render each team's box score (away first, then home)
    sortedTeams.forEach(([teamName, roster]) => {
        html += `
        <div class="boxscore-team-section">
            <div class="boxscore-team-title">${teamName}</div>
            <div class="table-container" style="max-height:none;">
                <table class="boxscore-table">
                    <thead><tr>
                        <th>Player</th><th>MIN</th><th>PTS</th><th>REB</th><th>AST</th>
                        <th>STL</th><th>BLK</th><th>TO</th><th>FG</th><th>3P</th><th>FT</th><th>+/-</th>
                    </tr></thead>
                    <tbody>`;

        // Starters
        if (roster.starters.length > 0) {
            html += `<tr class="roster-divider"><td colspan="12">Starters</td></tr>`;
            roster.starters.forEach(p => {
                html += renderBoxScoreRow(p);
            });
        }

        // Bench
        if (roster.bench.length > 0) {
            html += `<tr class="roster-divider"><td colspan="12">Bench</td></tr>`;
            roster.bench.forEach(p => {
                html += renderBoxScoreRow(p);
            });
        }

        html += '</tbody></table></div></div>';
    });

    html += '</div>'; // end bs-tab-box

    // BR data tabs (rendered lazily)
    if (gameInfo?.brShotChart) html += '<div class="bs-tab-content" id="bs-tab-shots" style="display:none;" data-game-id="' + gameId + '"></div>';
    if (gameInfo?.brPlusMinus) html += '<div class="bs-tab-content" id="bs-tab-plusminus" style="display:none;" data-game-id="' + gameId + '"></div>';
    if (gameInfo?.brPbp) html += '<div class="bs-tab-content" id="bs-tab-pbp" style="display:none;" data-game-id="' + gameId + '"></div>';

    detail.innerHTML = html;
    showSection('boxscore-view');
    updateURL('boxscore', { game: gameId });
}

// Box score sub-tab switching
function showBoxScoreTab(tabId, btn) {
    document.querySelectorAll('.bs-tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('#boxscore-detail .sub-tab').forEach(t => t.classList.remove('active'));
    if (btn) btn.classList.add('active');
    else { const b = document.querySelector(`#boxscore-detail .sub-tab[onclick*="'${tabId}'"]`); if (b) b.classList.add('active'); }

    const tabEl = document.getElementById('bs-tab-' + tabId);
    if (tabEl) {
        tabEl.style.display = 'block';
        // Lazy render
        if (!tabEl.dataset.rendered) {
            const gameId = tabEl.dataset.gameId;
            const gameInfo = (DATA.games || []).find(g => g.game_id === gameId);
            if (gameInfo) {
                if (tabId === 'shots') { _scTeamFilter = 'all'; _scQuarterFilter = 'all'; _scPlayerFilter = 'all'; tabEl.innerHTML = renderShotChart(gameInfo); updateScStatsPanel(); }
                else if (tabId === 'plusminus') tabEl.innerHTML = renderPlusMinus(gameInfo);
                else if (tabId === 'pbp') tabEl.innerHTML = renderPBPLog(gameInfo);
            }
            tabEl.dataset.rendered = '1';
        }
    }
}

// Open box score modal directly to shot chart with a specific shot highlighted
function showBoxScoreWithShot(gameId, shotIdx) {
    showBoxScore(gameId);
    // Switch to shots tab (filters reset to 'all' inside showBoxScoreTab)
    showBoxScoreTab('shots', null);
    // Highlight the shot after a brief delay for DOM rendering
    setTimeout(() => highlightShot(shotIdx), 80);
}

function highlightShot(shotIdx) {
    // Remove any existing highlight
    document.querySelectorAll('.sc-shot-highlight').forEach(el => el.classList.remove('sc-shot-highlight'));
    // Find the shot element
    const el = document.querySelector(`.sc-shot[data-idx="${shotIdx}"]`);
    if (!el) return;
    el.classList.add('sc-shot-highlight');
    // Scroll the court into view
    const court = document.querySelector('.sc-court-container');
    if (court) court.scrollIntoView({ behavior: 'smooth', block: 'center' });
    // Also show the tooltip for it
    const gameId = document.getElementById('bs-tab-shots')?.dataset.gameId;
    const gameInfo = (DATA.games || []).find(g => g.game_id === gameId);
    if (gameInfo?.brShotChart?.shots[shotIdx]) {
        const s = gameInfo.brShotChart.shots[shotIdx];
        const tip = document.getElementById('sc-tooltip');
        if (tip) {
            const result = s.made ? '<span style="color:#27ae60;font-weight:600">Made</span>' : '<span style="color:#e74c3c;font-weight:600">Missed</span>';
            const escapedId = (s.playerId || '').replace(/'/g, "\\'");
            const escapedName = (s.player || '').replace(/'/g, "\\'");
            const distMatch = s.description && s.description.match(/from (\d+) ft/);
            const distStr = distMatch ? ` (${distMatch[1]} ft)` : '';
            tip.innerHTML = `
                <div class="sc-tip-player">${s.player} <span style="color:var(--text-muted)">(${s.team})</span></div>
                <div class="sc-tip-desc">${s.description || 'Shot'}${distStr ? '' : ''}</div>
                <div class="sc-tip-meta">Q${s.quarter} ${result}</div>
                <div class="sc-tip-action"><a href="javascript:void(0)" onclick="filterByPlayer('${escapedId}','${escapedName}')">Show only ${s.player}'s shots</a></div>
            `;
            // Position near the shot using SVG coordinates
            const svg = document.querySelector('.sc-court');
            const container = document.querySelector('.sc-court-container');
            if (svg && container) {
                const svgRect = svg.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                // Convert SVG viewBox coords to pixel position
                const viewBox = svg.viewBox.baseVal;
                const scaleX = svgRect.width / viewBox.width;
                const scaleY = svgRect.height / viewBox.height;
                let left = (s.x - viewBox.x) * scaleX + (svgRect.left - containerRect.left) + 10;
                let top = (s.y - viewBox.y) * scaleY + (svgRect.top - containerRect.top) + 10;
                if (left + 200 > containerRect.width) left -= 220;
                if (top + 100 > containerRect.height) top -= 110;
                tip.style.left = left + 'px';
                tip.style.top = top + 'px';
            }
            tip.classList.add('visible');
        }
    }
}

// Shot Chart
function renderShotChart(gameInfo) {
    const data = gameInfo.brShotChart;
    if (!data || !data.shots || !data.shots.length) return '<p style="text-align:center;color:var(--text-muted);padding:2rem;">No shot chart data</p>';

    const shots = data.shots;
    const awayTeam = getTeamCode(gameInfo.away_team);
    const homeTeam = getTeamCode(gameInfo.home_team);

    // Detect teams from shot data
    const teams = [...new Set(shots.map(s => s.team))];
    const team1 = teams[0] || '';
    const team2 = teams[1] || '';

    // Count quarters
    const quarters = [...new Set(shots.map(s => s.quarter))].sort((a, b) => a - b);

    // Filter bar
    let html = '<div class="sc-filters">';
    html += '<div class="sc-filter-group">';
    html += `<button class="sc-filter-btn active" onclick="filterShotChart('all',null,this)">Both</button>`;
    if (team1) html += `<button class="sc-filter-btn" onclick="filterShotChart('${team1}',null,this)">${team1}</button>`;
    if (team2) html += `<button class="sc-filter-btn" onclick="filterShotChart('${team2}',null,this)">${team2}</button>`;
    html += '</div><div class="sc-filter-group">';
    html += `<button class="sc-filter-btn active" onclick="filterShotChart(null,'all',this)">All</button>`;
    quarters.forEach(q => {
        html += `<button class="sc-filter-btn" onclick="filterShotChart(null,${q},this)">Q${q}</button>`;
    });
    html += '</div>';
    html += '<div class="sc-filter-group" id="sc-player-filter" style="display:none;"><button class="sc-filter-btn active" id="sc-player-filter-btn" onclick="clearPlayerFilter()"></button></div>';
    html += '</div>';

    // Summary stats
    const made = shots.filter(s => s.made).length;
    const total = shots.length;
    const pct = total > 0 ? ((made / total) * 100).toFixed(1) : '0.0';
    html += `<div class="sc-summary" id="sc-summary">${made}/${total} FG (${pct}%)</div>`;

    // SVG court — BR coordinate system: 500px wide, hoop at ~(250,52), y increases toward half-court
    // viewBox expanded to fit deep shots (y up to ~380)
    html += '<div class="sc-court-container">';
    html += '<svg class="sc-court" viewBox="-20 -60 540 460" preserveAspectRatio="xMidYMid meet">';

    const lc = 'var(--border-color)'; // line color
    html += `
        <!-- Baseline -->
        <line x1="0" y1="0" x2="500" y2="0" stroke="${lc}" stroke-width="2"/>
        <!-- Sidelines -->
        <line x1="0" y1="0" x2="0" y2="395" stroke="${lc}" stroke-width="2"/>
        <line x1="500" y1="0" x2="500" y2="395" stroke="${lc}" stroke-width="2"/>
        <!-- Half-court line -->
        <line x1="0" y1="395" x2="500" y2="395" stroke="${lc}" stroke-width="2"/>
        <!-- Paint / key (19ft wide, 16ft from baseline = 160px) -->
        <rect x="170" y="0" width="160" height="190" fill="none" stroke="${lc}" stroke-width="1.5"/>
        <!-- Free throw circle (6ft radius = 60px) -->
        <circle cx="250" cy="190" r="60" fill="none" stroke="${lc}" stroke-width="1.5"/>
        <!-- Restricted area arc (4ft = 40px from hoop center) -->
        <path d="M 220 0 A 40 40 0 0 0 280 0" fill="none" stroke="${lc}" stroke-width="1"/>
        <!-- Backboard -->
        <line x1="220" y1="40" x2="280" y2="40" stroke="${lc}" stroke-width="2"/>
        <!-- Hoop -->
        <circle cx="250" cy="52" r="8" fill="none" stroke="${lc}" stroke-width="1.5"/>
        <!-- Three-point line: corners + arc (radius 224 from hoop at 250,52) -->
        <line x1="30" y1="0" x2="30" y2="92" stroke="${lc}" stroke-width="1.5"/>
        <line x1="470" y1="0" x2="470" y2="92" stroke="${lc}" stroke-width="1.5"/>
        <path d="M 30 92 A 224 224 0 0 0 470 92" fill="none" stroke="${lc}" stroke-width="1.5"/>
        <!-- Center court half-circle -->
        <path d="M 190 395 A 60 60 0 0 1 310 395" fill="none" stroke="${lc}" stroke-width="1.5"/>
    `;

    // Plot shots
    shots.forEach((s, i) => {
        const cx = s.x;
        const cy = s.y;
        const teamClass = `sc-team-${s.team}`;
        const qClass = `sc-q-${s.quarter}`;
        const pClass = `sc-p-${s.playerId || i}`;
        if (s.made) {
            html += `<circle class="sc-shot ${teamClass} ${qClass} ${pClass}" cx="${cx}" cy="${cy}" r="5" fill="rgba(39,174,96,0.8)" stroke="rgba(39,174,96,1)" stroke-width="1" data-idx="${i}"/>`;
        } else {
            html += `<g class="sc-shot ${teamClass} ${qClass} ${pClass}" data-idx="${i}"><line x1="${cx-4}" y1="${cy-4}" x2="${cx+4}" y2="${cy+4}" stroke="rgba(231,76,60,0.8)" stroke-width="2"/><line x1="${cx+4}" y1="${cy-4}" x2="${cx-4}" y2="${cy+4}" stroke="rgba(231,76,60,0.8)" stroke-width="2"/></g>`;
        }
    });

    html += '</svg>';
    // Tooltip (positioned absolutely within the court container)
    html += '<div class="sc-tooltip" id="sc-tooltip"></div>';
    html += '</div>';

    // Legend
    html += '<div class="sc-legend"><span class="sc-legend-item"><svg width="12" height="12"><circle cx="6" cy="6" r="5" fill="rgba(39,174,96,0.8)"/></svg> Made</span>';
    html += '<span class="sc-legend-item"><svg width="12" height="12"><line x1="1" y1="1" x2="11" y2="11" stroke="rgba(231,76,60,0.8)" stroke-width="2"/><line x1="11" y1="1" x2="1" y2="11" stroke="rgba(231,76,60,0.8)" stroke-width="2"/></svg> Missed</span>';
    html += '<span style="margin-left:0.5rem;color:var(--text-muted);font-size:0.75rem;">Click a shot for details</span></div>';

    // Stats panel (updates with filters)
    html += '<div class="sc-stats-panel" id="sc-stats-panel"></div>';

    return html;
}

function _parseDistance(desc) {
    const m = desc && desc.match(/from (\d+) ft/);
    return m ? parseInt(m[1]) : null;
}

function updateScStatsPanel() {
    const panel = document.getElementById('sc-stats-panel');
    if (!panel) return;

    const gameId = document.getElementById('bs-tab-shots')?.dataset.gameId;
    const gameInfo = (DATA.games || []).find(g => g.game_id === gameId);
    if (!gameInfo?.brShotChart?.shots) { panel.innerHTML = ''; return; }

    const allShots = gameInfo.brShotChart.shots;
    const shots = allShots.filter(s => {
        const matchTeam = _scTeamFilter === 'all' || s.team === _scTeamFilter;
        const matchQ = _scQuarterFilter === 'all' || s.quarter === _scQuarterFilter;
        const matchP = _scPlayerFilter === 'all' || (s.playerId || '') === _scPlayerFilter;
        return matchTeam && matchQ && matchP;
    });

    if (!shots.length) { panel.innerHTML = ''; return; }

    // Parse distances
    const withDist = shots.map(s => ({ ...s, dist: _parseDistance(s.description) })).filter(s => s.dist !== null);

    let html = '<div class="sc-stats-grid">';

    // --- Longest Makes ---
    const longestMakes = withDist.filter(s => s.made).sort((a, b) => b.dist - a.dist).slice(0, 5);
    if (longestMakes.length) {
        html += '<div class="sc-stat-card"><h5>Longest Makes</h5><ol class="sc-stat-list">';
        longestMakes.forEach(s => {
            html += `<li><span class="sc-stat-dist">${s.dist} ft</span> <span class="sc-stat-name">${s.player}</span> <span class="sc-stat-meta">Q${s.quarter}</span></li>`;
        });
        html += '</ol></div>';
    }

    // --- Zone Breakdown ---
    const zones = [
        { label: 'Paint', sublabel: '0-4 ft', test: d => d <= 4 },
        { label: 'Mid-Range', sublabel: '5-21 ft', test: d => d >= 5 && d <= 21 },
        { label: 'Three-Point', sublabel: '22+ ft', test: d => d >= 22 },
    ];
    html += '<div class="sc-stat-card"><h5>Shooting Zones</h5><div class="sc-zones">';
    zones.forEach(z => {
        const zShots = withDist.filter(s => z.test(s.dist));
        const made = zShots.filter(s => s.made).length;
        const total = zShots.length;
        const pct = total > 0 ? ((made / total) * 100).toFixed(1) : '-';
        const barWidth = total > 0 ? ((made / total) * 100) : 0;
        html += `<div class="sc-zone-row">
            <div class="sc-zone-label">${z.label}<span class="sc-zone-sub">${z.sublabel}</span></div>
            <div class="sc-zone-bar-bg"><div class="sc-zone-bar-fill" style="width:${barWidth}%"></div></div>
            <div class="sc-zone-val">${made}/${total} <span class="sc-zone-pct">${pct}%</span></div>
        </div>`;
    });
    html += '</div></div>';

    // --- Player Breakdown (top 8 by attempts) ---
    if (_scPlayerFilter === 'all') {
        const playerMap = {};
        withDist.forEach(s => {
            if (!playerMap[s.player]) playerMap[s.player] = { made: 0, total: 0, team: s.team };
            playerMap[s.player].total++;
            if (s.made) playerMap[s.player].made++;
        });
        const players = Object.entries(playerMap).sort((a, b) => b[1].total - a[1].total).slice(0, 8);
        if (players.length > 1) {
            html += '<div class="sc-stat-card sc-stat-card-wide"><h5>Player Breakdown</h5><div class="sc-players-grid">';
            players.forEach(([name, st]) => {
                const pct = st.total > 0 ? ((st.made / st.total) * 100).toFixed(1) : '0.0';
                html += `<div class="sc-player-row">
                    <span class="sc-stat-name">${name}</span>
                    <span class="sc-stat-meta">${st.team}</span>
                    <span class="sc-zone-val">${st.made}/${st.total} <span class="sc-zone-pct">${pct}%</span></span>
                </div>`;
            });
            html += '</div></div>';
        }
    }

    html += '</div>';
    panel.innerHTML = html;
}

// Shot chart active filters (module-level state)
let _scTeamFilter = 'all';
let _scQuarterFilter = 'all';
let _scPlayerFilter = 'all';

function filterShotChart(team, quarter, btn) {
    if (team !== null) _scTeamFilter = team;
    if (quarter !== null) _scQuarterFilter = quarter;

    // Update active buttons in the correct filter group
    if (btn) {
        const group = btn.parentElement;
        group.querySelectorAll('.sc-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    }

    _applyScFilters();
}

function _applyScFilters() {
    // Show/hide shots
    document.querySelectorAll('.sc-shot').forEach(el => {
        const matchTeam = _scTeamFilter === 'all' || el.classList.contains('sc-team-' + _scTeamFilter);
        const matchQ = _scQuarterFilter === 'all' || el.classList.contains('sc-q-' + _scQuarterFilter);
        const matchP = _scPlayerFilter === 'all' || el.classList.contains('sc-p-' + _scPlayerFilter);
        el.style.display = (matchTeam && matchQ && matchP) ? '' : 'none';
    });

    // Update summary
    const gameId = document.getElementById('bs-tab-shots')?.dataset.gameId;
    const gameInfo = (DATA.games || []).find(g => g.game_id === gameId);
    if (gameInfo?.brShotChart) {
        const shots = gameInfo.brShotChart.shots.filter(s => {
            const matchTeam = _scTeamFilter === 'all' || s.team === _scTeamFilter;
            const matchQ = _scQuarterFilter === 'all' || s.quarter === _scQuarterFilter;
            const matchP = _scPlayerFilter === 'all' || (s.playerId || '') === _scPlayerFilter;
            return matchTeam && matchQ && matchP;
        });
        const made = shots.filter(s => s.made).length;
        const total = shots.length;
        const pct = total > 0 ? ((made / total) * 100).toFixed(1) : '0.0';
        const sumEl = document.getElementById('sc-summary');
        if (sumEl) sumEl.textContent = `${made}/${total} FG (${pct}%)`;
    }

    // Update player filter button visibility
    const pfGroup = document.getElementById('sc-player-filter');
    if (pfGroup) pfGroup.style.display = _scPlayerFilter === 'all' ? 'none' : 'flex';

    updateScStatsPanel();
}

function filterByPlayer(playerId, playerName) {
    _scPlayerFilter = playerId;
    const btn = document.getElementById('sc-player-filter-btn');
    if (btn) btn.textContent = playerName + ' \u2715';
    _applyScFilters();
    dismissScTooltip();
}

function clearPlayerFilter() {
    _scPlayerFilter = 'all';
    _applyScFilters();
}

function dismissScTooltip() {
    const tip = document.getElementById('sc-tooltip');
    if (tip) { tip.classList.remove('visible'); }
}

// Click delegation on the SVG court
document.addEventListener('click', function(e) {
    const tip = document.getElementById('sc-tooltip');
    if (!tip) return;

    // Find if we clicked on a shot element (or child of one)
    const shotEl = e.target.closest('.sc-shot');
    if (shotEl) {
        const idx = parseInt(shotEl.dataset.idx);
        const gameId = document.getElementById('bs-tab-shots')?.dataset.gameId;
        const gameInfo = (DATA.games || []).find(g => g.game_id === gameId);
        if (!gameInfo?.brShotChart?.shots[idx]) return;

        const s = gameInfo.brShotChart.shots[idx];
        const result = s.made ? '<span style="color:#27ae60;font-weight:600">Made</span>' : '<span style="color:#e74c3c;font-weight:600">Missed</span>';
        const escapedId = (s.playerId || '').replace(/'/g, "\\'");
        const escapedName = (s.player || '').replace(/'/g, "\\'");

        tip.innerHTML = `
            <div class="sc-tip-player">${s.player} <span style="color:var(--text-muted)">(${s.team})</span></div>
            <div class="sc-tip-desc">${s.description || 'Shot'}</div>
            <div class="sc-tip-meta">Q${s.quarter} ${result}</div>
            <div class="sc-tip-action"><a href="javascript:void(0)" onclick="filterByPlayer('${escapedId}','${escapedName}')">Show only ${s.player}'s shots</a></div>
        `;

        // Position tooltip near the click within the court container
        const container = document.querySelector('.sc-court-container');
        if (container) {
            const rect = container.getBoundingClientRect();
            let left = e.clientX - rect.left + 10;
            let top = e.clientY - rect.top + 10;
            // Keep tooltip in bounds
            if (left + 200 > rect.width) left = left - 220;
            if (top + 100 > rect.height) top = top - 110;
            tip.style.left = left + 'px';
            tip.style.top = top + 'px';
        }
        tip.classList.add('visible');
        e.stopPropagation();
        return;
    }

    // Click outside shot -> dismiss tooltip (but not if clicking inside the tooltip itself)
    if (!e.target.closest('.sc-tooltip')) {
        dismissScTooltip();
    }
});

// Plus-Minus
function renderPlusMinus(gameInfo) {
    const data = gameInfo.brPlusMinus;
    if (!data) return '<p style="text-align:center;color:var(--text-muted);padding:2rem;">No plus-minus data</p>';

    const awayTeam = gameInfo.away_team || 'Away';
    const homeTeam = gameInfo.home_team || 'Home';

    function pmColor(val) {
        if (val > 0) return 'var(--success)';
        if (val < 0) return '#e74c3c';
        return 'var(--text-muted)';
    }

    function pmFormat(val) {
        return val > 0 ? '+' + val : '' + val;
    }

    function renderTeamPM(teamName, players) {
        if (!players || !players.length) return '';
        const sorted = [...players].sort((a, b) => b.net - a.net);
        let html = `<div class="pm-team-section"><div class="boxscore-team-title">${teamName}</div>`;
        html += '<div class="table-container" style="max-height:none;"><table class="pm-table"><thead><tr><th>Player</th><th>On</th><th>Off</th><th>Net</th></tr></thead><tbody>';
        sorted.forEach(p => {
            html += `<tr>
                <td>${p.player}</td>
                <td class="num" style="color:${pmColor(p.on)}">${pmFormat(p.on)}</td>
                <td class="num" style="color:${pmColor(p.off)}">${pmFormat(p.off)}</td>
                <td class="num" style="color:${pmColor(p.net)};font-weight:600">${pmFormat(p.net)}</td>
            </tr>`;
        });
        html += '</tbody></table></div></div>';
        return html;
    }

    return renderTeamPM(awayTeam, data.away) + renderTeamPM(homeTeam, data.home);
}

// Play-by-Play Log
function renderPBPLog(gameInfo) {
    const data = gameInfo.brPbp;
    if (!data || !data.plays || !data.plays.length) return '<p style="text-align:center;color:var(--text-muted);padding:2rem;">No play-by-play data</p>';

    const plays = data.plays;
    const quarters = [...new Set(plays.map(p => p.quarter))].sort((a, b) => a - b);

    // Quarter jump buttons
    let html = '<div class="pbp-quarter-btns">';
    quarters.forEach(q => {
        if (q > 0) html += `<button class="sc-filter-btn" onclick="document.getElementById('pbp-q-${q}').scrollIntoView({behavior:'smooth',block:'start'})">Q${q}</button>`;
    });
    html += '</div>';

    html += '<div class="pbp-log-container"><table class="pbp-table"><thead><tr><th class="pbp-time">Time</th><th class="pbp-away">Away</th><th class="pbp-score">Score</th><th class="pbp-home">Home</th></tr></thead><tbody>';

    let currentQ = 0;
    plays.forEach(p => {
        if (p.quarter !== currentQ && p.quarter > 0) {
            currentQ = p.quarter;
            html += `<tr class="pbp-quarter-header" id="pbp-q-${currentQ}"><td colspan="4">${formatPeriod(currentQ)}</td></tr>`;
        }

        if (!p.teamSide) {
            // Neutral event
            html += `<tr class="pbp-neutral"><td class="pbp-time">${p.time}</td><td colspan="3" class="pbp-center">${p.action}</td></tr>`;
        } else {
            const isScoring = p.awayScore !== null && p.homeScore !== null;
            const rowClass = isScoring ? ' class="pbp-scoring"' : '';
            const awayAction = p.teamSide === 'away' ? p.action : '';
            const homeAction = p.teamSide === 'home' ? p.action : '';
            const scoreStr = p.score || '';
            html += `<tr${rowClass}><td class="pbp-time">${p.time}</td><td class="pbp-away">${awayAction}</td><td class="pbp-score">${scoreStr}</td><td class="pbp-home">${homeAction}</td></tr>`;
        }
    });

    html += '</tbody></table></div>';
    return html;
}

function renderBoxScoreRow(p) {
    return `<tr>
        <td><span class="player-link" onclick="event.stopPropagation();showPlayerDetail('${(p.player||'').replace(/'/g, "\'")}')">${p.player}</span></td>
        <td class="num">${formatMinutes(p.mp)}</td>
        <td class="num">${p.pts || 0}</td>
        <td class="num">${p.trb || 0}</td>
        <td class="num">${p.ast || 0}</td>
        <td class="num">${p.stl || 0}</td>
        <td class="num">${p.blk || 0}</td>
        <td class="num">${p.tov || 0}</td>
        <td class="num">${p.fg || 0}-${p.fga || 0}</td>
        <td class="num">${p.fg3 || 0}-${p.fg3a || 0}</td>
        <td class="num">${p.ft || 0}-${p.fta || 0}</td>
        <td class="num">${p.plus_minus || 0}</td>
    </tr>`;
}

// Players Table
const playerCols = [
    'Player', 'Team', 'Games', 'MPG', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'TOPG',
    'FG%', '3P%', 'FT%', 'TS%', 'eFG%', 'Total PTS', 'Total REB', 'Total AST', 'Total +/-'
];

// Tooltips for stat abbreviations
const statTooltips = {
    'MPG': 'Minutes Per Game',
    'PPG': 'Points Per Game',
    'RPG': 'Rebounds Per Game',
    'APG': 'Assists Per Game',
    'SPG': 'Steals Per Game',
    'BPG': 'Blocks Per Game',
    'TOPG': 'Turnovers Per Game',
    'FG%': 'Field Goal Percentage',
    '3P%': 'Three-Point Percentage',
    'FT%': 'Free Throw Percentage',
    'TS%': 'True Shooting Percentage',
    'eFG%': 'Effective Field Goal Percentage',
    'Total PTS': 'Total Points Scored',
    'Total REB': 'Total Rebounds',
    'Total AST': 'Total Assists',
    'Total +/-': 'Cumulative Plus/Minus'
};

// Columns that should show 1 decimal (per-game stats)
const perGameCols = ['MPG', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'TOPG'];
// Columns that should show 3 decimals (percentages)
const pctCols = ['FG%', '3P%', 'FT%', 'TS%', 'eFG%'];

function formatStatValue(val, col) {
    if (val == null || val === '') return '';
    if (typeof val !== 'number') return val;
    if (pctCols.includes(col)) return val.toFixed(3);
    if (perGameCols.includes(col)) return val.toFixed(1);
    return Number.isInteger(val) ? val : val.toFixed(1);
}

function renderPlayersTable() {
    const table = document.getElementById('players-table');
    const data = filteredPlayers;

    if (!data || !data.length) {
        table.innerHTML = '<tr><td colspan="20" style="text-align:center;padding:2rem;">No players</td></tr>';
        return;
    }

    let html = '<thead><tr>' + playerCols.map(c => {
        const tooltip = statTooltips[c] ? ` title="${statTooltips[c]}"` : '';
        const sortIndicator = playerSortCol === c ? (playerSortAsc ? ' \u25B2' : ' \u25BC') : '';
        const activeClass = playerSortCol === c ? ' class="sort-active"' : '';
        return `<th onclick="sortPlayersTable('${c}')"${tooltip}${activeClass}>${c}${sortIndicator}</th>`;
    }).join('') + '</tr></thead><tbody>';
    data.forEach(row => {
        html += '<tr>';
        playerCols.forEach(col => {
            let v = row[col];
            if (v == null) v = '';
            if (typeof v === 'number') {
                v = formatStatValue(v, col);
                html += `<td class="num">${v}</td>`;
            } else if (col === 'Player') {
                html += `<td><span class="player-link" onclick="showPlayerDetail('${(v||'').replace(/'/g, "\\'")}')">${v}</span></td>`;
            } else if (col === 'Team') {
                html += `<td>${getTeamCode(v)}</td>`;
            } else {
                html += `<td>${v}</td>`;
            }
        });
        html += '</tr>';
    });
    table.innerHTML = html + '</tbody>';
}

function sortPlayersTable(col) {
    // Toggle direction if same column, otherwise default to descending for numbers, ascending for text
    if (playerSortCol === col) {
        playerSortAsc = !playerSortAsc;
    } else {
        playerSortCol = col;
        // Default: numbers sort descending (highest first), text sorts ascending (A-Z)
        const isNumericCol = filteredPlayers.length > 0 && typeof filteredPlayers[0][col] === 'number';
        playerSortAsc = !isNumericCol;
    }

    filteredPlayers.sort((a, b) => {
        let av = a[col], bv = b[col];
        if (av == null) av = '';
        if (bv == null) bv = '';

        let result;
        if (typeof av === 'number' && typeof bv === 'number') {
            result = av - bv;
        } else {
            result = String(av).localeCompare(String(bv));
        }

        return playerSortAsc ? result : -result;
    });
    renderPlayersTable();
}

function filterPlayersTable() {
    const search = document.getElementById('players-search').value.toLowerCase();
    const team = document.getElementById('players-team').value;
    const minG = parseInt(document.getElementById('players-min-games').value) || 0;

    filteredPlayers = (DATA.players || []).filter(p => {
        if (search && !Object.values(p).some(v => String(v).toLowerCase().includes(search))) return false;
        if (team && !String(p.Team || '').includes(team)) return false;
        if (minG && (p.Games || 0) < minG) return false;
        return true;
    });
    renderPlayersTable();
}

function clearPlayersFilters() {
    document.getElementById('players-search').value = '';
    document.getElementById('players-team').value = '';
    document.getElementById('players-min-games').value = '';
    playerSortCol = null;
    playerSortAsc = false;
    filterPlayersTable();
}

function populateTeamDropdown() {
    const teams = new Set();
    (DATA.players || []).forEach(p => { if (p.Team) p.Team.split(', ').forEach(t => teams.add(t)); });
    const sel = document.getElementById('players-team');
    Array.from(teams).sort().forEach(t => {
        const o = document.createElement('option'); o.value = t; o.textContent = t; sel.appendChild(o);
    });
}

// Player Detail with Chart
let playerChart = null;

function showPlayerDetail(name) {
    const games = (DATA.player_games || []).filter(g => g.player === name).sort((a,b) => (b.date_yyyymmdd||'').localeCompare(a.date_yyyymmdd||''));
    const stats = (DATA.players || []).find(p => p.Player === name);

    if (!stats && !games.length) { showToast('Player not found'); return; }

    let html = `<h2>${name}</h2>`;
    if (stats) {
        html += `<p style="color:var(--text-secondary);margin-bottom:1rem;">${stats.Team || ''} | ${stats.Games || 0} games</p>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.75rem;margin-bottom:1.5rem;">
            <div class="player-stat-box"><div class="number">${(stats.PPG||0).toFixed(1)}</div><div class="label">PPG</div></div>
            <div class="player-stat-box"><div class="number">${(stats.RPG||0).toFixed(1)}</div><div class="label">RPG</div></div>
            <div class="player-stat-box"><div class="number">${(stats.APG||0).toFixed(1)}</div><div class="label">APG</div></div>
            <div class="player-stat-box"><div class="number">${(stats.MPG||0).toFixed(1)}</div><div class="label">MPG</div></div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin-bottom:1.5rem;">
            <div style="text-align:center;"><strong>${((stats['FG%']||0)*100).toFixed(1)}%</strong><br><small>FG%</small></div>
            <div style="text-align:center;"><strong>${((stats['3P%']||0)*100).toFixed(1)}%</strong><br><small>3P%</small></div>
            <div style="text-align:center;"><strong>${((stats['FT%']||0)*100).toFixed(1)}%</strong><br><small>FT%</small></div>
        </div>`;
    }

    // Add chart section if multiple games
    if (games.length > 1) {
        html += `
        <div class="chart-section">
            <div class="chart-header">
                <h4>Performance Trend</h4>
                <div class="chart-toggles">
                    <button class="chart-toggle active" data-stat="pts">PTS</button>
                    <button class="chart-toggle" data-stat="trb">REB</button>
                    <button class="chart-toggle" data-stat="ast">AST</button>
                    <button class="chart-toggle" data-stat="game_score">GmSc</button>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="player-chart"></canvas>
            </div>
        </div>`;
    }

    if (games.length) {
        html += '<h4 style="margin-top:1.5rem;margin-bottom:0.5rem;">Game Log</h4><div class="table-container" style="max-height:250px;"><table><thead><tr><th>Date</th><th>Opp</th><th>MIN</th><th>PTS</th><th>REB</th><th>AST</th><th>STL</th><th>BLK</th><th>FG</th><th>+/-</th></tr></thead><tbody>';
        games.forEach(g => html += `<tr><td>${g.date||''}</td><td>${g.opponent||''}</td><td>${formatMinutes(g.mp)}</td><td>${g.pts||0}</td><td>${g.trb||0}</td><td>${g.ast||0}</td><td>${g.stl||0}</td><td>${g.blk||0}</td><td>${g.fg||0}-${g.fga||0}</td><td>${g.plus_minus||0}</td></tr>`);
        html += '</tbody></table></div>';
    }

    document.getElementById('player-detail').innerHTML = html;
    openPlayerPanel();

    // Initialize chart after DOM update
    if (games.length > 1) {
        setTimeout(() => initPlayerChart(games, 'pts'), 100);

        // Add toggle listeners
        document.querySelectorAll('.chart-toggle').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.chart-toggle').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                initPlayerChart(games, e.target.dataset.stat);
            });
        });
    }
}

function initPlayerChart(games, stat) {
    const ctx = document.getElementById('player-chart');
    if (!ctx) return;

    if (playerChart) {
        playerChart.destroy();
    }

    // Reverse for chart (oldest to newest, left to right)
    const chartGames = [...games].reverse();

    const labels = chartGames.map(g => {
        const d = g.date || '';
        // Shorten date for display
        const parts = d.split(' ');
        return parts.length >= 3 ? `${parts[0].slice(0,3)} ${parts[1].replace(',','')} '${parts[2].slice(2)}` : parts.length >= 2 ? `${parts[0].slice(0,3)} ${parts[1].replace(',','')}` : d;
    });

    const data = chartGames.map(g => g[stat] || 0);
    const avg = data.reduce((a,b) => a+b, 0) / data.length;

    const statLabels = { pts: 'Points', trb: 'Rebounds', ast: 'Assists', game_score: 'Game Score' };
    const statColors = { pts: '#4ade80', trb: '#60a5fa', ast: '#f472b6', game_score: '#fbbf24' };

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
    const textColor = isDark ? '#b0b0b0' : '#666666';

    playerChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: statLabels[stat] || stat,
                data: data,
                borderColor: statColors[stat] || '#4ade80',
                backgroundColor: (statColors[stat] || '#4ade80') + '20',
                fill: true,
                tension: 0.3,
                pointRadius: 5,
                pointHoverRadius: 7,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: (items) => chartGames[items[0].dataIndex]?.date || '',
                        afterLabel: (item) => `vs ${chartGames[item.dataIndex]?.opponent || ''}`
                    }
                },
                annotation: {
                    annotations: {
                        avgLine: {
                            type: 'line',
                            yMin: avg,
                            yMax: avg,
                            borderColor: 'rgba(255,255,255,0.5)',
                            borderWidth: 1,
                            borderDash: [5, 5],
                            label: {
                                display: true,
                                content: `Avg: ${avg.toFixed(1)}`,
                                position: 'end'
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: textColor, maxRotation: 45 }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                }
            }
        }
    });
}

// Venues
function renderVenuesTable() {
    const venues = DATA.venues || [];
    const visited = venues.filter(v => v.visited).length;
    document.getElementById('arena-progress-fill').style.width = `${(visited/30)*100}%`;
    document.getElementById('arena-progress-text').textContent = `${visited}/30 Arenas Visited`;
    filterVenuesTable();
}

function filterVenuesTable() {
    const filter = document.getElementById('venues-filter').value;
    let venues = DATA.venues || [];
    if (filter === 'visited') venues = venues.filter(v => v.visited);
    else if (filter === 'unvisited') venues = venues.filter(v => !v.visited);

    const tbody = document.querySelector('#venues-table tbody');
    tbody.innerHTML = venues.map(v => `
        <tr>
            <td>${v.team}</td>
            <td>${v.name}</td>
            <td>${v.city}</td>
            <td>${v.state}</td>
            <td class="num">${v.games}</td>
            <td>${v.first_visit || '-'}</td>
            <td class="${v.visited ? 'status-visited' : 'status-not-visited'}">${v.visited ? '✓ Visited' : 'Not Yet'}</td>
        </tr>
    `).join('');
}

// Map
function initMap() {
    arenaMap = L.map('arena-map').setView([39.8, -98.5], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(arenaMap);
    (DATA.venues || []).forEach(v => {
        const color = v.visited ? '#27ae60' : '#95a5a6';
        L.circleMarker([v.lat, v.lng], { radius: 10, fillColor: color, color: '#fff', weight: 2, fillOpacity: 0.9 })
            .addTo(arenaMap)
            .bindPopup(`<strong>${v.team}</strong><br>${v.name}<br>${v.city}, ${v.state}<br><em>${v.visited ? v.games + ' games' : 'Not visited'}</em>`);
    });
}

// Constants are auto-generated at the start of this script

// Team Checklist
let currentChecklistView = 'all';

function renderTeamChecklist() {
    const checklist = DATA.teamChecklist || {};
    const teams = checklist.teams || [];
    const divisions = checklist.divisions || {};
    const conferences = checklist.conferences || {};
    const summary = checklist.summary || { teamsSeen: 0, totalTeams: 30 };

    // Update progress bar
    document.getElementById('team-progress-fill').style.width = `${(summary.teamsSeen/30)*100}%`;
    document.getElementById('team-progress-text').textContent = `${summary.teamsSeen}/30 Teams Seen`;

    showChecklistView(currentChecklistView);
}

function showChecklistView(view) {
    currentChecklistView = view;
    const container = document.getElementById('team-checklist-container');
    const checklist = DATA.teamChecklist || {};
    const teams = checklist.teams || [];
    const divisions = checklist.divisions || {};
    const conferences = checklist.conferences || {};

    // Update tab styling
    document.querySelectorAll('.checklist-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-view="${view}"]`)?.classList.add('active');

    let html = '';

    if (view === 'all') {
        // Show all teams in a single grid
        const seen = teams.filter(t => t.seen).length;
        html = `
            <div class="division-card ${seen === 30 ? 'complete' : ''}">
                <div class="division-header">
                    <h4>All NBA Teams</h4>
                    <span class="badge ${seen === 30 ? 'badge-complete' : 'badge-progress'}">${seen}/30</span>
                </div>
                <div class="team-grid">
                    ${teams.sort((a,b) => a.name.localeCompare(b.name)).map(t => `
                        <div class="team-item ${t.seen ? 'seen' : ''}">
                            <span class="${t.seen ? 'check' : 'not-seen'}">${t.seen ? '✓' : '○'}</span>
                            <span>${getShortName(t.name)}</span>
                            ${t.visitCount > 0 ? `<span class="visit-count">${t.visitCount}x</span>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>`;
    } else if (view === 'east' || view === 'west') {
        const conf = view === 'east' ? 'East' : 'West';
        const confData = conferences[conf] || { teamsSeen: 0, totalTeams: 15, divisions: [] };
        const divNames = view === 'east' ? ['Atlantic', 'Central', 'Southeast'] : ['Northwest', 'Pacific', 'Southwest'];

        html = `
            <div class="conference-summary">
                <div class="conference-box ${confData.teamsSeen === 15 ? 'complete' : ''}">
                    <h5>${conf}ern Conference</h5>
                    <div class="count">${confData.teamsSeen}/15</div>
                </div>
            </div>`;

        divNames.forEach(divName => {
            const div = divisions[divName] || { teams: [], teamsSeen: 0, totalTeams: 5 };
            html += `
                <div class="division-card ${div.complete ? 'complete' : ''}">
                    <div class="division-header">
                        <h4>${divName} Division</h4>
                        <span class="badge ${div.complete ? 'badge-complete' : 'badge-progress'}">${div.teamsSeen}/${div.totalTeams}</span>
                    </div>
                    <div class="team-grid">
                        ${(div.teams || []).map(t => `
                            <div class="team-item ${t.seen ? 'seen' : ''}">
                                <span class="${t.seen ? 'check' : 'not-seen'}">${t.seen ? '✓' : '○'}</span>
                                <span>${getShortName(t.name)}</span>
                                ${t.visitCount > 0 ? `<span class="visit-count">${t.visitCount}x</span>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>`;
        });
    } else if (view === 'divisions') {
        // Show conference summaries first
        html = `<div class="conference-summary">`;
        ['East', 'West'].forEach(conf => {
            const confData = conferences[conf] || { teamsSeen: 0, totalTeams: 15 };
            html += `
                <div class="conference-box ${confData.teamsSeen === 15 ? 'complete' : ''}">
                    <h5>${conf}ern</h5>
                    <div class="count">${confData.teamsSeen}/15</div>
                </div>`;
        });
        html += '</div>';

        // Show all divisions
        const divOrder = ['Atlantic', 'Central', 'Southeast', 'Northwest', 'Pacific', 'Southwest'];
        divOrder.forEach(divName => {
            const div = divisions[divName] || { teams: [], teamsSeen: 0, totalTeams: 5, conference: '' };
            html += `
                <div class="division-card ${div.complete ? 'complete' : ''}">
                    <div class="division-header">
                        <h4>${divName} <small style="font-weight:normal;color:var(--text-muted);">(${div.conference || ''})</small></h4>
                        <span class="badge ${div.complete ? 'badge-complete' : 'badge-progress'}">${div.teamsSeen}/${div.totalTeams}</span>
                    </div>
                    <div class="team-grid">
                        ${(div.teams || []).map(t => `
                            <div class="team-item ${t.seen ? 'seen' : ''}">
                                <span class="${t.seen ? 'check' : 'not-seen'}">${t.seen ? '✓' : '○'}</span>
                                <span>${getShortName(t.name)}</span>
                                ${t.visitCount > 0 ? `<span class="visit-count">${t.visitCount}x</span>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>`;
        });
    }

    container.innerHTML = html;
}

// MILESTONE_CATEGORIES is auto-generated from Python constants

// Master order for displaying all milestones (grouped by category)
const MILESTONE_ORDER = [
    // Multi-stat achievements
    'quadruple_doubles', 'triple_doubles', 'near_triple_doubles', 'double_doubles', 'near_double_doubles',
    'five_by_fives', 'all_around_games',
    // Scoring (high to low)
    'seventy_point_games', 'sixty_point_games', 'fifty_point_games', 'forty_five_point_games',
    'forty_point_games', 'thirty_five_point_games', 'thirty_point_games', 'twenty_five_point_games', 'twenty_point_games',
    // Combined stats
    'twenty_twenty_games', 'thirty_ten_games', 'twenty_five_ten_games', 'twenty_ten_five_games',
    'twenty_ten_games', 'points_assists_double_double',
    // Rebounding (high to low)
    'twenty_five_rebound_games', 'twenty_rebound_games', 'eighteen_rebound_games',
    'fifteen_rebound_games', 'twelve_rebound_games', 'ten_rebound_games',
    // Assists (high to low)
    'twenty_assist_games', 'fifteen_assist_games', 'twelve_assist_games', 'ten_assist_games',
    // Three-pointers
    'ten_three_games', 'eight_three_games', 'seven_three_games', 'six_three_games', 'five_three_games', 'perfect_from_three',
    // Steals (high to low)
    'ten_steal_games', 'seven_steal_games', 'five_steal_games', 'four_steal_games',
    // Blocks (high to low)
    'ten_block_games', 'seven_block_games', 'five_block_games', 'four_block_games',
    // Efficiency
    'high_game_score', 'efficient_scoring_games', 'hot_shooting_games', 'perfect_fg_games', 'perfect_ft_games',
    // Defensive
    'defensive_monster_games', 'zero_turnover_games',
    // Plus/Minus
    'plus_25_games', 'plus_20_games', 'minus_25_games'
];

function renderMilestones() {
    filterMilestones();
}

function filterMilestones() {
    const category = document.getElementById('milestone-category').value;
    const search = document.getElementById('milestone-search').value.toLowerCase();
    const container = document.getElementById('milestones-container');
    const milestones = DATA.milestones || {};
    const descriptions = DATA.milestone_descriptions || {};

    let keysToShow = [];
    if (category === 'all') {
        // Use master order for "all" view to group related stats together
        keysToShow = MILESTONE_ORDER.filter(k => milestones[k] && milestones[k].length > 0);
        // Also include any milestones not in the master order
        Object.keys(milestones).forEach(k => {
            if (!keysToShow.includes(k) && milestones[k] && milestones[k].length > 0) {
                keysToShow.push(k);
            }
        });
    } else {
        keysToShow = (MILESTONE_CATEGORIES[category] || []).filter(k => milestones[k] && milestones[k].length > 0);
    }

    let html = '';
    keysToShow.forEach(key => {
        let data = milestones[key] || [];

        // Sort by date descending (most recent first)
        data = [...data].sort((a, b) => (b.date_yyyymmdd || '').localeCompare(a.date_yyyymmdd || ''));

        // Filter by search
        if (search) {
            data = data.filter(m => m.player?.toLowerCase().includes(search) || m.team?.toLowerCase().includes(search));
        }

        if (data.length === 0 && search) return;

        const title = descriptions[key] || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        html += `<div class="milestone-card">
            <h4>${title} <span class="count">${data.length}</span></h4>`;

        if (data.length === 0) {
            html += '<p class="empty">None recorded</p>';
        } else {
            html += '<div class="table-container" style="max-height:300px;"><table><thead><tr><th>Date</th><th>Player</th><th>Matchup</th><th>Line</th></tr></thead><tbody>';
            data.slice(0, 50).forEach(m => {
                // Shorten date: "February 22, 2026" -> "Feb 22, 2026"
                let shortDate = m.date || '';
                const dp = (m.date_yyyymmdd || '');
                if (dp.length === 8) {
                    const dt = new Date(dp.slice(0,4) + '-' + dp.slice(4,6) + '-' + dp.slice(6,8) + 'T12:00:00');
                    if (!isNaN(dt)) shortDate = dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                }
                // Clickable date -> box score
                const gameId = m.game_id || '';
                const dateCell = gameId ? `<td class="game-link" onclick="showBoxScore('${gameId}')">${shortDate}</td>` : `<td>${shortDate}</td>`;
                // Matchup: "GSW vs DEN"
                const matchup = `${getTeamCode(m.team || '')} vs ${getTeamCode(m.opponent || '')}`;
                // Build stat line from stats object when available
                let line = '';
                const st = m.stats;
                if (st) {
                    const mt = m.milestone_type || key;
                    if (mt.includes('five_by_five') || mt.includes('all_around')) {
                        line = `${st.pts||0} pts/${st.trb||0} reb/${st.ast||0} ast/${st.stl||0} stl/${st.blk||0} blk`;
                    } else if (mt.includes('triple_double') || mt.includes('double_double')) {
                        line = `${st.pts||0} pts/${st.trb||0} reb/${st.ast||0} ast`;
                    } else if (mt.includes('point_game') || mt.includes('scoring')) {
                        line = `${st.pts||0} pts`;
                    } else if (mt.includes('rebound')) {
                        line = `${st.trb||0} reb`;
                    } else if (mt.includes('assist')) {
                        line = `${st.ast||0} ast`;
                    } else if (mt.includes('steal')) {
                        line = `${st.stl||0} stl`;
                    } else if (mt.includes('block')) {
                        line = `${st.blk||0} blk`;
                    } else if (mt.includes('three')) {
                        line = `${st.fg3||0}-${st.fg3a||0} 3PT`;
                    } else if (mt.includes('ft') || mt.includes('free_throw')) {
                        line = `${st.ft||0}-${st.fta||0} FT`;
                    } else if (mt.includes('fg') && mt.includes('perfect')) {
                        line = `${st.fg||0}-${st.fga||0} FG`;
                    } else if (mt.includes('turnover')) {
                        line = `${st.tov||0} TO, ${Math.round(st.mp||0)} min`;
                    } else if (mt.includes('plus') || mt.includes('minus')) {
                        const pm = st.plus_minus||0;
                        line = `${pm > 0 ? '+' : ''}${pm}`;
                    } else if (mt.includes('shooting') || mt.includes('efficient') || mt.includes('game_score')) {
                        line = `${st.pts||0} pts`;
                    } else {
                        line = m.detail || '';
                    }
                } else {
                    line = m.detail || '';
                }
                html += `<tr>
                    ${dateCell}
                    <td><span class="player-link" onclick="showPlayerDetail('${(m.player||'').replace(/'/g, "\\'")}')">${m.player || ''}</span></td>
                    <td>${matchup}</td>
                    <td class="num">${line}</td>
                </tr>`;
            });
            if (data.length > 50) html += `<tr><td colspan="4" style="text-align:center;color:var(--text-muted);">...and ${data.length - 50} more</td></tr>`;
            html += '</tbody></table></div>';
        }
        html += '</div>';
    });

    if (!html) {
        html = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No milestones found</p>';
    }

    container.innerHTML = html;
}

// CSV Download
function downloadCSV(type) {
    const data = type === 'players' ? filteredPlayers : null;
    if (!data || !data.length) { showToast('No data'); return; }
    const headers = playerCols;
    const csv = [headers.join(','), ...data.map(r => headers.map(h => {
        let v = r[h]; if (v == null) v = '';
        if (typeof v === 'string' && (v.includes(',') || v.includes('"'))) v = '"' + v.replace(/"/g, '""') + '"';
        return v;
    }).join(','))].join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
    a.download = 'nba_players.csv'; a.click();
    showToast('Download started');
}

// Stat Leaders
function renderLeaders() {
    const players = DATA.players || [];
    const grid = document.getElementById('leaders-grid');

    if (!players.length) {
        grid.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No player data</p>';
        return;
    }

    const categories = [
        { key: 'PPG', label: 'Points Per Game', format: v => v.toFixed(1) },
        { key: 'RPG', label: 'Rebounds Per Game', format: v => v.toFixed(1) },
        { key: 'APG', label: 'Assists Per Game', format: v => v.toFixed(1) },
        { key: 'SPG', label: 'Steals Per Game', format: v => v.toFixed(1) },
        { key: 'BPG', label: 'Blocks Per Game', format: v => v.toFixed(1) },
        { key: 'FG%', label: 'Field Goal %', format: v => (v * 100).toFixed(1) + '%' },
        { key: '3P%', label: 'Three-Point %', format: v => (v * 100).toFixed(1) + '%' },
        { key: 'FT%', label: 'Free Throw %', format: v => (v * 100).toFixed(1) + '%' },
        { key: 'Total PTS', label: 'Total Points', format: v => v.toLocaleString() },
        { key: 'Total REB', label: 'Total Rebounds', format: v => v.toLocaleString() },
        { key: 'Total AST', label: 'Total Assists', format: v => v.toLocaleString() },
        { key: 'Total +/-', label: 'Total Plus/Minus', format: v => (v >= 0 ? '+' : '') + v },
    ];

    grid.innerHTML = categories.map(cat => {
        // Sort players by this stat and take top 5
        const sorted = [...players]
            .filter(p => p[cat.key] != null && p.Games >= 2)
            .sort((a, b) => b[cat.key] - a[cat.key])
            .slice(0, 5);

        return `
        <div class="leader-card">
            <h4>${cat.label}</h4>
            <ul class="leader-list">
                ${sorted.map((p, i) => `
                    <li class="leader-item">
                        <span class="leader-rank">${i + 1}</span>
                        <span class="leader-name" onclick="showPlayerDetail('${(p.Player||'').replace(/'/g, "\\'")}')">${p.Player}</span>
                        <span class="leader-team">${getTeamCode(p.Team)}</span>
                        <span class="leader-value">${cat.format(p[cat.key])}</span>
                    </li>
                `).join('')}
            </ul>
        </div>`;
    }).join('');
}

// Career Firsts
function renderCareerFirsts(filter = 'all', search = '') {
    const container = document.getElementById('career-firsts-container');
    if (!container) return;

    const firsts = DATA.careerFirsts || [];
    if (!firsts.length) {
        container.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No career firsts found. Run the career firsts scraper to populate this data.</p>';
        return;
    }

    // Filter
    let filtered = firsts;
    if (filter !== 'all') {
        filtered = filtered.filter(f => f.category === filter);
    }
    if (search) {
        const searchLower = search.toLowerCase();
        filtered = filtered.filter(f =>
            (f.player_name || '').toLowerCase().includes(searchLower) ||
            (f.milestone || '').toLowerCase().includes(searchLower)
        );
    }

    if (!filtered.length) {
        container.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No matching career firsts found.</p>';
        return;
    }

    // Group by category for display
    const firstsGroup = filtered.filter(f => f.category === 'first');
    const milestonesGroup = filtered.filter(f => f.category === 'milestone');

    let html = '';

    if (firstsGroup.length > 0 && (filter === 'all' || filter === 'first')) {
        html += `
            <div class="milestone-group">
                <h3 class="milestone-group-title">🌟 Career Firsts (${firstsGroup.length})</h3>
                <div class="milestone-cards">
                    ${firstsGroup.map(f => `
                        <div class="milestone-card career-first">
                            <div class="milestone-header">
                                <span class="milestone-player">${f.player_name || f.player_id}</span>
                                <span class="milestone-date">${formatCareerFirstDate(f.date)}</span>
                            </div>
                            <div class="milestone-detail">${f.milestone}</div>
                            <div class="milestone-meta">vs ${f.opponent || 'Unknown'}</div>
                        </div>
                    `).join('')}
                </div>
            </div>`;
    }

    if (milestonesGroup.length > 0 && (filter === 'all' || filter === 'milestone')) {
        html += `
            <div class="milestone-group">
                <h3 class="milestone-group-title">🏆 Career Milestones (${milestonesGroup.length})</h3>
                <div class="milestone-cards">
                    ${milestonesGroup.map(f => `
                        <div class="milestone-card career-milestone">
                            <div class="milestone-header">
                                <span class="milestone-player">${f.player_name || f.player_id}</span>
                                <span class="milestone-date">${formatCareerFirstDate(f.date)}</span>
                            </div>
                            <div class="milestone-detail">${f.milestone}</div>
                            <div class="milestone-meta">vs ${f.opponent || 'Unknown'}${f.career_total_after ? ` • Career total: ${f.career_total_after.toLocaleString()}` : ''}</div>
                        </div>
                    `).join('')}
                </div>
            </div>`;
    }

    container.innerHTML = html || '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No career firsts found.</p>';
}

function formatCareerFirstDate(dateStr) {
    if (!dateStr) return '';
    // Format: YYYYMMDD -> MM/DD/YYYY
    if (dateStr.length === 8 && /^\d{8}$/.test(dateStr)) {
        return `${dateStr.slice(4,6)}/${dateStr.slice(6,8)}/${dateStr.slice(0,4)}`;
    }
    // Format: YYYY-MM-DD -> MM/DD/YYYY
    if (dateStr.includes('-')) {
        const parts = dateStr.split('-');
        if (parts.length === 3) {
            return `${parts[1]}/${parts[2]}/${parts[0]}`;
        }
    }
    return dateStr;
}

function filterCareerFirsts() {
    const category = document.getElementById('career-firsts-category')?.value || 'all';
    const search = document.getElementById('career-firsts-search')?.value || '';
    renderCareerFirsts(category, search);
}

// Sub-tab helpers
function showRecordsSubTab(tabId) {
    document.querySelectorAll('#records .sub-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('#records .sub-section').forEach(s => s.classList.remove('active'));
    document.querySelector(`#records .sub-tab[onclick*="${tabId}"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
    updateURL('records', { sub: tabId });
}

function showMatchupsSubTab(tabId) {
    document.querySelectorAll('#matchups .sub-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('#matchups .sub-section').forEach(s => s.classList.remove('active'));
    document.querySelector(`#matchups .sub-tab[onclick*="${tabId}"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
    updateURL('matchups', { sub: tabId });
}

// Records
function renderRecords() {
    const games = DATA.games || [];
    const grid = document.getElementById('game-records-grid');
    if (!games.length) { grid.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No games found</p>'; return; }

    // Calculate records
    const withMargin = games.map(g => ({
        ...g,
        margin: Math.abs((g.home_score || 0) - (g.away_score || 0)),
        combined: (g.home_score || 0) + (g.away_score || 0),
        winner: (g.home_score || 0) > (g.away_score || 0) ? g.home_team : g.away_team,
        loser: (g.home_score || 0) > (g.away_score || 0) ? g.away_team : g.home_team,
        winScore: Math.max(g.home_score || 0, g.away_score || 0),
        loseScore: Math.min(g.home_score || 0, g.away_score || 0),
    }));

    const categories = [
        { title: 'Biggest Blowouts', data: [...withMargin].sort((a,b) => b.margin - a.margin).slice(0,10),
          render: g => `<td class="rank">${g._rank}</td><td class="game-link" onclick="showBoxScore('${g.game_id}')">${g.date}</td><td>${getTeamCode(g.winner)} ${g.winScore}, ${getTeamCode(g.loser)} ${g.loseScore}</td><td class="num">${g.margin}</td>` },
        { title: 'Closest Games', data: [...withMargin].sort((a,b) => a.margin - b.margin).slice(0,10),
          render: g => `<td class="rank">${g._rank}</td><td class="game-link" onclick="showBoxScore('${g.game_id}')">${g.date}</td><td>${getTeamCode(g.winner)} ${g.winScore}, ${getTeamCode(g.loser)} ${g.loseScore}</td><td class="num">${g.margin}</td>` },
        { title: 'Highest Scoring', data: [...withMargin].sort((a,b) => b.combined - a.combined).slice(0,10),
          render: g => `<td class="rank">${g._rank}</td><td class="game-link" onclick="showBoxScore('${g.game_id}')">${g.date}</td><td>${getTeamCode(g.away_team)} ${g.away_score} @ ${getTeamCode(g.home_team)} ${g.home_score}</td><td class="num">${g.combined}</td>` },
        { title: 'Lowest Scoring', data: [...withMargin].sort((a,b) => a.combined - b.combined).slice(0,10),
          render: g => `<td class="rank">${g._rank}</td><td class="game-link" onclick="showBoxScore('${g.game_id}')">${g.date}</td><td>${getTeamCode(g.away_team)} ${g.away_score} @ ${getTeamCode(g.home_team)} ${g.home_score}</td><td class="num">${g.combined}</td>` },
        { title: 'Most Points (Single Team)', data: [...withMargin].sort((a,b) => b.winScore - a.winScore).slice(0,10),
          render: g => `<td class="rank">${g._rank}</td><td class="game-link" onclick="showBoxScore('${g.game_id}')">${g.date}</td><td>${getTeamCode(g.winner)} vs ${getTeamCode(g.loser)}</td><td class="num">${g.winScore}</td>` },
        { title: 'Fewest Points (Single Team)', data: [...withMargin].sort((a,b) => a.loseScore - b.loseScore).slice(0,10),
          render: g => `<td class="rank">${g._rank}</td><td class="game-link" onclick="showBoxScore('${g.game_id}')">${g.date}</td><td>${getTeamCode(g.loser)} vs ${getTeamCode(g.winner)}</td><td class="num">${g.loseScore}</td>` },
    ];

    grid.innerHTML = categories.map(cat => {
        const rows = cat.data.map((g, i) => { g._rank = i + 1; return `<tr>${cat.render(g)}</tr>`; }).join('');
        return `<div class="record-item"><h4>${cat.title}</h4><table>${rows}</table></div>`;
    }).join('');

    // Show PBP records tab if any game has PBP data
    const hasPbp = games.some(g => g.espnPbpAnalysis);
    if (hasPbp) {
        document.getElementById('pbp-records-tab').style.display = '';
        renderPbpRecords();
    }

    // Show Shot Chart records tab if any game has shot chart data
    const hasShotChart = games.some(g => g.brShotChart && g.brShotChart.shots && g.brShotChart.shots.length);
    if (hasShotChart) {
        document.getElementById('shot-records-tab').style.display = '';
        renderShotRecords();
    }
}

function renderPlayerRecords() {
    const playerGames = DATA.player_games || [];
    const grid = document.getElementById('player-records-grid');
    if (!playerGames.length) { grid.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No player data</p>'; return; }

    const statCats = [
        { key: 'pts', title: 'Most Points', label: 'PTS' },
        { key: 'trb', title: 'Most Rebounds', label: 'REB' },
        { key: 'ast', title: 'Most Assists', label: 'AST' },
        { key: 'fg3', title: 'Most 3-Pointers', label: '3PM' },
        { key: 'stl', title: 'Most Steals', label: 'STL' },
        { key: 'blk', title: 'Most Blocks', label: 'BLK' },
    ];

    grid.innerHTML = statCats.map(cat => {
        const sorted = [...playerGames].filter(p => p[cat.key] != null).sort((a,b) => (b[cat.key] || 0) - (a[cat.key] || 0)).slice(0, 10);
        const rows = sorted.map((p, i) => {
            // Format date shorter: "Nov 10, 2021"
            const d = p.date_yyyymmdd || '';
            let shortDate = p.date || '';
            if (d.length === 8) {
                const dt = new Date(d.slice(0,4) + '-' + d.slice(4,6) + '-' + d.slice(6,8) + 'T12:00:00');
                if (!isNaN(dt)) shortDate = dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
            }
            return `<tr>
            <td class="rank">${i+1}</td>
            <td><span class="player-link" onclick="showPlayerDetail('${(p.player||'').replace(/'/g, "\\'")}')">${p.player}</span></td>
            <td>${shortDate}</td>
            <td>${getTeamCode(p.team || '')}</td>
            <td class="num">${p[cat.key]}</td>
        </tr>`;
        }).join('');
        return `<div class="record-item player-record"><h4>${cat.title}</h4><table><colgroup><col style="width:24px"><col><col><col style="width:36px"><col style="width:32px"></colgroup>${rows}</table></div>`;
    }).join('');
}

function renderPbpRecords() {
    const games = DATA.games || [];
    const grid = document.getElementById('pbp-records-grid');
    const pbpGames = games.filter(g => g.espnPbpAnalysis);
    if (!pbpGames.length) { grid.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No PBP data available</p>'; return; }

    // Biggest Comebacks
    const comebacks = pbpGames
        .filter(g => g.espnPbpAnalysis.biggestComeback && g.espnPbpAnalysis.biggestComeback.deficit > 0)
        .map(g => ({ ...g, comeback: g.espnPbpAnalysis.biggestComeback }))
        .sort((a,b) => b.comeback.deficit - a.comeback.deficit)
        .slice(0, 10);

    // Largest Scoring Runs
    const runs = [];
    pbpGames.forEach(g => {
        (g.espnPbpAnalysis.teamScoringRuns || []).forEach(r => {
            runs.push({ ...r, game: g });
        });
    });
    runs.sort((a,b) => b.points - a.points);

    // Player Streaks
    const streaks = [];
    pbpGames.forEach(g => {
        (g.espnPbpAnalysis.playerPointStreaks || []).forEach(s => {
            streaks.push({ ...s, game: g });
        });
    });
    streaks.sort((a,b) => b.points - a.points);

    // Decisive Shots
    const shots = pbpGames
        .filter(g => g.espnPbpAnalysis.gameWinningShots && g.espnPbpAnalysis.gameWinningShots.decisiveShot)
        .map(g => ({ ...g, shot: g.espnPbpAnalysis.gameWinningShots.decisiveShot }));

    let html = '';

    if (comebacks.length) {
        const rows = comebacks.map((g, i) => `<tr>
            <td class="rank">${i+1}</td>
            <td class="game-link" onclick="showBoxScore('${g.game_id}')">${g.date}</td>
            <td>${getTeamCode(g.comeback.team)}</td>
            <td class="num">${g.comeback.deficit} pts</td>
        </tr>`).join('');
        html += `<div class="record-item pbp-record"><h4>Biggest Comebacks</h4><table>${rows}</table></div>`;
    }

    if (runs.length) {
        const rows = runs.slice(0, 10).map((r, i) => `<tr>
            <td class="rank">${i+1}</td>
            <td class="game-link" onclick="showBoxScore('${r.game.game_id}')">${r.game.date}</td>
            <td>${getTeamCode(r.team)}</td>
            <td class="num">${r.points}-0 run</td>
        </tr>`).join('');
        html += `<div class="record-item pbp-record"><h4>Largest Scoring Runs</h4><table>${rows}</table></div>`;
    }

    if (streaks.length) {
        const rows = streaks.slice(0, 10).map((s, i) => `<tr>
            <td class="rank">${i+1}</td>
            <td class="game-link" onclick="showBoxScore('${s.game.game_id}')">${s.game.date}</td>
            <td>${s.player} (${getTeamCode(s.team)})</td>
            <td class="num">${s.points} pts</td>
        </tr>`).join('');
        html += `<div class="record-item pbp-record"><h4>Longest Player Scoring Streaks</h4><table>${rows}</table></div>`;
    }

    if (shots.length) {
        const sorted = [...shots].sort((a,b) => {
            const aPeriod = a.shot.period || 0;
            const bPeriod = b.shot.period || 0;
            if (aPeriod !== bPeriod) return bPeriod - aPeriod;
            return (a.shot.time || '').localeCompare(b.shot.time || '');
        }).slice(0, 10);
        const rows = sorted.map((g, i) => `<tr>
            <td class="rank">${i+1}</td>
            <td class="game-link" onclick="showBoxScore('${g.game_id}')">${g.date}</td>
            <td>${g.shot.player} (${getTeamCode(g.shot.team)})</td>
            <td class="num">Q${g.shot.period} ${g.shot.time}</td>
        </tr>`).join('');
        html += `<div class="record-item pbp-record"><h4>Decisive Shots</h4><table>${rows}</table></div>`;
    }

    grid.innerHTML = html || '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No PBP records available</p>';
}

// Shot Chart Records
function renderShotRecords() {
    const games = DATA.games || [];
    const grid = document.getElementById('shot-records-grid');
    const scGames = games.filter(g => g.brShotChart && g.brShotChart.shots && g.brShotChart.shots.length);
    if (!scGames.length) { grid.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No shot chart data</p>'; return; }

    // Collect all shots with game context, distance, and original index
    const allShots = [];
    scGames.forEach(g => {
        g.brShotChart.shots.forEach((s, idx) => {
            const m = s.description && s.description.match(/from (\d+) ft/);
            if (m) allShots.push({ ...s, dist: parseInt(m[1]), game: g, shotIdx: idx });
        });
    });

    let html = '';

    function shotRow(s, i) {
        return `<tr class="shot-record-row" onclick="showBoxScoreWithShot('${s.game.game_id}',${s.shotIdx})">
            <td class="rank">${i + 1}</td>
            <td class="game-link">${s.game.date}</td>
            <td><span class="player-link" onclick="event.stopPropagation();showPlayerDetail('${(s.player || '').replace(/'/g, "\\'")}')">${s.player}</span></td>
            <td class="num">${s.dist} ft</td>
        </tr>`;
    }

    // --- Longest Made Shots ---
    const longestMade = allShots.filter(s => s.made).sort((a, b) => b.dist - a.dist).slice(0, 10);
    if (longestMade.length) {
        const rows = longestMade.map((s, i) => shotRow(s, i)).join('');
        html += `<div class="record-item shot-record"><h4>Longest Made Shots</h4><table>${rows}</table></div>`;
    }

    // --- Longest Made 2-Pointers ---
    const longest2 = allShots.filter(s => s.made && s.description && s.description.includes('2-pointer')).sort((a, b) => b.dist - a.dist).slice(0, 10);
    if (longest2.length) {
        const rows = longest2.map((s, i) => shotRow(s, i)).join('');
        html += `<div class="record-item shot-record"><h4>Longest 2-Pointers</h4><table>${rows}</table></div>`;
    }

    // --- Longest Made 3-Pointers ---
    const longest3 = allShots.filter(s => s.made && s.description && s.description.includes('3-pointer')).sort((a, b) => b.dist - a.dist).slice(0, 10);
    if (longest3.length) {
        const rows = longest3.map((s, i) => shotRow(s, i)).join('');
        html += `<div class="record-item shot-record"><h4>Longest 3-Pointers</h4><table>${rows}</table></div>`;
    }

    // --- Best Single-Game FG% (min 10 FGA) ---
    const playerGameStats = {};
    scGames.forEach(g => {
        g.brShotChart.shots.forEach(s => {
            const key = s.player + '|' + g.game_id;
            if (!playerGameStats[key]) playerGameStats[key] = { player: s.player, team: s.team, game: g, made: 0, total: 0 };
            playerGameStats[key].total++;
            if (s.made) playerGameStats[key].made++;
        });
    });
    const bestFg = Object.values(playerGameStats)
        .filter(p => p.total >= 10)
        .map(p => ({ ...p, pct: p.made / p.total }))
        .sort((a, b) => b.pct - a.pct || b.total - a.total)
        .slice(0, 10);
    if (bestFg.length) {
        const rows = bestFg.map((p, i) => `<tr>
            <td class="rank">${i + 1}</td>
            <td class="game-link" onclick="showBoxScore('${p.game.game_id}')">${p.game.date}</td>
            <td><span class="player-link" onclick="showPlayerDetail('${(p.player || '').replace(/'/g, "\\'")}')">${p.player}</span></td>
            <td class="num">${p.made}/${p.total} (${(p.pct * 100).toFixed(1)}%)</td>
        </tr>`).join('');
        html += `<div class="record-item shot-record"><h4>Best FG% (min 10 FGA)</h4><table>${rows}</table></div>`;
    }

    // --- Most FGA in a Single Game ---
    const mostFga = Object.values(playerGameStats).sort((a, b) => b.total - a.total).slice(0, 10);
    if (mostFga.length) {
        const rows = mostFga.map((p, i) => `<tr>
            <td class="rank">${i + 1}</td>
            <td class="game-link" onclick="showBoxScore('${p.game.game_id}')">${p.game.date}</td>
            <td><span class="player-link" onclick="showPlayerDetail('${(p.player || '').replace(/'/g, "\\'")}')">${p.player}</span></td>
            <td class="num">${p.made}/${p.total}</td>
        </tr>`).join('');
        html += `<div class="record-item shot-record"><h4>Most FGA (Single Game)</h4><table>${rows}</table></div>`;
    }

    // --- Best 3PT% in a Game (min 5 3PA) ---
    const threeStats = {};
    scGames.forEach(g => {
        g.brShotChart.shots.forEach(s => {
            if (!s.description || !s.description.includes('3-pointer')) return;
            const key = s.player + '|' + g.game_id;
            if (!threeStats[key]) threeStats[key] = { player: s.player, team: s.team, game: g, made: 0, total: 0 };
            threeStats[key].total++;
            if (s.made) threeStats[key].made++;
        });
    });
    const best3pt = Object.values(threeStats)
        .filter(p => p.total >= 5)
        .map(p => ({ ...p, pct: p.made / p.total }))
        .sort((a, b) => b.pct - a.pct || b.made - a.made)
        .slice(0, 10);
    if (best3pt.length) {
        const rows = best3pt.map((p, i) => `<tr>
            <td class="rank">${i + 1}</td>
            <td class="game-link" onclick="showBoxScore('${p.game.game_id}')">${p.game.date}</td>
            <td><span class="player-link" onclick="showPlayerDetail('${(p.player || '').replace(/'/g, "\\'")}')">${p.player}</span></td>
            <td class="num">${p.made}/${p.total} (${(p.pct * 100).toFixed(1)}%)</td>
        </tr>`).join('');
        html += `<div class="record-item shot-record"><h4>Best 3PT% (min 5 3PA)</h4><table>${rows}</table></div>`;
    }

    // --- Overall Zone Efficiency ---
    const zones = [
        { label: 'Paint (0-4 ft)', test: d => d <= 4 },
        { label: 'Short Mid (5-14 ft)', test: d => d >= 5 && d <= 14 },
        { label: 'Long Mid (15-21 ft)', test: d => d >= 15 && d <= 21 },
        { label: 'Three-Point (22+ ft)', test: d => d >= 22 },
    ];
    const zoneRows = zones.map(z => {
        const zShots = allShots.filter(s => z.test(s.dist));
        const made = zShots.filter(s => s.made).length;
        const total = zShots.length;
        const pct = total > 0 ? ((made / total) * 100).toFixed(1) : '-';
        return `<tr><td>${z.label}</td><td class="num">${made}/${total}</td><td class="num">${pct}%</td></tr>`;
    }).join('');
    html += `<div class="record-item shot-record"><h4>Overall Zone Efficiency</h4><table><thead><tr><th>Zone</th><th>FG</th><th>FG%</th></tr></thead><tbody>${zoneRows}</tbody></table></div>`;

    grid.innerHTML = html;
}

// Scorigami
function renderScorigami() {
    const games = DATA.games || [];
    const statsDiv = document.getElementById('scorigami-stats');
    const gridEl = document.getElementById('scorigami-grid');
    if (!games.length) { gridEl.innerHTML = '<tr><td>No games</td></tr>'; return; }

    // Build score map: winScore-loseScore -> [games]
    const scoreMap = {};
    let minWin = 999, maxWin = 0, minLose = 999, maxLose = 0;

    games.forEach(g => {
        const high = Math.max(g.home_score || 0, g.away_score || 0);
        const low = Math.min(g.home_score || 0, g.away_score || 0);
        if (high === 0 && low === 0) return;
        const key = `${high}-${low}`;
        if (!scoreMap[key]) scoreMap[key] = [];
        scoreMap[key].push(g);
        minWin = Math.min(minWin, high);
        maxWin = Math.max(maxWin, high);
        minLose = Math.min(minLose, low);
        maxLose = Math.max(maxLose, low);
    });

    const uniqueScores = Object.keys(scoreMap).length;
    const totalGames = games.length;
    const maxFreq = Math.max(...Object.values(scoreMap).map(v => v.length));

    // Stats summary
    statsDiv.innerHTML = `
        <div class="scorigami-stat"><div class="number">${totalGames}</div><div class="label">Total Games</div></div>
        <div class="scorigami-stat"><div class="number">${uniqueScores}</div><div class="label">Unique Scores</div></div>
        <div class="scorigami-stat"><div class="number">${maxFreq}</div><div class="label">Most Repeated</div></div>
    `;

    // Round boundaries for better grid
    minWin = Math.floor(minWin / 5) * 5;
    maxWin = Math.ceil(maxWin / 5) * 5;
    minLose = Math.floor(minLose / 5) * 5;
    maxLose = Math.ceil(maxLose / 5) * 5;

    // Build grid: rows = winner score, cols = loser score
    let html = '<thead><tr><th></th>';
    for (let l = minLose; l <= maxLose; l++) {
        html += `<th>${l}</th>`;
    }
    html += '</tr></thead><tbody>';

    for (let w = minWin; w <= maxWin; w++) {
        html += `<tr><td class="row-header">${w}</td>`;
        for (let l = minLose; l <= maxLose; l++) {
            if (l >= w) {
                html += '<td></td>';
                continue;
            }
            const key = `${w}-${l}`;
            const count = scoreMap[key] ? scoreMap[key].length : 0;
            if (count === 0) {
                html += '<td></td>';
            } else {
                const freq = count >= 5 ? 5 : count >= 4 ? 4 : count >= 3 ? 3 : count >= 2 ? 2 : 1;
                html += `<td class="has-score freq-${freq}" data-key="${key}" onmouseenter="showScorigamiTooltip(event,'${key}')" onmouseleave="hideScorigamiTooltip()" onclick="showScorigamiGames('${key}')">${count}</td>`;
            }
        }
        html += '</tr>';
    }
    html += '</tbody>';
    gridEl.innerHTML = html;
}

// Scorigami helpers stored for tooltip
const _scorigamiMap = {};
function _buildScorigamiMap() {
    const games = DATA.games || [];
    games.forEach(g => {
        const high = Math.max(g.home_score || 0, g.away_score || 0);
        const low = Math.min(g.home_score || 0, g.away_score || 0);
        if (high === 0 && low === 0) return;
        const key = `${high}-${low}`;
        if (!_scorigamiMap[key]) _scorigamiMap[key] = [];
        _scorigamiMap[key].push(g);
    });
}

function showScorigamiTooltip(event, key) {
    if (!Object.keys(_scorigamiMap).length) _buildScorigamiMap();
    const games = _scorigamiMap[key] || [];
    if (!games.length) return;
    const tooltip = document.getElementById('scorigami-tooltip');
    const parts = key.split('-');
    let html = `<strong>${parts[0]}-${parts[1]}</strong> (${games.length} game${games.length > 1 ? 's' : ''})<br>`;
    games.slice(0, 5).forEach(g => {
        html += `${g.date}: ${getTeamCode(g.away_team)} ${g.away_score} @ ${getTeamCode(g.home_team)} ${g.home_score}<br>`;
    });
    if (games.length > 5) html += `<em>...and ${games.length - 5} more</em>`;
    tooltip.innerHTML = html;
    tooltip.style.left = (event.clientX + 10) + 'px';
    tooltip.style.top = (event.clientY + 10) + 'px';
    tooltip.classList.add('visible');
}

function hideScorigamiTooltip() {
    document.getElementById('scorigami-tooltip').classList.remove('visible');
}

function showScorigamiGames(key) {
    if (!Object.keys(_scorigamiMap).length) _buildScorigamiMap();
    const games = _scorigamiMap[key] || [];
    if (!games.length) return;
    if (games.length === 1) { showBoxScore(games[0].game_id); return; }
    const parts = key.split('-');
    let html = `<h3>Score: ${parts[0]}-${parts[1]} (${games.length} games)</h3><div class="day-games-list">`;
    games.forEach(g => {
        html += `<div class="day-game-item" onclick="closeModal('day-games-modal');showBoxScore('${g.game_id}')">
            <div class="matchup">${getTeamCode(g.away_team)} @ ${getTeamCode(g.home_team)}</div>
            <div class="score">${g.away_score} - ${g.home_score} | ${g.date}</div>
        </div>`;
    });
    html += '</div>';
    document.getElementById('day-games-detail').innerHTML = html;
    openModal('day-games-modal');
}

// Calendar
function renderCalendar() {
    const games = DATA.games || [];
    const container = document.getElementById('calendar-grid');
    if (!games.length) { container.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No games found</p>'; return; }

    // Group games by month-day (year agnostic): key = "MM-DD"
    const gamesByMonthDay = {};
    const monthsWithGames = new Set();
    games.forEach(g => {
        const d = g.date_yyyymmdd || '';
        if (d.length < 8) return;
        const mm = d.slice(4, 6);
        const dd = d.slice(6, 8);
        const key = `${mm}-${dd}`;
        if (!gamesByMonthDay[key]) gamesByMonthDay[key] = [];
        gamesByMonthDay[key].push(g);
        monthsWithGames.add(parseInt(mm));
    });

    // NBA season ordering: Oct=10, Nov=11, Dec=12, Jan=1, ..., Jun=6
    const seasonOrder = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9];
    const monthsToShow = seasonOrder.filter(m => monthsWithGames.has(m));

    const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December'];
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    // Count progress: days with games vs total season days
    let totalDays = 0, daysWithGames = 0;
    monthsToShow.forEach(month => {
        const daysInMonth = new Date(2024, month, 0).getDate();
        for (let d = 1; d <= daysInMonth; d++) {
            totalDays++;
            const key = `${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
            if (gamesByMonthDay[key]) daysWithGames++;
        }
    });

    let html = `<div class="calendar-progress" style="margin-bottom:1.5rem;text-align:center;">
        <div style="margin-bottom:0.5rem;font-size:1.1rem;"><strong>${daysWithGames}</strong> of <strong>${totalDays}</strong> calendar days with a game (${(daysWithGames/totalDays*100).toFixed(1)}%)</div>
        <div style="height:24px;background:var(--bg-secondary);border-radius:12px;overflow:hidden;border:1px solid var(--border-color);">
            <div style="height:100%;width:${(daysWithGames/totalDays*100)}%;background:linear-gradient(90deg,var(--accent-color),#27ae60);border-radius:12px;transition:width 0.3s ease;"></div>
        </div>
    </div>`;

    html += '<div class="calendar-months">';

    monthsToShow.forEach(month => {
        const mm = String(month).padStart(2, '0');
        // Use 2024 as reference year for day-of-week layout (leap year, covers Feb 29)
        const daysInMonth = new Date(2024, month, 0).getDate();
        const firstDay = new Date(2024, month - 1, 1).getDay();

        let days = '';
        for (let i = 0; i < firstDay; i++) {
            days += '<div class="calendar-day"></div>';
        }
        for (let d = 1; d <= daysInMonth; d++) {
            const key = `${mm}-${String(d).padStart(2, '0')}`;
            const dayGames = gamesByMonthDay[key] || [];
            const count = dayGames.length;
            let cls = 'calendar-day';
            if (count > 1) cls += ' has-multiple';
            else if (count === 1) cls += ' has-game';
            const onclick = count > 0 ? ` onclick="showCalendarDay('${key}')"` : '';
            const years = dayGames.map(g => g.date_yyyymmdd.slice(0, 4));
            const uniqueYears = [...new Set(years)].sort();
            const title = count > 0 ? ` title="${count} game${count > 1 ? 's' : ''} (${uniqueYears.join(', ')})"` : '';
            days += `<div class="${cls}"${onclick}${title}>${d}</div>`;
        }

        return html += `<div class="calendar-month">
            <h4>${monthNames[month]}</h4>
            <div class="calendar-weekdays">${dayNames.map(d => `<div>${d}</div>`).join('')}</div>
            <div class="calendar-days">${days}</div>
        </div>`;
    });

    html += '</div>';
    container.innerHTML = html;
}

function showCalendarDay(monthDayKey) {
    const games = DATA.games || [];
    // monthDayKey is "MM-DD"
    const mm = monthDayKey.slice(0, 2);
    const dd = monthDayKey.slice(3, 5);
    const dayGames = games.filter(g => {
        const d = g.date_yyyymmdd || '';
        return d.slice(4, 6) === mm && d.slice(6, 8) === dd;
    });
    if (!dayGames.length) return;
    if (dayGames.length === 1) { showBoxScore(dayGames[0].game_id); return; }

    const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December'];
    let html = `<h3>Games on ${monthNames[parseInt(mm)]} ${parseInt(dd)}</h3><div class="day-games-list">`;
    dayGames.sort((a, b) => (a.date_yyyymmdd || '').localeCompare(b.date_yyyymmdd || ''));
    dayGames.forEach(g => {
        const year = (g.date_yyyymmdd || '').slice(0, 4);
        html += `<div class="day-game-item" onclick="closeModal('day-games-modal');showBoxScore('${g.game_id}')">
            <span class="day-game-year">${year}</span>
            <div class="day-game-matchup">${getTeamCode(g.away_team)} @ ${getTeamCode(g.home_team)}</div>
            <div class="day-game-score">${g.away_score} - ${g.home_score}</div>
        </div>`;
    });
    html += '</div>';
    document.getElementById('day-games-detail').innerHTML = html;
    openModal('day-games-modal');
}

// Matchups
function renderMatchups() {
    renderTeamMatrix();
    populateH2HDropdowns();
}

function renderTeamMatrix() {
    const games = DATA.games || [];
    const container = document.getElementById('matchup-matrix-container');
    if (!games.length) { container.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No games found</p>'; return; }

    // Build H2H records
    const h2h = {}; // teamA -> teamB -> { wins, losses }
    const teamsSet = new Set();

    games.forEach(g => {
        const away = getTeamCode(g.away_team);
        const home = getTeamCode(g.home_team);
        if (!away || !home) return;
        teamsSet.add(away);
        teamsSet.add(home);

        if (!h2h[away]) h2h[away] = {};
        if (!h2h[home]) h2h[home] = {};
        if (!h2h[away][home]) h2h[away][home] = { wins: 0, losses: 0 };
        if (!h2h[home][away]) h2h[home][away] = { wins: 0, losses: 0 };

        if ((g.away_score || 0) > (g.home_score || 0)) {
            h2h[away][home].wins++;
            h2h[home][away].losses++;
        } else {
            h2h[home][away].wins++;
            h2h[away][home].losses++;
        }
    });

    const teams = [...teamsSet].sort();

    let html = '<table class="matchup-matrix"><thead><tr><th></th>';
    teams.forEach(t => { html += `<th>${t}</th>`; });
    html += '</tr></thead><tbody>';

    teams.forEach(row => {
        html += `<tr><td class="row-header">${row}</td>`;
        teams.forEach(col => {
            if (row === col) {
                html += '<td class="self-cell">-</td>';
            } else {
                const record = h2h[row] && h2h[row][col] ? h2h[row][col] : { wins: 0, losses: 0 };
                const total = record.wins + record.losses;
                if (total === 0) {
                    html += '<td>-</td>';
                } else {
                    let cls = '';
                    if (record.wins > record.losses) cls = 'win-record';
                    else if (record.losses > record.wins) cls = 'loss-record';
                    else cls = 'split-record';
                    html += `<td class="${cls}">${record.wins}-${record.losses}</td>`;
                }
            }
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

function populateH2HDropdowns() {
    const games = DATA.games || [];
    const teamsSet = new Set();
    games.forEach(g => {
        if (g.away_team) teamsSet.add(g.away_team);
        if (g.home_team) teamsSet.add(g.home_team);
    });
    const teams = [...teamsSet].sort();

    ['h2h-team1', 'h2h-team2'].forEach((id, idx) => {
        const sel = document.getElementById(id);
        sel.innerHTML = '<option value="">Select Team</option>' +
            teams.map(t => `<option value="${t}">${t}</option>`).join('');
    });
}

function renderH2H() {
    const team1 = document.getElementById('h2h-team1').value;
    const team2 = document.getElementById('h2h-team2').value;
    const container = document.getElementById('h2h-results');
    if (!team1 || !team2 || team1 === team2) {
        container.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">Select two different teams</p>';
        return;
    }

    const games = (DATA.games || []).filter(g =>
        (g.away_team === team1 && g.home_team === team2) ||
        (g.away_team === team2 && g.home_team === team1)
    );

    if (!games.length) {
        container.innerHTML = `<p style="text-align:center;padding:2rem;color:var(--text-muted);">No matchups found between ${getTeamCode(team1)} and ${getTeamCode(team2)}</p>`;
        return;
    }

    let t1Wins = 0, t2Wins = 0;
    games.forEach(g => {
        const winner = (g.home_score || 0) > (g.away_score || 0) ? g.home_team : g.away_team;
        if (winner === team1) t1Wins++;
        else t2Wins++;
    });

    let html = `<div class="h2h-summary">
        <div class="h2h-team">
            <div class="team-name">${getTeamCode(team1)}</div>
            <div class="wins ${t1Wins > t2Wins ? 'leading' : ''}">${t1Wins}</div>
        </div>
        <div style="display:flex;align-items:center;font-size:1.5rem;color:var(--text-muted);">vs</div>
        <div class="h2h-team">
            <div class="team-name">${getTeamCode(team2)}</div>
            <div class="wins ${t2Wins > t1Wins ? 'leading' : ''}">${t2Wins}</div>
        </div>
    </div>`;

    html += '<div class="table-container"><table><thead><tr><th>Date</th><th>Away</th><th>Score</th><th>Home</th><th>Score</th></tr></thead><tbody>';
    const sorted = [...games].sort((a,b) => (b.date_yyyymmdd || '').localeCompare(a.date_yyyymmdd || ''));
    sorted.forEach(g => {
        const awayWon = (g.away_score || 0) > (g.home_score || 0);
        html += `<tr class="game-link" onclick="showBoxScore('${g.game_id}')" style="cursor:pointer;">
            <td>${g.date}</td>
            <td style="${awayWon ? 'font-weight:700;color:var(--success);' : ''}">${getTeamCode(g.away_team)}</td>
            <td class="num" style="${awayWon ? 'font-weight:700;color:var(--success);' : ''}">${g.away_score}</td>
            <td style="${!awayWon ? 'font-weight:700;color:var(--success);' : ''}">${getTeamCode(g.home_team)}</td>
            <td class="num" style="${!awayWon ? 'font-weight:700;color:var(--success);' : ''}">${g.home_score}</td>
        </tr>`;
    });
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// Season Stats
let seasonChart = null;

function getNbaSeason(dateStr) {
    // dateStr is YYYYMMDD. NBA season: Oct-Jun. Oct 2024 through Jun 2025 = "2024-25"
    if (!dateStr || dateStr.length < 6) return 'Unknown';
    const year = parseInt(dateStr.slice(0, 4));
    const month = parseInt(dateStr.slice(4, 6));
    // Oct-Dec: season starts this year. Jan-Sep: season started previous year.
    const startYear = month >= 10 ? year : year - 1;
    const endYear = startYear + 1;
    return `${startYear}-${String(endYear).slice(2)}`;
}

function renderSeasonStats() {
    const games = DATA.games || [];
    const playerGames = DATA.player_games || [];
    if (!games.length) return;

    // Aggregate by season
    const seasonData = {};
    games.forEach(g => {
        const season = getNbaSeason(g.date_yyyymmdd || '');
        if (!seasonData[season]) seasonData[season] = { games: 0, teams: new Set(), arenas: new Set(), players: new Set() };
        seasonData[season].games++;
        if (g.away_team) seasonData[season].teams.add(g.away_team);
        if (g.home_team) seasonData[season].teams.add(g.home_team);
        // Extract arena from game_id (home team code)
        if (g.game_id && g.game_id.length >= 12) {
            seasonData[season].arenas.add(g.game_id.slice(9, 12));
        }
    });

    playerGames.forEach(pg => {
        const season = getNbaSeason(pg.date_yyyymmdd || '');
        if (seasonData[season] && pg.player) {
            seasonData[season].players.add(pg.player);
        }
    });

    // Sort seasons chronologically
    const seasons = Object.keys(seasonData).sort((a, b) => {
        const aYear = parseInt(a.split('-')[0]);
        const bYear = parseInt(b.split('-')[0]);
        return aYear - bYear;
    });

    const stats = seasons.map(s => ({
        season: s,
        games: seasonData[s].games,
        teams: seasonData[s].teams.size,
        arenas: seasonData[s].arenas.size,
        players: seasonData[s].players.size,
    }));

    // Chart
    const ctx = document.getElementById('season-chart');
    if (ctx && stats.length > 1) {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
        const textColor = isDark ? '#b0b0b0' : '#666666';

        if (seasonChart) seasonChart.destroy();
        seasonChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: stats.map(s => s.season),
                datasets: [{
                    label: 'Games',
                    data: stats.map(s => s.games),
                    backgroundColor: 'rgba(74, 158, 255, 0.6)',
                    borderColor: 'rgba(74, 158, 255, 1)',
                    borderWidth: 1,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { beginAtZero: true, grid: { color: gridColor }, ticks: { color: textColor, stepSize: 1 } }
                }
            }
        });
    }

    // Summary
    const summaryDiv = document.getElementById('season-summary');
    if (summaryDiv && stats.length > 0) {
        const totalGames = stats.reduce((sum, s) => sum + s.games, 0);
        const avgPerSeason = Math.round(totalGames / stats.length);
        const bestSeason = stats.reduce((best, s) => s.games > best.games ? s : best, stats[0]);
        summaryDiv.innerHTML = `
            <div class="season-summary-card"><div class="number">${stats.length}</div><div class="label">Seasons</div></div>
            <div class="season-summary-card"><div class="number">${totalGames}</div><div class="label">Total Games</div></div>
            <div class="season-summary-card"><div class="number">${avgPerSeason}</div><div class="label">Avg/Season</div></div>
            <div class="season-summary-card"><div class="number">${bestSeason.season}</div><div class="label">Best Season (${bestSeason.games})</div></div>
        `;
    }

    // Table
    const tbody = document.querySelector('#season-table tbody');
    if (tbody) {
        tbody.innerHTML = stats.map(s => `<tr>
            <td>${s.season}</td>
            <td class="num">${s.games}</td>
            <td class="num">${s.teams}</td>
            <td class="num">${s.arenas}</td>
            <td class="num">${s.players}</td>
        </tr>`).join('');
    }
}

// Calendar Sub-tabs (legacy compat - calendar no longer has sub-tabs, but keep function for safety)
function showCalendarSubTab(subId) {
    if (subId === 'calendar-onthisday') {
        showSection('onthisday');
        return;
    }
}

function renderOnThisDay() {
    const games = DATA.games || [];
    const today = new Date();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December'];
    document.getElementById('onthisday-date').textContent =
        `${monthNames[parseInt(mm)]} ${parseInt(dd)}`;

    const matchingGames = games.filter(g => {
        const d = g.date_yyyymmdd || '';
        return d.length >= 8 && d.slice(4, 6) === mm && d.slice(6, 8) === dd;
    });

    const contentEl = document.getElementById('onthisday-content');
    const emptyEl = document.getElementById('onthisday-empty');

    if (!matchingGames.length) {
        contentEl.innerHTML = '';
        emptyEl.style.display = 'block';
        return;
    }

    emptyEl.style.display = 'none';
    const byYear = {};
    matchingGames.forEach(g => {
        const year = (g.date_yyyymmdd || '').slice(0, 4);
        if (!byYear[year]) byYear[year] = [];
        byYear[year].push(g);
    });

    const currentYear = today.getFullYear();
    let html = '';
    Object.keys(byYear).sort((a, b) => b - a).forEach(year => {
        const yearsAgo = currentYear - parseInt(year);
        const agoLabel = yearsAgo === 0 ? 'This year' : yearsAgo === 1 ? '1 year ago' : `${yearsAgo} years ago`;
        html += `<div style="margin-bottom:1.5rem;">
            <div style="display:flex;align-items:baseline;gap:0.75rem;margin-bottom:0.75rem;">
                <h4 style="color:var(--accent-color);margin:0;">${year}</h4>
                <span style="color:var(--text-muted);font-size:0.85rem;">${agoLabel}</span>
            </div>`;
        byYear[year].forEach(g => {
            html += `<div class="day-game-item" onclick="showBoxScore('${g.game_id}')">
                <div class="day-game-matchup">${getTeamCode(g.away_team)} ${g.away_score} @ ${getTeamCode(g.home_team)} ${g.home_score}</div>
            </div>`;
        });
        html += '</div>';
    });
    contentEl.innerHTML = html;
}

// Global Search (legacy functions kept for compat, main search is now command palette)
let _searchTimeout = null;

function handleGlobalSearch(event) {
    // Redirect to command palette
    openCommandPalette();
    const input = document.getElementById('cmd-palette-input');
    if (input && event.target.value) {
        input.value = event.target.value;
        handleCmdSearch({ target: input, key: '' });
    }
}

function performGlobalSearch(query) {
    const q = query.toLowerCase();
    const results = { games: [], players: [], arenas: [] };
    (DATA.games || []).forEach(g => {
        if (results.games.length >= 5) return;
        if ((g.away_team || '').toLowerCase().includes(q) ||
            (g.home_team || '').toLowerCase().includes(q) ||
            (g.date || '').toLowerCase().includes(q)) {
            results.games.push(g);
        }
    });
    (DATA.players || []).forEach(p => {
        if (results.players.length >= 5) return;
        if ((p.Player || '').toLowerCase().includes(q) ||
            (p.Team || '').toLowerCase().includes(q)) {
            results.players.push(p);
        }
    });
    (DATA.venues || []).forEach(v => {
        if (results.arenas.length >= 5) return;
        if ((v.name || '').toLowerCase().includes(q) ||
            (v.team || '').toLowerCase().includes(q) ||
            (v.city || '').toLowerCase().includes(q)) {
            results.arenas.push(v);
        }
    });
    return results;
}

function renderGlobalSearchResults(results) {
    const container = document.getElementById('global-search-results');
    const hasResults = results.games.length || results.players.length || results.arenas.length;
    if (!hasResults) {
        container.innerHTML = '<div class="search-no-results">No results found</div>';
        container.style.display = 'block';
        return;
    }
    let html = '';
    if (results.games.length) {
        html += '<div class="search-category"><div class="search-category-label">Games</div>';
        results.games.forEach(g => {
            html += `<div class="search-result-item" onclick="selectGlobalSearchResult('game','${g.game_id}')">
                <span>${getTeamCode(g.away_team)} @ ${getTeamCode(g.home_team)} (${g.away_score}-${g.home_score})</span>
                <span class="search-result-meta">${g.date}</span>
            </div>`;
        });
        html += '</div>';
    }
    if (results.players.length) {
        html += '<div class="search-category"><div class="search-category-label">Players</div>';
        results.players.forEach(p => {
            const safeName = (p.Player || '').replace(/'/g, "\\'");
            html += `<div class="search-result-item" onclick="selectGlobalSearchResult('player','${safeName}')">
                <span>${p.Player}</span>
                <span class="search-result-meta">${getTeamCode(p.Team)} | ${p.Games || 0}G</span>
            </div>`;
        });
        html += '</div>';
    }
    if (results.arenas.length) {
        html += '<div class="search-category"><div class="search-category-label">Arenas</div>';
        results.arenas.forEach(v => {
            html += `<div class="search-result-item" onclick="selectGlobalSearchResult('arena','${v.code}')">
                <span>${v.name}</span>
                <span class="search-result-meta">${v.team}</span>
            </div>`;
        });
        html += '</div>';
    }
    container.innerHTML = html;
    container.style.display = 'block';
}

function selectGlobalSearchResult(type, id) {
    if (type === 'game') showBoxScore(id);
    else if (type === 'player') showPlayerDetail(id);
    else if (type === 'arena') showSection('venues');
}

function showGlobalSearchResults() {}
function hideGlobalSearchResults() {}

// Division Progress
function renderDivisionProgress() {
    const checklist = DATA.teamChecklist || {};
    const divisions = checklist.divisions || {};
    const conferences = checklist.conferences || {};
    const container = document.getElementById('divisions-content');

    let html = '<div class="conference-summary" style="margin-bottom:1.5rem;">';
    ['East', 'West'].forEach(conf => {
        const confData = conferences[conf] || { teamsSeen: 0, totalTeams: 15 };
        const pct = (confData.teamsSeen / 15 * 100).toFixed(0);
        html += `<div class="conference-box ${confData.teamsSeen === 15 ? 'complete' : ''}">
                <h5>${conf}ern Conference</h5>
                <div class="count">${confData.teamsSeen}/15</div>
                <div class="progress-bar" style="margin-top:0.5rem;height:8px;">
                    <div class="progress-fill" style="width:${pct}%;"></div>
                </div>
            </div>`;
    });
    html += '</div>';

    html += '<div class="division-progress-grid">';
    const divOrder = ['Atlantic', 'Central', 'Southeast', 'Northwest', 'Pacific', 'Southwest'];
    divOrder.forEach(divName => {
        const div = divisions[divName] || { teams: [], teamsSeen: 0, totalTeams: 5, conference: '' };
        const pct = (div.teamsSeen / div.totalTeams * 100).toFixed(0);
        html += `<div class="division-progress-card ${div.complete ? 'complete' : ''}" onclick="toggleDivisionDetail('${divName}')">
                <div class="division-header">
                    <h4>${divName}</h4>
                    <span class="badge ${div.complete ? 'badge-complete' : 'badge-progress'}">${div.teamsSeen}/${div.totalTeams}</span>
                </div>
                <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:0.5rem;">${div.conference || ''}ern Conference</div>
                <div class="progress-bar" style="height:6px;margin-bottom:0.75rem;">
                    <div class="progress-fill" style="width:${pct}%;"></div>
                </div>
                <div class="division-team-dots">
                    ${(div.teams || []).map(t =>
                        '<span class="division-team-dot ' + (t.seen ? 'seen' : '') + '" title="' + getShortName(t.name) + (t.visitCount ? ' (' + t.visitCount + 'x)' : '') + '"></span>'
                    ).join('')}
                </div>
                <div class="division-detail" id="div-detail-${divName}" style="display:none;">
                    ${(div.teams || []).map(t =>
                        '<div class="team-item ' + (t.seen ? 'seen' : '') + '">' +
                        '<span class="' + (t.seen ? 'check' : 'not-seen') + '">' + (t.seen ? '\u2713' : '\u25CB') + '</span>' +
                        '<span>' + getShortName(t.name) + '</span>' +
                        (t.visitCount > 0 ? '<span class="visit-count">' + t.visitCount + 'x</span>' : '') +
                        '</div>'
                    ).join('')}
                </div>
            </div>`;
    });
    html += '</div>';
    container.innerHTML = html;
}

function toggleDivisionDetail(divName) {
    const detail = document.getElementById('div-detail-' + divName);
    if (detail) {
        detail.style.display = detail.style.display === 'none' ? 'block' : 'none';
    }
}

// Init
document.addEventListener('DOMContentLoaded', function() {
    // Eagerly init essential data
    renderLeaders();
    populateTeamDropdown();
    filteredPlayers = DATA.players ? [...DATA.players] : [];
    renderPlayersTable();
    renderTeamChecklist();
    renderVenuesTable();
    renderMilestones();
    renderCareerFirsts();

    // Add sidebar overlay for mobile
    const overlayDiv = document.createElement('div');
    overlayDiv.className = 'sidebar-overlay';
    overlayDiv.id = 'sidebar-overlay';
    overlayDiv.onclick = closeSidebar;
    document.body.appendChild(overlayDiv);

    // Handle URL or default to dashboard
    const { section } = parseURL();
    if (section) {
        handleURLNavigation();
    } else {
        showSection('dashboard');
    }
});

window.addEventListener('popstate', handleURLNavigation);

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        // Close in priority order: command palette, player panel, modal
        if (document.getElementById('cmd-palette-overlay')?.classList.contains('active')) {
            closeCommandPalette();
        } else if (document.getElementById('player-panel')?.classList.contains('active')) {
            closePlayerPanel();
        } else {
            document.querySelectorAll('.modal.active').forEach(m => closeModal(m.id));
        }
    }
    // Cmd+K / Ctrl+K shortcut for command palette
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        openCommandPalette();
    }
});
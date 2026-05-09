/* ═══════════════════════════════════════════════════════════
   AI选题助手 — 前端逻辑
   ═══════════════════════════════════════════════════════════ */

// ── 配置 ──────────────────────────────────────────────────
const DATA_PATHS = {
  selected: './data/selected_news.json',
  daily: './data/daily_report.json',
};

// ── 状态 ──────────────────────────────────────────────────
let state = {
  activeTab: 'daily',
  activeFilter: 'all',
  selectedNews: [],
  dailyReport: null,
};

// ── DOM 引用 ──────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ══════════════════════════════════════════════════════════
// 数据加载
// ══════════════════════════════════════════════════════════

async function loadData() {
  try {
    const [selected, daily] = await Promise.all([
      fetch(DATA_PATHS.selected).then(r => r.json()),
      fetch(DATA_PATHS.daily).then(r => r.json()),
    ]);
    state.selectedNews = selected.items || [];
    state.dailyReport = daily;
  } catch (e) {
    console.warn('数据加载失败，使用示例数据:', e.message);
    useSampleData();
  }
}

function useSampleData() {
  state.selectedNews = getSampleNews();
  state.dailyReport = getSampleReport();
}

// ══════════════════════════════════════════════════════════
// Tab 切换
// ══════════════════════════════════════════════════════════

function initTabs() {
  $$('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const tab = link.dataset.tab;
      switchTab(tab);
    });
  });
}

function switchTab(tab) {
  state.activeTab = tab;
  $$('.nav-link').forEach(l => l.classList.toggle('active', l.dataset.tab === tab));
  ['daily', 'feed', 'topics', 'sources'].forEach(id => {
    $(`#tab-${id}`).classList.toggle('hidden', id !== tab);
  });
  render();
}

// ══════════════════════════════════════════════════════════
// 筛选
// ══════════════════════════════════════════════════════════

function initFilters() {
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('filter-tag')) {
      const parent = e.target.parentElement;
      parent.querySelectorAll('.filter-tag').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');
      state.activeFilter = e.target.dataset.filter;
      render();
    }
  });
}

function filterByTopic(items) {
  if (state.activeFilter === 'all') return items;
  return items.filter(item =>
    (item.topics || []).some(t => t.tag === state.activeFilter)
  );
}

// ══════════════════════════════════════════════════════════
// 渲染总控
// ══════════════════════════════════════════════════════════

function render() {
  switch (state.activeTab) {
    case 'daily': renderDaily(); break;
    case 'feed': renderFeed(); break;
    case 'topics': renderTopics(); break;
    case 'sources': renderSources(); break;
  }
  updateFooter();
}

// ══════════════════════════════════════════════════════════
// 1. 日报渲染
// ══════════════════════════════════════════════════════════

function renderDaily() {
  const el = $('#daily-content');
  const report = state.dailyReport;

  if (!report || !report.sections || report.sections.length === 0) {
    el.innerHTML = `<div class="daily-report">
      <div class="report-header"><h2>AI日报</h2></div>
      <p style="text-align:center;color:var(--text-muted);padding:40px">
        数据加载中，请稍后刷新...
      </p>
    </div>`;
    return;
  }

  const sectionIcons = {
    '模型/产品发布': '🚀',
    '行业动态': '📊',
    '论文/研究': '🔬',
    '技巧与观点': '💭',
    'Models & Products': '🚀',
    'Industry News': '📊',
    'Research & Papers': '🔬',
    'Tips & Opinions': '💭',
  };

  const sectionsHTML = report.sections.map(sec => `
    <div class="section-block">
      <div class="section-title">${sectionIcons[sec.name] || '📌'} ${sec.name}</div>
      <div class="section-items">
        ${(sec.items || []).map(item => `
          <div class="section-item">
            <div class="si-title">${item.title || ''}</div>
            ${item.summary ? `<div class="si-summary">${item.summary}</div>` : ''}
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');

  el.innerHTML = `
    <div class="daily-report">
      <div class="report-header">
        <h2>${report.title || 'AI日报'}</h2>
        <div class="report-date">${formatDate(report.generated_at)} · ${report.source_count || 0}条精选</div>
      </div>
      ${report.summary ? `<div class="report-summary">📝 ${report.summary}</div>` : ''}
      ${sectionsHTML}
    </div>
  `;
}

// ══════════════════════════════════════════════════════════
// 2. 精选流渲染
// ══════════════════════════════════════════════════════════

function renderFeed() {
  const el = $('#feed-content');
  let items = filterByTopic(state.selectedNews);

  if (items.length === 0) {
    el.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:40px">暂无数据</p>';
    return;
  }

  const listHTML = items.map(item => `
    <article class="news-card">
      <div class="card-header">
        <div class="card-title">
          <a href="${item.link || '#'}" target="_blank" rel="noopener">${item.title || '(无标题)'}</a>
        </div>
        <span class="score-badge ${item.quality_score >= 7 ? 'high' : ''}">
          ${item.quality_score != null ? item.quality_score.toFixed(1) + '分' : 'N/A'}
        </span>
      </div>
      <div class="card-meta">
        <span class="source-tag">${item.source_name || ''}</span>
        <span class="tier-tag ${(item.source_tier || '').toLowerCase()}">${item.source_tier || ''}</span>
        <span class="card-time">${formatDate(item.published)}</span>
      </div>
      ${item.summary ? `<p class="card-summary">${stripHTML(item.summary)}</p>` : ''}
      ${renderTopicPills(item)}
    </article>
  `).join('');

  el.innerHTML = `<div class="news-list">${listHTML}</div>`;
}

function renderTopicPills(item) {
  if (!item.topics || item.topics.length === 0) return '';
  return `<div class="topic-pills">
    ${item.topics.map(t => `
      <div class="topic-pill">
        <span class="topic-tag">${topicEmoji(t.tag)} ${t.title || ''}</span>
        ${t.angle ? `— ${t.angle}` : ''}
        <span class="topic-diff">[${t.difficulty || '入门'}]</span>
      </div>
    `).join('')}
  </div>`;
}

// ══════════════════════════════════════════════════════════
// 3. 选题推荐渲染
// ══════════════════════════════════════════════════════════

function renderTopics() {
  const el = $('#topics-content');
  let items = filterByTopic(state.selectedNews);

  // 只显示有选题推荐的新闻
  items = items.filter(item => item.topics && item.topics.length > 0);

  if (items.length === 0) {
    el.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:40px">暂无选题推荐</p>';
    return;
  }

  const listHTML = items.map(item => `
    <div class="topic-card">
      <div class="news-ref">
        📰 <a href="${item.link || '#'}" target="_blank" rel="noopener">${item.title || '(无标题)'}</a>
        <span style="color:var(--text-muted)">· ${item.source_name || ''}</span>
      </div>
      ${(item.topics || []).map(t => `
        <div class="topic-idea">
          <div class="idea-title">${topicEmoji(t.tag)} ${t.title || ''}</div>
          ${t.angle ? `<div class="idea-angle">${t.angle}</div>` : ''}
          <div style="font-size:11px;color:var(--text-muted);margin-top:4px">
            难度: ${t.difficulty || '入门'} · 类型: ${topicLabel(t.tag)}
          </div>
        </div>
      `).join('')}
    </div>
  `).join('');

  el.innerHTML = `<div style="padding-bottom:40px">${listHTML}</div>`;
}

// ══════════════════════════════════════════════════════════
// 4. 信源页渲染
// ══════════════════════════════════════════════════════════

const STATIC_SOURCES = [
  { name: 'Microsoft Research', tier: 'T1', url: 'https://www.microsoft.com/en-us/research/feed/', category: '官方一手' },
  { name: 'NVIDIA Technical Blog', tier: 'T1', url: 'https://developer.nvidia.com/blog/feed/', category: '官方一手' },
  { name: 'Hugging Face Blog', tier: 'T1', url: 'https://huggingface.co/blog/feed.xml', category: '官方一手' },
  { name: 'Apple ML Research', tier: 'T1', url: 'https://machinelearning.apple.com/', category: '官方一手' },
  { name: '36氪', tier: 'T2', url: 'https://36kr.com/feed', category: '中文媒体' },
  { name: '少数派', tier: 'T2', url: 'https://sspai.com/feed', category: '中文媒体' },
  { name: '极客公园', tier: 'T2', url: 'https://www.geekpark.net/rss', category: '中文媒体' },
  { name: '爱范儿', tier: 'T2', url: 'https://www.ifanr.com/feed', category: '中文媒体' },
  { name: 'Reddit r/MachineLearning', tier: 'T2', url: 'https://www.reddit.com/r/MachineLearning/.rss', category: '社区' },
  { name: 'Hacker News (AI)', tier: 'T2', url: 'https://hnrss.org/', category: '社区' },
  { name: 'OpenAI Blog', tier: 'T1', url: 'https://openai.com/blog/', category: '官方一手 (待修复)' },
  { name: 'Google DeepMind', tier: 'T1', url: 'https://deepmind.google/', category: '官方一手 (待修复)' },
  { name: 'Anthropic News', tier: 'T1', url: 'https://www.anthropic.com/blog/', category: '官方一手 (待修复)' },
  { name: '机器之心', tier: 'T2', url: 'https://www.jiqizhixin.com/', category: '中文媒体 (待修复)' },
  { name: '量子位', tier: 'T2', url: 'https://www.qbitai.com/', category: '中文媒体 (待修复)' },
];

function renderSources() {
  const el = $('#sources-content');

  const active = STATIC_SOURCES.filter(s => !s.category.includes('待修复'));
  const broken = STATIC_SOURCES.filter(s => s.category.includes('待修复'));

  const cardHTML = (s, cls) => `
    <div class="source-card ${cls}">
      <span class="sc-tier ${s.tier.toLowerCase()}"></span>
      <div>
        <div>${s.name}</div>
        <div style="font-size:11px;color:var(--text-muted)">${s.category} · ${s.tier}</div>
      </div>
    </div>
  `;

  el.innerHTML = `
    <h3 style="margin:16px 0 12px">✅ 可用信源 (${active.length}个)</h3>
    <div class="sources-grid">${active.map(s => cardHTML(s, '')).join('')}</div>
    ${broken.length > 0 ? `
      <h3 style="margin:16px 0 12px;color:var(--text-muted)">⏳ 待修复信源 (${broken.length}个)</h3>
      <div class="sources-grid">${broken.map(s => cardHTML(s, 'broken')).join('')}</div>
    ` : ''}
  `;
}

// ══════════════════════════════════════════════════════════
// 工具函数
// ══════════════════════════════════════════════════════════

function formatDate(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    const now = new Date();
    const diffMs = now - d;
    const diffH = Math.floor(diffMs / 3600000);
    if (diffH < 1) return Math.floor(diffMs / 60000) + '分钟前';
    if (diffH < 24) return diffH + '小时前';
    if (diffH < 48) return '昨天';
    return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  } catch { return ''; }
}

function stripHTML(html) {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
}

function topicEmoji(tag) {
  const map = { tutorial: '🎬', money: '💰', science: '🧠', product: '📦', hotspot: '🔥' };
  return map[tag] || '📌';
}

function topicLabel(tag) {
  const map = { tutorial: '教程向', money: '搞钱向', science: '科普向', product: '产品向', hotspot: '热点向' };
  return map[tag] || tag;
}

function updateFooter() {
  const el = $('#update-time');
  const ts = state.dailyReport?.generated_at || state.selectedNews[0]?.published || '';
  if (ts) {
    el.textContent = '数据更新于 ' + new Date(ts).toLocaleString('zh-CN');
  } else {
    el.textContent = '等待数据加载...';
  }
}

// ══════════════════════════════════════════════════════════
// 示例数据（数据文件不可用时展示）
// ══════════════════════════════════════════════════════════

function getSampleNews() {
  return [
    {
      id: 'demo-1',
      title: 'OpenAI 发布 GPT-5.5 Instant，推理速度提升3倍，API价格下调60%',
      source_name: 'OpenAI Blog',
      source_tier: 'T1',
      link: '#',
      summary: 'OpenAI正式发布了GPT-5.5 Instant模型，在保持GPT-5.5同等智能水平的同时，推理速度提升3倍，API价格下调60%。该模型特别适合需要低延迟的场景，如实时对话、代码补全等。',
      published: new Date().toISOString(),
      quality_score: 9.2,
      scores: { importance: 9, timeliness: 10, actionability: 9, scarcity: 8, virality: 9 },
      topics: [
        { tag: 'tutorial', title: 'GPT-5.5 Instant实测：速度到底有多快？', angle: '上手实测，对比新旧模型速度差异', difficulty: '入门' },
        { tag: 'money', title: 'GPT-5.5降价60%，接入AI的成本低了多少？', angle: '算一笔账，讲商业机会', difficulty: '进阶' },
      ],
    },
    {
      id: 'demo-2',
      title: 'DeepSeek 开源 DeepSeek-V4 技术报告，MoE架构细节首次披露',
      source_name: 'Hugging Face Blog',
      source_tier: 'T1',
      link: '#',
      summary: 'DeepSeek发布了V4模型的技术报告，详细披露了其MoE（混合专家）架构的设计细节。报告显示V4使用了256个专家中激活8个的稀疏架构，在训练效率和推理成本上达到了新的平衡。',
      published: new Date(Date.now() - 3600000).toISOString(),
      quality_score: 8.7,
      scores: { importance: 9, timeliness: 8, actionability: 7, scarcity: 9, virality: 8 },
      topics: [
        { tag: 'science', title: '什么是MoE架构？DeepSeek V4为什么这么快？', angle: '用通俗语言解释MoE原理', difficulty: '进阶' },
        { tag: 'hotspot', title: 'DeepSeek V4开源意味着什么？', angle: '评论开源对AI行业的影响', difficulty: '入门' },
      ],
    },
    {
      id: 'demo-3',
      title: 'Claude Code 发布 Windows 原生版本，支持VS Code深度集成',
      source_name: 'Anthropic Blog',
      source_tier: 'T1',
      link: '#',
      summary: 'Anthropic发布了Claude Code的Windows原生版本，支持VS Code和JetBrains IDE的深度集成。新增了Worktree隔离、多Agent协作等企业级功能。',
      published: new Date(Date.now() - 7200000).toISOString(),
      quality_score: 8.1,
      scores: { importance: 7, timeliness: 9, actionability: 8, scarcity: 7, virality: 8 },
      topics: [
        { tag: 'tutorial', title: 'Claude Code Windows安装教程，5分钟上手', angle: 'Windows用户入门指南', difficulty: '入门' },
        { tag: 'product', title: 'Claude Code vs GitHub Copilot，哪个更好用？', angle: '横向对比评测', difficulty: '进阶' },
      ],
    },
    {
      id: 'demo-4',
      title: 'AI视频生成赛道大洗牌：Runway发布Gen-4，可灵推出2.0版本',
      source_name: '36氪',
      source_tier: 'T2',
      link: '#',
      summary: 'AI视频生成领域迎来密集更新。Runway发布了Gen-4模型，支持长达30秒的连贯视频生成；快手可灵推出了2.0版本，在画面质量和运动流畅度上有显著提升。',
      published: new Date(Date.now() - 14400000).toISOString(),
      quality_score: 7.5,
      scores: { importance: 7, timeliness: 8, actionability: 7, scarcity: 6, virality: 8 },
      topics: [
        { tag: 'tutorial', title: '2026年5月AI视频工具横评：Gen-4 vs 可灵2.0', angle: '实测对比各工具效果', difficulty: '入门' },
        { tag: 'money', title: 'AI视频工具这么强，普通人怎么靠它赚钱？', angle: '分析AI视频商业机会', difficulty: '入门' },
      ],
    },
    {
      id: 'demo-5',
      title: 'Apple Intelligence 重大更新：Siri接入大模型，支持跨应用自动化',
      source_name: 'Apple ML Research',
      source_tier: 'T1',
      link: '#',
      summary: '苹果推送iOS 19更新，Siri全面接入大语言模型，支持跨应用自动化操作。用户可以用自然语言让Siri完成\"帮我把昨天的会议纪要发给张三并设置提醒\"等复杂任务。',
      published: new Date(Date.now() - 18000000).toISOString(),
      quality_score: 8.3,
      scores: { importance: 8, timeliness: 9, actionability: 8, scarcity: 7, virality: 9 },
      topics: [
        { tag: 'product', title: 'iOS 19 Siri深度体验：苹果AI终于能用了？', angle: '上手体验，讲新功能实际表现', difficulty: '入门' },
        { tag: 'hotspot', title: '苹果AI追上来了吗？Siri新版实测对比', angle: '蹭苹果热度做对比内容', difficulty: '入门' },
      ],
    },
  ];
}

function getSampleReport() {
  const today = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
  return {
    title: `AI日报 - ${today}`,
    generated_at: new Date().toISOString(),
    source_count: 20,
    summary: '今日AI圈以模型迭代和产品更新为主旋律，OpenAI、DeepSeek同日释放重要更新，视频生成赛道竞争白热化。整体趋势：模型能力持续提升，同时价格不断下探，AI应用落地窗口正在加速打开。',
    sections: [
      {
        name: '模型/产品发布',
        items: [
          { title: 'OpenAI 发布 GPT-5.5 Instant，推理速度提升3倍，API价格下调60%', summary: 'OpenAI推出性能更强、价格更低的Instant版本' },
          { title: 'DeepSeek 开源 DeepSeek-V4 技术报告', summary: 'MoE架构细节首次公开，256专家中激活8个' },
          { title: 'AI视频生成赛道大洗牌：Runway Gen-4 vs 可灵2.0', summary: '视频生成迎来新突破，多家厂商同日更新' },
        ],
      },
      {
        name: '行业动态',
        items: [
          { title: 'Claude Code 发布 Windows 原生版本', summary: '支持VS Code和JetBrains深度集成' },
          { title: 'Apple Intelligence 重大更新：Siri接入大模型', summary: 'iOS 19推送，Siri支持跨应用自动化' },
        ],
      },
      {
        name: '论文/研究',
        items: [
          { title: 'DeepSeek V4技术报告公布MoE架构细节', summary: '稀疏激活策略在效率与性能间取得新平衡' },
        ],
      },
      {
        name: '技巧与观点',
        items: [
          { title: 'AI视频生成时代，内容创作者还需要学剪辑吗？', summary: '行业观点：工具进化不等于技能贬值' },
        ],
      },
    ],
  };
}

// ══════════════════════════════════════════════════════════
// 启动
// ══════════════════════════════════════════════════════════

async function init() {
  initTabs();
  initFilters();
  await loadData();
  switchTab('daily');
}

document.addEventListener('DOMContentLoaded', init);

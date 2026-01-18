(function(){
  const $ = sel => document.querySelector(sel);
  const $$ = sel => Array.from(document.querySelectorAll(sel));

  let rg2SubjectVocab = null;

  // Tab switching
  $$('.tab-headers .btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      $$('.tab').forEach(section => section.classList.remove('active'));
      const target = document.querySelector('#tab-' + tab);
      if (target) target.classList.add('active');
    });
  });

  async function getJ(url){
    const res = await fetch(url, {credentials: 'same-origin'});
    if (!res.ok) throw new Error(url + ': ' + res.status);
    return res.json();
  }

  async function postJ(url, body){
    const res = await fetch(url, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      credentials: 'same-origin',
      body: JSON.stringify(body || {}),
    });
    if (!res.ok) throw new Error(url + ': ' + res.status);
    return res.json();
  }

  // --- Prompt Workshop ------------------------------------------------------

  async function loadPrompts(){
    const data = await getJ('/api/admin/prompts');
    const sel = $('#promptSelect');
    if (!sel) return;
    sel.innerHTML = '';
    (data.prompts || []).forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.name;
      opt.textContent = p.name;
      opt.dataset.content = p.content || '';
      sel.appendChild(opt);
    });
    const first = sel.options[0];
    $('#promptEditor').value = first ? (first.dataset.content || '') : '';
  }

  function bindPromptSelection(){
    const sel = $('#promptSelect');
    if (!sel) return;
    sel.addEventListener('change', () => {
      const opt = sel.options[sel.selectedIndex];
      $('#promptEditor').value = opt ? (opt.dataset.content || '') : '';
    });
  }

  async function savePrompt(){
    const sel = $('#promptSelect');
    const editor = $('#promptEditor');
    if (!sel || !editor) return;
    const name = sel.value || 'default_prompt.txt';
    const content = editor.value || '';
    await postJ('/api/admin/prompts/update', {name, content});
    alert('Prompt saved');
    await loadPrompts();
  }

  const refreshBtn = $('#refreshPrompts');
  if (refreshBtn) refreshBtn.addEventListener('click', () => {
    loadPrompts().catch(console.error);
  });
  const savePromptBtn = $('#savePrompt');
  if (savePromptBtn) savePromptBtn.addEventListener('click', () => {
    savePrompt().catch(console.error);
  });
  bindPromptSelection();

  // --- Confidence Engine ----------------------------------------------------

  function renderKV(obj, parent, path){
    Object.keys(obj || {}).forEach(key => {
      const value = obj[key];
      const nextPath = path.concat(key);
      if (value !== null && typeof value === 'object' && !Array.isArray(value)){
        const legend = document.createElement('div');
        legend.textContent = nextPath.join('.');
        legend.style.fontWeight = 'bold';
        legend.style.marginTop = '.25rem';
        parent.appendChild(legend);
        renderKV(value, parent, nextPath);
      } else if (typeof value === 'number') {
        const row = document.createElement('div');
        row.style.margin = '.15rem 0';
        const label = document.createElement('label');
        label.textContent = nextPath.join('.');
        label.style.display = 'inline-block';
        label.style.width = '220px';
        const input = document.createElement('input');
        input.type = 'number';
        input.step = '0.01';
        input.value = String(value);
        input.dataset.path = nextPath.join('.');
        input.style.width = '80px';
        row.appendChild(label);
        row.appendChild(input);
        parent.appendChild(row);
      }
    });
  }

  let confCache = {};

  async function loadConfidence(){
    const resp = await getJ('/api/admin/confidence');
    confCache = resp.config || {};
    const host = $('#confEditor');
    if (!host) return;
    host.innerHTML = '';
    renderKV(confCache, host, []);
  }

  function collectConfidence(){
    const result = {};
    const inputs = Array.from(document.querySelectorAll('#confEditor input[data-path]'));
    inputs.forEach(inp => {
      const path = (inp.dataset.path || '').split('.').filter(Boolean);
      if (!path.length) return;
      let cursor = result;
      for (let i = 0; i < path.length - 1; i++){
        const key = path[i];
        if (!(key in cursor) || typeof cursor[key] !== 'object'){
          cursor[key] = {};
        }
        cursor = cursor[key];
      }
      const leaf = path[path.length - 1];
      const v = parseFloat(inp.value);
      cursor[leaf] = isNaN(v) ? 0 : v;
    });
    return result;
  }

  const saveConfBtn = $('#saveConfidence');
  if (saveConfBtn) saveConfBtn.addEventListener('click', () => {
    const payload = collectConfidence();
    postJ('/api/admin/confidence/update', payload)
      .then(() => alert('Confidence weights saved'))
      .catch(console.error);
  });

  // --- RuleGraph v2 / Subject Panel ----------------------------------------

  let rg2Events = [];

let rg2CurrentRule = null;
let rg2CurrentPaperId = null;

function fillSubjectFormFromRule(rule){
  if (!rule) return;
  const scope = rule.subject_scope || {};
  const demo = scope.demographics || {};
  const clin = scope.clinical_status || {};
  const cult = scope.culture || {};
  const traits = scope.traits_measured || [];
  const ageInput = $('#rg2AgeBandInput');
  const eduInput = $('#rg2EducationBandInput');
  const clinicalInput = $('#rg2ClinicalPopInput');
  const cultureInput = $('#rg2CultureRegionInput');
  const selfConstrInput = $('#rg2SelfConstrualInput');
  const nInput = $('#rg2SampleSizeInput');
  const traitsInput = $('#rg2TraitsInput');
  const modsInput = $('#rg2ModeratorsInput');

  if (ageInput) ageInput.value = demo.age_band || '';
  if (eduInput) eduInput.value = demo.education_band || '';
  if (clinicalInput) clinicalInput.value = clin.population || '';
  if (cultureInput) cultureInput.value = cult.region || '';
  if (selfConstrInput) selfConstrInput.value = cult.self_construal_profile || '';
  if (nInput){
    const n = demo.sample_size;
    nInput.value = (n === undefined || n === null) ? '' : String(n);
  }

  const traitNames = [];
  (traits || []).forEach(t => {
    if (t && t.name){
      traitNames.push(t.name);
    }
  });
  if (traitsInput) traitsInput.value = traitNames.join(', ');

  const lines = [];
  const mods = rule.subject_moderators || [];
  (mods || []).forEach(m => {
    if (!m) return;
    const dim = (m.dimension || m.moderator || '').trim();
    const attr = (m.attribute || '').trim();
    if (!dim && !attr) return;
    lines.push((dim || '') + '|' + (attr || ''));
  });
  if (modsInput) modsInput.value = lines.join('\n');
}

function 
function validateSubjectAgainstVocab(scope){
  const warnings = [];
  const vocab = rg2SubjectVocab || {};
  const demoV = (vocab.demographics || {});
  const clinV = (vocab.clinical_status || {});
  const cultV = (vocab.culture || {});

  const demo = (scope.demographics || {});
  const clin = (scope.clinical_status || {});
  const cult = (scope.culture || {});

  const age = (demo.age_band || '').trim();
  const edu = (demo.education_band || '').trim();
  const pop = (clin.population || '').trim();
  const region = (cult.region || '').trim();
  const selfC = (cult.self_construal_profile || '').trim();

  if (age && Array.isArray(demoV.age_band) && !demoV.age_band.includes(age)){
    warnings.push('Non-canonical age_band: ' + age);
  }
  if (edu && Array.isArray(demoV.education_band) && !demoV.education_band.includes(edu)){
    warnings.push('Non-canonical education_band: ' + edu);
  }
  if (pop && Array.isArray(clinV.population) && !clinV.population.includes(pop)){
    warnings.push('Non-canonical clinical population: ' + pop);
  }
  if (region && Array.isArray(cultV.region) && !cultV.region.includes(region)){
    warnings.push('Non-canonical culture region: ' + region);
  }
  if (selfC && Array.isArray(cultV.self_construal_profile) && !cultV.self_construal_profile.includes(selfC)){
    warnings.push('Non-canonical self-construal profile: ' + selfC);
  }

  return warnings;
}

buildSubjectScopeFromForm(){
  const ageInput = $('#rg2AgeBandInput');
  const eduInput = $('#rg2EducationBandInput');
  const clinicalInput = $('#rg2ClinicalPopInput');
  const cultureInput = $('#rg2CultureRegionInput');
  const selfConstrInput = $('#rg2SelfConstrualInput');
  const nInput = $('#rg2SampleSizeInput');
  const traitsInput = $('#rg2TraitsInput');

  const scope = {};
  const demographics = {};
  const clinical = {};
  const culture = {};

  if (ageInput && ageInput.value.trim()){
    demographics.age_band = ageInput.value.trim();
  }
  if (eduInput && eduInput.value.trim()){
    demographics.education_band = eduInput.value.trim();
  }
  if (nInput && nInput.value !== ''){
    const n = parseInt(nInput.value, 10);
    if (!Number.isNaN(n)){
      demographics.sample_size = n;
    }
  }
  if (clinicalInput && clinicalInput.value.trim()){
    clinical.population = clinicalInput.value.trim();
  }
  if (cultureInput && cultureInput.value.trim()){
    culture.region = cultureInput.value.trim();
  }
  if (selfConstrInput && selfConstrInput.value.trim()){
    culture.self_construal_profile = selfConstrInput.value.trim();
  }

  const traits = [];
  if (traitsInput && traitsInput.value){
    traitsInput.value.split(',').forEach(raw => {
      const name = raw.trim();
      if (name){
        traits.push({name});
      }
    });
  }

  if (Object.keys(demographics).length){
    scope.demographics = demographics;
  }
  if (Object.keys(clinical).length){
    scope.clinical_status = clinical;
  }
  if (Object.keys(culture).length){
    scope.culture = culture;
  }
  if (traits.length){
    scope.traits_measured = traits;
  }
  return scope;
}

function buildSubjectModeratorsFromForm(){
  const modsInput = $('#rg2ModeratorsInput');
  const out = [];
  if (!modsInput || !modsInput.value) return out;
  const lines = modsInput.value.split(/\r?\n/);
  lines.forEach(line => {
    const trimmed = line.trim();
    if (!trimmed) return;
    const parts = trimmed.split('|');
    const dim = (parts[0] || '').trim();
    const attr = (parts[1] || '').trim();
    if (!dim && !attr) return;
    const m = {};
    if (dim) m.dimension = dim;
    if (attr) m.attribute = attr;
    out.push(m);
  });
  return out;
}


  function collectAgeBands(events){
    const bands = new Set();
    (events || []).forEach(ev => {
      (ev.rules || []).forEach(rule => {
        const scope = rule.subject_scope || {};
        const demo = scope.demographics || {};
        const band = demo.age_band || null;
        if (band) bands.add(band);
      });
    });
    return Array.from(bands).sort();
  }

  function collectTraits(events){
    const traits = new Set();
    (events || []).forEach(ev => {
      (ev.rules || []).forEach(rule => {
        const scope = rule.subject_scope || {};
        const tlist = scope.traits_measured || [];
        tlist.forEach(t => {
          if (t && t.name){
            traits.add(t.name);
          }
        });
      });
    });
    return Array.from(traits).sort();
  }

  function populatePaperFilter(events){
    const sel = $('#rg2PaperFilter');
    if (!sel) return;
    const current = sel.value;
    const ids = Array.from(new Set((events || []).map(ev => ev.paper_id || '<unknown>'))).sort();
    sel.innerHTML = '';
    const optAll = document.createElement('option');
    optAll.value = '';
    optAll.textContent = 'All papers';
    sel.appendChild(optAll);
    ids.forEach(id => {
      const opt = document.createElement('option');
      opt.value = id;
      opt.textContent = id;
      sel.appendChild(opt);
    });
    if (current) {
      sel.value = current;
    }
  }

  function populateAgeBandFilter(events){
    const sel = $('#rg2AgeBandFilter');
    if (!sel) return;
    const current = sel.value;
    const bands = collectAgeBands(events);
    sel.innerHTML = '';
    const optAll = document.createElement('option');
    optAll.value = '';
    optAll.textContent = 'All age bands';
    sel.appendChild(optAll);
    bands.forEach(band => {
      const opt = document.createElement('option');
      opt.value = band;
      opt.textContent = band;
      sel.appendChild(opt);
    });
    if (current) {
      sel.value = current;
    }
  }

  function populateTraitFilter(events){
    const sel = $('#rg2TraitFilter');
    if (!sel) return;
    const current = sel.value;
    const traits = collectTraits(events);
    sel.innerHTML = '';
    const optAll = document.createElement('option');
    optAll.value = '';
    optAll.textContent = 'All traits';
    sel.appendChild(optAll);
    traits.forEach(tr => {
      const opt = document.createElement('option');
      opt.value = tr;
      opt.textContent = tr;
      sel.appendChild(opt);
    });
    if (current) {
      sel.value = current;
    }
  }

  function ruleMatchesFilters(ev, rule){
    const paperSel = $('#rg2PaperFilter');
    const paperIdFilter = paperSel ? (paperSel.value || '') : '';
    const searchInput = $('#rg2RuleSearch');
    const textFilter = searchInput ? (searchInput.value || '').trim().toLowerCase() : '';
    const ageSel = $('#rg2AgeBandFilter');
    const ageFilter = ageSel ? (ageSel.value || '') : '';
    const traitSel = $('#rg2TraitFilter');
    const traitFilter = traitSel ? (traitSel.value || '') : '';

    const paperId = ev.paper_id || '<unknown>';
    if (paperIdFilter && paperId !== paperIdFilter){
      return false;
    }

    const scopeSummary = rule.subject_scope_summary || '';
    const modsSummary = rule.moderators_summary || '';
    const text = (rule.rule_text || '') + ' ' + scopeSummary + ' ' + modsSummary;
    if (textFilter){
      if (!text.toLowerCase().includes(textFilter)){
        return false;
      }
    }

    const scope = rule.subject_scope || {};
    const demo = scope.demographics || {};
    const band = demo.age_band || '';
    if (ageFilter){
      if (!band || band !== ageFilter){
        return false;
      }
    }

    if (traitFilter){
      let found = false;
      const tlist = scope.traits_measured || [];
      tlist.forEach(t => {
        if (t && t.name === traitFilter){
          found = true;
        }
      });
      if (!found){
        return false;
      }
    }

    return true;
  }

  function renderRulegraphSummary(events, coverage){
    const container = $('#rulegraphV2Summary');
    if (!container) return;
    container.innerHTML = '';
    if (!events || !events.length){
      container.textContent = 'No RuleGraph v2 events found yet. Run Agent_Finder_v2 on at least one paper to populate subject-aware rules.';
      return;
    }

    const visibleEvents = [];

    (events || []).forEach(ev => {
const coveragePanel = $('#rg2CoveragePanel');
const globalEl = $('#rg2CoverageGlobal');
const paperEl = $('#rg2CoveragePaper');
if (coverage && coverage.global && globalEl){
  const g = coverage.global;
  const pct = (val) => (val * 100).toFixed(1) + '%';
  globalEl.textContent =
    'Global: ' + (g.rules_total || 0) + ' rule(s); ' +
    'age band ' + pct(g.pct_with_age_band || 0) + ', ' +
    'culture region ' + pct(g.pct_with_culture_region || 0) + ', ' +
    'clinical population ' + pct(g.pct_with_clinical_population || 0) + ', ' +
    'traits ' + pct(g.pct_with_traits || 0) + ', ' +
    'moderators ' + pct(g.pct_with_moderators || 0);
}
if (coveragePanel && paperEl){
  const paperSel = $('#rg2PaperFilter');
  const pid = paperSel ? paperSel.value : '';
  if (!pid){
    paperEl.textContent = 'Current paper: (All papers; select a specific paper to see per-paper coverage).';
  } else if (coverage && coverage.by_paper && coverage.by_paper[pid]){
    const cov = coverage.by_paper[pid];
    const pct = (val) => (val * 100).toFixed(1) + '%';
    paperEl.textContent =
      'Current paper ' + pid + ': ' + (cov.rules_total || 0) + ' rule(s); ' +
      'age band ' + pct(cov.pct_with_age_band || 0) + ', ' +
      'culture region ' + pct(cov.pct_with_culture_region || 0) + ', ' +
      'clinical population ' + pct(cov.pct_with_clinical_population || 0) + ', ' +
      'traits ' + pct(cov.pct_with_traits || 0) + ', ' +
      'moderators ' + pct(cov.pct_with_moderators || 0);
  } else {
    paperEl.textContent = 'Current paper: no coverage data available for this paper.';
  }
}


      const keptRules = [];
      (ev.rules || []).forEach(rule => {
        if (ruleMatchesFilters(ev, rule)){
          keptRules.push(rule);
        }
      });
      if (keptRules.length){
        visibleEvents.push({
          paper_id: ev.paper_id,
          rules_count: keptRules.length,
          rules: keptRules,
        });
      }
    });

    if (!visibleEvents.length){
      container.textContent = 'No rules match the current filters.';
      return;
    }

    visibleEvents.forEach(ev => {
      const card = document.createElement('div');
      card.className = 'rg2-card';

      const h = document.createElement('h3');
      h.textContent = ev.paper_id || '<unknown paper>';
      card.appendChild(h);

      const meta = document.createElement('div');
      meta.className = 'rg2-meta';
      meta.textContent = (ev.rules_count || 0) + ' rule(s)';
      card.appendChild(meta);

      (ev.rules || []).slice(0, 5).forEach(rule => {
        const row = document.createElement('div');
        row.className = 'rg2-rule';

        const txt = document.createElement('div');
        txt.textContent = rule.rule_text || '';
        row.appendChild(txt);

        const scope = document.createElement('div');
        scope.className = 'rg2-rule-code';
        scope.textContent = 'scope: ' + (rule.subject_scope_summary || '—');
        row.appendChild(scope);

        const mods = document.createElement('div');
        mods.className = 'rg2-rule-code';
        mods.textContent = 'moderators: ' + (rule.moderators_summary || '—');
        row.appendChild(mods);

        const typing = document.createElement('div');
        typing.className = 'rg2-rule-code';
        typing.textContent = rule.has_overrides ? 'subject typing: curated override' : 'subject typing: raw';
        row.appendChild(typing);

        const detailBtn = document.createElement('button');
        detailBtn.className = 'btn';
        detailBtn.textContent = 'Details';
        detailBtn.style.marginTop = '.25rem';
        detailBtn.addEventListener('click', () => {
          openRuleDetail(ev.paper_id || '<unknown>', rule.rule_id);
        });
        row.appendChild(detailBtn);

        card.appendChild(row);
      });

      container.appendChild(card);
    });
  }

  

function populateSubjectVocabControls(){
  if (!rg2SubjectVocab) return;
  const vocab = rg2SubjectVocab;
  const demo = vocab.demographics || {};
  const clin = vocab.clinical_status || {};
  const cult = vocab.culture || {};

  function fillSelect(id, values){
    const el = document.querySelector('#' + id);
    if (!el || !Array.isArray(values)) return;
    const current = el.value;
    while (el.firstChild) el.removeChild(el.firstChild);
    const optNone = document.createElement('option');
    optNone.value = '';
    optNone.textContent = '(none)';
    el.appendChild(optNone);
    values.forEach(v => {
      const opt = document.createElement('option');
      opt.value = v;
      opt.textContent = v;
      el.appendChild(opt);
    });
    if (current && values.includes(current)){
      el.value = current;
    }
  }

  fillSelect('rg2AgeBandInput', demo.age_band || []);
  fillSelect('rg2EducationBandInput', demo.education_band || []);
  fillSelect('rg2ClinicalPopInput', clin.population || []);
  fillSelect('rg2CultureRegionInput', cult.region || []);
  fillSelect('rg2SelfConstrualInput', cult.self_construal_profile || []);
}

async function loadRulegraphV2(){
    const data = await getJ('/api/admin/rulegraph_v2');
    rg2Events = data.events || [];
    rg2SubjectVocab = data.subject_vocab || null;
    populateSubjectVocabControls();
    populatePaperFilter(rg2Events);
    populateAgeBandFilter(rg2Events);
    populateTraitFilter(rg2Events);
    renderRulegraphSummary(rg2Events, data.coverage || null);
  }


async function openRuleDetail(paperId, ruleId){
  try{
    const data = await getJ('/api/admin/rulegraph_v2/' + encodeURIComponent(paperId));
    const rules = data.rules || [];
    const rule = rules.find(r => r.rule_id === ruleId) || null;
    const modal = $('#rg2DetailModal');
    const bodyJson = $('#rg2ModalBodyJson');
    const title = $('#rg2ModalTitle');
    const statusEl = $('#rg2SubjectStatus');
    if (!modal || !bodyJson || !title){
      console.warn('Rule detail modal elements missing');
      return;
    }
    rg2CurrentPaperId = paperId;
    rg2CurrentRule = rule;
    title.textContent = ruleId + ' @ ' + paperId;
    if (rule){
      bodyJson.textContent = JSON.stringify(rule, null, 2);
      fillSubjectFormFromRule(rule);
      if (statusEl){
        statusEl.textContent = rule.has_overrides ?
          'Using curated subject info (override stored on disk).' :
          'Using raw subject info from extraction (no override yet).';
      }
    } else {
      bodyJson.textContent = 'Rule not found in backend response.';
      if (statusEl){
        statusEl.textContent = '';
      }
    }
    modal.classList.remove('hidden');
  } catch(err){
    console.error(err);
    alert('Failed to load rule details: ' + err);
  }
}

hFilters(){
    const paperSel = $('#rg2PaperFilter');
    const searchInput = $('#rg2RuleSearch');
    const ageSel = $('#rg2AgeBandFilter');
    const traitSel = $('#rg2TraitFilter');

    if (paperSel){
      paperSel.addEventListener('change', () => {
        renderRulegraphSummary(rg2Events);
      });
    }
    if (searchInput){
      searchInput.addEventListener('input', () => {
        renderRulegraphSummary(rg2Events);
      });
    }
    if (ageSel){
      ageSel.addEventListener('change', () => {
        renderRulegraphSummary(rg2Events);
      });
    }
    if (traitSel){
      traitSel.addEventListener('change', () => {
        renderRulegraphSummary(rg2Events);
      });
    }
  }

  
function bindRulegraphModal(){
  const modal = $('#rg2DetailModal');
  const closeBtn = $('#rg2ModalClose');
  const saveBtn = $('#rg2SubjectSave');
  const resetBtn = $('#rg2SubjectReset');
  const statusEl = $('#rg2SubjectStatus');
  if (!modal || !closeBtn) return;

  const closeModal = () => {
    modal.classList.add('hidden');
  };

  closeBtn.addEventListener('click', () => {
    closeModal();
  });
  modal.addEventListener('click', (ev) => {
    if (ev.target && ev.target.classList.contains('modal-backdrop')){
      closeModal();
    }
  });
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape'){
      closeModal();
    }
  });

  if (saveBtn){
    saveBtn.addEventListener('click', async () => {
      if (!rg2CurrentPaperId || !rg2CurrentRule){
        if (statusEl) statusEl.textContent = 'No rule is currently selected.';
        return;
      }
      const scope = buildSubjectScopeFromForm();
      const moderators = buildSubjectModeratorsFromForm();
      const payload = {
        subject_scope: scope,
        subject_moderators: moderators,
      };
      const warnings = validateSubjectAgainstVocab(scope);
      try{
        const url = '/api/admin/rulegraph_v2/' +
          encodeURIComponent(rg2CurrentPaperId) + '/' +
          encodeURIComponent(rg2CurrentRule.rule_id) + '/subject';
        const res = await fetch(url, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          credentials: 'same-origin',
          body: JSON.stringify(payload),
        });
        if (!res.ok){
          throw new Error('Server error ' + res.status);
        }
        if (statusEl){
          if (warnings && warnings.length){
            statusEl.textContent = 'Saved subject info (non-canonical values: ' + warnings.join('; ') + ').';
          } else {
            statusEl.textContent = 'Saved subject info; BN export will now use curated values for this rule.';
          }
        }
        // Refresh the summary so scope/moderator text and override flags update.
        loadRulegraphV2().catch(console.error);
      } catch(err){
        console.error(err);
        if (statusEl){
          statusEl.textContent = 'Failed to save subject info: ' + err;
        }
      }
    });
  }

  if (resetBtn){
    resetBtn.addEventListener('click', () => {
      if (!rg2CurrentRule){
        if (statusEl) statusEl.textContent = 'No rule loaded to reset.';
        return;
      }
      const raw = Object.assign({}, rg2CurrentRule);
      raw.subject_scope = rg2CurrentRule.subject_scope_original || {};
      raw.subject_moderators = rg2CurrentRule.subject_moderators_original || [];
      fillSubjectFormFromRule(raw);
      if (statusEl){
        statusEl.textContent = 'Form reset to raw extracted subject info; Save to commit override, or close to discard.';
      }
    });
  }
}

;

window.addEventListener('load', () => {
  const downloadBtn = document.querySelector('#rg2DownloadCoverage');
  if (downloadBtn){
    downloadBtn.addEventListener('click', async () => {
      try{
        const data = await getJ('/api/admin/rulegraph_v2');
        const payload = {
          generated_at: new Date().toISOString(),
          coverage: data.coverage || null
        };
        const blob = new Blob([JSON.stringify(payload, null, 2)], {type: 'application/json'

const smokeBtn = document.querySelector('#rg2RunSmoke');
if (smokeBtn){
  smokeBtn.addEventListener('click', async () => {
    const original = smokeBtn.textContent;
    smokeBtn.disabled = true;  // keep simple boolean
    smokeBtn.textContent = 'Running v2 smoke...';
    try{
      const resp = await postJ('/api/admin/run_v2_smoke', {});
      const status = resp.status || 'unknown';
      alert('v2 subject pipeline smoke test: ' + status + '\n(returncode=' + (resp.returncode ?? 'n/a') + ')');
      console.log('run_v2_smoke response', resp);
    } catch(err){
      console.error('Failed to run v2 smoke', err);
      alert('Failed to run v2 smoke: ' + err);
    } finally {
      smokeBtn.disabled = false;
      smokeBtn.textContent = original;
    }
  });
}
});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'subject_coverage_snapshot.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } catch (err){
        console.error('Failed to download coverage JSON', err);
        alert('Failed to download coverage JSON: ' + err);
      }
    });
  }
});

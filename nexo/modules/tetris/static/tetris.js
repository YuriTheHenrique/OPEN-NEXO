(() => {
'use strict';

/* =========================================================
   NEXO · TEMA (SINCRONIZAÇÃO DO CANVAS)
   ========================================================= */

// Quando o botão do header alternar o tema, redesenha o canvas do jogo
document.getElementById('themeButton')?.addEventListener('click', () => {
    setTimeout(() => {
        if (typeof draw === 'function') {
            draw();
        }
    }, 50);
});


/* ============================ constants ============================ */
const COLS = 10, ROWS = 20, HIDDEN = 2, TOTAL_ROWS = ROWS + HIDDEN;

const COLORS = {
  I:['#22d3ee','#0891b2'], J:['#60a5fa','#2563eb'], L:['#fb923c','#ea580c'],
  O:['#fde047','#eab308'], S:['#4ade80','#16a34a'], T:['#c084fc','#9333ea'],
  Z:['#fb7185','#e11d48']
};

const SHAPES = {
  I:[[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
  J:[[1,0,0],[1,1,1],[0,0,0]],
  L:[[0,0,1],[1,1,1],[0,0,0]],
  O:[[1,1],[1,1]],
  S:[[0,1,1],[1,1,0],[0,0,0]],
  T:[[0,1,0],[1,1,1],[0,0,0]],
  Z:[[1,1,0],[0,1,1],[0,0,0]]
};

// SRS wall kicks, y already flipped to screen space (positive = down)
const KICKS = {
  '0>1':[[0,0],[-1,0],[-1,-1],[0,2],[-1,2]],
  '1>0':[[0,0],[1,0],[1,1],[0,-2],[1,-2]],
  '1>2':[[0,0],[1,0],[1,1],[0,-2],[1,-2]],
  '2>1':[[0,0],[-1,0],[-1,-1],[0,2],[-1,2]],
  '2>3':[[0,0],[1,0],[1,-1],[0,2],[1,2]],
  '3>2':[[0,0],[-1,0],[-1,1],[0,-2],[-1,-2]],
  '3>0':[[0,0],[-1,0],[-1,1],[0,-2],[-1,-2]],
  '0>3':[[0,0],[1,0],[1,-1],[0,2],[1,2]]
};
const KICKS_I = {
  '0>1':[[0,0],[-2,0],[1,0],[-2,1],[1,-2]],
  '1>0':[[0,0],[2,0],[-1,0],[2,-1],[-1,2]],
  '1>2':[[0,0],[-1,0],[2,0],[-1,-2],[2,1]],
  '2>1':[[0,0],[1,0],[-2,0],[1,2],[-2,-1]],
  '2>3':[[0,0],[2,0],[-1,0],[2,-1],[-1,2]],
  '3>2':[[0,0],[-2,0],[1,0],[-2,1],[1,-2]],
  '3>0':[[0,0],[1,0],[-2,0],[1,2],[-2,-1]],
  '0>3':[[0,0],[-1,0],[2,0],[-1,-2],[2,1]]
};

const LOCK_DELAY = 500, MAX_RESETS = 15, CLEAR_MS = 240;
const DAS = 150, ARR = 35, SOFT_MS = 35;
const gravityMs = lvl => Math.pow(0.8 - (lvl - 1) * 0.007, lvl - 1) * 1000;

/* ============================ canvases ============================ */
const $ = id => document.getElementById(id);
const boardCv = $('board'), bctx = boardCv.getContext('2d');
const nextCv  = $('next'),  nctx = nextCv.getContext('2d');
const holdCv  = $('hold'),  hctx = holdCv.getContext('2d');

let CELL = 24, NEXT_COUNT = 5, narrow = false;

function fitCanvas(cv, ctx, w, h){
  const dpr = Math.min(window.devicePixelRatio || 1, 2.5);
  cv.style.width = w + 'px'; cv.style.height = h + 'px';
  cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  cv._w = w; cv._h = h;
}
function cardInner(el){ return Math.max(48, el.clientWidth - 20); }

function layout(){
  narrow = window.innerWidth <= 640;
  NEXT_COUNT = narrow ? 3 : 5;

  // 1. size the previews first — their widths come from the cards, not the board
  const previewH = narrow ? (window.innerHeight <= 720 ? 36 : 42) : 74;
  fitCanvas(holdCv, hctx, cardInner($('holdCard')), previewH);
  fitCanvas(nextCv, nctx, cardInner($('nextCard')), narrow ? previewH : NEXT_COUNT * 44);

  // 2. shrink the board to a probe size and measure everything around it, so the
  //    board always gets exactly the height that's actually left over
  const PROBE = 10;
  fitCanvas(boardCv, bctx, COLS * PROBE, ROWS * PROBE);
  const gameContainer =
      document.querySelector('.game-section');

  const chrome =
      gameContainer.getBoundingClientRect().height -
      ROWS * PROBE;
  const availH = window.innerHeight - chrome - 20;
  const availW = narrow ? window.innerWidth - 34 : Math.min(window.innerWidth - 340, 470);

  // 3. give the board the biggest square cell that fits
  CELL = Math.max(12, Math.min(Math.floor(Math.min(availW / COLS, availH / ROWS)), 38));
  fitCanvas(boardCv, bctx, COLS * CELL, ROWS * CELL);

  draw();
}

/* ============================ state ============================ */
let grid, piece, holdType, canHold, queue, bag;
let score = 0, lines = 0, level = 1, combo = -1, backToBack = false;
let dropTimer = 0, lockTimer = 0, lockResets = 0, grounded = false;
let lastMoveWasRotate = false;
let clearing = null;
let state = 'menu';                       // menu | playing | paused | over
let last = 0, overSince = 0;
const RESTART_GRACE = 800;                // don't let a mashed key skip the score screen
let best = +(localStorage.getItem('tetris-best') || 0);
let soundOn = localStorage.getItem('tetris-sound') !== '0';

const newGrid = () => Array.from({length:TOTAL_ROWS}, () => Array(COLS).fill(null));

function refillBag(){
  const p = ['I','J','L','O','S','T','Z'];
  for (let i = p.length - 1; i > 0; i--){
    const j = Math.floor(Math.random() * (i + 1));
    [p[i], p[j]] = [p[j], p[i]];
  }
  bag.push(...p);
}
function nextType(){ while (bag.length < 8) refillBag(); return bag.shift(); }

function makePiece(type){
  const m = SHAPES[type].map(r => r.slice());
  let top = 0;
  while (m[top].every(v => !v)) top++;
  return { type, m, r:0, x: Math.floor((COLS - m.length) / 2), y: HIDDEN - top };
}
function rotateM(m, dir){
  const n = m.length, out = Array.from({length:n}, () => Array(n).fill(0));
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++)
    dir > 0 ? out[x][n-1-y] = m[y][x] : out[n-1-x][y] = m[y][x];
  return out;
}
function collides(p, ox = 0, oy = 0, m = p.m){
  for (let y = 0; y < m.length; y++) for (let x = 0; x < m.length; x++){
    if (!m[y][x]) continue;
    const gx = p.x + x + ox, gy = p.y + y + oy;
    if (gx < 0 || gx >= COLS || gy >= TOTAL_ROWS) return true;
    if (gy >= 0 && grid[gy][gx]) return true;
  }
  return false;
}

/* ============================ game flow ============================ */
function reset(){
  grid = newGrid(); bag = []; queue = [];
  for (let i = 0; i < 6; i++) queue.push(nextType());
  holdType = null; canHold = true;
  score = 0; lines = 0; level = 1; combo = -1; backToBack = false;
  clearing = null; lastMoveWasRotate = false;
  held.left = held.right = false; softHeld = false;
  spawn();
  updateHUD();
}
function spawn(){
  piece = makePiece(queue.shift());
  queue.push(nextType());
  canHold = true; grounded = false;
  lockTimer = 0; lockResets = 0; dropTimer = 0; lastMoveWasRotate = false;
  if (collides(piece)) gameOver();
}

function move(dx){
  if (!piece || collides(piece, dx, 0)) return false;
  piece.x += dx; lastMoveWasRotate = false; touchLock(); sfx('move'); draw();
  return true;
}
function rotate(dir){
  if (!piece) return;
  if (piece.type === 'O'){ sfx('rot'); return; }
  const from = piece.r, to = (piece.r + (dir > 0 ? 1 : 3)) % 4;
  const m = rotateM(piece.m, dir);
  const table = piece.type === 'I' ? KICKS_I : KICKS;
  for (const [kx, ky] of table[from + '>' + to]){
    if (!collides(piece, kx, ky, m)){
      piece.m = m; piece.r = to; piece.x += kx; piece.y += ky;
      lastMoveWasRotate = true; touchLock(); sfx('rot'); draw();
      return;
    }
  }
}
function softDrop(){
  if (!piece || collides(piece, 0, 1)) return;
  piece.y++; score++; dropTimer = 0; lastMoveWasRotate = false;
  updateHUD(); draw();
}
function hardDrop(){
  if (!piece) return;
  let d = 0;
  while (!collides(piece, 0, d + 1)) d++;
  piece.y += d; score += d * 2;
  if (d) lastMoveWasRotate = false;
  sfx('drop'); lockNow();
}
function hold(){
  if (!piece || !canHold) return;
  const t = piece.type;
  if (holdType) piece = makePiece(holdType);
  else { piece = makePiece(queue.shift()); queue.push(nextType()); }
  holdType = t; canHold = false;
  grounded = false; lockTimer = 0; lockResets = 0; dropTimer = 0; lastMoveWasRotate = false;
  sfx('hold');
  if (collides(piece)) gameOver(); else draw();
}
function touchLock(){
  if (!collides(piece, 0, 1)) { grounded = false; return; }
  if (grounded && lockResets < MAX_RESETS){ lockTimer = 0; lockResets++; }
}

/* T-spin: 3-corner rule, last action must have been a rotation */
function tSpinKind(){
  if (piece.type !== 'T' || !lastMoveWasRotate) return null;
  const cx = piece.x + 1, cy = piece.y + 1;
  const occ = (x, y) => (x < 0 || x >= COLS || y >= TOTAL_ROWS) ? true
                      : (y < 0 ? false : !!grid[y][x]);
  const c = [[cx-1,cy-1],[cx+1,cy-1],[cx-1,cy+1],[cx+1,cy+1]];   // TL TR BL BR
  const filled = c.map(([x,y]) => occ(x,y));
  if (filled.filter(Boolean).length < 3) return null;
  const frontIdx = {0:[0,1], 1:[1,3], 2:[3,2], 3:[2,0]}[piece.r];
  return (filled[frontIdx[0]] && filled[frontIdx[1]]) ? 'tspin' : 'mini';
}

function lockNow(){
  if (!piece) return;
  const spin = tSpinKind();
  for (let y = 0; y < piece.m.length; y++) for (let x = 0; x < piece.m.length; x++){
    if (!piece.m[y][x]) continue;
    const gy = piece.y + y, gx = piece.x + x;
    if (gy >= 0) grid[gy][gx] = piece.type;
  }
  piece = null;

  const full = [];
  for (let y = 0; y < TOTAL_ROWS; y++) if (grid[y].every(Boolean)) full.push(y);

  if (full.length){
    clearing = { rows: full, t: 0, spin };
    sfx(full.length === 4 ? 'tetris' : 'clear');
    draw();
    return;
  }

  if (spin){
    score += (spin === 'tspin' ? 400 : 100) * level;
    toast(spin === 'tspin' ? 'T-SPIN' : 'T-SPIN MINI');
    backToBack = true;
  }
  combo = -1;
  updateHUD();
  spawn();
  draw();
}

function applyClear(){
  const { rows, spin } = clearing;
  const n = rows.length;
  // remove bottom-up: splicing top-down would shift the indices still to come
  for (const y of [...rows].sort((a, b) => b - a)) grid.splice(y, 1);
  for (let i = 0; i < n; i++) grid.unshift(Array(COLS).fill(null));

  const base = spin
    ? (spin === 'tspin' ? [0,800,1200,1600][n] : [0,200,400,600][n])
    : [0,100,300,500,800][n];

  const difficult = (n === 4) || !!spin;
  let pts = base * level;
  const b2b = difficult && backToBack;
  if (b2b) pts = Math.round(pts * 1.5);
  backToBack = difficult;

  combo++;
  if (combo > 0) pts += 50 * combo * level;

  score += pts;
  lines += n;
  const newLevel = Math.min(20, Math.floor(lines / 10) + 1);
  const levelled = newLevel > level;
  level = newLevel;

  let label = spin ? (spin === 'tspin' ? 'T-SPIN ' : 'T-SPIN MINI ') : '';
  label += ['','LINHA','DUPLA','TRIPLA','TETRIS'][n];
  if (b2b) label = 'B2B ' + label;
  if (combo > 0) label += '  ×' + (combo + 1);
  toast(label);
  if (levelled){ setTimeout(() => toast('NÍVEL ' + level), 420); sfx('level'); }

  clearing = null;
  updateHUD();
  spawn();
  draw();
}

function gameOver(){
  state = 'over';
  overSince = performance.now();
  piece = null;
  const isBest = score > best && score > 0;
  if (isBest){ best = score; localStorage.setItem('tetris-best', best); }
  sfx('over');
  updateHUD();
  showOverlay('GAME OVER',
    isBest ? 'Novo recorde pessoal. Boa partida.' : 'Dessa vez a pilha levou a melhor.',
    'Jogar novamente',
    `Score <b>${score.toLocaleString()}</b> · Lines <b>${lines}</b> · Level <b>${level}</b><br>` +
    `Best <b>${best.toLocaleString()}</b>`);
  draw();
}

/* ============================ loop ============================ */
function tick(ts){
  requestAnimationFrame(tick);
  const dt = Math.min(ts - last, 100); last = ts;
  if (state !== 'playing') return;

  if (clearing){
    clearing.t += dt;
    if (clearing.t >= CLEAR_MS) applyClear(); else draw();
    return;
  }
  if (!piece) return;

  handleRepeat(dt);
  if (!piece) return;

  const speed = softHeld ? Math.min(gravityMs(level), SOFT_MS) : gravityMs(level);
  dropTimer += dt;
  if (dropTimer >= speed){
    dropTimer = 0;
    if (!collides(piece, 0, 1)){
      piece.y++;
      if (softHeld){ score++; updateHUD(); }
      lastMoveWasRotate = false;
      draw();
    }
  }

  if (collides(piece, 0, 1)){
    grounded = true;
    lockTimer += dt;
    if (lockTimer >= LOCK_DELAY) lockNow();
  } else {
    grounded = false; lockTimer = 0;
  }
}

/* ============================ drawing ============================ */
function roundRect(ctx, x, y, w, h, r){
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y,     x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x,     y + h, r);
  ctx.arcTo(x,     y + h, x,     y,     r);
  ctx.arcTo(x,     y,     x + w, y,     r);
  ctx.closePath();
}

function block(ctx, px, py, size, type, alpha = 1, ghost = false){

  const [c1, c2] = COLORS[type];

  const pad = Math.max(1, size * 0.055);
  const r = Math.max(2, size * 0.18);

  const x = px + pad;
  const y = py + pad;
  const s = size - pad * 2;

  ctx.save();

  ctx.globalAlpha = alpha;

  if (ghost){

    ctx.globalAlpha = alpha * 0.10;
    ctx.fillStyle = c1;

    roundRect(ctx, x, y, s, s, r);
    ctx.fill();

    ctx.globalAlpha = alpha * 0.45;
    ctx.strokeStyle = c1;
    ctx.lineWidth = Math.max(1.2, size * 0.065);

    roundRect(ctx, x, y, s, s, r);
    ctx.stroke();

  } else {

    /* Peça sólida, sem degradê ou brilho */
    ctx.fillStyle = c1;

    roundRect(ctx, x, y, s, s, r);
    ctx.fill();

    /* Borda discreta para separar os blocos */
    ctx.globalAlpha = alpha * 0.28;
    ctx.strokeStyle = c2;
    ctx.lineWidth = Math.max(1, size * 0.045);

    roundRect(ctx, x, y, s, s, r);
    ctx.stroke();
  }

  ctx.restore();
}

function draw(){
  const W = COLS * CELL, H = ROWS * CELL;
  const rootStyle =
      getComputedStyle(document.documentElement);

  const boardBg =
      rootStyle
          .getPropertyValue('--board-bg')
          .trim();

  const gridColor =
      rootStyle
          .getPropertyValue('--grid')
          .trim();

  bctx.fillStyle = boardBg || '#edf1f3';
  bctx.fillRect(0, 0, W, H);

  bctx.strokeStyle =
      gridColor || 'rgba(8, 49, 74, 0.075)';

  bctx.lineWidth = 1;
  bctx.beginPath();
  for (let x = 1; x < COLS; x++){ bctx.moveTo(x * CELL + .5, 0); bctx.lineTo(x * CELL + .5, H); }
  for (let y = 1; y < ROWS; y++){ bctx.moveTo(0, y * CELL + .5); bctx.lineTo(W, y * CELL + .5); }
  bctx.stroke();

  if (!grid) return;

  const flash = clearing ? Math.min(1, clearing.t / CLEAR_MS) : 0;

  for (let y = HIDDEN; y < TOTAL_ROWS; y++){
    const isClearing = clearing && clearing.rows.includes(y);
    for (let x = 0; x < COLS; x++){
      const t = grid[y][x];
      if (!t) continue;
      const px = x * CELL, py = (y - HIDDEN) * CELL;
      if (isClearing){
        block(bctx, px, py, CELL, t, 1 - flash);
        bctx.save();
        bctx.globalAlpha = Math.max(0, 1 - Math.abs(flash - .3) * 2.4) * 0.95;
        bctx.fillStyle = '#fff';
        roundRect(bctx, px + 2, py + 2, CELL - 4, CELL - 4, CELL * .18);
        bctx.fill();
        bctx.restore();
      } else {
        block(bctx, px, py, CELL, t);
      }
    }
  }

  if (piece && state === 'playing'){
    let d = 0;
    while (!collides(piece, 0, d + 1)) d++;
    if (d > 0) drawPiece(piece, piece.y + d, true);
    drawPiece(piece, piece.y, false);
  }

  if (state === 'playing'){
    let top = TOTAL_ROWS;
    for (let y = HIDDEN; y < TOTAL_ROWS; y++) if (grid[y].some(Boolean)){ top = y; break; }
    const depth = (top - HIDDEN) / ROWS;
    if (depth < 0.22){
      const a = (0.22 - depth) / 0.22 * 0.3;
      const g = bctx.createLinearGradient(0, 0, 0, H * 0.5);
      g.addColorStop(0, `rgba(244,63,94,${a})`);
      g.addColorStop(1, 'rgba(244,63,94,0)');
      bctx.fillStyle = g; bctx.fillRect(0, 0, W, H);
    }
  }

  drawNext(); drawHold();
}

function drawPiece(p, atY, ghost){
  for (let y = 0; y < p.m.length; y++) for (let x = 0; x < p.m.length; x++){
    if (!p.m[y][x]) continue;
    const gy = atY + y;
    if (gy < HIDDEN) continue;
    block(bctx, (p.x + x) * CELL, (gy - HIDDEN) * CELL, CELL, p.type, 1, ghost);
  }
}

function miniPiece(ctx, type, cx, cy, size){
  const m = SHAPES[type], cells = [];
  for (let y = 0; y < m.length; y++) for (let x = 0; x < m.length; x++) if (m[y][x]) cells.push([x, y]);
  const xs = cells.map(c => c[0]), ys = cells.map(c => c[1]);
  const minX = Math.min(...xs), minY = Math.min(...ys);
  const w = Math.max(...xs) - minX + 1, h = Math.max(...ys) - minY + 1;
  const ox = cx - w * size / 2 - minX * size;
  const oy = cy - h * size / 2 - minY * size;
  for (const [x, y] of cells) block(ctx, ox + x * size, oy + y * size, size, type);
}

function drawNext(){
  if (!nextCv._w || !queue) return;
  const w = nextCv._w, h = nextCv._h;
  nctx.clearRect(0, 0, w, h);
  const n = Math.min(NEXT_COUNT, queue.length);
  for (let i = 0; i < n; i++){
    const size = narrow ? Math.min(13, (w / n) / 4.6, h / 2.6)
                        : Math.min(19, w / 5.2, (h / n) / 2.4);
    if (narrow) miniPiece(nctx, queue[i], (i + .5) * (w / n), h / 2, size);
    else        miniPiece(nctx, queue[i], w / 2, (i + .5) * (h / n), i === 0 ? size * 1.1 : size);
  }
}
function drawHold(){
  if (!holdCv._w) return;
  const w = holdCv._w, h = holdCv._h;
  hctx.clearRect(0, 0, w, h);
  if (!holdType) return;
  hctx.globalAlpha = canHold ? 1 : 0.3;
  miniPiece(hctx, holdType, w / 2, h / 2, Math.min(20, w / 5, h / 2.4));
  hctx.globalAlpha = 1;
}

/* ============================ HUD ============================ */
function updateHUD(){
  $('score').textContent = score.toLocaleString();
  $('best').textContent  = best.toLocaleString();
  $('lines').textContent = lines;
  $('level').textContent = level;
}
let toastTimer;
function toast(msg){
  const el = $('toast');
  el.textContent = msg;
  el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('pop'), 1000);
}
function showOverlay(title, text, btn, scoreLine){
  $('ovTitle').textContent = title;
  $('ovText').textContent = text;
  $('ovBtn').textContent = btn;
  const s = $('ovScore');
  if (scoreLine){ s.innerHTML = scoreLine; s.style.display = ''; } else s.style.display = 'none';
  $('overlay').classList.add('show');
}
const hideOverlay = () => $('overlay').classList.remove('show');

/* ============================ sound ============================ */
let ac = null;
const NOTES = {
  move:[[330,.03,.05,'square']], rot:[[440,.04,.06,'square']],
  drop:[[180,.08,.09,'triangle']], hold:[[520,.05,.07,'sine']],
  clear:[[660,.08,.10,'triangle'],[880,.08,.10,'triangle']],
  tetris:[[523,.09,.10,'square'],[659,.09,.10,'square'],[784,.09,.12,'square'],[1047,.11,.20,'square']],
  level:[[659,.08,.10,'sine'],[880,.08,.16,'sine']],
  over:[[330,.11,.16,'sawtooth'],[247,.11,.18,'sawtooth'],[165,.11,.32,'sawtooth']]
};
function sfx(kind){
  if (!soundOn || !NOTES[kind]) return;
  try{
    ac = ac || new (window.AudioContext || window.webkitAudioContext)();
    if (ac.state === 'suspended') ac.resume();
    const t0 = ac.currentTime;
    NOTES[kind].forEach(([f, v, d, type], i) => {
      const o = ac.createOscillator(), g = ac.createGain();
      o.type = type; o.frequency.value = f;
      const st = t0 + i * 0.075;
      g.gain.setValueAtTime(0.0001, st);
      g.gain.linearRampToValueAtTime(v, st + 0.008);
      g.gain.exponentialRampToValueAtTime(0.0001, st + d);
      o.connect(g); g.connect(ac.destination);
      o.start(st); o.stop(st + d + 0.02);
    });
  }catch(e){}
}

/* ============================ input ============================ */
const held = { left:false, right:false };
let dasDir = 0, dasTimer = 0, arrTimer = 0, softHeld = false;

function handleRepeat(dt){
  const dir = held.left && !held.right ? -1 : (held.right && !held.left ? 1 : 0);
  if (dir === 0){ dasDir = 0; dasTimer = 0; arrTimer = 0; return; }
  if (dir !== dasDir){ dasDir = dir; dasTimer = 0; arrTimer = 0; move(dir); return; }
  dasTimer += dt;
  if (dasTimer >= DAS){
    arrTimer += dt;
    while (arrTimer >= ARR){ arrTimer -= ARR; if (!move(dir)) break; }
  }
}

function act(a){
  if (a === 'left')  held.left = true;
  if (a === 'right') held.right = true;
  if (a === 'soft')  softHeld = true;
  if (state !== 'playing' || clearing || !piece) return;
  switch(a){
    case 'left':  dasDir = 0; move(-1); dasDir = -1; dasTimer = 0; arrTimer = 0; break;
    case 'right': dasDir = 0; move(1);  dasDir =  1; dasTimer = 0; arrTimer = 0; break;
    case 'soft':  softDrop(); break;
    case 'rotcw': rotate(1); break;
    case 'rotccw':rotate(-1); break;
    case 'hard':  hardDrop(); break;
    case 'hold':  hold(); break;
  }
}
function release(a){
  if (a === 'left')  held.left = false;
  if (a === 'right') held.right = false;
  if (a === 'soft')  softHeld = false;
}

const KEYMAP = {
  arrowleft:'left', arrowright:'right', arrowdown:'soft',
  arrowup:'rotcw', x:'rotcw', z:'rotccw', control:'rotccw',
  ' ':'hard', c:'hold', shift:'hold'
};

document.addEventListener('keydown', e => {
  const k = e.key.toLowerCase();
  if (k in KEYMAP) e.preventDefault();

  if (k === 'p' || k === 'escape'){ togglePause(); return; }
  if (state !== 'playing' && (k === 'enter' || k === ' ')){ e.preventDefault(); startOrResume(); return; }
  if (e.repeat) return;
  const a = KEYMAP[k];
  if (a) act(a);
});
document.addEventListener('keyup', e => {
  const a = KEYMAP[e.key.toLowerCase()];
  if (a === 'left' || a === 'right' || a === 'soft') release(a);
});
window.addEventListener('blur', () => { held.left = held.right = false; softHeld = false; });

document.querySelectorAll('.touch button').forEach(b => {
  const a = b.dataset.act;
  const down = e => { e.preventDefault(); act(a); };
  const up   = e => { e.preventDefault(); release(a); };
  b.addEventListener('touchstart', down, {passive:false});
  b.addEventListener('touchend', up, {passive:false});
  b.addEventListener('touchcancel', up, {passive:false});
  b.addEventListener('mousedown', down);
  b.addEventListener('mouseup', up);
  b.addEventListener('mouseleave', up);
});

/* swipe / tap on the board */
let tp = null;
boardCv.addEventListener('touchstart', e => {
  const t = e.touches[0];
  tp = { x:t.clientX, y:t.clientY, lx:t.clientX, ly:t.clientY, time:performance.now(), moved:false };
}, {passive:true});
boardCv.addEventListener('touchmove', e => {
  if (!tp || state !== 'playing') return;
  const t = e.touches[0];
  const dx = t.clientX - tp.lx, dy = t.clientY - tp.ly;
  const step = Math.max(18, CELL * 1.05);
  if (Math.abs(dx) > step && Math.abs(dx) >= Math.abs(dy)){
    const dir = dx > 0 ? 'right' : 'left';
    act(dir); release(dir);
    tp.lx = t.clientX; tp.ly = t.clientY; tp.moved = true;
  } else if (dy > step){
    softDrop();
    tp.ly = t.clientY; tp.lx = t.clientX; tp.moved = true;
  }
}, {passive:true});
boardCv.addEventListener('touchend', e => {
  if (!tp) return;
  const ch = e.changedTouches[0];
  const dt = performance.now() - tp.time;
  const dx = ch.clientX - tp.x, dy = ch.clientY - tp.y;
  if (!tp.moved && dt < 260 && Math.abs(dx) < 14 && Math.abs(dy) < 14) act('rotcw');
  else if (!tp.moved && dy > 70 && dt < 320) act('hard');
  softHeld = false;
  tp = null;
}, {passive:true});

/* ============================ buttons ============================ */
function startOrResume(){
  if (state === 'playing') return;
  if (state === 'over' && performance.now() - overSince < RESTART_GRACE) return;
  if (state === 'paused'){ state = 'playing'; hideOverlay(); last = performance.now(); return; }
  reset();
  state = 'playing';
  hideOverlay();
  last = performance.now();
  sfx('level');
  draw();
}
function togglePause(){
  if (state === 'playing'){
    state = 'paused';
    held.left = held.right = false; softHeld = false;
    showOverlay('PAUSA', 'Cuidado pra não cair do cavalo.', 'Continuar');
  } else if (state === 'paused'){
    startOrResume();
  }
}
// blur after clicking, so later Space/Enter presses go to the game and not the button
const onTap = (id, fn) => $(id).addEventListener('click', e => { e.currentTarget.blur(); fn(); });
onTap('ovBtn', () => {
    console.log('TETRIS: INICIAR CLICADO');
    console.log('TETRIS: estado antes =', state);

    startOrResume();

    console.log('TETRIS: estado depois =', state);
});
onTap('btnPause', togglePause);
$('btnSound').addEventListener('click', e => {
  e.currentTarget.blur();
  soundOn = !soundOn;
  localStorage.setItem('tetris-sound', soundOn ? '1' : '0');
  paintSoundBtn();
  if (soundOn) sfx('hold');
});
function paintSoundBtn(){
  const b = $('btnSound');
  b.textContent = soundOn ? 'SOUND' : 'MUTED';
  b.style.color = soundOn ? '' : 'rgba(255,255,255,.24)';
}
paintSoundBtn();

document.addEventListener('visibilitychange', () => { if (document.hidden && state === 'playing') togglePause(); });
window.addEventListener('resize', layout);
window.addEventListener('orientationchange', () => setTimeout(layout, 200));

/* ============================ boot ============================ */
grid = newGrid(); bag = []; queue = [];
for (let i = 0; i < 6; i++) queue.push(nextType());
updateHUD();
layout();
requestAnimationFrame(tick);

})();

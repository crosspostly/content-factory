# ✅ Content Factory - Следующие шаги

**Дата:** Декабрь 2025  
**Статус:** Active sprint planning  
**Timeframe:** Next 2 weeks

---

## 🎯 Immediate Priorities (This Week)

### Day 1-2: Documentation & Planning

- [x] **ТЗ #1: Актуализация документации** ✅ DONE
  - [x] README.md updated
  - [x] IMPLEMENTATION_STATUS.md created
  - [x] SUBTITLE_IMPLEMENTATION_PLAN.md verified
  - [x] All references to Edge-TTS removed

- [x] **ТЗ #2: Анализ и план развития** ✅ IN PROGRESS
  - [x] IMPLEMENTATION_STATUS.md - детальный анализ
  - [x] MODES_ARCHITECTURE.md - архитектура
  - [x] DEVELOPMENT_ROADMAP.md - дорожная карта
  - [x] BOTTLENECKS_AND_IMPROVEMENTS.md - узкие места
  - [x] NEXT_STEPS.md - action items (this file)

- [ ] **Create GitHub Issues** для всех tasks
  - [ ] Issue #25: [CRITICAL] Fix TTS Module (создать тишину → реальный голос)
  - [ ] Issue #26: [HIGH] Add monitoring & structured logging
  - [ ] Issue #27: [HIGH] Add video rendering retry logic
  - [ ] Issue #28: [MEDIUM] Implement script caching
  - [ ] Issue #29: [MEDIUM] Optimize video rendering performance
  - [ ] Issue #30: [LOW] Add thumbnail generation
  - **Owner:** Tech Lead
  - **Effort:** 2 hours

- [ ] **Setup GitHub Projects** для tracking
  - [ ] Create "Content Factory Development" project
  - [ ] Add all issues to Kanban board
  - [ ] Columns: Backlog / In Progress / Review / Done
  - **Owner:** Tech Lead
  - **Effort:** 1 hour

---

## 🔴 Sprint 1: Critical Bugfixes (Week 1)

**Goal:** Исправить TTS блокер и добавить quick wins

### Priority 1: Fix TTS Module (🔴 CRITICAL)

**Issue:** #25  
**Owner:** Tech Lead / Backend Dev  
**Effort:** 2-3 дня

#### Day 1: Research & Prototype

- [ ] **Research TTS options**
  - [ ] Test Edge-TTS (free alternative)
  - [ ] Research Google Cloud TTS API
  - [ ] Compare voice quality
  - [ ] Test Russian language support
  - **Deliverable:** Technical decision document
  - **Time:** 4 hours

- [ ] **Prototype Edge-TTS integration**
  - [ ] Install `edge-tts` package
  - [ ] Create simple test script
  - [ ] Synthesize test audio (ru-RU-DariyaNeural)
  - [ ] Verify audio quality
  - **Deliverable:** Working prototype
  - **Time:** 2 hours

#### Day 2: Implementation

- [ ] **Update `tts_generator.py`**
  - [ ] Replace Gemini TTS calls with Edge-TTS
  - [ ] Keep same interface (async synthesis)
  - [ ] Add error handling
  - [ ] Add fallback (silent audio as last resort)
  - **Deliverable:** Updated module
  - **Time:** 4 hours

- [ ] **Test integration**
  - [ ] Test shorts synthesis
  - [ ] Test long-form synthesis (3 blocks)
  - [ ] Test ad synthesis
  - [ ] Verify audio format (22050Hz mono WAV)
  - **Deliverable:** Passing integration tests
  - **Time:** 2 hours

#### Day 3: Testing & Deployment

- [ ] **Update unit tests**
  - [ ] Modify `test_tts_generator.py`
  - [ ] Add Edge-TTS specific tests
  - [ ] Test error scenarios
  - [ ] Run full test suite
  - **Deliverable:** Passing tests
  - **Time:** 3 hours

- [ ] **End-to-end test**
  - [ ] Generate complete video (script → TTS → render)
  - [ ] Verify voice is NOT silent
  - [ ] Check audio quality
  - [ ] Test all modes (shorts, long_form, ad)
  - **Deliverable:** Working video with voice
  - **Time:** 2 hours

- [ ] **Documentation update**
  - [ ] Update IMPLEMENTATION_STATUS.md
  - [ ] Document Edge-TTS usage
  - [ ] Add troubleshooting guide
  - **Deliverable:** Updated docs
  - **Time:** 1 hour

**Success Criteria:**
- [x] Videos have REAL voice (not silence)
- [x] Voice quality: 7+/10 (subjective)
- [x] Success rate: >95%
- [x] All tests passing

---

### Priority 2: Add Retry Logic (🟠 HIGH)

**Issue:** #27  
**Owner:** Backend Dev  
**Effort:** 4-6 hours

- [ ] **Install retry library**
  ```bash
  pip install tenacity
  ```

- [ ] **Add retry decorator to video rendering**
  ```python
  from tenacity import retry, stop_after_attempt, wait_exponential
  
  @retry(
      stop=stop_after_attempt(3),
      wait=wait_exponential(multiplier=1, min=2, max=16)
  )
  def render_video(script, audio, mode):
      ...
  ```

- [ ] **Add cleanup on retry**
  - [ ] Delete partial video files
  - [ ] Close MoviePy resources
  - [ ] Log retry attempts

- [ ] **Test retry logic**
  - [ ] Simulate failure (disconnect network)
  - [ ] Verify automatic retry
  - [ ] Check cleanup

**Success Criteria:**
- [x] Failed renders automatically retry (max 3x)
- [x] Cleanup происходит правильно
- [x] Logs показывают retry attempts

---

### Priority 3: Add Script Caching (🟡 MEDIUM)

**Issue:** #28  
**Owner:** Backend Dev  
**Effort:** 2-3 hours

- [ ] **Implement cache check**
  ```python
  def get_or_generate_script(project, date, mode, force=False):
      if not force:
          cached = check_cache(project, date, mode)
          if cached:
              logger.info("Using cached script")
              return cached
      
      logger.info("Generating new script")
      return generate_script(project, date, mode)
  ```

- [ ] **Add CLI flag**
  ```bash
  python main.py --force-refresh  # Ignore cache
  ```

- [ ] **Add cache cleanup**
  - [ ] Delete scripts older than 30 days
  - [ ] Run daily via cron/GitHub Actions

**Success Criteria:**
- [x] Running twice на same day reuses script
- [x] `--force-refresh` ignores cache
- [x] Cache cleanup works

---

## 🟠 Sprint 2: Monitoring & Logging (Week 2)

**Goal:** Add visibility для production debugging

### Priority 1: Structured Logging (🟠 HIGH)

**Issue:** #26  
**Owner:** DevOps / Backend Dev  
**Effort:** 2-3 дня

#### Day 1: Implement JSON logging

- [ ] **Create JSON formatter**
  - [ ] File: `core/utils/json_logger.py`
  - [ ] Format: timestamp, level, component, message, context
  - [ ] Add request ID tracking
  - **Time:** 2 hours

- [ ] **Update all loggers**
  - [ ] `script_generator.py`
  - [ ] `tts_generator.py`
  - [ ] `video_renderer.py`
  - [ ] `pipeline_orchestrator.py`
  - **Time:** 3 hours

- [ ] **Add log rotation**
  - [ ] Use `logging.handlers.RotatingFileHandler`
  - [ ] Max size: 10MB per file
  - [ ] Keep last 10 files
  - **Time:** 1 hour

#### Day 2: Performance tracking

- [ ] **Create performance decorator**
  - [ ] File: `core/utils/performance.py`
  - [ ] Track duration для каждого component
  - [ ] Log timing information
  - **Time:** 2 hours

- [ ] **Apply to all generators**
  - [ ] `@track_performance("script_generator")`
  - [ ] `@track_performance("tts_generator")`
  - [ ] `@track_performance("video_renderer")`
  - **Time:** 2 hours

- [ ] **Add metrics collection**
  - [ ] Success/failure counts
  - [ ] Average duration
  - [ ] Error rates
  - **Time:** 2 hours

#### Day 3: Error tracking

- [ ] **Implement GitHub Issue auto-creation**
  - [ ] File: `core/utils/error_tracker.py`
  - [ ] On error → create GitHub Issue
  - [ ] Categorize errors (script/TTS/video)
  - [ ] Add duplicate detection
  - **Time:** 4 hours

- [ ] **Add error context**
  - [ ] Request ID
  - [ ] Project, mode, date
  - [ ] Stack trace
  - [ ] Config snapshot
  - **Time:** 2 hours

**Success Criteria:**
- [x] All logs in JSON format
- [x] Performance timing for all components
- [x] Errors auto-create GitHub Issues
- [x] No duplicate issues

---

### Priority 2: Alerting (🟡 MEDIUM)

**Owner:** DevOps  
**Effort:** 1-2 дня

- [ ] **Setup email alerts**
  - [ ] On critical errors (TTS failure, video crash)
  - [ ] Daily summary report
  - **Time:** 3 hours

- [ ] **Optional: Telegram bot**
  - [ ] Create bot via @BotFather
  - [ ] Send alerts to admin chat
  - **Time:** 2 hours

- [ ] **Configure alert thresholds**
  - [ ] Error rate > 5%
  - [ ] Average duration > 10 minutes
  - **Time:** 1 hour

**Success Criteria:**
- [x] Email alerts на critical failures
- [x] Daily summary reports
- [x] No false positives (< 1%)

---

## 📅 Week 3-4: Performance Optimization

**Goal:** Ускорить рендеринг в 2x

### Priority 1: FFmpeg Optimization

- [ ] **Change preset to "fast"**
  ```python
  clip.write_videofile(
      preset="fast",  # Instead of "medium"
      threads=4
  )
  ```
  - **Expected:** 2x faster
  - **Time:** 1 hour

- [ ] **Benchmark comparison**
  - [ ] Test quality difference
  - [ ] Measure speed improvement
  - [ ] Compare file sizes
  - **Time:** 2 hours

### Priority 2: Stock Video Caching

- [ ] **Implement cache system**
  ```python
  def get_stock_video(keywords):
      cache_key = hashlib.md5(keywords.encode()).hexdigest()
      cache_path = Path("cache/stock") / f"{cache_key}.mp4"
      
      if cache_path.exists():
          return str(cache_path)
      
      download_and_cache(keywords, cache_path)
      return str(cache_path)
  ```
  - **Expected:** 30-60 sec saving per video
  - **Time:** 3 hours

- [ ] **Add cache cleanup**
  - [ ] LRU eviction (100 videos max)
  - [ ] Or time-based (30 days)
  - **Time:** 2 hours

### Priority 3: Parallel Rendering (Long-form)

- [ ] **Implement parallel block rendering**
  ```python
  from concurrent.futures import ProcessPoolExecutor
  
  with ProcessPoolExecutor(max_workers=3) as executor:
      futures = [
          executor.submit(render_block, "love", ...),
          executor.submit(render_block, "money", ...),
          executor.submit(render_block, "health", ...)
      ]
      blocks = [f.result() for f in futures]
  ```
  - **Expected:** 3x faster для long-form
  - **Time:** 1 day

**Success Criteria:**
- [x] Shorts: <5 minutes (down from 5-10)
- [x] Long-form: <10 minutes (down from 15-20)
- [x] Quality: same or better

---

## 📊 Success Metrics (2 weeks)

### Technical Metrics

- [ ] **TTS Success Rate:** 95%+ (currently 0%)
- [ ] **Video Generation Success Rate:** 95%+ (currently ~90%)
- [ ] **Average Script Generation Time:** <2 minutes
- [ ] **Average Shorts Rendering Time:** <5 minutes
- [ ] **Average Long-form Rendering Time:** <10 minutes

### Operational Metrics

- [ ] **Manual Interventions per Week:** 0 (currently ~5)
- [ ] **Mean Time To Detect (MTTD):** <1 hour
- [ ] **Mean Time To Repair (MTTR):** <2 hours
- [ ] **Test Coverage:** 80%+ (currently unknown)

### Business Metrics

- [ ] **Videos Generated per Day:** 10+ consistently
- [ ] **API Cost per Video:** <$0.20
- [ ] **Infrastructure Cost per Video:** <$0.50
- [ ] **Total Cost per Video:** <$1

---

## 🚀 How to Get Started

### For Tech Lead

1. **Create GitHub Issues** (2 hours)
   ```bash
   # Use GitHub CLI
   gh issue create --title "[CRITICAL] Fix TTS Module" --body "..."
   gh issue create --title "[HIGH] Add monitoring" --body "..."
   # etc.
   ```

2. **Setup project board** (1 hour)
   ```bash
   gh project create --title "Content Factory Development"
   gh project item-add <project-id> --issue <issue-number>
   ```

3. **Assign tasks** (30 min)
   - Assign #25 (TTS) to Backend Dev
   - Assign #26 (Monitoring) to DevOps
   - Assign #27-28 to Backend Dev

### For Backend Dev

1. **Start with Issue #25** (TTS fix)
   ```bash
   git checkout -b fix/tts-module
   # Work on Edge-TTS integration
   git commit -m "fix: replace Gemini TTS with Edge-TTS"
   gh pr create --title "Fix TTS Module" --body "Fixes #25"
   ```

2. **Then Issue #27** (Retry logic)
   ```bash
   git checkout -b feat/video-retry
   # Add retry decorator
   git commit -m "feat: add retry logic for video rendering"
   gh pr create --title "Add Video Retry Logic" --body "Fixes #27"
   ```

### For DevOps

1. **Work on Issue #26** (Monitoring)
   ```bash
   git checkout -b feat/structured-logging
   # Implement JSON logging
   git commit -m "feat: add structured JSON logging"
   gh pr create --title "Add Structured Logging" --body "Fixes #26"
   ```

2. **Setup CI/CD improvements**
   - Add pytest-cov для coverage reports
   - Add linting (ruff)
   - Add type checking (mypy)

---

## 📝 Daily Standup Template

```markdown
## Daily Standup - [Date]

### ✅ Yesterday
- [ ] Task 1 completed
- [ ] Task 2 in progress (70% done)

### 🚧 Today
- [ ] Complete Task 2
- [ ] Start Task 3

### ⚠️ Blockers
- None / [Blocker description]

### 📊 Metrics
- TTS success rate: X%
- Videos generated: X
- Errors: X (link to issues)
```

---

## 🎯 Definition of Done

Для каждой задачи:

- [ ] **Code complete** and reviewed
- [ ] **Tests passing** (unit + integration)
- [ ] **Documentation updated**
- [ ] **PR merged** to main branch
- [ ] **Deployed** to production
- [ ] **Monitoring** shows success
- [ ] **Issue closed**

---

## 📞 Support & Questions

**Technical questions:**
- Create GitHub Issue с label "question"
- Tag @tech-lead

**Urgent production issues:**
- Create GitHub Issue с label "critical"
- Send email to tech-lead@company.com
- (Optional) Message на Telegram

**General discussion:**
- GitHub Discussions
- Weekly team meeting

---

## 📅 Calendar

```
Week 1 (Dec 16-22):
  Mon-Tue: Documentation (ТЗ #1, #2) ✅
  Wed-Fri: TTS fix + Quick wins

Week 2 (Dec 23-29):
  Mon-Wed: Monitoring & logging
  Thu-Fri: Performance optimization start

Week 3 (Dec 30 - Jan 5):
  Mon-Fri: Performance optimization complete

Week 4 (Jan 6-12):
  Mon-Fri: Testing, polish, wrap-up Sprint 1-2
```

---

## ✅ Checklist Before Starting

- [x] All documentation reviewed
- [ ] GitHub Issues created
- [ ] Project board setup
- [ ] Team notified
- [ ] Environment verified (dependencies installed)
- [ ] Test suite running
- [ ] Production access confirmed

---

**Последнее обновление:** Декабрь 2025  
**Owner:** Tech Lead  
**Следующий review:** End of Week 1

**Related Documents:**
- IMPLEMENTATION_STATUS.md - current state
- DEVELOPMENT_ROADMAP.md - long-term plan
- BOTTLENECKS_AND_IMPROVEMENTS.md - detailed analysis
- MODES_ARCHITECTURE.md - system architecture

#!/bin/bash
#
# Model Compliance Verification Script
# Checks that all workflows and code use only Gemini 2.5 Flash models
#
# Usage: ./verify-model-compliance.sh
# Exit codes:
#   0 = All compliant
#   1 = Violations found
#

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  🔍 Gemini Model Compliance Verification"
echo "═══════════════════════════════════════════════════════════"
echo ""

VIOLATIONS=0
REPO_ROOT="${1:-.}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📂 Repository root: $REPO_ROOT"
echo ""

# ============================================================================
# CHECK 1: Scan for deprecated Gemini models
# ============================================================================
echo "🔎 CHECK 1: Scanning for deprecated Gemini models..."
echo "   Looking for: gemini-2.0, gemini-1.5, gemini-1.0, gemini-pro"
echo ""

DEPRECATED_PATTERNS="gemini-2\.0-flash|gemini-1\.5-flash|gemini-1\.0|gemini-pro"
FOUND_DEPRECATED=$(grep -r "$DEPRECATED_PATTERNS" "$REPO_ROOT" \
  --include="*.yml" \
  --include="*.yaml" \
  --include="*.py" \
  --include="*.md" \
  2>/dev/null || true)

if [ -z "$FOUND_DEPRECATED" ]; then
    echo -e "   ${GREEN}✅ PASS${NC} - No deprecated models found"
else
    echo -e "   ${RED}❌ FAIL${NC} - Found deprecated models:"
    echo "$FOUND_DEPRECATED" | sed 's/^/     /'
    VIOLATIONS=$((VIOLATIONS + 1))
fi
echo ""

# ============================================================================
# CHECK 2: Verify workflows only use gemini-2.5
# ============================================================================
echo "🔎 CHECK 2: Verifying workflows use only Gemini 2.5 models..."
echo ""

WORKFLOW_DIR="$REPO_ROOT/.github/workflows"
if [ -d "$WORKFLOW_DIR" ]; then
    WORKFLOW_COUNT=$(find "$WORKFLOW_DIR" -name "*.yml" -o -name "*.yaml" | wc -l)
    echo "   Found $WORKFLOW_COUNT workflow files"
    
    # Check each workflow
    for workflow in $(find "$WORKFLOW_DIR" -name "*.yml" -o -name "*.yaml" 2>/dev/null); do
        FILENAME=$(basename "$workflow")
        
        # Skip non-Gemini workflows
        if ! grep -q "gemini\|GEMINI" "$workflow" 2>/dev/null; then
            echo "   ⊘ $FILENAME - No Gemini models (N/A)"
            continue
        fi
        
        # Check for valid models
        HAS_2_5=$(grep -q "gemini-2\.5" "$workflow" && echo "yes" || echo "no")
        if [ "$HAS_2_5" = "yes" ]; then
            echo "   ${GREEN}✅${NC} $FILENAME - Uses Gemini 2.5"
        else
            echo "   ${RED}❌${NC} $FILENAME - Missing Gemini 2.5 models"
            VIOLATIONS=$((VIOLATIONS + 1))
        fi
    done
else
    echo "   ⚠️  Workflow directory not found: $WORKFLOW_DIR"
fi
echo ""

# ============================================================================
# CHECK 3: Verify Python code uses model_router
# ============================================================================
echo "🔎 CHECK 3: Checking Python code for proper Gemini usage..."
echo ""

PYTHON_FILES=$(find "$REPO_ROOT/core" "$REPO_ROOT/tests" -name "*.py" 2>/dev/null | wc -l)
echo "   Found $PYTHON_FILES Python files in core/ and tests/"

# Check for hardcoded deprecated models in Python
DEPRECATED_PY=$(grep -r "GenerativeModel\(.*gemini-2\.0\|GenerativeModel\(.*gemini-1\." \
  "$REPO_ROOT/core" "$REPO_ROOT/tests" \
  2>/dev/null || true)

if [ -z "$DEPRECATED_PY" ]; then
    echo "   ${GREEN}✅${NC} PASS - No deprecated models in Python code"
else
    echo "   ${RED}❌${NC} FAIL - Found deprecated models in Python:"
    echo "$DEPRECATED_PY" | sed 's/^/     /'
    VIOLATIONS=$((VIOLATIONS + 1))
fi
echo ""

# ============================================================================
# CHECK 4: Verify model_router.py configuration
# ============================================================================
echo "🔎 CHECK 4: Verifying model_router.py configuration..."
echo ""

ROUTER_FILE="$REPO_ROOT/core/utils/model_router.py"
if [ -f "$ROUTER_FILE" ]; then
    # Check for required models
    HAS_2_5_FLASH=$(grep -q "gemini-2\.5-flash" "$ROUTER_FILE" && echo "yes" || echo "no")
    HAS_2_5_LITE=$(grep -q "gemini-2\.5-flash-lite" "$ROUTER_FILE" && echo "yes" || echo "no")
    
    if [ "$HAS_2_5_FLASH" = "yes" ] && [ "$HAS_2_5_LITE" = "yes" ]; then
        echo "   ${GREEN}✅${NC} PASS - model_router.py has 2.5-flash and 2.5-flash-lite"
    else
        echo "   ${RED}❌${NC} FAIL - model_router.py missing required models"
        echo "     - Has 2.5-flash: $HAS_2_5_FLASH"
        echo "     - Has 2.5-flash-lite: $HAS_2_5_LITE"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
else
    echo "   ⚠️  model_router.py not found: $ROUTER_FILE"
fi
echo ""

# ============================================================================
# CHECK 5: Count total Gemini model references
# ============================================================================
echo "🔎 CHECK 5: Summary of Gemini model usage..."
echo ""

TOTAL_2_5=$(grep -r "gemini-2\.5" "$REPO_ROOT" \
  --include="*.yml" --include="*.py" --include="*.md" \
  2>/dev/null | wc -l)

TOTAL_2_5_FLASH=$(grep -r "gemini-2\.5-flash" "$REPO_ROOT" \
  --include="*.yml" --include="*.py" --include="*.md" \
  2>/dev/null | wc -l)

TOTAL_2_5_LITE=$(grep -r "gemini-2\.5-flash-lite" "$REPO_ROOT" \
  --include="*.yml" --include="*.py" --include="*.md" \
  2>/dev/null | wc -l)

echo "   Total Gemini 2.5 references: $TOTAL_2_5"
echo "   - gemini-2.5-flash: $TOTAL_2_5_FLASH"
echo "   - gemini-2.5-flash-lite: $TOTAL_2_5_LITE"
echo ""

# ============================================================================
# FINAL RESULT
# ============================================================================
echo "═══════════════════════════════════════════════════════════"

if [ $VIOLATIONS -eq 0 ]; then
    echo -e "${GREEN}✅ COMPLIANCE CHECK PASSED${NC}"
    echo ""
    echo "All workflows and code are compliant with Gemini 2.5 Flash standards."
    exit 0
else
    echo -e "${RED}❌ COMPLIANCE CHECK FAILED${NC}"
    echo ""
    echo "Found $VIOLATIONS violation(s) in model standards."
    echo ""
    echo "To fix, see: .github/gemini/MODEL_STANDARDIZATION.md"
    exit 1
fi

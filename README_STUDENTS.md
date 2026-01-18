# Article Eater v20.7.0 - Student Guide 🎓
Ports: Source-of-truth in contracts/ports.json.

**Learn to extract evidence from papers with AI in 5 minutes!**

---

## ⚡ Super Quick Start

```bash
# 1. Install (one time)
pip install jsonschema pyyaml pydantic

# 2. Test it works (no API key needed!)
python3 STUDENT_QUICKSTART.py

# 3. Done! You're ready to extract evidence!
```

---

## 🎯 What You'll Learn

- Extract findings from academic papers automatically
- Cluster findings into design rules
- Discover links between concepts
- Weight evidence by study quality

**Perfect for**: CNfA research, systematic reviews, meta-analyses

---

## 📚 Three Ways to Learn

### 1. Mock Mode (Start Here!)

No API keys needed. Perfect for learning:

```python
import os
os.environ['AE_LLM_PROVIDER'] = 'mock'

from src.agents.agent_stubs import Agent_Finder

paper = "Natural light reduces stress (p<0.01)..."
result = Agent_Finder(paper, "Study abstract")

print(f"Found {len(result.items)} findings!")
```

### 2. Free Tier (Get Started)

Get a free API key from Google:

```bash
# Sign up at: https://makersuite.google.com/app/apikey
export AE_LLM_PROVIDER=gemini
export GEMINI_API_KEY=your-free-key

# Now use real AI!
python3 -c "from src.agents.agent_stubs import Agent_Finder; \
            r=Agent_Finder('Your paper', 'abstract'); \
            print(f'Extracted {len(r.items)} findings!')"
```

### 3. Production (Advanced)

For serious research:

- OpenAI GPT-4: Best quality
- Anthropic Claude: Good balance
- Gemini Pro: Fast and free

---

## 🔬 Complete Example

```python
from src.agents.agent_stubs import (
    Agent_Finder, Agent_Aggregator, Agent_Linker, BBN_Calibrator
)

# Your paper text
paper_text = """
Study examined effects of natural light on stress.
Results showed 23% reduction in cortisol (p=0.003, d=0.67, N=120).
Confidence interval: [0.42, 0.92].
"""

# Extract findings
findings = Agent_Finder(paper_text, "Study on natural light and stress")
items = [item.dict() for item in findings.items]

print(f"✅ Extracted {len(items)} findings")

# Cluster into rules
rules = Agent_Aggregator(items)
print(f"✅ Generated {len(rules['rule_candidates'])} rule candidates")

# Find connections
links = Agent_Linker(rules, items)
print(f"✅ Found {len(links['links'])} connections")

# Calculate confidence
confidence = BBN_Calibrator(items)
print(f"✅ Overall confidence: {confidence['overall_weight']:.2f}")
```

---

## 📖 Learning Path

### Week 1: Basics
1. Run `STUDENT_QUICKSTART.py`
2. Test with mock provider
3. Extract from one paper

### Week 2: Real Data
1. Get API key (Gemini free tier)
2. Extract from 5 papers
3. Explore the results

### Week 3: Advanced
1. Aggregate findings into rules
2. Discover links
3. Calculate confidence weights

### Week 4: Research
1. Process your own papers
2. Build evidence base
3. Generate insights

---

## 🎓 Class Projects

### Beginner Project
**Extract findings from 10 papers on biophilic design**
- Use Agent_Finder
- Compare p-values and effect sizes
- Create summary table

### Intermediate Project
**Generate design rules from 20 papers**
- Extract findings
- Cluster with Agent_Aggregator
- Identify contradictions

### Advanced Project
**Map knowledge network in CNfA**
- Extract from 50+ papers
- Find all chains and synergies
- Calculate confidence weights
- Visualize the network

---

## 🐛 Common Issues

### "No module named 'jsonschema'"
**Fix**: `pip install jsonschema`

### "No module named 'src'"
**Fix**: Make sure you're in the `ae_v20_7_0` directory

### "LLM provider not set"
**Fix**: `export AE_LLM_PROVIDER=mock` (for testing)

### "API key invalid"
**Fix**: Check your key, use mock mode, or get new key

---

## 💡 Pro Tips

1. **Start with mock** - Learn without spending money
2. **Use Gemini free tier** - 60 requests/minute free
3. **Save your extractions** - JSON files are your friend
4. **Check the schema** - See `prompts/seven_panel_schema.json`
5. **Edit prompts** - They're in `prompts/` and you can change them!

---

## 📞 Help Resources

- **Quick Start**: Run `python3 STUDENT_QUICKSTART.py`
- **Full Guide**: Read `HANDOFF_v20.7.0_BUGFIX.md`
- **API Docs**: Check `docs/` directory
- **Examples**: See code snippets above

---

## ✅ Checklist

Before starting your research:

- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Tested with mock provider (works!)
- [ ] Got API key (or using mock)
- [ ] Read this guide
- [ ] Ran first extraction
- [ ] Understand the output

---

## 🎉 You're Ready!

You now have:
- ✅ AI-powered evidence extraction
- ✅ Automatic rule generation
- ✅ Link discovery
- ✅ Confidence weighting
- ✅ Complete documentation

**Start extracting evidence now!**

---

**Version**: 20.7.0  
**Status**: Student-Ready ✅  
**Cost**: Free (with Gemini) or paid (OpenAI/Anthropic)

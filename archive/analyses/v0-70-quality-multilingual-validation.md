> *Type: Document (specification) · Audience: QA · Status: Archived — v0 historical generation*

# 📚 Multi-lingual Documentation Validation System

**AI-powered semantic similarity checking for translations across 11 languages**

---

## 🎯 Quick Overview

This system automatically validates semantic equivalence between documentation translations using:

- **Embeddings** (multilingual-e5-large) for fast similarity checks
- **LLM reasoning** (DeepSeek-R1-Distill-32B) for deep validation
- **On-demand GPU** (A100 spot instances) - only when documents change
- **Two deployment options** - Self-hosted or AWS Cloud

### Your Use Case

- 📄 **1,000 documents** (11,000 with translations)
- 🌍 **11 languages** (English + 10 Indian languages)
- ⏱️ **Periodic validation** (4 runs/month, ~20 min each)
- 💰 **Total cost:** $70-90/month including infrastructure

---

## 💰 Cost Summary

| Component                   | Self-Hosted               | GitHub + AWS      |
| --------------------------- | ------------------------- | ----------------- |
| **Infrastructure**    | $90/month | $73/month     |                   |
| **GPU (16 hrs/year)** | $1.04/month | $1.04/month |                   |
| **Setup Time**        | 4 hours                   | 2 hours           |
| **5-Year Total**      | $5,460 | $4,440           |                   |
| **Maintenance**       | High (you manage)         | Low (AWS manages) |

**Winner:** GitHub + AWS (cheaper, faster, less work)

---

## 🚀 Quick Start

### Option 1: Self-Hosted GitLab

```bash
cd gitlab-selfhosted/
cp .env.example .env
nano .env  # Configure
sudo ./scripts/setup.sh
# Access GitLab at http://your-ip:8080
# Access Wiki.js at http://your-ip:3000
```

### Option 2: GitHub + AWS

```bash
cd github-aws/
cp .env.example .env
nano .env  # Configure AWS credentials
cd terraform && terraform init && terraform apply
cd .. && ./scripts/setup-github.sh
# Access Wiki.js at ALB URL from terraform output
```

---

## 📊 How It Works

```
Developer commits → CI/CD detects changes → Provisions A100 GPU (2 min)
    ↓
Validation Pipeline (20 min):
  • Load multilingual embedding model
  • Generate embeddings for changed docs
  • Calculate cosine similarity
  • Deep LLM check for borderline cases
    ↓
Results posted to PR/commit → GPU terminated automatically
```

**Key Insight:** Self-hosting an A100 GPU would waste 99.8% capacity and cost $32,600 over 5 years. Our solution uses on-demand spot instances costing only $18.72 over 5 years.

---

## 🎯 Which Version to Choose?

### Choose GitHub + AWS ✅ (Recommended)

- ✅ Cheaper: $74/month vs $91/month
- ✅ Faster setup: 2 hours vs 4 hours
- ✅ Less maintenance: AWS manages 90%
- ✅ Better uptime: 99.99% SLA
- ✅ Auto-scaling included

### Choose Self-Hosted GitLab

- ✅ Full data control
- ✅ On-premise deployment
- ✅ Government/compliance requirements
- ✅ Open-source preference
- ✅ No cloud vendor dependency

---

## 📦 Package Contents

```
.
├── README.md (this file)
├── gitlab-selfhosted/
│   ├── README.md (complete setup guide)
│   ├── docker-compose.yml
│   ├── .gitlab-ci.yml
│   ├── .env.example
│   ├── scripts/
│   │   ├── setup.sh
│   │   ├── provision_gpu.py
│   │   └── backup.sh
│   └── validation/
│       └── validate.py
└── github-aws/
    ├── README.md (complete AWS guide)
    ├── .github/workflows/validate.yml
    ├── terraform/main.tf
    ├── .env.example
    ├── lambda/gpu_orchestrator.py
    └── scripts/setup-github.sh
```

---

## 🔍 Technology Stack

- **Documentation:** Wiki.js (Git-backed, 200K context)
- **Embeddings:** multilingual-e5-large (100+ languages)
- **Reasoning:** DeepSeek-R1-Distill-32B (32B params, MIT license)
- **Vector DB:** Qdrant (embedding cache)
- **GPU:** A100 80GB spot instances ($0.78/hr)

---

## 📚 Documentation

Comprehensive guides included:

- ✅ **gitlab-selfhosted/README.md** - 800+ lines, complete setup
- ✅ **github-aws/README.md** - 900+ lines, AWS deployment
- ✅ Architecture diagrams
- ✅ Troubleshooting guides
- ✅ Security hardening
- ✅ Cost optimization
- ✅ Backup/recovery procedures

---

## 📞 Next Steps

1. **Choose your version** based on requirements
2. **Read the README** in that directory
3. **Follow setup guide** (mostly automated)
4. **Configure and deploy** (~2-4 hours)
5. **Test with sample docs**

**Ready to deploy!** 🚀

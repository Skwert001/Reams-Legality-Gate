# How to Publish to Zendo / Zenodo

**Purpose:**  
To create a formal, citable record of the Reams-Legality-Gate project and assign a DOI (Digital Object Identifier) for permanent reference.

---

## 1. Create a Zenodo account

1. Visit [https://zenodo.org](https://zenodo.org)  
2. Sign in using your GitHub credentials.  
3. Authorize Zenodo to access your GitHub repositories.

---

## 2. Link the GitHub repository

1. Go to [Zenodo GitHub Link](https://zenodo.org/account/settings/github/).  
2. Enable **Skwert001 / Reams-Legality-Gate** by toggling the switch.  
3. Zenodo will now archive each tagged release you make on GitHub.

---

## 3. Create a release on GitHub

1. Navigate to your repo:  
   [https://github.com/Skwert001/Reams-Legality-Gate](https://github.com/Skwert001/Reams-Legality-Gate)  
2. Click **Releases → Create a new release**.  
3. Tag version: `v0.84.0`  
4. Release title: `Ω.84 – Energy-Based Legality-Gate SDK`  
5. Description: paste your abstract summary from `docs/ZENDO_ABSTRACT.md`.  
6. Attach any key files you want archived (optional).  
7. Click **Publish release**.

Zenodo will automatically create a new record and assign a DOI.

---

## 4. Verify the DOI

1. After publishing, visit your [Zenodo Dashboard](https://zenodo.org/account/).  
2. You’ll see the Reams-Legality-Gate record with a DOI (e.g., `10.5281/zenodo.xxxxx`).  
3. Copy the DOI and add it to your GitHub README under **Citation / DOI**.

Example snippet to insert in your README:

```markdown
## Citation
If you use this work, please cite:

**Reams, Matthew William (2025). _Reams-Legality-Gate: Energy-Based Legality Gating for AI Reasoning (Ω.84)._ Zenodo.**
[https://doi.org/10.5281/zenodo.xxxxx](https://doi.org/10.5281/zenodo.xxxxx)

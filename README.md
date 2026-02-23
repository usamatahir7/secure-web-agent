# Adversarial-Resilient Agent Harness

A secure execution harness for an autonomous ReAct agent. This project equips an LLM with the ability to dynamically search the web and fetch webpage content, while heavily sanitizing the untrusted HTML payload to defend against indirect prompt injections, DoS attacks, and data exfiltration.

📖 **[Read the Design Document](https://docs.google.com/document/d/1w9jmXLV9FDeDPTZtfgphw2TdniKnSVphELg0Imr20XY)**

## ⚙️ Setup & Installation

**1. Clone the repository and navigate to the directory:**

```bash
git clone https://github.com/usamatahir7/secure-web-agent.git
cd YOUR_REPO_NAME

```

**2. Create and activate a virtual environment:**

* **Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```

* **Windows:**
```bash
python -m venv venv
venv\Scripts\activate

```

**3. Install dependencies:**
Install the required libraries via the requirements file:

```bash
pip install -r requirements.txt

```

**4. Set your OpenAI API Key:**
This project requires an OpenAI API key to run the `gpt-4o-mini` model. Please set it as an environment variable in your terminal as follows:

* **Mac/Linux:**
```bash
export OPENAI_API_KEY="your-api-key-here"

```

* **Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your-api-key-here

```

* **Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"

```

---

## 🚀 How to Run the Agent

To execute the agent loop, simply run the `agent.py` file:

```bash
python agent.py

```

By default, the agent will execute the test query: *"How is the weather in Tokyo?"* If you wish to test a different research goal, open `agent.py` and modify the `test_query` string located at the very bottom of the file inside the `if __name__ == "__main__":` block.

---

## 🛡️ How to Run the Adversarial Test Suite

To validate the harness defenses without exposing the agent to live malicious infrastructure, a local testing suite is provided. It uses Python's `unittest` framework and `unittest.mock.patch` to intercept network requests and serve simulated adversarial HTML payloads.

Run the test suite with a single command:

```bash
python tests.py

```

**The suite tests 5 specific adversarial vectors:**

1. **Data Exfiltration:** Attempts to steal the user's prompt via an embedded `<img>` tracking pixel.
2. **Malicious Redirects:** Attempts to force the scraper to a phishing site using `<script>` tags.
3. **Denial of Service (DoS):** Attempts to overflow the LLM context window with a massive 20,000+ character payload.
4. **Invisible Prompt Injections:** Attempts to hide malicious system overrides in hidden `<style>` CSS blocks.
5. **Iframe Hijacking:** Attempts to embed secondary malicious domains inside the legitimate target page.

---

## ⏱️ Assumptions & Shortcuts (Time Constraints)

Given the 4–6 hour time budget, the following engineering trade-offs and assumptions were made:

* **Search Provider & Routing:** I utilized the unofficial `duckduckgo-search` library to remove the friction of requiring reviewers to use third-party API keys. In production, I would replace this with an enterprise API (like Tavily) and implement a **Semantic Router** to forcefully trigger the search loop for factual queries rather than relying solely on the LLM's judgment.
* **Pre-Fetch vs. Post-Fetch Sanitization:** The agent currently relies entirely on post-fetch DOM sanitization. With more time, I would integrate a Threat Intelligence API (like VirusTotal) at the orchestration layer to block malicious URLs *before* the agent ever visits them.
* **Semantic Prompt Injections:** My guardrails physically strip executable code and hidden CSS, but an attacker could still write plain-text jailbreaks disguised as normal paragraphs. A production system would utilize a secondary, highly restricted **Evaluator LLM** to scan scraped text for manipulative intent before passing it to the main agent.
* **DOM Sanitization vs. Headless Browser:** I used `BeautifulSoup` and `requests` for fast, lightweight scraping. Because `requests` cannot execute JavaScript, this harness will fail to read Single Page Applications (SPAs). Ideally, I would upgrade to an isolated Playwright/Puppeteer Docker container with strict network egress policies.
* **Context Memory Compression:** The loop currently appends up to 5,000 characters of raw scraped text directly to the message history. To prevent blowing out the LLM's token limit and inflating API costs on longer tasks, I would add an intermediate summarization tool to compress the facts before the next loop iteration.
* **CoT Exposure Risk:** To ensure `gpt-4o-mini` reliably generated accurate search queries, I forced it to output its reasoning via a `thought_process` parameter in the tool schema. I accepted the theoretical risk of "Chain of Thought Forgery," though a public release would require **Context Scrubbing** (deleting the reasoning tokens from the permanent memory array) or upgrading to a model with native hidden reasoning (like `o1`).
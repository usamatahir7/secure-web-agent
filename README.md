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
This project requires an OpenAI API key to run the `gpt-4o-mini` model. **Do not hardcode your key into the files.** Instead, set it as an environment variable in your terminal:

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

* **Search Provider (DuckDuckGo):** I utilized the unofficial `duckduckgo-search` library instead of a robust enterprise API (like Tavily or Google Programmable Search). This was chosen to remove the friction of requiring reviewers to generate third-party search API keys, acknowledging that DDGS is prone to rate-limiting and poorer snippet quality in a true production environment.
* **DOM Sanitization vs. Headless Browser:** I used `BeautifulSoup` and `requests` for fast, lightweight DOM sanitization. Because `requests` cannot execute JavaScript, this harness will fail to read Single Page Applications (SPAs) like React sites. With more time, I would upgrade to an isolated, sandboxed Playwright/Puppeteer environment to safely render modern web pages.
* **Blunt Iframe Stripping:** The agent unconditionally destroys all `<iframe>` tags. While this protects against payload injection, it sacrifices usability by blinding the agent to legitimate embedded content (e.g., YouTube videos, Twitter embeds).
* **CoT Exposure Risk:** To ensure the smaller `gpt-4o-mini` model reliably generated accurate search queries and selected credible URLs, I forced it to output its reasoning via a `thought_process` parameter in the tool schema. I am assuming the risk of "Chain of Thought Poisoning" (where an attacker embeds fake thoughts into the HTML to confuse the model) is acceptable for this prototype, though Context Scrubbing or utilizing a model with native hidden reasoning (like `o1`) would be required for a public release.

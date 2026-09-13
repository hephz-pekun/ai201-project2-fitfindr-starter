# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This tool searches the thrift store listings and return items that match the user's requested style, category, size and price limit. It helps find the products before recommending

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): Represent the style, aesthetic or cloth description
- `size` (str): Represent the cloth size of the user
- `max_price` (float): Represnts the highest amount the user is willing to spend

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
It returns a list with listings that match. each listings has:
```python
{
    "id": int,
    "title": str,
    "description": str,
    "price": float,
    "size": str,
    "category": str,
    "style_tags": list[str],
    "brand": str,
    "platform": str
}
```

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
If there's no match. It should inform the user that no exact matches were found and it could recommend the closest alternative.

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This tool generates an outfit recommendation by combining a selected listing with items already in the user's wardrobe.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): Respresents the listing selected from search results.
- `wardrobe` (dict): Represnts data clothing items already in user's wardrobe.

**What it returns:**
<!-- Describe the return value -->
It returns the name of the outfits, the listings, and a reasoning explaining why. Kinda like this:
```python
{
    "outfit_name": str,
    "items": list,
    "style_reasoning": str
}
```

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
If the wardrobe is empty or there's no outfit suggested,inform the user or
provide general styling suggestions based only on the selected item.
---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This tool formats the final outfit recommendation into a user-friendly fashion card that summarizes the purchase recommendation and styling advice, so it can be shared.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): Represents the text that give recommendation of the outfit.
- `new_item` (dict): Represents the information of selected listiing.

**What it returns:**
<!-- Describe the return value -->
It should return the recommendation text containing the listing, price, summary and reasoning. Kinda like this:
```python
{
    "title": str,
    "listing": str,
    "price": float,
    "outfit_summary": str,
    "style_notes": str
}
```

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If the outfit data is incomplete rebuild the card using available information, omit the missing fields, and provide a text-only recommendation so the user still receives a result.
---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

### Tool 4: rank_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This tool Ranks candidate listings based on style match, budget fit, and wardrobe compatibility so the best items appear first.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
listings (list): Represents the candidate search results.
wardrobe (dict): Represent the user's wardrobe.
preferences (dict): Resprents the user's style preferences

**What it returns:**
<!-- Describe the return value -->
It should return a lsit of ranked listings and their respective scores. Kinda like this:
```python
{
    "ranked_listings": list,
    "scores": list
}
```

**What happens if it fails or returns nothing:**
<!-- What should the agent do if it fails? -->
If the agent fails it should fall back to the original search order and continue
---


### Tool 5: validate_budget

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This tool checks whether the recommended item is within the user's spending limit.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- listing (dict): Represents the candidate listing.
- budget (float): Represnts the user's budget.

**What it returns:**
<!-- Describe the return value -->
It should return t/f  if its within budget and remainder. Kinda like this:
```python
{
    "within_budget": bool,
    "remaining_budget": float
}
```

**What happens if it fails or returns nothing:**
<!-- What should the agent do if it fails? -->
If the tool fails assume that the item may exceed the budget and warns the user.
---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
1. Receive user request and store description, size, budget, and wardrobe in session state.

2. Call search_listings(description, size, max_price).

3. If search_results is empty:
    - Store an error message in session state.
    - Return "No matching listings found."
    - End workflow.

4. If search_results is not empty:
    - Save search_results in session state.
    - Call rank_listings(search_results, wardrobe, preferences).

5. Set selected_listing to the highest-ranked item.

6. Call validate_budget(selected_listing, budget).

7. If within_budget is False:
    - Select the next ranked listing.
    - Repeat budget validation.
    - If no listings remain, return an error message and end workflow.

8. Call suggest_outfit(selected_listing, wardrobe).

9. If wardrobe is empty:
    - Generate styling advice using only the selected item.

10. Save the generated outfit in session state.

11. Call create_fit_card(outfit, selected_listing).

12. Save fit_card in session state.

13. Return fit_card to the user.

14. End workflow.

The tool knows it is finished when:

A valid listing has been found,
an outfit recommendation has been generated, and
a fit card has been successfully created.
---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
A state object is shared, like...
```python
state = {
    "user_query": "",
    "user_size": "",
    "budget": 0,
    "wardrobe": {},
    "search_results": [],
    "selected_listing": None,
    "ranked_results": [],
    "recommended_outfit": None,
    "fit_card": None
}
```

Flows like this:
User Request
      ↓
search_listings
      ↓
search_results
      ↓
rank_listings
      ↓
selected_listing
      ↓
validate_budget
      ↓
suggest_outfit
      ↓
recommended_outfit
      ↓
create_fit_card
      ↓
fit_card
      ↓
Final Response

The state persists throughout the session so each tool can access outputs from previous tools without repeating work. If a tool fails, the agent uses existing state data to recover and continue whenever possible.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool              | Failure mode                          | Agent response                                                                                                                                                                      |
| ----------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| search\_listings  | No results match the query            | If there are no matches found, return a message such as: "I couldn't find an exact match for your search. Here are the closest alternatives under your budget." |
| search\_listings  | Invalid or missing input parameters   | If required fields are missing, prompt the user for the necessary information or use reasonable defaults.                                         |
| suggest\_outfit   | Wardrobe is empty                     | Create recommendations using only the selected listing and provide general styling advice. Notify the user that more wardrobe information would improve future suggestions.         |
| suggest\_outfit   | No compatible wardrobe items found    | Recommend the new item as a standalone purchase and suggest complementary clothing categories the user may already own.                                                             |
| create\_fit\_card | Outfit input is missing or incomplete | Generate a simplified fit card using available listing details and indicate which outfit information is unavailable.                                                                |
| create\_fit\_card | Formatting or rendering error         | Fall back to a plain-text recommendation summary so the user still receives a useful result.                                                                                        |
| rank\_listings    | Unable to calculate ranking scores    | Return listings in their original search order and continue with the recommendation process.                                                                                        |
| validate\_budget  | Budget information is missing         | Warn the user that budget validation could not be completed and continue with the recommendation while displaying the item's price.                                                 |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     Use ASCII art or a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html).
     Do NOT embed an image — graders need to read your diagram directly in the file;
     an embedded image or screenshot cannot be evaluated.
     You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

```text
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       │ Request:
       │ style, size, budget
       ▼
┌──────────────────┐
│   Planning Loop  │
└──────┬───────────┘
       │
       │ Read/Update
       | Writes user_query, size, budget
       ▼
┌──────────────────┐
│  Session State   │
│------------------│
│ user_query       │
│ budget           │
│ wardrobe         │
│ search_results   │
│ selected_item    │
│ outfit           │
│ fit_card         │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ search_listings  │
└──────┬───────────┘
       │search_results[] 
       |listings
       ▼
┌──────────────────┐
│  rank_listings   │
└──────┬───────────┘
       │ best item
       ▼
┌──────────────────┐
│ validate_budget  │
└──────┬───────────┘
       │ approved item
       ▼
┌──────────────────┐
│ suggest_outfit   │
└──────┬───────────┘
       │ outfit
       ▼
┌──────────────────┐
│ create_fit_card  │
└──────┬───────────┘
       │ fit card
       ▼
┌─────────────┐
│ Final Reply │
└─────────────┘


ERROR BRANCHES
===============

search_listings
       │
       ├─ No results found
       ▼
 Retry with broader filters
       │
       ├─ Success → Continue workflow
       ▼
 Terminate with "No matching items found"


suggest_outfit
       │
       ├─ Empty wardrobe
       ▼
 Generate basic styling advice
       │
       ▼
 Continue workflow


create_fit_card
       │
       ├─ Missing outfit data
       ▼
 Create simplified text-only card
       │
       ▼
 Continue workflow
```
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**
#### search_listings

- AI Tool Used: Microsoft Copilot
- Input Provided:
     - Tool 1 specification from planning.md
     - Function stub and docstring from tools.py
     - Dataset schema from listings.json
- Expected Output:
     - A search function that loads listings, filters by size and price, scores listings based on keyword relevance, and returns sorted results.
- Verification:
     - Ran pytest tests for successful searches, empty results, and price filtering.
     - Tested manually with queries such as:
          - "vintage graphic tee under $30"
          - "flowy midi skirt under $40"
          - "designer ballgown size XXS under $5"
     - Confirmed empty searches return an empty list rather than raising an exception.

#### suggest_outfit
- AI Tool Used: Microsoft Copilot
- Input Provided:
     - Tool 2 specification from planning.md
     - Function stub and docstring from tools.py
     - Wardrobe schema and example wardrobe
- Expected Output:
     - A function that sends the selected item and wardrobe information to the Groq LLM and returns outfit suggestions.
- Verification:
     - Tested with both example and empty wardrobes.
     - Confirmed the function returns styling advice when the wardrobe is empty.
     - Confirmed the function returns a non-empty string and does not crash.

#### create_fit_card
- AI Tool Used: Microsoft Copilot
- Input Provided:
     - Tool 3 specification from planning.md
     - Function stub and docstring from tools.py
- Expected Output:
     - A function that generates a social-media style outfit caption using the selected item and outfit suggestion.
- Verification:
     - Tested using multiple outfit suggestions.
     - Confirmed empty outfit input returns an error message string instead of causing a crash.
     - Confirmed generated captions include the item, price, and platform.

### Milestone 4 — Planning loop and state management

- AI Tool Used: Microsoft Copilot
- Input Provided:
     - Planning Loop section from planning.md
     - State Management section from planning.md
     - Architecture diagram
     - agent.py function stub
- Expected Output:
     - A run_agent() implementation that coordinates tool calls and updates session state.
- Verification:
     - Confirmed search results are stored in session["search_results"].
     - Confirmed the selected item is stored in session["selected_item"].
     - Confirmed the outfit suggestion is stored in session["outfit_suggestion"].
     - Confirmed the fit card is stored in session["fit_card"].
     - Confirmed the no-results branch returns early and does not call suggest_outfit() or create_fit_card().

**Milestone 4 — Gradio Integration:**
- AI Tool Used: Microsoft Copilot
- Input Provided:
     - handle_query() requirements from app.py
     - State structure from planning.md
- Expected Output:
     - A function that takes user input, calls run_agent(), and formats results for display in the interface.
- Verification:
     - Tested valid queries and confirmed all three output panels populate correctly.
     - Tested invalid queries and confirmed error messages appear in the listing panel while the other panels remain empty.
---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The user submits the query through the FitFindr interface.
The agent initializes a new session object:
{
"query": "...",
"parsed": {},
"search_results": [],
"selected_item": None,
"wardrobe": {...},
"outfit_suggestion": None,
"fit_card": None,
"error": None
}

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
The planning loop parses the query and extracts:
{
"description": "vintage graphic tee under $30",
"size": None,
"max_price": 30
}
The parsed values are stored in:
session["parsed"]

**Step 3:**
<!-- Continue until the full interaction is complete -->
The agent calls:
search_listings(
description="vintage graphic tee under $30",
size=None,
max_price=30
)
The tool searches the listings dataset and returns a ranked list of matching items.
The results are stored in:
session["search_results"]

### Step 4
The planning loop checks if any results were found.
If the results list is empty:
- session["error"] is populated.
- The agent returns early.
In this example, matching items are found.

### Step 5
The highest-ranked listing is selected and stored:
session["selected_item"]
Example:
{
"title": "Vintage Graphic Hoodie — Faded Black",
"price": 25,
...
}

### Step 6
The agent calls:
suggest_outfit(
session["selected_item"],
session["wardrobe"]
)

The tool sends the selected item and wardrobe information to the LLM and receives outfit recommendations.
The response is stored in:
session["outfit_suggestion"]

### Step 7
The agent calls:
create_fit_card(
session["outfit_suggestion"],
session["selected_item"]
)
The tool generates a social-media style caption describing the outfit.
The response is stored in:
session["fit_card"]

### Step 8
The planning loop confirms:
- Search completed successfully.
- A listing was selected.
- An outfit was generated.
- A fit card was generated.
The completed session is returned to the interface.

**Final output to user:**
<!-- What does the user actually see at the end? -->
Top Listing Found:
Title: Vintage Graphic Hoodie — Faded Black
Price: $25
Platform: Depop
Description: Oversized vintage-inspired hoodie with faded graphics and a relaxed fit.

Outfit Idea:
Pair the hoodie with baggy jeans and chunky sneakers for a relaxed vintage streetwear look. Add a crossbody bag and layered accessories for extra texture and personality.

Your Fit Card:
Just picked up this faded vintage graphic hoodie on Depop for $25 and it instantly became the centerpiece of today's fit. Paired it with baggy jeans and chunky sneakers for an easy vintage streetwear vibe. Comfortable, relaxed, and perfect for everyday wear.
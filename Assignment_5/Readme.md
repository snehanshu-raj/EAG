# PDF Query Agentic Project

Have lots of PDF? Notes? This is a basic (version 1) agent where you can give a query/topic which you want to search from your lecture notes and the agent will pin point open the exact page in the exact PDF where that topic is present in a new, navigable window.

The LLM:
- Receives a task query.
- Decides what tool to invoke next.
- Executes tools (e.g., PDF matchers, viewers).
- Stores state across multiple turns.
- Follows structured prompting and schema validation.

---

## 🧠 High-Level Workflow

1. **User gives a query** (e.g., "Find where stable matching is taught").
2. The system builds a prompt with tool descriptions and state.
3. Gemini generates a structured JSON with:
   - tool to call
   - parameters
   - reasoning type
4. Tool is executed.
5. Result is logged and fed into the next reasoning iteration.

---

## 🧩 Project Structure & Responsibilities

- ├── ll_perception.py # Calls Gemini API and validates JSON responses 
- ├── memory_handler.py # Handles iteration state tracking and persistence 
- ├── action_performer.py # Executes tools and maps arguments based on schema 
- ├── decision_maker.py # Prepares LLM prompt based on context, tools, and memory
- ├── pdf_handler.py # To handle PDF related operations upon successfull search


---

## 🗂 Module Breakdown

### 📍 `ll_perception.py`
- Responsible for:
  - Sending prompts to the Gemini LLM
  - Handling timeouts
  - Enforcing response schema (`Response` model)
  - Validating that the response is JSON and structurally correct
- Key function: `generate_with_timeout(prompt, timeout)`
- Output: a `Response` object or error

### 🧠 `memory_handler.py`
- Maintains decision-making memory across multiple iterations.
- Uses a local `state.json` file to:
  - Save tool calls, arguments, and LLM responses
  - Load and clear history
- Key functions:
  - `load_state()`
  - `add_iteration(response)`
  - `clear_state()`

### 🛠 `action_performer.py`
- Takes a selected tool and arguments decided by the LLM and **executes it**.
- Dynamically:
  - Maps and converts `params` to correct types using the tool's input schema.
  - Returns structured output from the tool's response.
- Key function: `execute_tool(session, tool, func_name, params)`

### 🤖 `decision_maker.py`
- Assembles the complete system prompt to be passed to the LLM.
- Pulls:
  - Tool descriptions (name, parameters, description)
  - Current decision memory
  - User's original query
- Key functions:
  - `create_tool_descriptions(tools)`
  - `construct_prompt(tools_desc, original_query)`
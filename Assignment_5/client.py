import asyncio
import sys
import traceback

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from llm_perception import generate_with_timeout, validate_response
from decision_maker import create_tool_descriptions, construct_prompt
from action_performer import execute_tool
from memory_handler import add_iteration, clear_state

MAX_ITERATIONS = 25

async def main(query):
    clear_state()
    iteration_count = 0

    server_params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            tool_desc = create_tool_descriptions(tools)

            while iteration_count < MAX_ITERATIONS:
                print(f"\n--- Iteration {iteration_count + 1} ---")
                
                prompt = construct_prompt(tool_desc, query)

                try:
                    response = await generate_with_timeout(prompt)
                    parsed_llm_response = validate_response(response.text)
                except Exception as e:
                    add_iteration(f"Issue in JSON response schema from LLM as: {e}")
                    iteration_count += 1
                    continue

                func_name = parsed_llm_response.get("function_name")
                if func_name and func_name != "None":
                    try:
                        tool = next(t for t in tools if t.name == func_name)
                        args, output = await execute_tool(session, tool, func_name, parsed_llm_response["params"])
                        # print(output)
                        # print(type(output))
                        
                        result = {
                            "llm_response": parsed_llm_response,
                            "tool": func_name,
                            "params": args,
                            "result": output,
                        }
                        add_iteration(result)

                        if func_name == "finish_task":
                            print(f"{output}")
                            break
                    except Exception as e:
                        traceback.print_exc()
                        add_iteration(f"Error executing {func_name}: {e}")
                        break
                else:
                    add_iteration({"Exception": parsed_llm_response})

                iteration_count += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<your query>\"")
        sys.exit(1)
    query_input = sys.argv[1]
    asyncio.run(main(query_input))

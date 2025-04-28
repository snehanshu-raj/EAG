import traceback
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from credentials import config
from mcp.client.sse import sse_client
from mcp import ClientSession

from llm_perception import generate_with_timeout, validate_response
from decision_maker import create_tool_descriptions, construct_prompt
from action_performer import execute_tool
from memory_handler import add_iteration, clear_state

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs.log",
    format='%(asctime)s - %(process)d - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

BOT_TOKEN = config.telegram_token
MAX_ITERATIONS = 25

async def client(query):
    clear_state()
    iteration_count = 0

    async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
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
                
                logger.info(f"Parsed llm response: {parsed_llm_response}")
                func_name = parsed_llm_response.get("function_name")
                if func_name and func_name != "None":
                    try:
                        tool = next(t for t in tools if t.name == func_name)
                        args, output = await execute_tool(session, tool, func_name, parsed_llm_response["params"])
                        
                        result = {
                            "llm_response": parsed_llm_response,
                            "tool": func_name,
                            "params": args,
                            "result": output,
                        }
                        add_iteration(result)

                        if func_name == "finish_task":
                            print(f"{output}")
                            return output
                    except Exception as e:
                        traceback.print_exc()
                        add_iteration(f"Error executing {func_name}: {e}")
                        return str(e)
                else:
                    add_iteration({"Exception": parsed_llm_response})

                iteration_count += 1

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    incoming_text = update.message.text
    print(f"Received message: {incoming_text}")

    response = await client(incoming_text)
    await update.message.reply_text(response)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

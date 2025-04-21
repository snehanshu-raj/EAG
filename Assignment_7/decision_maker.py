from prompt import prefix_prompt, main_prompt
from memory_handler import load_state

def create_tool_descriptions(tools):
    descriptions = []
    for i, tool in enumerate(tools):
        try:
            name = getattr(tool, 'name', f'tool_{i}')
            desc = getattr(tool, 'description', 'No description available')
            props = tool.inputSchema.get('properties', {})
            param_details = [f"{p}: {info.get('type', 'unknown')}" for p, info in props.items()]
            params_str = ', '.join(param_details) if param_details else 'no parameters'
            descriptions.append(f"{i+1}. {name}({params_str}) - {desc}")
        except Exception as e:
            descriptions.append(f"{i+1}. Error processing tool")
    return "\n".join(descriptions)

def construct_prompt(tools_desc: str, original_query: str, image_present: str, type: str) -> str:
    context = f"{prefix_prompt}: {tools_desc} \
                {main_prompt}"
    image_msg = "An image has been provided by the user." if image_present == "True" else "No image was provided."
    history = load_state()
    return f"Context: {context} \
             Query string: {original_query} \
             Image presence info: {image_msg} \
             Search Type: {type} \
             Decision History which has been taken for this task: {history} \
             Now what should I do next? "

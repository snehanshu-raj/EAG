import json
from ast import literal_eval

async def execute_tool(session, tool, func_name, params):
    arguments = {}
    schema = tool.inputSchema.get('properties', {})
    
    for param_name, info in schema.items():
        if not params:
            raise ValueError(f"Not enough parameters for {func_name}")
        value = params.pop(0)
        ptype = info.get('type', 'string')
        if ptype == 'integer':
            arguments[param_name] = int(value)
        elif ptype == 'number':
            arguments[param_name] = float(value)
        elif ptype == 'array':
            arguments[param_name] = [int(v.strip()) for v in value.strip('[]').split(',')]
        else:
            arguments[param_name] = str(value)
    
    result = await session.call_tool(func_name, arguments=arguments)
    
    # if hasattr(result, 'content'):
    #     print(f"Yes for result: {result}")
    #     if isinstance(result.content, list):
    #         output = [item.text if hasattr(item, 'text') else item for item in result.content]
    #         print("list instance")
    #     else:
    #         output = result.content
    # else:
    #     output = result
    
    return arguments, literal_eval(json.loads(json.dumps(result.content[0].text)))

import json
from ast import literal_eval

async def execute_tool(session, tool, func_name, params: dict, image_bytes):
    arguments = {}
    schema = tool.inputSchema.get('properties', {})

    for param_name, info in schema.items():
        if param_name not in params:
            raise ValueError(f"Missing parameter '{param_name}' for function '{func_name}'")
        
        value = params[param_name]
        ptype = info.get('type', 'string')

        if ptype == 'integer':
            arguments[param_name] = int(value)
        elif ptype == 'number':
            arguments[param_name] = float(value)
        elif ptype == 'array':
            if isinstance(value, str):
                arguments[param_name] = [v.strip() for v in value.strip('[]').split(',')]
            else:
                arguments[param_name] = value
        else:
            arguments[param_name] = str(value) if value is not None else None

    if (arguments["image_bytes"] == "True"):
        arguments['image_bytes'] = image_bytes
    else:
        arguments["image_bytes"] = "None"

    result = await session.call_tool(func_name, arguments=arguments)
    return arguments, literal_eval(json.loads(json.dumps(result.content[0].text)))


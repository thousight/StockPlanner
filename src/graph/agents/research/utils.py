import inspect

async def execute_tool(step, tools_list, user_agent="", subject=None):
    """
    Executes a tool from a given list of tools based on the step definition.
    """
    # Build a lookup mapping for tool names from the provided function list
    tool_map = {tool.__name__: tool for tool in tools_list}
    tool = tool_map.get(step.tool_name)
    if tool:
        try:
            # Check if the tool accepts a user_agent parameter or **kwargs
            sig = inspect.signature(tool)
            params = sig.parameters
            accepts_kwargs = any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()
            )
            
            if "user_agent" in params or accepts_kwargs:
                step.tool_params["user_agent"] = user_agent
                
            # AUTO-MAPPING for missing symbol/ticker from global subject
            if subject:
                # 1. Map to 'symbol' if missing but required
                if "symbol" in params and "symbol" not in step.tool_params:
                    step.tool_params["symbol"] = subject
                # 2. Map to 'ticker' if missing but required
                if "ticker" in params and "ticker" not in step.tool_params:
                    step.tool_params["ticker"] = subject
                # 3. Fallback for mixed naming
                if step.tool_name == "get_stock_financials" and "symbol" not in step.tool_params:
                    step.tool_params["symbol"] = subject

            # Quick fix for web_search arguments
            if step.tool_name == "web_search":
                if "query" in step.tool_params and "queries" not in step.tool_params:
                    step.tool_params["queries"] = [step.tool_params.pop("query")]
                elif "q" in step.tool_params and "queries" not in step.tool_params:
                    step.tool_params["queries"] = [step.tool_params.pop("q")]
                elif "queries" in step.tool_params and isinstance(step.tool_params["queries"], str):
                    step.tool_params["queries"] = [step.tool_params["queries"]]
                elif "queries" not in step.tool_params:
                    # Fallback if somehow it's empty but called
                    step.tool_params["queries"] = ["latest market news"]
                
            # Execute standard function with unpacked dictionary parameters
            if inspect.iscoroutinefunction(tool):
                result = await tool(**step.tool_params)
            else:
                result = tool(**step.tool_params)
                
            if isinstance(result, str):
                return result
            return str(result) + "\n"
        except Exception as e:
            print(f"Error executing tool {step.tool_name}: {e}")
            return f"Error executing tool {step.tool_name}: {e}\n"
    else:
            print(f"Tool {step.tool_name} not found in the allowed tools list.")
            return f"Tool {step.tool_name} not found.\n"

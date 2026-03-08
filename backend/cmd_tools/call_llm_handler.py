"""
CallLLM command handler
Calls an LLM with a system prompt and parameters using existing call_llm function
"""

import json
import logging
from typing import Dict, Any
import gridfs
from cmd_tools.youtube.utils.call_llm import call_llm

logger = logging.getLogger('call_llm')

async def call_llm_handler(args: Dict[str, Any], db, fs: gridfs.GridFS) -> Dict[str, Any]:
    """
    Call an LLM with a system prompt and parameters
    
    Args:
        args: Dict containing:
            - 'prompt': System prompt for the LLM
            - 'params': Dictionary of parameters to pass to the LLM (will be formatted into the user message)
            - 'output_schema': Optional JSON schema describing expected output structure
            - 'model': Optional model name (ignored for now, uses gpt-4o from existing implementation)
            - 'temperature': Optional temperature (ignored for now, uses default from existing implementation)
        db: MongoDB database connection
        fs: GridFS instance
        
    Returns:
        Dict containing:
            - 'success': boolean
            - 'llm_response': The LLM's response text
            - 'parsed_output': If output_schema provided, the parsed JSON object
    """
    
    # Extract parameters
    system_prompt = args.get("prompt")
    params = args.get("params", {})
    output_schema = args.get("output_schema")
    
    if not system_prompt:
        raise ValueError("No prompt provided for LLM call")
    
    logger.info(f"Calling LLM with prompt length: {len(system_prompt)} chars")
    logger.info(f"Parameters: {list(params.keys())}")
    
    # Build full prompt: system prompt + formatted parameters
    prompt_parts = [system_prompt]
    
    if params:
        prompt_parts.append("\n\n---INPUT DATA---")
        for key, value in params.items():
            if isinstance(value, (dict, list)):
                prompt_parts.append(f"\n{key}:\n{json.dumps(value, indent=2)}")
            else:
                prompt_parts.append(f"\n{key}: {value}")
    
    # Add output schema instruction if provided
    if output_schema:
        schema_instruction = f"\n\n---REQUIRED OUTPUT FORMAT---\nYou MUST respond with a valid JSON object matching this schema:\n{json.dumps(output_schema, indent=2)}"
        prompt_parts.append(schema_instruction)
        prompt_parts.append("\n\nRespond ONLY with the JSON object, no additional text.")
    
    full_prompt = "".join(prompt_parts)
    
    logger.info(f"Full prompt length: {len(full_prompt)} chars")
    
    # Make the API call using existing call_llm function
    try:
        llm_response = await call_llm(full_prompt)
        
        logger.info(f"LLM response length: {len(llm_response)} chars")
        
        result = {
            "success": True,
            "llm_response": llm_response,
            "model_used": "gpt-4o"  # From existing implementation
        }
        
        # Parse JSON if output_schema was provided
        if output_schema:
            try:
                # Try to extract JSON from response (in case LLM added extra text)
                response_text = llm_response.strip()
                
                # Find JSON object boundaries
                if '{' in response_text:
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    json_str = response_text[start_idx:end_idx]
                    parsed_output = json.loads(json_str)
                else:
                    # Try parsing the whole response
                    parsed_output = json.loads(response_text)
                
                result["parsed_output"] = parsed_output
                logger.info(f"Successfully parsed JSON output")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.error(f"Response was: {llm_response[:500]}")
                result["parse_error"] = str(e)
                result["raw_response"] = llm_response
        
        return result
        
    except Exception as e:
        logger.error(f"LLM API call failed: {str(e)}")
        raise Exception(f"Failed to call LLM: {str(e)}")

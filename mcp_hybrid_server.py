#!/usr/bin/env python3
import json
import sys
import asyncio
import requests
import sys
sys.path.append(r'H:\ACTOR_DEV_ENV')
from hybrid_llm_engine_v2 import HybridLLMEngineV2

class HybridMCPServer:
    def __init__(self):
        self.engine = HybridLLMEngineV2()
        self.default_model = "qwen2.5:3b"

    async def handle_request(self, request: dict) -> dict:
        method = request.get("method")
        params = request.get("params", {})
        if method == "tools/list":
            return self.list_tools()
        elif method == "tools/call":
            return await self.call_tool(params)
        elif method == "resources/list":
            return {"resources": []}
        return {"error": f"Unknown method: {method}"}

    def list_tools(self) -> dict:
        return {
            "tools": [
                {
                    "name": "analyze_file",
                    "description": "Analyze a file using hybrid engine",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "model": {"type": "string"}
                        },
                        "required": ["file_path"]
                    }
                }
            ]
        }

    async def call_tool(self, params: dict) -> dict:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        if tool_name == "analyze_file":
            result = self.engine.analyze_file(arguments.get("file_path"), arguments.get("model", self.default_model))
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
        return {"error": f"Unknown tool: {tool_name}"}

    async def run(self):
        while True:
            line = sys.stdin.readline()
            if not line: break
            try:
                request = json.loads(line)
                response = await self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except Exception as e:
                pass
if __name__ == "__main__":
    asyncio.run(HybridMCPServer().run())

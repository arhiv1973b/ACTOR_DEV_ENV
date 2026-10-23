# Start-MCPFilesystem.ps1

docker rm -f mcp_filesystem_full | Out-Null

docker run -i --rm --name mcp_filesystem_full 
  -v "H:\ACTOR_DEV_ENV\run:/run" 
  -v "C:\Users\arhiv:/arhiv" 
  mcp/filesystem /run /arhiv

gemini mcp remove MCP_DOCKER | Out-Null
gemini mcp add MCP_DOCKER "docker run -i --rm -v H:\ACTOR_DEV_ENV\run:/run -v C:\Users\arhiv:/arhiv mcp/filesystem /run /arhiv"
gemini mcp enable MCP_DOCKER
gemini mcp list

opencode mcp remove MCP_DOCKER | Out-Null
opencode mcp add MCP_DOCKER "docker run -i --rm -v H:\ACTOR_DEV_ENV\run:/run -v C:\Users\arhiv:/arhiv mcp/filesystem /run /arhiv"
opencode mcp enable MCP_DOCKER
opencode mcp list

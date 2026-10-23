import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    async with stdio_client(StdioServerParameters(command='python', args=['H:\\ACTOR_DEV_ENV\\mcp_server.py'])) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print('[TEST] Calling verify_artifact...')
            res = await s.call_tool('verify_artifact', arguments={'artifact_path': 'H:\\ACTOR_DEV_ENV\\test.txt'})
            print(f'[RESULT] {res.content}')
            
            print('[TEST] Calling run_model (anomaly)...')
            res = await s.call_tool('run_model', arguments={'model_type': 'anomaly', 'audit_events': [{'type': 'file.access'}]})
            print(f'[RESULT] {res.content}')

asyncio.run(main())

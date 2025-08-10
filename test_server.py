from fastmcp import Client

async def main():
    # Connect via stdio to a local script
    async with Client("server.py") as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        
        # Test web_search tool and get result
        print("\n🔍 Testing web_search tool:")
        search_result = await client.call_tool("web_search", {"query": "What is the capital of France?"})
        print(f"Web Search Result: {search_result}")

        # Write the search result to clipboard via tool
        print("\n📋 Writing to clipboard via tool:")
        _ = await client.call_tool("write_clipboard", {"text": str(search_result)})

        # Read back from clipboard to confirm
        print("\n📋 Reading from clipboard via tool:")
        clip = await client.call_tool("read_clipboard", {})
        print(f"Clipboard: {clip}")

        # Send clipboard via email using send_gmail
        print("\n📧 Sending clipboard via send_gmail:")
        email_result = await client.call_tool("send_gmail", {
            "to": "debanshudas1992@gmail.com",
            "subject": "Clipboard: Web Search Result",
            "body": f"Clipboard contents as sent by MCP:\n\n{clip}"
        })
        print(f"Email Result: {email_result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())